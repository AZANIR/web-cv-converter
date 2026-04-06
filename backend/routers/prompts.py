"""Admin-only CRUD for AI prompts stored in DB."""

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException

from core.auth import require_admin
from services import prompt_service

router = APIRouter(prefix="/prompts", tags=["prompts"])


class UpdatePromptBody(BaseModel):
    content: str


@router.get("")
async def list_prompts(_admin: dict = Depends(require_admin)):
    items = prompt_service.list_prompts()
    return {"items": items}


@router.get("/{slug}")
async def get_prompt(slug: str, _admin: dict = Depends(require_admin)):
    data = prompt_service.get_prompt_full(slug)
    if not data:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return data


@router.put("/{slug}")
async def update_prompt(slug: str, body: UpdatePromptBody, admin: dict = Depends(require_admin)):
    try:
        updated = prompt_service.update_prompt(slug, body.content, admin["user_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated
