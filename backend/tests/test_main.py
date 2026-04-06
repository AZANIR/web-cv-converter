from __future__ import annotations

from unittest.mock import MagicMock


async def test_health_ok(client, mock_supabase):
    mock_supabase.execute.return_value = MagicMock(data=[{"id": "1"}])

    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"


async def test_health_db_error(client, mock_supabase):
    mock_supabase.execute.side_effect = Exception("connection failed")

    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["db"] == "error"
