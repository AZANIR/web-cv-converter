from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest

from services.ai_service import (
    _strip_json_fences,
    _extract_json,
    _parse_gemini_json,
    _build_prompt,
    _finish_reason_is_max_tokens,
    _assistant_text_anthropic,
    convert_md_to_json,
)


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


class TestExtractJson:
    def test_parses_clean_json(self):
        result = _extract_json('{"name": "Bob"}')
        assert result == {"name": "Bob"}

    def test_parses_json_with_surrounding_text(self):
        text = 'Here is the result: {"name": "Bob"} end'
        result = _extract_json(text)
        assert result == {"name": "Bob"}

    def test_parses_json_inside_fences(self):
        text = '```json\n{"key": "val"}\n```'
        result = _extract_json(text)
        assert result == {"key": "val"}

    def test_raises_on_empty_string(self):
        with pytest.raises(ValueError, match="no text"):
            _extract_json("")

    def test_raises_on_invalid_json(self):
        with pytest.raises(ValueError, match="Could not parse"):
            _extract_json("this is not json at all")

    def test_raises_on_truncated_json(self):
        with pytest.raises(ValueError, match="Could not parse"):
            _extract_json('{"name": "incomplete')


class TestParseGeminiJson:
    def test_parses_valid_json(self):
        result = _parse_gemini_json('{"a": 1}', None)
        assert result == {"a": 1}

    def test_raises_on_empty(self):
        with pytest.raises(ValueError, match="empty"):
            _parse_gemini_json("", None)

    def test_raises_on_max_tokens(self):
        fr = MagicMock()
        fr.name = "MAX_TOKENS"
        with pytest.raises(ValueError, match="token limit"):
            _parse_gemini_json('{"a": 1}', fr)

    def test_repairs_broken_json(self):
        broken = '{"name": "Alice", "age": 30'
        result = _parse_gemini_json(broken + "}", None)
        assert result["name"] == "Alice"


class TestFinishReasonIsMaxTokens:
    def test_none_returns_false(self):
        assert _finish_reason_is_max_tokens(None) is False

    def test_name_attribute_match(self):
        fr = MagicMock()
        fr.name = "MAX_TOKENS"
        assert _finish_reason_is_max_tokens(fr) is True

    def test_string_contains_max_tokens(self):
        assert _finish_reason_is_max_tokens("FINISH_REASON_MAX_TOKENS") is True


class TestBuildPrompt:
    @patch("services.ai_service._load_prompt_template")
    def test_inserts_markdown(self, mock_load):
        mock_load.return_value = "Template: [INSERT CV MARKDOWN HERE]"
        result = _build_prompt("# My CV")
        assert result == "Template: # My CV"


class TestAssistantTextAnthropic:
    def test_extracts_text_blocks(self):
        block = MagicMock()
        block.type = "text"
        block.text = "Hello world"
        msg = MagicMock()
        msg.content = [block]
        assert _assistant_text_anthropic(msg) == "Hello world"

    def test_skips_non_text_blocks(self):
        block = MagicMock()
        block.type = "image"
        msg = MagicMock()
        msg.content = [block]
        assert _assistant_text_anthropic(msg) == ""


class TestConvertMdToJson:
    @patch("services.ai_service._convert_with_gemini")
    @patch("services.ai_service.get_settings")
    def test_dispatches_to_gemini(self, mock_settings, mock_gemini):
        s = MagicMock()
        s.ai_provider = "gemini"
        mock_settings.return_value = s
        mock_gemini.return_value = {"name": "Test"}

        result = convert_md_to_json("# CV")
        mock_gemini.assert_called_once()
        assert result == {"name": "Test"}

    @patch("services.ai_service._convert_with_anthropic")
    @patch("services.ai_service.get_settings")
    def test_dispatches_to_anthropic(self, mock_settings, mock_anthropic):
        s = MagicMock()
        s.ai_provider = "anthropic"
        mock_settings.return_value = s
        mock_anthropic.return_value = {"name": "Test"}

        result = convert_md_to_json("# CV")
        mock_anthropic.assert_called_once()
        assert result == {"name": "Test"}

    @patch("services.ai_service.get_settings")
    def test_raises_on_unknown_provider(self, mock_settings):
        s = MagicMock()
        s.ai_provider = "openai"
        mock_settings.return_value = s

        with pytest.raises(RuntimeError, match="Unknown AI_PROVIDER"):
            convert_md_to_json("# CV")
