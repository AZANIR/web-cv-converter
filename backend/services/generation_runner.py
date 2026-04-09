"""Pipeline: vacancy → templatize → semantic search → generate CV markdown."""

import asyncio
import json
import logging
from datetime import datetime

from core.ai_client import get_ai_client
from core.supabase import get_supabase
from services import embedding_service, prompt_service, vacancy_parser

logger = logging.getLogger(__name__)


def _generate_md_with_ai(full_prompt: str) -> str:
    """Call AI to generate CV markdown from the assembled prompt."""
    client = get_ai_client()
    return client.generate(full_prompt, temperature=0.7)


async def run_generation_pipeline(vacancy_id: str, cv_id: str) -> None:
    sb = get_supabase()

    vacancy_row = sb.table("vacancies").select("*").eq("id", vacancy_id).limit(1).execute()
    if not vacancy_row.data:
        return
    vacancy = vacancy_row.data[0]
    raw_input = vacancy["raw_input"]

    try:
        sb.table("vacancies").update({"status": "processing"}).eq("id", vacancy_id).execute()
        sb.table("generated_cvs").update({"status": "generating"}).eq("id", cv_id).execute()

        # 1. Templatize vacancy into case study
        templatize_prompt = prompt_service.get_prompt("vacancy_to_case_study")
        case_study_json = await asyncio.to_thread(
            vacancy_parser.templatize_vacancy, raw_input, templatize_prompt
        )
        case_study_md = json.dumps(case_study_json, indent=2, ensure_ascii=False)

        sb.table("vacancies").update({
            "case_study_json": case_study_json,
            "case_study_md": case_study_md,
            "status": "completed",
        }).eq("id", vacancy_id).execute()

        # 2. Vectorize the vacancy
        await asyncio.to_thread(
            embedding_service.store_embedding,
            doc_type="vacancy",
            content=case_study_md,
            metadata=case_study_json.get("tags", []),
            doc_id=vacancy_id,
        )

        # 3. Semantic search for relevant context
        search_query = case_study_md
        case_studies = await asyncio.to_thread(
            embedding_service.search_similar, search_query, "case_study", 3
        )
        past_cvs = await asyncio.to_thread(
            embedding_service.search_similar, search_query, "generated_cv", 2
        )

        cs_text = "\n\n---\n\n".join(doc["content"] for doc in case_studies) if case_studies else "(none available)"
        cv_text = "\n\n---\n\n".join(doc["content"] for doc in past_cvs) if past_cvs else "(none yet)"

        # 4. Assemble and run CV generation prompt
        current_month_year = datetime.now().strftime("%B %Y")
        generation_prompt = prompt_service.render_prompt("cv_generation", {
            "VACANCY_CASE_STUDY": case_study_md,
            "RELEVANT_CASE_STUDIES": cs_text,
            "RELEVANT_PAST_CVS": cv_text,
            "CURRENT_MONTH_YEAR": current_month_year,
        })

        md_content = await asyncio.to_thread(_generate_md_with_ai, generation_prompt)

        # 5. Save generated CV
        sb.table("generated_cvs").update({
            "md_content": md_content,
            "status": "draft",
            "error_message": None,
        }).eq("id", cv_id).execute()

        # 6. Vectorize the generated CV
        await asyncio.to_thread(
            embedding_service.store_embedding,
            doc_type="generated_cv",
            content=md_content,
            metadata={"vacancy_id": vacancy_id, "tags": case_study_json.get("tags", [])},
            doc_id=cv_id,
        )

    except Exception as e:
        logger.exception("Generation pipeline failed for vacancy=%s cv=%s", vacancy_id, cv_id)
        sb.table("vacancies").update({
            "status": "failed",
            "error_message": str(e)[:2000],
        }).eq("id", vacancy_id).execute()
        sb.table("generated_cvs").update({
            "status": "failed",
            "error_message": str(e)[:2000],
        }).eq("id", cv_id).execute()


_running_tasks: set[asyncio.Task] = set()


def schedule_generation(vacancy_id: str, cv_id: str) -> None:
    task = asyncio.create_task(run_generation_pipeline(vacancy_id, cv_id))
    _running_tasks.add(task)
    task.add_done_callback(_running_tasks.discard)


async def recover_pending_generations() -> None:
    """On startup, reschedule generations stuck in pending/generating state."""
    sb = get_supabase()
    res = (
        sb.table("generated_cvs")
        .select("id, vacancy_id")
        .in_("status", ["pending", "generating"])
        .execute()
    )
    if res.data:
        logger.info("Recovering %d stuck generation(s)", len(res.data))
        for row in res.data:
            schedule_generation(row["vacancy_id"], row["id"])
