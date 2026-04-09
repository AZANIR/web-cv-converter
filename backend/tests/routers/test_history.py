from __future__ import annotations

from unittest.mock import MagicMock, patch

from tests.conftest import FAKE_USER


async def test_list_history(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.order.return_value = mock_supabase
    mock_supabase.range.return_value = mock_supabase
    
    count_result = MagicMock(count=1)
    data_result = MagicMock(data=[{"id": "c1", "original_filename": "cv.md", "status": "completed"}])
    mock_supabase.execute.side_effect = [count_result, data_result]

    resp = await client.get("/api/history")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


@patch("routers.history.storage_service")
async def test_history_download_success(mock_storage, client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": "c1",
        "user_id": FAKE_USER["user_id"],
        "status": "completed",
        "pdf_storage_path": "path/to/file.pdf",
    }])
    mock_storage.get_signed_url.return_value = "https://signed.url"

    resp = await client.get("/api/history/c1/download")
    assert resp.status_code == 200
    assert resp.json()["download_url"] == "https://signed.url"


async def test_history_download_404_not_found(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.get("/api/history/nonexistent/download")
    assert resp.status_code == 404


async def test_delete_history_item(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.delete.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": "c1",
        "user_id": FAKE_USER["user_id"],
        "pdf_storage_path": None,
    }])

    resp = await client.delete("/api/history/c1")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


async def test_delete_all_history(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.delete.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.delete("/api/history")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
