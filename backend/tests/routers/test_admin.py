from __future__ import annotations

from unittest.mock import MagicMock

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
