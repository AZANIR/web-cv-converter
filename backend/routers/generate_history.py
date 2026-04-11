"""History endpoint for generated CVs, extracted from generate.py."""

from fastapi import APIRouter, Depends
from supabase import Client

from core.auth import get_current_user
from core.supabase import get_supabase

router = APIRouter(prefix="/generate", tags=["generate"])


def _build_vacancy_map(sb: Client, vacancy_ids: list[str]) -> dict[str, dict]:
    """Fetch vacancy metadata and return a dict keyed by vacancy id."""
    if not vacancy_ids:
        return {}
    vres = (
        sb.table("vacancies")
        .select("id,case_study_json,input_type,original_filename")
        .in_("id", vacancy_ids)
        .execute()
    )
    return {v["id"]: v for v in vres.data or []}


def _enrich_items(items: list[dict], vacancy_map: dict[str, dict]) -> None:
    """Add vacancy_title and input_type to each history item in-place."""
    for row in items:
        v = vacancy_map.get(row.get("vacancy_id"), {})
        cs = v.get("case_study_json") or {}
        row["vacancy_title"] = cs.get("title", v.get("original_filename", "Untitled"))
        row["input_type"] = v.get("input_type")


@router.get("/history")
async def generation_history(user: dict = Depends(get_current_user), sb: Client = Depends(get_supabase)):
    res = (
        sb.table("generated_cvs")
        .select("id,vacancy_id,status,pdf_filename,created_at,error_message")
        .eq("user_id", user["user_id"])
        .order("created_at", desc=True)
        .execute()
    )
    items = res.data or []

    vacancy_ids = list({r["vacancy_id"] for r in items if r.get("vacancy_id")})
    vacancy_map = _build_vacancy_map(sb, vacancy_ids)
    _enrich_items(items, vacancy_map)

    return {"items": items}
