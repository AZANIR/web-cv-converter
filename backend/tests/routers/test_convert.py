from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest


async def test_convert_rejects_non_md_file(client):
    resp = await client.post(
        "/api/convert",
        files={"file": ("resume.txt", b"content", "text/plain")},
        data={"include_header": "true"},
    )
    assert resp.status_code == 400
    assert "Only .md" in resp.json()["detail"]


async def test_convert_rejects_large_file(client, settings):
    settings.max_upload_bytes = 10
    resp = await client.post(
        "/api/convert",
        files={"file": ("cv.md", b"x" * 20, "text/markdown")},
        data={"include_header": "true"},
    )
    assert resp.status_code == 400
    assert "too large" in resp.json()["detail"].lower()


@patch("routers.convert.schedule_conversion")
@patch("routers.convert.check_and_record_conversion")
async def test_convert_success(mock_check_rate, mock_schedule, client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.insert.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(
        data=[{"id": "conv-123"}]
    )

    resp = await client.post(
        "/api/convert",
        files={"file": ("cv.md", b"# My CV", "text/markdown")},
        data={"include_header": "true"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "conversion_id" in data
    mock_schedule.assert_called_once()
    mock_check_rate.assert_called_once()


async def test_get_conversion_status_404_when_not_found(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(data=[])

    resp = await client.get("/api/conversions/nonexistent")
    assert resp.status_code == 404


async def test_get_conversion_status_404_for_wrong_user(client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(
        data=[{"id": "c1", "user_id": "other-user", "status": "completed"}]
    )

    resp = await client.get("/api/conversions/c1")
    assert resp.status_code == 404


async def test_get_conversion_status_success(client, mock_supabase):
    from tests.conftest import FAKE_USER

    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.execute.return_value = MagicMock(
        data=[{
            "id": "c1",
            "user_id": FAKE_USER["user_id"],
            "status": "processing",
            "original_filename": "cv.md",
            "error_message": None,
            "created_at": "2025-01-01",
            "pdf_storage_path": None,
        }]
    )

    resp = await client.get("/api/conversions/c1")
    assert resp.status_code == 200
    assert resp.json()["status"] == "processing"
