"""Parse vacancy input (text / URL / file) and templatize via AI into case study JSON."""

import json
import logging
import re
from typing import Any

import httpx

from core.config import Settings, get_settings

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


def _strip_json_fences(text: str) -> str:
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def templatize_vacancy(raw_text: str, prompt_content: str, s: Settings | None = None) -> dict[str, Any]:
    """Use AI to convert raw vacancy text into structured case study JSON."""
    s = s or get_settings()
    full_prompt = prompt_content.replace("{{VACANCY_TEXT}}", raw_text)

    provider = (s.ai_provider or "gemini").strip().lower()
    if provider == "gemini":
        return _templatize_gemini(full_prompt, s)
    if provider == "anthropic":
        return _templatize_anthropic(full_prompt, s)
    raise RuntimeError(f"Unknown AI_PROVIDER={provider!r}")


def _templatize_gemini(prompt: str, s: Settings) -> dict[str, Any]:
    from google.genai import Client, types

    client = Client(api_key=s.gemini_api_key)
    response = client.models.generate_content(
        model=s.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=s.gemini_max_output_tokens,
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )
    raw = _strip_json_fences((response.text or "").strip())
    return json.loads(raw)


def _templatize_anthropic(prompt: str, s: Settings) -> dict[str, Any]:
    import anthropic

    client = anthropic.Anthropic(api_key=s.anthropic_api_key)
    message = client.messages.create(
        model=s.anthropic_model,
        max_tokens=s.anthropic_max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = ""
    for block in message.content or []:
        if getattr(block, "type", None) == "text":
            raw += getattr(block, "text", "") or ""
    raw = _strip_json_fences(raw.strip())
    return json.loads(raw)
