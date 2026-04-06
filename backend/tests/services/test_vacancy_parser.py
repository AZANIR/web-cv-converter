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


class TestTemplatizeVacancy:
    @patch("services.vacancy_parser.get_settings")
    @patch("services.vacancy_parser._templatize_gemini")
    def test_dispatches_to_gemini(self, mock_gemini, mock_settings):
        s = MagicMock()
        s.ai_provider = "gemini"
        mock_settings.return_value = s

        expected = {"title": "QA Engineer", "tags": ["Playwright"]}
        mock_gemini.return_value = expected

        from services.vacancy_parser import templatize_vacancy

        result = templatize_vacancy("We need a QA", "prompt {{VACANCY_TEXT}}", s)
        assert result == expected

    @patch("services.vacancy_parser.get_settings")
    def test_unknown_provider_raises(self, mock_settings):
        s = MagicMock()
        s.ai_provider = "openai"
        mock_settings.return_value = s

        from services.vacancy_parser import templatize_vacancy

        with pytest.raises(RuntimeError, match="Unknown AI_PROVIDER"):
            templatize_vacancy("text", "prompt {{VACANCY_TEXT}}", s)


class TestStripJsonFences:
    def test_strips_json_fence(self):
        from services.vacancy_parser import _strip_json_fences

        text = '```json\n{"key": "val"}\n```'
        assert _strip_json_fences(text) == '{"key": "val"}'

    def test_returns_plain_text(self):
        from services.vacancy_parser import _strip_json_fences

        assert _strip_json_fences('{"a": 1}') == '{"a": 1}'
