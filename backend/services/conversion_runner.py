import asyncio
import logging

from core.supabase import get_supabase
from services import ai_service, pdf_service, storage_service

logger = logging.getLogger(__name__)


async def run_conversion_pipeline(conversion_id: str) -> None:
    sb = get_supabase()
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

        cv_json = await asyncio.to_thread(ai_service.convert_md_to_json, md)
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
    except Exception as e:
        logger.exception("Conversion %s failed", conversion_id)
        sb.table("conversions").update(
            {
                "status": "failed",
                "error_message": str(e)[:2000],
            }
        ).eq("id", conversion_id).execute()


def schedule_conversion(conversion_id: str) -> None:
    asyncio.create_task(run_conversion_pipeline(conversion_id))
