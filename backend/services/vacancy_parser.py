"""Parse vacancy input (text / URL / file) and templatize via AI into case study JSON."""

import logging
from typing import Any

import httpx

from core.ai_client import get_ai_client
from core.config import Settings

logger = logging.getLogger(__name__)


async def extract_text_from_url(url: str) -> str:
    """Fetch URL and extract main text content."""
    import trafilatura

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    extracted = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
    if not extracted:
        raise ValueError(f"Could not extract text content from URL: {url}")
    return extracted


def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text from uploaded file bytes."""
    lower = filename.lower()
    if lower.endswith((".md", ".txt")):
        return content.decode("utf-8")
    if lower.endswith(".pdf"):
        from pypdf import PdfReader
        import io

        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if not text:
            raise ValueError("PDF contains no extractable text")
        return text
    raise ValueError(f"Unsupported file type: {filename}")


def templatize_vacancy(raw_text: str, prompt_content: str, s: Settings | None = None) -> dict[str, Any]:
    """Use AI to convert raw vacancy text into structured case study JSON."""
    full_prompt = prompt_content.replace("{{VACANCY_TEXT}}", raw_text)
    client = get_ai_client(s)
    return client.generate_json(full_prompt, temperature=0.2)
