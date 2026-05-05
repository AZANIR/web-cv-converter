import asyncio
import logging

from core.config import get_settings
from core.supabase import get_supabase
from services import ai_service, pdf_service, storage_service

logger = logging.getLogger(__name__)

_MAX_CONCURRENT_TASKS = 10
_semaphore = asyncio.Semaphore(_MAX_CONCURRENT_TASKS)


async def run_conversion_pipeline(conversion_id: str) -> None:
    async with _semaphore:
        sb = get_supabase()
        settings = get_settings()
        res = sb.table("conversions").select("*").eq("id", conversion_id).limit(1).execute()
        if not res.data:
            return
        conv = res.data[0]
        md = conv["md_content"]
        user_id = conv["user_id"]
        orig_name = conv["original_filename"]
        include_header = conv.get("include_header", True)
        if include_header is None:
            include_header = True

        try:
            sb.table("conversions").update({"status": "processing"}).eq("id", conversion_id).execute()

            cv_json = await asyncio.wait_for(
                asyncio.to_thread(ai_service.convert_md_to_json, md),
                timeout=settings.conversion_ai_timeout_seconds,
            )
            pdf_bytes = await asyncio.to_thread(pdf_service.generate_pdf, cv_json, include_header)
            path, pdf_name = await asyncio.to_thread(
                storage_service.upload_pdf, pdf_bytes, user_id, orig_name
            )

            sb.table("conversions").update(
                {
                    "status": "completed",
                    "json_data": cv_json,
                    "pdf_storage_path": path,
                    "pdf_filename": pdf_name,
                    "error_message": None,
                }
            ).eq("id", conversion_id).execute()
        except TimeoutError:
            logger.exception("Conversion %s timed out during AI step", conversion_id)
            sb.table("conversions").update(
                {
                    "status": "failed",
                    "error_message": (
                        "AI conversion timed out. Please retry in a minute."
                    ),
                }
            ).eq("id", conversion_id).execute()
        except Exception:
            logger.exception("Conversion %s failed", conversion_id)
            sb.table("conversions").update(
                {
                    "status": "failed",
                    "error_message": "Conversion failed. Please try again or contact support.",
                }
            ).eq("id", conversion_id).execute()


_running_tasks: set[asyncio.Task] = set()


def schedule_conversion(conversion_id: str) -> None:
    task = asyncio.create_task(run_conversion_pipeline(conversion_id))
    _running_tasks.add(task)
    task.add_done_callback(_running_tasks.discard)


async def recover_pending_conversions() -> None:
    """On startup, reschedule conversions stuck in pending/processing state."""
    sb = get_supabase()
    res = sb.table("conversions").select("id").in_("status", ["pending", "processing"]).execute()
    if res.data:
        logger.info("Recovering %d stuck conversion(s)", len(res.data))
        for row in res.data:
            schedule_conversion(row["id"])
