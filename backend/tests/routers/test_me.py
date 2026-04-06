from __future__ import annotations

from unittest.mock import MagicMock, patch

from tests.conftest import FAKE_USER


async def test_get_me_with_profile(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": FAKE_USER["user_id"],
        "email": FAKE_USER["email"],
        "full_name": "Test User",
        "avatar_url": None,
        "role": "user",
    }])

    resp = await client.get("/api/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == FAKE_USER["email"]
    assert data["role"] == "user"


@patch("routers.me.is_config_listed_admin")
async def test_get_me_admin_via_config(mock_admin_check, client, mock_supabase):
    mock_admin_check.return_value = True
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": FAKE_USER["user_id"],
        "email": FAKE_USER["email"],
        "full_name": "Admin User",
        "avatar_url": None,
        "role": "user",
    }])

    resp = await client.get("/api/me")
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


async def test_get_me_no_profile(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.get("/api/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == FAKE_USER["user_id"]
    assert data["email"] == FAKE_USER["email"]
