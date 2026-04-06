from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from core.auth import get_current_user, require_admin
from tests.conftest import FAKE_USER, FAKE_ADMIN


async def test_list_prompts_admin(client, mock_supabase):
    mock_supabase.execute.return_value = MagicMock(data=[
        {"id": "1", "slug": "cv_generation", "name": "CV Gen", "description": "", "version": 1, "updated_by": None, "updated_at": None},
    ])

    resp = await client.get("/api/prompts")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["slug"] == "cv_generation"


async def test_list_prompts_non_admin_403(app, mock_supabase):
    from httpx import ASGITransport, AsyncClient

    app.dependency_overrides[require_admin] = lambda: (_ for _ in ()).throw(
        __import__("fastapi").HTTPException(status_code=403, detail="Admin access required")
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/prompts")
        assert resp.status_code == 403

    app.dependency_overrides[require_admin] = lambda: FAKE_ADMIN


async def test_get_prompt_by_slug(client, mock_supabase):
    mock_supabase.execute.return_value = MagicMock(data=[
        {"id": "1", "slug": "cv_generation", "name": "CV Gen", "content": "prompt text", "version": 2},
    ])

    resp = await client.get("/api/prompts/cv_generation")
    assert resp.status_code == 200
    assert resp.json()["content"] == "prompt text"


async def test_get_prompt_not_found(client, mock_supabase):
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.get("/api/prompts/nonexistent")
    assert resp.status_code == 404


@patch("services.prompt_service.get_prompt_full")
@patch("services.prompt_service.invalidate_cache")
async def test_update_prompt(mock_invalidate, mock_full, client, mock_supabase):
    mock_full.return_value = {"id": "1", "slug": "cv_generation", "version": 3, "content": "old"}
    mock_supabase.execute.return_value = MagicMock(data=[
        {"id": "1", "slug": "cv_generation", "version": 4, "content": "new content", "updated_at": "now"},
    ])

    resp = await client.put(
        "/api/prompts/cv_generation",
        json={"content": "new content"},
    )
    assert resp.status_code == 200
    assert resp.json()["version"] == 4
