from fastapi import APIRouter, Depends
from supabase import Client

from core.auth import get_current_user, is_config_listed_admin
from core.supabase import get_supabase

router = APIRouter(tags=["me"])


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user), sb: Client = Depends(get_supabase)):
    res = sb.table("profiles").select("id,email,full_name,avatar_url,role").eq("id", user["user_id"]).limit(1).execute()
    row = res.data[0] if res.data else None
    if not row:
        role = "admin" if is_config_listed_admin(user["email"]) else "user"
        return {
            "id": user["user_id"],
            "email": user["email"],
            "full_name": None,
            "avatar_url": None,
            "role": role,
        }
    db_role = row.get("role") or "user"
    if db_role == "admin" or is_config_listed_admin(user["email"]):
        row = {**row, "role": "admin"}
    else:
        row = {**row, "role": db_role}
    return row
