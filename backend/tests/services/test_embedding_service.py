from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestEmbedText:
    @patch("services.embedding_service.get_settings")
    @patch("services.embedding_service._get_client")
    def test_returns_vector_list(self, mock_client_fn, mock_settings):
        s = MagicMock()
        s.embedding_model = "text-embedding-004"
        mock_settings.return_value = s

        fake_embedding = MagicMock()
        fake_embedding.values = [0.1] * 768

        client = MagicMock()
        client.models.embed_content.return_value = MagicMock(embeddings=[fake_embedding])
        mock_client_fn.return_value = client

        from services.embedding_service import embed_text

        result = embed_text("test text")
        assert isinstance(result, list)
        assert len(result) == 768
        assert result[0] == 0.1


class TestEmbedBatch:
    @patch("services.embedding_service.get_settings")
    @patch("services.embedding_service._get_client")
    def test_batch_embedding(self, mock_client_fn, mock_settings):
        s = MagicMock()
        s.embedding_model = "text-embedding-004"
        mock_settings.return_value = s

        e1 = MagicMock()
        e1.values = [0.1] * 768
        e2 = MagicMock()
        e2.values = [0.2] * 768

        client = MagicMock()
        client.models.embed_content.return_value = MagicMock(embeddings=[e1, e2])
        mock_client_fn.return_value = client

        from services.embedding_service import embed_batch

        result = embed_batch(["text1", "text2"])
        assert len(result) == 2
        assert len(result[0]) == 768

    def test_empty_list_returns_empty(self):
        from services.embedding_service import embed_batch

        assert embed_batch([]) == []


class TestStoreEmbedding:
    @patch("services.embedding_service.get_supabase")
    @patch("services.embedding_service.embed_text")
    def test_stores_and_returns_id(self, mock_embed, mock_sb):
        mock_embed.return_value = [0.1] * 768
        sb = MagicMock()
        sb.table.return_value = sb
        sb.insert.return_value = sb
        sb.execute.return_value = MagicMock(data=[{"id": "emb-123"}])
        mock_sb.return_value = sb

        from services.embedding_service import store_embedding

        result = store_embedding(
            doc_type="case_study",
            content="test content",
            metadata={"tags": ["QA"]},
            source_file="test.md",
        )
        assert result == "emb-123"
        sb.insert.assert_called_once()
        call_args = sb.insert.call_args[0][0]
        assert call_args["doc_type"] == "case_study"
        assert call_args["source_file"] == "test.md"


class TestSearchSimilar:
    @patch("services.embedding_service.get_supabase")
    @patch("services.embedding_service.embed_text")
    def test_search_returns_results(self, mock_embed, mock_sb):
        mock_embed.return_value = [0.1] * 768
        sb = MagicMock()
        sb.rpc.return_value = sb
        sb.execute.return_value = MagicMock(data=[
            {"id": "1", "doc_type": "case_study", "similarity": 0.95, "content": "test", "metadata": {}, "doc_id": None},
        ])
        mock_sb.return_value = sb

        from services.embedding_service import search_similar

        results = search_similar("query text", doc_type="case_study", limit=3)
        assert len(results) == 1
        assert results[0]["similarity"] == 0.95
        sb.rpc.assert_called_once_with("match_documents", {
            "query_embedding": [0.1] * 768,
            "match_count": 3,
            "filter_doc_type": "case_study",
        })

    @patch("services.embedding_service.get_supabase")
    @patch("services.embedding_service.embed_text")
    def test_search_without_filter(self, mock_embed, mock_sb):
        mock_embed.return_value = [0.1] * 768
        sb = MagicMock()
        sb.rpc.return_value = sb
        sb.execute.return_value = MagicMock(data=[])
        mock_sb.return_value = sb

        from services.embedding_service import search_similar

        search_similar("query")
        call_args = sb.rpc.call_args[0][1]
        assert "filter_doc_type" not in call_args
