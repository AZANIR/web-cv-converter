from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest


@patch("routers.generate.schedule_generation")
@patch("routers.generate.check_and_record_conversion")
async def test_generate_with_text(mock_check_rate, mock_schedule, client, mock_supabase):
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.insert.return_value = mock_supabase
    
    vacancy_result = MagicMock(data=[{"id": "vac-123"}])
    cv_result = MagicMock(data=[{"id": "cv-123"}])
    mock_supabase.execute.side_effect = [vacancy_result, cv_result]

    resp = await client.post(
        "/api/generate",
        data={"vacancy_text": "We need a Senior QA Automation Engineer"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "vacancy_id" in data
    assert "cv_id" in data
    mock_schedule.assert_called_once()


@patch("routers.generate.schedule_generation")
@patch("routers.generate.vacancy_parser")
@patch("routers.generate.check_and_record_conversion")
async def test_generate_with_file(mock_check_rate, mock_parser, mock_schedule, client, mock_supabase):
    mock_parser.extract_text_from_file.return_value = "parsed file content"
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.insert.return_value = mock_supabase
    
    vacancy_result = MagicMock(data=[{"id": "vac-123"}])
    cv_result = MagicMock(data=[{"id": "cv-123"}])
    mock_supabase.execute.side_effect = [vacancy_result, cv_result]

    resp = await client.post(
        "/api/generate",
        files={"file": ("vacancy.md", b"# QA Job", "text/markdown")},
    )
    assert resp.status_code == 200
    assert "cv_id" in resp.json()


async def test_generate_no_input_400(client):
    resp = await client.post("/api/generate")
    assert resp.status_code == 400
    assert "Provide" in resp.json()["detail"]


async def test_get_cv_not_found(client, mock_supabase):
    mock_supabase.execute.return_value = MagicMock(data=[])
    resp = await client.get("/api/generate/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 404


async def test_get_cv_success(client, mock_supabase):
    from tests.conftest import FAKE_USER

    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": "00000000-0000-0000-0000-000000000001",
        "user_id": FAKE_USER["user_id"],
        "vacancy_id": "vac-1",
        "md_content": "# CV",
        "status": "draft",
        "include_header": True,
        "error_message": None,
        "created_at": "2025-01-01",
        "pdf_storage_path": None,
    }])

    resp = await client.get("/api/generate/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "draft"
    assert data["md_content"] == "# CV"


async def test_get_cv_wrong_user_404(client, mock_supabase):
    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": "00000000-0000-0000-0000-000000000001",
        "user_id": "other-user",
        "vacancy_id": "vac-1",
        "md_content": "# CV",
        "status": "draft",
        "include_header": True,
        "error_message": None,
        "created_at": "2025-01-01",
        "pdf_storage_path": None,
    }])
    resp = await client.get("/api/generate/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 404


@patch("routers.generate.embedding_service")
async def test_update_cv_md(mock_embed, client, mock_supabase):
    from tests.conftest import FAKE_USER

    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": "00000000-0000-0000-0000-000000000001",
        "user_id": FAKE_USER["user_id"],
    }])

    resp = await client.put(
        "/api/generate/00000000-0000-0000-0000-000000000001",
        data={"md_content": "# Updated CV"},
    )
    assert resp.status_code == 200


@patch("routers.generate.schedule_conversion")
@patch("routers.generate.check_and_record_conversion")
async def test_convert_cv_to_pdf(mock_check_rate, mock_schedule, client, mock_supabase):
    from tests.conftest import FAKE_USER

    mock_supabase.table.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.eq.return_value = mock_supabase
    mock_supabase.limit.return_value = mock_supabase
    mock_supabase.insert.return_value = mock_supabase
    mock_supabase.update.return_value = mock_supabase
    
    cv_result = MagicMock(data=[{
        "id": "00000000-0000-0000-0000-000000000001",
        "user_id": FAKE_USER["user_id"],
        "vacancy_id": "vac-1",
        "md_content": "# CV Content",
        "status": "draft",
        "include_header": True,
        "error_message": None,
        "pdf_storage_path": None,
    }])
    # Three execute calls: select, insert, update
    mock_supabase.execute.side_effect = [cv_result, MagicMock(), MagicMock()]

    resp = await client.post(
        "/api/generate/00000000-0000-0000-0000-000000000001/convert",
        data={"include_header": "true"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "conversion_id" in data
    mock_schedule.assert_called_once()
    mock_check_rate.assert_called_once()


@patch("routers.generate.schedule_conversion")
async def test_convert_empty_md_400(mock_schedule, client, mock_supabase):
    from tests.conftest import FAKE_USER

    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": "00000000-0000-0000-0000-000000000001",
        "user_id": FAKE_USER["user_id"],
        "vacancy_id": "vac-1",
        "md_content": None,
        "status": "draft",
        "include_header": True,
        "error_message": None,
        "pdf_storage_path": None,
    }])

    resp = await client.post("/api/generate/00000000-0000-0000-0000-000000000001/convert", data={"include_header": "true"})
    assert resp.status_code == 400


async def test_delete_cv(client, mock_supabase):
    from tests.conftest import FAKE_USER

    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": "00000000-0000-0000-0000-000000000001",
        "user_id": FAKE_USER["user_id"],
        "pdf_storage_path": None,
    }])

    resp = await client.delete("/api/generate/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 200


async def test_get_history(client, mock_supabase):
    mock_supabase.execute.return_value = MagicMock(data=[])
    resp = await client.get("/api/generate/history")
    assert resp.status_code == 200
    assert resp.json()["items"] == []
