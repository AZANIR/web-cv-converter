from pathlib import Path

from core.ai_client import get_ai_client
from core.config import get_settings

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "cv_to_json_prompt.md"


def _load_prompt_template() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_prompt(md_content: str) -> str:
    template = _load_prompt_template()
    delimited_content = f"<user_document>\n{md_content}\n</user_document>"
    return template.replace("[INSERT CV MARKDOWN HERE]", delimited_content)


def convert_md_to_json(md_content: str) -> dict:
    full_prompt = _build_prompt(md_content)
    settings = get_settings()
    providers = [(settings.ai_provider or "gemini").strip().lower()]
    if settings.ai_fallback_providers:
        for raw in settings.ai_fallback_providers.split(","):
            provider = raw.strip().lower()
            if provider and provider not in providers:
                providers.append(provider)

    last_exc: Exception | None = None
    for provider in providers:
        try:
            client = get_ai_client(settings.model_copy(update={"ai_provider": provider}))
            return client.generate_json(full_prompt, temperature=0.2)
        except Exception as exc:
            last_exc = exc
            if provider != providers[-1]:
                continue
            raise
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("No AI provider configured")
