from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from services.storage_service import (
    _safe_filename_segment,
    _user_storage_prefix,
    upload_pdf,
    get_signed_url,
    BUCKET,
)


class TestSafeFilenameSegment:
    def test_passes_through_safe_name(self):
        assert _safe_filename_segment("my_cv.pdf") == "my_cv.pdf"

    def test_replaces_special_characters(self):
        result = _safe_filename_segment("my cv (final).pdf")
        assert " " not in result
        assert "(" not in result

    def test_collapses_underscores(self):
        result = _safe_filename_segment("a___b")
        assert "___" not in result

    def test_truncates_to_max_len(self):
        long_name = "a" * 200 + ".pdf"
        result = _safe_filename_segment(long_name, max_len=50)
        assert len(result) <= 50

    def test_returns_cv_for_empty_input(self):
        assert _safe_filename_segment("") == "cv"

    def test_strips_leading_trailing_dots_underscores(self):
        assert _safe_filename_segment("..._test_...") == "test"


class TestUserStoragePrefix:
    def test_returns_hex_string(self):
        prefix = _user_storage_prefix("auth0|user123")
        assert len(prefix) == 40
        assert all(c in "0123456789abcdef" for c in prefix)

    def test_deterministic(self):
        assert _user_storage_prefix("user1") == _user_storage_prefix("user1")

    def test_different_users_get_different_prefixes(self):
        assert _user_storage_prefix("user1") != _user_storage_prefix("user2")


class TestUploadPdf:
    @patch("services.storage_service.get_supabase")
    def test_uploads_and_returns_path(self, mock_get_sb):
        mock_sb = MagicMock()
        mock_get_sb.return_value = mock_sb

        path, filename = upload_pdf(b"pdf-bytes", "auth0|u1", "resume.md")

        assert filename.endswith(".pdf")
        assert "resume" in filename
        mock_sb.storage.from_.assert_called_once_with(BUCKET)
        mock_sb.storage.from_().upload.assert_called_once()

    @patch("services.storage_service.get_supabase")
    def test_handles_filename_without_extension(self, mock_get_sb):
        mock_sb = MagicMock()
        mock_get_sb.return_value = mock_sb

        path, filename = upload_pdf(b"pdf-bytes", "auth0|u1", "resume")
        assert filename.endswith(".pdf")


class TestGetSignedUrl:
    @patch("services.storage_service.get_settings")
    @patch("services.storage_service.get_supabase")
    def test_returns_signed_url_from_signedURL_key(self, mock_sb_fn, mock_settings):
        mock_settings.return_value = MagicMock(signed_url_expires_seconds=3600)
        mock_sb = MagicMock()
        mock_sb.storage.from_().create_signed_url.return_value = {
            "signedURL": "https://storage.example.com/signed"
        }
        mock_sb_fn.return_value = mock_sb

        url = get_signed_url("prefix/uuid/file.pdf")
        assert url == "https://storage.example.com/signed"

    @patch("services.storage_service.get_settings")
    @patch("services.storage_service.get_supabase")
    def test_returns_signed_url_from_signedUrl_key(self, mock_sb_fn, mock_settings):
        mock_settings.return_value = MagicMock(signed_url_expires_seconds=3600)
        mock_sb = MagicMock()
        mock_sb.storage.from_().create_signed_url.return_value = {
            "signedUrl": "https://storage.example.com/signed2"
        }
        mock_sb_fn.return_value = mock_sb

        url = get_signed_url("prefix/uuid/file.pdf")
        assert url == "https://storage.example.com/signed2"

    @patch("services.storage_service.get_settings")
    @patch("services.storage_service.get_supabase")
    def test_raises_on_unexpected_response(self, mock_sb_fn, mock_settings):
        mock_settings.return_value = MagicMock(signed_url_expires_seconds=3600)
        mock_sb = MagicMock()
        mock_sb.storage.from_().create_signed_url.return_value = {"error": "oops"}
        mock_sb_fn.return_value = mock_sb

        with pytest.raises(RuntimeError, match="Unexpected"):
            get_signed_url("some/path.pdf")
