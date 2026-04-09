"""Prompt service: read prompts from DB with in-memory cache."""

import logging
from typing import Any

from cachetools import TTLCache
from supabase import Client

from core.supabase import get_supabase

logger = logging.getLogger(__name__)

_cache: TTLCache = TTLCache(maxsize=100, ttl=300)  # 5-minute TTL


def get_prompt(slug: str) -> str:
    """Return prompt content from DB (cached). Raises ValueError if not found."""
    if slug in _cache:
        return _cache[slug]

    sb = get_supabase()
    res = sb.table("prompts").select("content").eq("slug", slug).limit(1).execute()
    if not res.data:
        raise ValueError(f"Prompt not found: {slug!r}")
    content = res.data[0]["content"]
    _cache[slug] = content
    return content


def invalidate_cache(slug: str | None = None) -> None:
    if slug:
        _cache.pop(slug, None)
    else:
        _cache.clear()


def render_prompt(slug: str, context: dict[str, str] | None = None) -> str:
    """Get prompt and substitute {{PLACEHOLDER}} values from context."""
    content = get_prompt(slug)
    if context:
        for key, val in context.items():
            content = content.replace("{{" + key + "}}", val)
    return content


def list_prompts(sb: Client) -> list[dict[str, Any]]:
    res = (
        sb.table("prompts")
        .select("id,slug,name,description,version,updated_by,updated_at")
        .order("slug")
        .execute()
    )
    return res.data or []


def get_prompt_full(slug: str, sb: Client) -> dict[str, Any] | None:
    res = sb.table("prompts").select("*").eq("slug", slug).limit(1).execute()
    return res.data[0] if res.data else None


def update_prompt(slug: str, content: str, updated_by: str, sb: Client) -> dict[str, Any]:
    """Update prompt content and increment version."""
    current = get_prompt_full(slug, sb)
    if not current:
        raise ValueError(f"Prompt not found: {slug!r}")
    new_version = (current.get("version") or 0) + 1
    res = (
        sb.table("prompts")
        .update({
            "content": content,
            "version": new_version,
            "updated_by": updated_by,
        })
        .eq("slug", slug)
        .execute()
    )
    invalidate_cache(slug)
    return res.data[0] if res.data else {**current, "content": content, "version": new_version}
