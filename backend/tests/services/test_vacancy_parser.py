from __future__ import annotations

import json
from unittest.mock import MagicMock, patch, AsyncMock

import pytest


class TestExtractTextFromFile:
    def test_parse_md_file(self):
        from services.vacancy_parser import extract_text_from_file

        content = b"# Job Title\nSenior QA needed"
        result = extract_text_from_file(content, "job.md")
        assert "Senior QA needed" in result

    def test_parse_txt_file(self):
        from services.vacancy_parser import extract_text_from_file

        content = b"QA Engineer role"
        result = extract_text_from_file(content, "vacancy.txt")
        assert result == "QA Engineer role"

    def test_parse_pdf_file(self):
        from services.vacancy_parser import extract_text_from_file

        with patch("pypdf.PdfReader") as MockReader:
            page = MagicMock()
            page.extract_text.return_value = "PDF text content"
            reader_instance = MagicMock()
            reader_instance.pages = [page]
            MockReader.return_value = reader_instance

            result = extract_text_from_file(b"%PDF-1.4", "job.pdf")
            assert "PDF text content" in result

    def test_empty_input_raises(self):
        from services.vacancy_parser import extract_text_from_file

        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text_from_file(b"data", "job.docx")


@pytest.mark.anyio
class TestExtractTextFromUrl:
    async def test_parse_url(self):
        mock_resp = MagicMock()
        mock_resp.text = "<html><body>Job description here</body></html>"
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)

        with (
            patch("services.vacancy_parser.httpx.AsyncClient") as mock_cls,
            patch("trafilatura.extract", return_value="Job description here"),
        ):
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            from services.vacancy_parser import extract_text_from_url

            result = await extract_text_from_url("https://example.com/job")
            assert result == "Job description here"

    async def test_parse_url_no_content_raises(self):
        mock_resp = MagicMock()
        mock_resp.text = "<html></html>"
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)

        with (
            patch("services.vacancy_parser.httpx.AsyncClient") as mock_cls,
            patch("trafilatura.extract", return_value=None),
        ):
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            from services.vacancy_parser import extract_text_from_url

            with pytest.raises(ValueError, match="Could not extract"):
                await extract_text_from_url("https://example.com/empty")


class TestUrlValidation:
    def test_rejects_localhost(self):
        from services.vacancy_parser import _validate_url
        with pytest.raises(ValueError, match="Internal"):
            _validate_url("http://127.0.0.1/secret")

    def test_rejects_metadata_endpoint(self):
        from services.vacancy_parser import _validate_url
        with pytest.raises(ValueError, match="Internal"):
            _validate_url("http://169.254.169.254/latest/meta-data/")

    def test_rejects_ipv6_loopback(self):
        from services.vacancy_parser import _validate_url
        with pytest.raises(ValueError, match="Internal"):
            _validate_url("http://[::1]/secret")

    def test_rejects_file_scheme(self):
        from services.vacancy_parser import _validate_url
        with pytest.raises(ValueError, match="Only HTTP"):
            _validate_url("file:///etc/passwd")

    def test_rejects_hex_ip(self):
        from services.vacancy_parser import _validate_url
        with pytest.raises(ValueError, match="Internal"):
            _validate_url("http://0x7f000001/secret")

    def test_rejects_private_10_range(self):
        from services.vacancy_parser import _validate_url
        with pytest.raises(ValueError, match="Internal"):
            _validate_url("http://10.0.0.1/admin")

    def test_rejects_private_172_range(self):
        from services.vacancy_parser import _validate_url
        with pytest.raises(ValueError, match="Internal"):
            _validate_url("http://172.16.0.1/admin")

    def test_rejects_private_192_range(self):
        from services.vacancy_parser import _validate_url
        with pytest.raises(ValueError, match="Internal"):
            _validate_url("http://192.168.1.1/admin")

    def test_allows_valid_external_url(self):
        from services.vacancy_parser import _validate_url
        _validate_url("https://www.example.com/job-posting")  # should not raise

    def test_rejects_ftp_scheme(self):
        from services.vacancy_parser import _validate_url
        with pytest.raises(ValueError, match="Only HTTP"):
            _validate_url("ftp://example.com/file")

