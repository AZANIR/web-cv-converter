"""Embedding service: vectorize text via Gemini and search with pgvector."""

import logging
from typing import Any

from core.config import get_settings
from core.supabase import get_supabase

logger = logging.getLogger(__name__)


def _get_client():
    from google.genai import Client

    s = get_settings()
    if not s.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY required for embeddings")
    return Client(api_key=s.gemini_api_key)


def embed_text(text: str) -> list[float]:
    s = get_settings()
    client = _get_client()
    result = client.models.embed_content(
        model=s.embedding_model,
        contents=text,
    )
    return list(result.embeddings[0].values)


def embed_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    s = get_settings()
    client = _get_client()
    result = client.models.embed_content(
        model=s.embedding_model,
        contents=texts,
    )
    return [list(e.values) for e in result.embeddings]


def store_embedding(
    doc_type: str,
    content: str,
    metadata: dict[str, Any] | None = None,
    doc_id: str | None = None,
    source_file: str | None = None,
) -> str:
    """Vectorize content and store in document_embeddings. Returns the row id."""
    vector = embed_text(content)
    sb = get_supabase()
    row: dict[str, Any] = {
        "doc_type": doc_type,
        "content": content,
        "metadata": metadata or {},
        "embedding": vector,
    }
    if doc_id:
        row["doc_id"] = doc_id
    if source_file:
        row["source_file"] = source_file
    res = sb.table("document_embeddings").insert(row).execute()
    return res.data[0]["id"]


def update_embedding(doc_type: str, doc_id: str, content: str, metadata: dict[str, Any] | None = None) -> None:
    """Re-vectorize: delete old embedding for this doc, insert new one."""
    sb = get_supabase()
    sb.table("document_embeddings").delete().eq("doc_type", doc_type).eq("doc_id", doc_id).execute()
    store_embedding(doc_type=doc_type, content=content, metadata=metadata, doc_id=doc_id)


def search_similar(
    query: str,
    doc_type: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Semantic search via Supabase RPC match_documents."""
    query_vector = embed_text(query)
    sb = get_supabase()
    params: dict[str, Any] = {
        "query_embedding": query_vector,
        "match_count": limit,
    }
    if doc_type:
        params["filter_doc_type"] = doc_type
    res = sb.rpc("match_documents", params).execute()
    return res.data or []
