"""Admin-only CRUD for AI prompts stored in DB."""

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from core.auth import require_admin
from core.supabase import get_supabase
from services import prompt_service

router = APIRouter(prefix="/prompts", tags=["prompts"])


class UpdatePromptBody(BaseModel):
    content: str


@router.get("")
async def list_prompts(_admin: dict = Depends(require_admin), sb: Client = Depends(get_supabase)):
    items = prompt_service.list_prompts(sb)
    return {"items": items}


@router.get("/{slug}")
async def get_prompt(slug: str, _admin: dict = Depends(require_admin), sb: Client = Depends(get_supabase)):
    data = prompt_service.get_prompt_full(slug, sb)
    if not data:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return data


@router.put("/{slug}")
async def update_prompt(slug: str, body: UpdatePromptBody, admin: dict = Depends(require_admin), sb: Client = Depends(get_supabase)):
    try:
        updated = prompt_service.update_prompt(slug, body.content, admin["user_id"], sb)
    except ValueError:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated
