import logging

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user
from core.supabase import get_supabase
from services import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["history"])

BUCKET = storage_service.BUCKET


def _remove_storage_paths(sb, paths: list[str]) -> None:
    paths = [p for p in paths if p]
    if not paths:
        return
    chunk = 50
    for i in range(0, len(paths), chunk):
        batch = paths[i : i + chunk]
        try:
            sb.storage.from_(BUCKET).remove(batch)
        except Exception:
            logger.exception("Storage remove failed for %s objects", len(batch))


@router.get("/history")
async def list_history(user: dict = Depends(get_current_user)):
    sb = get_supabase()
    res = (
        sb.table("conversions")
        .select("id,original_filename,status,created_at,error_message")
        .eq("user_id", user["user_id"])
        .order("created_at", desc=True)
        .execute()
    )
    return {"items": res.data or []}


@router.get("/history/{conversion_id}/download")
async def history_download(
    conversion_id: str,
    user: dict = Depends(get_current_user),
):
    sb = get_supabase()
    res = sb.table("conversions").select("*").eq("id", conversion_id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Not found")
    row = res.data[0]
    if row["user_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="Not found")
    if row["status"] != "completed" or not row.get("pdf_storage_path"):
        raise HTTPException(status_code=400, detail="PDF not available")

    url = storage_service.get_signed_url(row["pdf_storage_path"])
    return {"download_url": url}


@router.delete("/history/{conversion_id}")
async def delete_history_item(
    conversion_id: str,
    user: dict = Depends(get_current_user),
):
    sb = get_supabase()
    res = sb.table("conversions").select("*").eq("id", conversion_id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Not found")
    row = res.data[0]
    if row["user_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="Not found")
    path = row.get("pdf_storage_path")
    if path:
        _remove_storage_paths(sb, [path])
    sb.table("conversions").delete().eq("id", conversion_id).execute()
    return {"ok": True}


@router.delete("/history")
async def delete_all_history(user: dict = Depends(get_current_user)):
    sb = get_supabase()
    res = (
        sb.table("conversions")
        .select("pdf_storage_path")
        .eq("user_id", user["user_id"])
        .execute()
    )
    paths = [r["pdf_storage_path"] for r in (res.data or []) if r.get("pdf_storage_path")]
    _remove_storage_paths(sb, paths)
    sb.table("conversions").delete().eq("user_id", user["user_id"]).execute()
    return {"ok": True}
