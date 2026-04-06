from __future__ import annotations

from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest


class TestLoadAll:
    @patch("services.case_study_loader.CASE_STUDIES_DIR")
    def test_load_all_parses_files(self, mock_dir, tmp_path):
        md1 = tmp_path / "fintech-payment.md"
        md1.write_text(
            "# Fintech Payment Platform\n\n## Overview\n"
            "- **Industry:** Fintech\n- **Tags:** Playwright, CI/CD\n"
            "\n## What I Did\n- Automated E2E tests"
        )
        md2 = tmp_path / "healthcare-portal.md"
        md2.write_text("# Healthcare Portal\n\n## Overview\n- **Industry:** Healthcare\n")

        template = tmp_path / "_case_study_template.md"
        template.write_text("# Template\n")

        mock_dir.is_dir.return_value = True
        mock_dir.glob.return_value = sorted(tmp_path.glob("*.md"))

        from services.case_study_loader import load_all

        studies = load_all()
        assert len(studies) == 2
        assert studies[0]["filename"] == "fintech-payment.md"
        assert studies[0]["metadata"]["industry"] == "Fintech"
        assert "Playwright" in studies[0]["metadata"]["tags"]

    @patch("services.case_study_loader.CASE_STUDIES_DIR")
    def test_load_all_missing_dir(self, mock_dir):
        mock_dir.is_dir.return_value = False

        from services.case_study_loader import load_all

        assert load_all() == []


class TestSeedEmbeddings:
    @patch("services.embedding_service.store_embedding")
    @patch("core.supabase.get_supabase")
    @patch("services.case_study_loader.load_all")
    def test_seed_creates_embeddings(self, mock_load, mock_sb, mock_store):
        mock_load.return_value = [
            {"filename": "test.md", "title": "Test", "content": "# Test", "metadata": {"industry": "Fintech"}},
        ]
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[])
        mock_sb.return_value = sb

        from services.case_study_loader import seed_embeddings

        count = seed_embeddings()
        assert count == 1
        mock_store.assert_called_once()

    @patch("services.embedding_service.store_embedding")
    @patch("core.supabase.get_supabase")
    @patch("services.case_study_loader.load_all")
    def test_seed_skips_existing(self, mock_load, mock_sb, mock_store):
        mock_load.return_value = [
            {"filename": "test.md", "title": "Test", "content": "# Test", "metadata": {}},
        ]
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[{"id": "existing"}])
        mock_sb.return_value = sb

        from services.case_study_loader import seed_embeddings

        count = seed_embeddings()
        assert count == 0
        mock_store.assert_not_called()
