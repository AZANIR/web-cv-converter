from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest

from core.ai_client import _strip_json_fences
from services.ai_service import _build_prompt, convert_md_to_json


class TestStripJsonFences:
    def test_strips_json_code_fence(self):
        text = '```json\n{"name": "Alice"}\n```'
        assert _strip_json_fences(text) == '{"name": "Alice"}'

    def test_strips_plain_code_fence(self):
        text = '```\n{"a": 1}\n```'
        assert _strip_json_fences(text) == '{"a": 1}'

    def test_returns_text_unchanged_when_no_fence(self):
        text = '{"a": 1}'
        assert _strip_json_fences(text) == '{"a": 1}'

    def test_handles_empty_string(self):
        assert _strip_json_fences("") == ""

    def test_handles_none(self):
        assert _strip_json_fences(None) == ""


class TestBuildPrompt:
    @patch("services.ai_service._load_prompt_template")
    def test_inserts_markdown(self, mock_load):
        mock_load.return_value = "Template: [INSERT CV MARKDOWN HERE]"
        result = _build_prompt("# My CV")
        assert result == "Template: # My CV"


class TestConvertMdToJson:
    @patch("services.ai_service.get_ai_client")
    def test_dispatches_to_ai_client(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.generate_json.return_value = {"name": "Test"}
        mock_get_client.return_value = mock_client

        result = convert_md_to_json("# CV")
        assert result == {"name": "Test"}
        mock_client.generate_json.assert_called_once()
