from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, Query

from core.auth import require_admin
from core.supabase import get_supabase

router = APIRouter(prefix="/admin", tags=["admin"])


class AddUserBody(BaseModel):
    email: EmailStr
    note: str | None = None


@router.get("/users")
async def list_allowed_users(_admin: dict = Depends(require_admin)):
    sb = get_supabase()
    res = sb.table("allowed_emails").select("*").order("created_at", desc=True).execute()
    return {"items": res.data or []}


@router.post("/users")
async def add_allowed_user(body: AddUserBody, admin: dict = Depends(require_admin)):
    sb = get_supabase()
    sb.table("allowed_emails").insert(
        {
            "email": str(body.email).lower(),
            "added_by": admin["user_id"],
            "note": body.note,
        }
    ).execute()
    return {"status": "ok"}


@router.delete("/users")
async def remove_allowed_user(
    email: EmailStr = Query(...),
    _admin: dict = Depends(require_admin),
):
    sb = get_supabase()
    sb.table("allowed_emails").delete().eq("email", str(email).lower()).execute()
    return {"status": "ok"}


@router.get("/conversions")
async def all_conversions(_admin: dict = Depends(require_admin)):
    sb = get_supabase()
    res = (
        sb.table("conversions")
        .select("id,user_id,original_filename,status,created_at,error_message")
        .order("created_at", desc=True)
        .execute()
    )
    items = res.data or []
    user_ids = list({r["user_id"] for r in items if r.get("user_id")})
    profiles_map: dict[str, dict] = {}
    if user_ids:
        pres = sb.table("profiles").select("id,email,full_name").in_("id", user_ids).execute()
        for p in pres.data or []:
            profiles_map[p["id"]] = p
    for row in items:
        p = profiles_map.get(row.get("user_id"))
        row["user_email"] = p["email"] if p else None
        row["user_full_name"] = p["full_name"] if p else None
    return {"items": items}
