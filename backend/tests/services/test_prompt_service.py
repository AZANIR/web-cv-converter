from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestGetPrompt:
    @patch("services.prompt_service.get_supabase")
    def test_returns_content_from_db(self, mock_sb):
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[{"content": "prompt text"}])
        mock_sb.return_value = sb

        from services.prompt_service import get_prompt, _cache
        _cache.clear()

        result = get_prompt("cv_generation")
        assert result == "prompt text"

    @patch("services.prompt_service.get_supabase")
    def test_caches_result(self, mock_sb):
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[{"content": "cached prompt"}])
        mock_sb.return_value = sb

        from services.prompt_service import get_prompt, _cache
        _cache.clear()

        get_prompt("test_slug")
        get_prompt("test_slug")
        # Only one DB call (Supabase execute called once for this slug)
        assert sb.execute.call_count == 1

    @patch("services.prompt_service.get_supabase")
    def test_not_found_raises(self, mock_sb):
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[])
        mock_sb.return_value = sb

        from services.prompt_service import get_prompt, _cache
        _cache.clear()

        with pytest.raises(ValueError, match="Prompt not found"):
            get_prompt("nonexistent")


class TestRenderPrompt:
    @patch("services.prompt_service.get_prompt")
    def test_substitutes_placeholders(self, mock_get):
        mock_get.return_value = "Hello {{NAME}}, your data: {{DATA}}"

        from services.prompt_service import render_prompt

        result = render_prompt("test", {"NAME": "World", "DATA": "stuff"})
        assert result == "Hello World, your data: stuff"


class TestUpdatePrompt:
    @patch("services.prompt_service.get_supabase")
    @patch("services.prompt_service.get_prompt_full")
    def test_increments_version(self, mock_full, mock_sb):
        mock_full.return_value = {"id": "1", "slug": "test", "version": 3, "content": "old"}

        sb = MagicMock()
        sb.table.return_value = sb
        sb.update.return_value = sb
        sb.eq.return_value = sb
        sb.execute.return_value = MagicMock(data=[{"slug": "test", "version": 4, "content": "new"}])
        mock_sb.return_value = sb

        from services.prompt_service import update_prompt, _cache
        _cache.clear()

        result = update_prompt("test", "new content", "user-1")
        assert result["version"] == 4
        update_call = sb.update.call_args[0][0]
        assert update_call["version"] == 4

    @patch("services.prompt_service.get_prompt_full")
    def test_not_found_raises(self, mock_full):
        mock_full.return_value = None

        from services.prompt_service import update_prompt

        with pytest.raises(ValueError, match="Prompt not found"):
            update_prompt("missing", "content", "user-1")


class TestInvalidateCache:
    def test_invalidate_specific_slug(self):
        from services.prompt_service import _cache, invalidate_cache
        import time

        _cache["slug1"] = ("val1", time.time())
        _cache["slug2"] = ("val2", time.time())
        invalidate_cache("slug1")
        assert "slug1" not in _cache
        assert "slug2" in _cache

    def test_invalidate_all(self):
        from services.prompt_service import _cache, invalidate_cache
        import time

        _cache["a"] = ("va", time.time())
        _cache["b"] = ("vb", time.time())
        invalidate_cache()
        assert len(_cache) == 0
