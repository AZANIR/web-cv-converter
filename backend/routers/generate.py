"""API endpoints for CV generation from vacancy input."""

import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from supabase import Client

from core.auth import get_current_user
from core.config import get_settings
from core.supabase import get_supabase
from services.conversion_runner import schedule_conversion
from services.generation_runner import schedule_generation
from services.rate_limit import check_and_record_conversion
from services import vacancy_parser, embedding_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("")
async def generate_cv(
    vacancy_text: str = Form(None),
    vacancy_url: str = Form(None),
    file: UploadFile | None = File(None),
    user: dict = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Create a CV from a vacancy. Accepts text, URL, or file upload."""
    if not vacancy_text and not vacancy_url and not file:
        raise HTTPException(status_code=400, detail="Provide vacancy_text, vacancy_url, or a file")

    check_and_record_conversion(user["user_id"], sb)

    # Determine raw input and input_type
    raw_input = ""
    input_type = "text"
    original_filename = None

    if vacancy_text:
        raw_input = vacancy_text.strip()
        input_type = "text"
    elif vacancy_url:
        raw_input = vacancy_url.strip()
        input_type = "url"
    elif file:
        raw_bytes = await file.read()
        s = get_settings()
        if len(raw_bytes) > s.max_upload_bytes:
            raise HTTPException(status_code=400, detail="File too large (max 5 MB)")
        raw_input = vacancy_parser.extract_text_from_file(raw_bytes, file.filename or "upload.txt")
        input_type = "file"
        original_filename = file.filename

    if not raw_input:
        raise HTTPException(status_code=400, detail="Empty vacancy input")

    vacancy_id = str(uuid.uuid4())
    sb.table("vacancies").insert({
        "id": vacancy_id,
        "user_id": user["user_id"],
        "raw_input": raw_input,
        "input_type": input_type,
        "original_filename": original_filename,
        "status": "pending",
    }).execute()

    cv_id = str(uuid.uuid4())
    sb.table("generated_cvs").insert({
        "id": cv_id,
        "user_id": user["user_id"],
        "vacancy_id": vacancy_id,
        "status": "pending",
    }).execute()

    schedule_generation(vacancy_id, cv_id)

    return {"vacancy_id": vacancy_id, "cv_id": cv_id}


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
    vacancy_map: dict[str, dict] = {}
    if vacancy_ids:
        vres = (
            sb.table("vacancies")
            .select("id,case_study_json,input_type,original_filename")
            .in_("id", vacancy_ids)
            .execute()
        )
        for v in vres.data or []:
            vacancy_map[v["id"]] = v

    for row in items:
        v = vacancy_map.get(row.get("vacancy_id"), {})
        cs = v.get("case_study_json") or {}
        row["vacancy_title"] = cs.get("title", v.get("original_filename", "Untitled"))
        row["input_type"] = v.get("input_type")

    return {"items": items}


@router.get("/{cv_id}")
async def get_generated_cv(cv_id: uuid.UUID, user: dict = Depends(get_current_user), sb: Client = Depends(get_supabase)):
    res = sb.table("generated_cvs").select("*").eq("id", str(cv_id)).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Not found")
    row = res.data[0]
    if row["user_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="Not found")

    out: dict = {
        "id": row["id"],
        "vacancy_id": row["vacancy_id"],
        "md_content": row.get("md_content"),
        "status": row["status"],
        "include_header": row.get("include_header", True),
        "error_message": row.get("error_message"),
        "created_at": row.get("created_at"),
    }

    if row["status"] == "completed" and row.get("pdf_storage_path"):
        from services import storage_service

        try:
            out["download_url"] = storage_service.get_signed_url(row["pdf_storage_path"])
        except Exception as e:
            logger.warning(
                "Failed to get download_url for cv_id=%s path=%s: %s",
                cv_id, row["pdf_storage_path"], e, exc_info=True,
            )
            out["download_url"] = None

    return out


@router.put("/{cv_id}")
async def update_cv_md(cv_id: uuid.UUID, md_content: str = Form(...), user: dict = Depends(get_current_user), sb: Client = Depends(get_supabase)):
    """Update the generated CV markdown (editor save)."""
    res = sb.table("generated_cvs").select("id,user_id").eq("id", str(cv_id)).limit(1).execute()
    if not res.data or res.data[0]["user_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="Not found")

    sb.table("generated_cvs").update({"md_content": md_content}).eq("id", str(cv_id)).execute()

    try:
        embedding_service.update_embedding("generated_cv", str(cv_id), md_content)
    except Exception:
        logger.exception("Failed to update embedding for generated_cv cv_id=%s", cv_id)

    return {"status": "ok"}


@router.post("/{cv_id}/convert")
async def convert_generated_cv(
    cv_id: uuid.UUID,
    include_header: bool = Form(True),
    user: dict = Depends(get_current_user),
    sb: Client = Depends(get_supabase),
):
    """Convert generated CV markdown to PDF using the existing pipeline."""
    res = sb.table("generated_cvs").select("*").eq("id", str(cv_id)).limit(1).execute()
    if not res.data or res.data[0]["user_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="Not found")

    row = res.data[0]
    if not row.get("md_content"):
        raise HTTPException(status_code=400, detail="CV has no markdown content yet")

    check_and_record_conversion(user["user_id"], sb)

    # Insert into conversions table so existing pipeline works
    conversion_id = str(uuid.uuid4())
    sb.table("conversions").insert({
        "id": conversion_id,
        "user_id": user["user_id"],
        "original_filename": f"generated_cv_{str(cv_id)[:8]}.md",
        "md_content": row["md_content"],
        "status": "pending",
        "include_header": include_header,
    }).execute()

    sb.table("generated_cvs").update({
        "status": "converting",
        "include_header": include_header,
    }).eq("id", str(cv_id)).execute()

    schedule_conversion(conversion_id)

    return {"conversion_id": conversion_id, "cv_id": str(cv_id)}


@router.delete("/{cv_id}")
async def delete_generated_cv(cv_id: uuid.UUID, user: dict = Depends(get_current_user), sb: Client = Depends(get_supabase)):
    res = sb.table("generated_cvs").select("id,user_id,pdf_storage_path").eq("id", str(cv_id)).limit(1).execute()
    if not res.data or res.data[0]["user_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="Not found")

    row = res.data[0]
    if row.get("pdf_storage_path"):
        try:
            from services import storage_service
            storage_service.delete_object(row["pdf_storage_path"])
        except Exception:
            logger.exception(
                "Failed to delete storage object for cv_id=%s path=%s",
                cv_id, row["pdf_storage_path"],
            )

    sb.table("document_embeddings").delete().eq("doc_type", "generated_cv").eq("doc_id", str(cv_id)).execute()
    sb.table("generated_cvs").delete().eq("id", str(cv_id)).execute()

    return {"status": "ok"}
