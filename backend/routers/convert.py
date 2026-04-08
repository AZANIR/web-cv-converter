import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from supabase import Client

from core.auth import get_current_user
from core.config import get_settings
from core.supabase import get_supabase
from services.conversion_runner import schedule_conversion
from services.rate_limit import check_and_record_conversion

logger = logging.getLogger(__name__)

router = APIRouter(tags=["convert"])


@router.post("/convert")
async def convert_cv(
    file: UploadFile = File(...),
    include_header: bool = Form(True),
    user: dict = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    s = get_settings()
    if not file.filename or not file.filename.lower().endswith(".md"):
        raise HTTPException(status_code=400, detail="Only .md files are allowed")

    raw = await file.read()
    if len(raw) > s.max_upload_bytes:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")

    try:
        md_content = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 text")

    check_and_record_conversion(user["user_id"], sb)

    conversion_id = str(uuid.uuid4())
    sb.table("conversions").insert(
        {
            "id": conversion_id,
            "user_id": user["user_id"],
            "original_filename": file.filename,
            "md_content": md_content,
            "status": "pending",
            "include_header": include_header,
        }
    ).execute()

    schedule_conversion(conversion_id)

    return {"conversion_id": conversion_id}


@router.get("/conversions/{conversion_id}")
async def get_conversion_status(
    conversion_id: str,
    user: dict = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    res = sb.table("conversions").select("*").eq("id", conversion_id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Not found")
    row = res.data[0]
    if row["user_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="Not found")

    out = {
        "id": row["id"],
        "status": row["status"],
        "original_filename": row["original_filename"],
        "error_message": row.get("error_message"),
        "created_at": row.get("created_at"),
    }
    if row["status"] == "completed" and row.get("pdf_storage_path"):
        from services import storage_service

        try:
            out["download_url"] = storage_service.get_signed_url(row["pdf_storage_path"])
        except Exception as e:
            logger.warning(
                "Failed to get download_url for conversion %s (path=%r): %s",
                conversion_id,
                row["pdf_storage_path"],
                e,
                exc_info=True,
            )
            out["download_url"] = None
    return out


@router.post("/regenerate/{conversion_id}")
async def regenerate_cv(
    conversion_id: str,
    user: dict = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    res = sb.table("conversions").select("*").eq("id", conversion_id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Not found")
    row = res.data[0]
    if row["user_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="Not found")

    check_and_record_conversion(user["user_id"], sb)

    sb.table("conversions").update(
        {
            "status": "pending",
            "error_message": None,
            "json_data": None,
            "pdf_storage_path": None,
            "pdf_filename": None,
        }
    ).eq("id", conversion_id).execute()

    schedule_conversion(conversion_id)

    return {"conversion_id": conversion_id}
