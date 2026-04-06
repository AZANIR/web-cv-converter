"""Load and index QA case studies from backend/case_studies/ directory."""

import logging
import os
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CASE_STUDIES_DIR = Path(__file__).resolve().parent.parent / "case_studies"


def _parse_overview(text: str) -> dict[str, Any]:
    """Extract metadata from the ## Overview section."""
    meta: dict[str, Any] = {}
    overview_match = re.search(r"## Overview\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not overview_match:
        return meta

    block = overview_match.group(1)
    for line in block.splitlines():
        line = line.strip().lstrip("- ")
        m = re.match(r"\*\*(.+?):\*\*\s*(.+)", line)
        if not m:
            continue
        key = m.group(1).strip().lower()
        val = m.group(2).strip()
        if key == "tags":
            meta["tags"] = [t.strip() for t in val.split(",")]
        elif key == "industry":
            meta["industry"] = val
        elif key == "client type":
            meta["client_type"] = val
        elif key == "service provided":
            meta["service"] = val
    return meta


def load_all() -> list[dict[str, Any]]:
    """Parse all .md case study files (excluding template) and return structured data."""
    studies: list[dict[str, Any]] = []
    if not CASE_STUDIES_DIR.is_dir():
        logger.warning("Case studies directory not found: %s", CASE_STUDIES_DIR)
        return studies

    for path in sorted(CASE_STUDIES_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        content = path.read_text(encoding="utf-8")
        title_match = re.match(r"#\s+(.+)", content)
        title = title_match.group(1).strip() if title_match else path.stem
        meta = _parse_overview(content)
        studies.append({
            "filename": path.name,
            "title": title,
            "content": content,
            "metadata": meta,
        })
    return studies


def seed_embeddings() -> int:
    """One-time: load all case studies and store embeddings. Returns count of new entries."""
    from services.embedding_service import store_embedding
    from core.supabase import get_supabase

    sb = get_supabase()
    studies = load_all()
    created = 0

    for study in studies:
        existing = (
            sb.table("document_embeddings")
            .select("id")
            .eq("doc_type", "case_study")
            .eq("source_file", study["filename"])
            .limit(1)
            .execute()
        )
        if existing.data:
            logger.info("Skipping already-embedded: %s", study["filename"])
            continue

        store_embedding(
            doc_type="case_study",
            content=study["content"],
            metadata=study["metadata"],
            source_file=study["filename"],
        )
        created += 1
        logger.info("Embedded case study: %s", study["filename"])

    return created
