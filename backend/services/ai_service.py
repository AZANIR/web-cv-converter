import json
import re
from pathlib import Path
from typing import Any

from core.config import Settings, get_settings

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "cv_to_json_prompt.md"


def _load_prompt_template() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _assistant_text_anthropic(message: Any) -> str:
    parts: list[str] = []
    for block in message.content or []:
        btype = getattr(block, "type", None)
        if btype == "text":
            t = getattr(block, "text", None) or ""
            if t:
                parts.append(t)
    return "\n".join(parts).strip()


def _finish_reason_is_max_tokens(fr: Any) -> bool:
    if fr is None:
        return False
    if getattr(fr, "name", None) == "MAX_TOKENS":
        return True
    return "MAX_TOKENS" in str(fr).upper()


def _strip_json_fences(text: str) -> str:
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def _extract_json(text: str) -> dict:
    """Parse model output for Anthropic (may include fences / extra text)."""
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


def _parse_gemini_json(text: str, finish_reason: Any) -> dict:
    """
    Gemini with response_mime_type=application/json should return a single object.
    Do not use rfind('}') slicing — on truncated output it cuts mid-structure and
    produces misleading 'Expecting ,' errors.
    """
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
        from json_repair import repair_json

        try:
            fixed = repair_json(text, return_objects=True)
            if isinstance(fixed, dict):
                return fixed
        except Exception:
            pass
        hint = ""
        if text.count("{") > text.count("}") or not text.rstrip().endswith("}"):
            hint = " Output looks truncated — raise GEMINI_MAX_OUTPUT_TOKENS."
        raise ValueError(
            f"Could not parse JSON from Gemini: {e}.{hint}"
        ) from e


def _build_prompt(md_content: str) -> str:
    template = _load_prompt_template()
    return template.replace("[INSERT CV MARKDOWN HERE]", md_content)


def _convert_with_gemini(full_prompt: str, s: Settings) -> dict:
    if not s.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY not set (required when AI_PROVIDER=gemini)")

    from google.genai import Client, types

    client = Client(api_key=s.gemini_api_key)
    response = client.models.generate_content(
        model=s.gemini_model,
        contents=full_prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=s.gemini_max_output_tokens,
            temperature=0.2,
            response_mime_type="application/json",
        ),
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
                "Gemini hit max output tokens; increase GEMINI_MAX_OUTPUT_TOKENS (e.g. 65536) or shorten the CV."
            )

    raw = (response.text or "").strip()
    if not raw and response.candidates:
        fr = response.candidates[0].finish_reason
        raise ValueError(f"Gemini returned no text (finish_reason={fr!r}).")

    if not raw:
        raise ValueError("Gemini returned an empty response.")

    return _parse_gemini_json(raw, fr)


def _convert_with_anthropic(full_prompt: str, s: Settings) -> dict:
    if not s.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set (required when AI_PROVIDER=anthropic)")

    import anthropic

    client = anthropic.Anthropic(api_key=s.anthropic_api_key)
    message = client.messages.create(
        model=s.anthropic_model,
        max_tokens=s.anthropic_max_tokens,
        messages=[{"role": "user", "content": full_prompt}],
    )
    if getattr(message, "stop_reason", None) == "max_tokens":
        raise ValueError(
            "Claude hit max_tokens; increase ANTHROPIC_MAX_TOKENS or shorten the CV / prompt."
        )

    raw = _assistant_text_anthropic(message)
    return _extract_json(raw)


def convert_md_to_json(md_content: str) -> dict:
    s = get_settings()
    full_prompt = _build_prompt(md_content)
    provider = (s.ai_provider or "gemini").strip().lower()

    if provider == "gemini":
        return _convert_with_gemini(full_prompt, s)
    if provider == "anthropic":
        return _convert_with_anthropic(full_prompt, s)

    raise RuntimeError(f"Unknown AI_PROVIDER={provider!r}; use 'gemini' or 'anthropic'.")
