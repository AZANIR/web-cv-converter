"""Unified AI client factory for Gemini and Anthropic providers.

Usage:
    from core.ai_client import get_ai_client

    client = get_ai_client()
    text = client.generate(prompt, temperature=0.7)
    data = client.generate_json(prompt, temperature=0.2)
"""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any

from core.config import Settings, get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers shared across providers
# ---------------------------------------------------------------------------

def _strip_json_fences(text: str) -> str:
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def _finish_reason_is_max_tokens(fr: Any) -> bool:
    if fr is None:
        return False
    if getattr(fr, "name", None) == "MAX_TOKENS":
        return True
    return "MAX_TOKENS" in str(fr).upper()


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------

class AIClient(ABC):
    """Common interface for all AI provider clients."""

    @abstractmethod
    def generate(self, prompt: str, *, temperature: float = 0.7) -> str:
        """Send *prompt* to the AI model and return the raw text response."""

    @abstractmethod
    def generate_json(self, prompt: str, *, temperature: float = 0.2) -> dict[str, Any]:
        """Send *prompt* and parse the response as a JSON object."""


# ---------------------------------------------------------------------------
# Gemini implementation
# ---------------------------------------------------------------------------

class GeminiClient(AIClient):
    """AI client backed by Google Gemini."""

    def __init__(self, s: Settings) -> None:
        if not s.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY not set (required when AI_PROVIDER=gemini)")
        self._s = s

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _call(self, prompt: str, *, temperature: float, response_mime_type: str | None = None) -> tuple[str, Any]:
        """Call the Gemini API and return (raw_text, finish_reason)."""
        from google.genai import Client, types  # type: ignore[import]

        cfg_kwargs: dict[str, Any] = {
            "max_output_tokens": self._s.gemini_max_output_tokens,
            "temperature": temperature,
        }
        if response_mime_type:
            cfg_kwargs["response_mime_type"] = response_mime_type

        client = Client(api_key=self._s.gemini_api_key)
        response = client.models.generate_content(
            model=self._s.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(**cfg_kwargs),
        )

        if response.prompt_feedback is not None:
            br = getattr(response.prompt_feedback, "block_reason", None)
            if br is not None:
                raise ValueError(f"Gemini blocked the request: {br}")

        fr = None
        if response.candidates:
            fr = response.candidates[0].finish_reason
            if fr == types.FinishReason.MAX_TOKENS or _finish_reason_is_max_tokens(fr):
                raise ValueError(
                    "Gemini hit max output tokens; increase GEMINI_MAX_OUTPUT_TOKENS "
                    "(e.g. 65536) or shorten the input."
                )

        raw = (response.text or "").strip()
        if not raw and response.candidates:
            fr = response.candidates[0].finish_reason
            raise ValueError(f"Gemini returned no text (finish_reason={fr!r}).")
        if not raw:
            raise ValueError("Gemini returned an empty response.")

        return raw, fr

    # ------------------------------------------------------------------
    # AIClient interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, *, temperature: float = 0.7) -> str:
        raw, _ = self._call(prompt, temperature=temperature)
        return raw

    def generate_json(self, prompt: str, *, temperature: float = 0.2) -> dict[str, Any]:
        raw, fr = self._call(prompt, temperature=temperature, response_mime_type="application/json")
        return self._parse_json(raw, fr)

    def _parse_json(self, text: str, finish_reason: Any) -> dict[str, Any]:
        text = _strip_json_fences((text or "").strip())
        if not text:
            raise ValueError("Gemini returned an empty response.")

        if _finish_reason_is_max_tokens(finish_reason):
            raise ValueError(
                "Gemini hit the output token limit (response was cut off). "
                "Increase GEMINI_MAX_OUTPUT_TOKENS in backend/.env and restart."
            )

        try:
            out = json.loads(text)
            if isinstance(out, dict):
                return out
            raise ValueError("Expected a JSON object at the root, got another JSON type.")
        except json.JSONDecodeError as e:
            try:
                from json_repair import repair_json  # type: ignore[import]

                fixed = repair_json(text, return_objects=True)
                if isinstance(fixed, dict):
                    return fixed
            except Exception:
                pass
            hint = ""
            if text.count("{") > text.count("}") or not text.rstrip().endswith("}"):
                hint = " Output looks truncated — raise GEMINI_MAX_OUTPUT_TOKENS."
            raise ValueError(f"Could not parse JSON from Gemini: {e}.{hint}") from e


# ---------------------------------------------------------------------------
# Anthropic implementation
# ---------------------------------------------------------------------------

class AnthropicClient(AIClient):
    """AI client backed by Anthropic Claude."""

    def __init__(self, s: Settings) -> None:
        if not s.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set (required when AI_PROVIDER=anthropic)")
        self._s = s

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _call(self, prompt: str, *, temperature: float) -> str:
        """Call the Anthropic API and return the raw text response."""
        import anthropic  # type: ignore[import]

        client = anthropic.Anthropic(api_key=self._s.anthropic_api_key)
        message = client.messages.create(
            model=self._s.anthropic_model,
            max_tokens=self._s.anthropic_max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        if getattr(message, "stop_reason", None) == "max_tokens":
            raise ValueError(
                "Claude hit max_tokens; increase ANTHROPIC_MAX_TOKENS or shorten the input / prompt."
            )

        parts: list[str] = []
        for block in message.content or []:
            if getattr(block, "type", None) == "text":
                t = getattr(block, "text", None) or ""
                if t:
                    parts.append(t)
        return "\n".join(parts).strip()

    # ------------------------------------------------------------------
    # AIClient interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, *, temperature: float = 0.7) -> str:
        return self._call(prompt, temperature=temperature)

    def generate_json(self, prompt: str, *, temperature: float = 0.2) -> dict[str, Any]:
        raw = self._call(prompt, temperature=temperature)
        return self._parse_json(raw)

    def _parse_json(self, text: str) -> dict[str, Any]:
        text = _strip_json_fences(text)
        if not text:
            raise ValueError("The model returned no text; check the API response and model name.")

        try:
            out = json.loads(text)
            if isinstance(out, dict):
                return out
        except json.JSONDecodeError:
            pass

        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                out = json.loads(text[start : end + 1])
                if isinstance(out, dict):
                    return out
            except json.JSONDecodeError as e:
                raise ValueError(
                    "Found {...} in the response but JSON is invalid "
                    f"(truncated output or bad syntax): {e}"
                ) from e

        preview = text[:400].replace("\n", " ")
        raise ValueError(f"Could not parse JSON from the model. First 400 chars: {preview!r}")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_ai_client(s: Settings | None = None) -> AIClient:
    """Return an :class:`AIClient` for the configured provider.

    Reads ``settings.ai_provider`` (``"gemini"`` or ``"anthropic"``).
    Pass *s* explicitly in tests to avoid loading the real settings.
    """
    if s is None:
        s = get_settings()
    provider = (s.ai_provider or "gemini").strip().lower()
    if provider == "gemini":
        return GeminiClient(s)
    if provider == "anthropic":
        return AnthropicClient(s)
    raise RuntimeError(f"Unknown AI_PROVIDER={provider!r}; use 'gemini' or 'anthropic'.")
