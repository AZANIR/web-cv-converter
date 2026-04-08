from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from services.conversion_runner import run_conversion_pipeline
from tests.conftest import make_supabase_mock


@patch("services.conversion_runner.get_supabase")
async def test_returns_early_if_no_conversion_found(mock_get_sb, mock_supabase):
    mock_supabase.execute.return_value = MagicMock(data=[])
    mock_get_sb.return_value = mock_supabase

    await run_conversion_pipeline("nonexistent-id")
    mock_supabase.update.assert_not_called()


@patch("services.conversion_runner.storage_service")
@patch("services.conversion_runner.pdf_service")
@patch("services.conversion_runner.ai_service")
@patch("services.conversion_runner.get_supabase")
async def test_successful_pipeline(mock_get_sb, mock_ai, mock_pdf, mock_storage):
    sb = make_supabase_mock()

    conv_row = {
        "id": "conv-1",
        "md_content": "# Test CV",
        "user_id": "user-1",
        "original_filename": "cv.md",
        "include_header": True,
    }
    sb.execute.return_value = MagicMock(data=[conv_row])
    mock_get_sb.return_value = sb

    mock_ai.convert_md_to_json.return_value = {"name": "Test"}
    mock_pdf.generate_pdf.return_value = b"pdf-bytes"
    mock_storage.upload_pdf.return_value = ("path/to/file.pdf", "file.pdf")

    await run_conversion_pipeline("conv-1")

    mock_ai.convert_md_to_json.assert_called_once_with("# Test CV")
    mock_pdf.generate_pdf.assert_called_once()
    mock_storage.upload_pdf.assert_called_once()


@patch("services.conversion_runner.ai_service")
@patch("services.conversion_runner.get_supabase")
async def test_pipeline_failure_sets_failed_status(mock_get_sb, mock_ai, mock_supabase):
    mock_supabase.execute.return_value = MagicMock(data=[{
        "id": "conv-1",
        "md_content": "# Bad CV",
        "user_id": "user-1",
        "original_filename": "bad.md",
        "include_header": True,
    }])
    mock_get_sb.return_value = mock_supabase

    mock_ai.convert_md_to_json.side_effect = ValueError("AI failed")

    await run_conversion_pipeline("conv-1")

    update_calls = [
        c for c in mock_supabase.update.call_args_list if "failed" in str(c)
    ]
    assert len(update_calls) > 0
