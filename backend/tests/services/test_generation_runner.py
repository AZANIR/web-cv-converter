from __future__ import annotations

from unittest.mock import MagicMock, patch, AsyncMock
import json

import pytest


@pytest.mark.anyio
class TestRunGenerationPipeline:
    @patch("services.generation_runner.embedding_service")
    @patch("services.generation_runner.prompt_service")
    @patch("services.generation_runner.vacancy_parser")
    @patch("services.generation_runner._generate_md_with_ai")
    @patch("services.generation_runner.get_supabase")
    async def test_full_pipeline_success(self, mock_sb, mock_ai, mock_parser, mock_prompts, mock_embed):
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.update.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[{
            "id": "vac-1",
            "raw_input": "Senior QA needed",
            "status": "pending",
        }])
        mock_sb.return_value = sb

        mock_prompts.get_prompt.return_value = "templatize: {{VACANCY_TEXT}}"
        mock_prompts.render_prompt.return_value = "generate CV prompt"

        case_study = {"title": "QA Role", "tags": ["Playwright"]}
        mock_parser.templatize_vacancy.return_value = case_study

        mock_embed.store_embedding.return_value = "emb-1"
        mock_embed.search_similar.return_value = [
            {"content": "case study text", "similarity": 0.9},
        ]

        mock_ai.return_value = "# Generated CV\n\nContent here"

        from services.generation_runner import run_generation_pipeline

        await run_generation_pipeline("vac-1", "cv-1")

        mock_parser.templatize_vacancy.assert_called_once()
        assert mock_embed.store_embedding.call_count == 2
        assert mock_embed.search_similar.call_count == 2
        mock_ai.assert_called_once()

    @patch("services.generation_runner.embedding_service")
    @patch("services.generation_runner.prompt_service")
    @patch("services.generation_runner.vacancy_parser")
    @patch("services.generation_runner.get_supabase")
    async def test_pipeline_failure_sets_status(self, mock_sb, mock_parser, mock_prompts, mock_embed):
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.update.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[{
            "id": "vac-1",
            "raw_input": "bad input",
            "status": "pending",
        }])
        mock_sb.return_value = sb

        mock_prompts.get_prompt.side_effect = ValueError("Prompt not found")

        from services.generation_runner import run_generation_pipeline

        await run_generation_pipeline("vac-1", "cv-1")

        # Should have called update to set status to 'failed'
        update_calls = [c for c in sb.update.call_args_list if "failed" in str(c)]
        assert len(update_calls) > 0

    @patch("services.generation_runner.get_supabase")
    async def test_pipeline_no_vacancy_returns(self, mock_sb):
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[])
        mock_sb.return_value = sb

        from services.generation_runner import run_generation_pipeline

        await run_generation_pipeline("nonexistent", "cv-1")

    @patch("services.generation_runner.embedding_service")
    @patch("services.generation_runner.prompt_service")
    @patch("services.generation_runner.vacancy_parser")
    @patch("services.generation_runner._generate_md_with_ai")
    @patch("services.generation_runner.get_supabase")
    async def test_embedding_failure_does_not_raise(
        self, mock_sb, mock_ai, mock_parser, mock_prompts, mock_embed
    ):
        """Embedding store failure must not propagate as an unhandled exception.

        The pipeline should either complete or set status to 'failed' — but must
        never let an exception bubble out of run_generation_pipeline itself.
        """
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.update.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[{
            "id": "vac-2",
            "raw_input": "Senior Engineer needed",
            "status": "pending",
        }])
        mock_sb.return_value = sb

        mock_prompts.get_prompt.return_value = "templatize: {{VACANCY_TEXT}}"
        mock_prompts.render_prompt.return_value = "generate CV prompt"
        mock_parser.templatize_vacancy.return_value = {"title": "Eng Role", "tags": ["Python"]}

        # Make store_embedding blow up on the first call
        mock_embed.store_embedding.side_effect = RuntimeError("Vector DB unavailable")
        mock_embed.search_similar.return_value = []
        mock_ai.return_value = "# Generated CV\n\nContent"

        from services.generation_runner import run_generation_pipeline

        # Must not raise
        await run_generation_pipeline("vac-2", "cv-2")

        # Pipeline must have attempted to set a terminal status (failed or draft)
        terminal_calls = [
            c for c in sb.update.call_args_list
            if any(k in str(c) for k in ("failed", "draft", "generating"))
        ]
        assert len(terminal_calls) > 0

    @patch("services.generation_runner.embedding_service")
    @patch("services.generation_runner.prompt_service")
    @patch("services.generation_runner.vacancy_parser")
    @patch("services.generation_runner._generate_md_with_ai")
    @patch("services.generation_runner.get_supabase")
    async def test_url_input_flow(
        self, mock_sb, mock_ai, mock_parser, mock_prompts, mock_embed
    ):
        """When raw_input is a URL the pipeline should treat it like any other
        text input and complete successfully (URL fetching happens in the router,
        not inside the generation runner itself).
        """
        vacancy_url = "https://example.com/job/senior-qa"

        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.update.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[{
            "id": "vac-url",
            "raw_input": vacancy_url,
            "status": "pending",
        }])
        mock_sb.return_value = sb

        mock_prompts.get_prompt.return_value = "templatize: {{VACANCY_TEXT}}"
        mock_prompts.render_prompt.return_value = "cv generation prompt"
        mock_parser.templatize_vacancy.return_value = {
            "title": "Senior QA Engineer",
            "tags": ["Playwright", "Python"],
        }
        mock_embed.store_embedding.return_value = "emb-url"
        mock_embed.search_similar.return_value = []
        mock_ai.return_value = "# Senior QA CV\n\nGenerated from URL"

        from services.generation_runner import run_generation_pipeline

        await run_generation_pipeline("vac-url", "cv-url")

        # vacancy_parser should have been called with the URL string as-is
        mock_parser.templatize_vacancy.assert_called_once()
        call_args = mock_parser.templatize_vacancy.call_args
        assert vacancy_url in call_args[0]

        # AI generator must have been invoked
        mock_ai.assert_called_once()

        # Generated CV status should have been set to 'draft'
        draft_calls = [c for c in sb.update.call_args_list if "draft" in str(c)]
        assert len(draft_calls) > 0
