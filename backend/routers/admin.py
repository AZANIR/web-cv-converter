from math import ceil

from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, Query
from supabase import Client

from core.auth import require_admin
from core.supabase import get_supabase

router = APIRouter(prefix="/admin", tags=["admin"])

_VALID_STATUSES = {"pending", "processing", "completed", "failed"}


class AddUserBody(BaseModel):
    email: EmailStr
    note: str | None = None


@router.get("/users")
async def list_allowed_users(
    _admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sb: Client = Depends(get_supabase),
):
    offset = (page - 1) * per_page

    count_res = (
        sb.table("allowed_emails")
        .select("id", count="exact")
        .execute()
    )
    total: int = count_res.count or 0

    res = (
        sb.table("allowed_emails")
        .select("*")
        .order("created_at", desc=True)
        .range(offset, offset + per_page - 1)
        .execute()
    )

    return {
        "items": res.data or [],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": ceil(total / per_page) if total > 0 else 1,
    }


@router.post("/users")
async def add_allowed_user(body: AddUserBody, admin: dict = Depends(require_admin), sb: Client = Depends(get_supabase)):
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
    sb: Client = Depends(get_supabase),
):
    sb.table("allowed_emails").delete().eq("email", str(email).lower()).execute()
    return {"status": "ok"}


@router.get("/conversions")
async def all_conversions(
    _admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(
        None,
        description="Filter by status: pending | processing | completed | failed",
    ),
    user_id: str | None = Query(None, description="Filter by user UUID"),
    sb: Client = Depends(get_supabase),
):
    offset = (page - 1) * per_page

    # Build a reusable filter helper
    def _apply_filters(query):
        if status is not None:
            if status not in _VALID_STATUSES:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid status '{status}'. Must be one of: {', '.join(sorted(_VALID_STATUSES))}",
                )
            query = query.eq("status", status)
        if user_id is not None:
            query = query.eq("user_id", user_id)
        return query

    # Total count with filters applied
    count_q = _apply_filters(
        sb.table("conversions").select("id", count="exact")
    )
    count_res = count_q.execute()
    total: int = count_res.count or 0

    # Paginated data with filters applied
    data_q = _apply_filters(
        sb.table("conversions")
        .select("id,user_id,original_filename,status,created_at,error_message")
    )
    res = (
        data_q
        .order("created_at", desc=True)
        .range(offset, offset + per_page - 1)
        .execute()
    )
    items = res.data or []

    # Enrich with profile data
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

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": ceil(total / per_page) if total > 0 else 1,
    }
