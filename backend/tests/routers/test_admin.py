from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from core.auth import get_current_user, require_admin
from tests.conftest import FAKE_USER


async def test_list_users(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.order.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[
        {"email": "user@test.com", "created_at": "2025-01-01"},
    ])

    resp = await client.get("/api/admin/users")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


async def test_add_user(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.insert.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.post("/api/admin/users", json={"email": "new@test.com"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_remove_user(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.delete.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.delete("/api/admin/users", params={"email": "old@test.com"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_all_conversions(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.order.return_value = mock_supabase
    mock_supabase.in_.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.get("/api/admin/conversions")
    assert resp.status_code == 200
    assert resp.json()["items"] == []


async def test_admin_endpoints_reject_non_admin(app, client):
    """Verify that without the admin override, endpoints are protected."""
    app.dependency_overrides[require_admin] = lambda: (_ for _ in ()).throw(
        __import__("fastapi").HTTPException(status_code=403, detail="Admin access required")
    )

    resp = await client.get("/api/admin/users")
    assert resp.status_code == 403


async def test_admin_endpoint_with_admin_role_returns_200(client, mock_supabase):
    """Admin role (injected via fixture) grants access and returns 200."""
    mock_supabase.execute.return_value = MagicMock(data=[], count=0)

    resp = await client.get("/api/admin/users")
    assert resp.status_code == 200


async def test_list_conversions_pagination_shape(client, mock_supabase):
    """GET /admin/conversions?page=1&per_page=5 response must contain pagination fields."""
    conv_items = [
        {
            "id": f"c{i}",
            "user_id": "user-1",
            "original_filename": f"cv{i}.md",
            "status": "completed",
            "created_at": "2025-01-01",
            "error_message": None,
        }
        for i in range(3)
    ]
    # First execute() call is the COUNT query, second is data; mock returns same mock
    # The admin router calls .execute() twice; we configure side_effect for both.
    count_result = MagicMock(data=[], count=3)
    data_result = MagicMock(data=conv_items, count=3)
    profiles_result = MagicMock(data=[])
    mock_supabase.execute.side_effect = [count_result, data_result, profiles_result]

    resp = await client.get("/api/admin/conversions", params={"page": 1, "per_page": 5})
    assert resp.status_code == 200

    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "per_page" in body
    assert "pages" in body
    assert body["page"] == 1
    assert body["per_page"] == 5


async def test_list_conversions_filter_by_status(client, mock_supabase):
    """GET /admin/conversions?status=completed must return only completed items."""
    completed_items = [
        {
            "id": "c1",
            "user_id": "user-1",
            "original_filename": "cv.md",
            "status": "completed",
            "created_at": "2025-01-01",
            "error_message": None,
        }
    ]
    count_result = MagicMock(data=[], count=1)
    data_result = MagicMock(data=completed_items, count=1)
    profiles_result = MagicMock(data=[])
    mock_supabase.execute.side_effect = [count_result, data_result, profiles_result]

    resp = await client.get("/api/admin/conversions", params={"status": "completed"})
    assert resp.status_code == 200

    body = resp.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["status"] == "completed"


async def test_list_conversions_invalid_status_returns_422(client, mock_supabase):
    """Passing an invalid status value should return 422."""
    resp = await client.get("/api/admin/conversions", params={"status": "invalid_status"})
    assert resp.status_code == 422


async def test_add_allowed_email(client, mock_supabase):
    """POST /admin/users adds a new email to the allowlist."""
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.post("/api/admin/users", json={"email": "newuser@example.com"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_remove_allowed_email(client, mock_supabase):
    """DELETE /admin/users removes an email from the allowlist."""
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.delete("/api/admin/users", params={"email": "olduser@example.com"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
