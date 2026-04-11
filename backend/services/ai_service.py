from pathlib import Path

from core.ai_client import get_ai_client

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "cv_to_json_prompt.md"


def _load_prompt_template() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_prompt(md_content: str) -> str:
    template = _load_prompt_template()
    delimited_content = f"<user_document>\n{md_content}\n</user_document>"
    return template.replace("[INSERT CV MARKDOWN HERE]", delimited_content)


def convert_md_to_json(md_content: str) -> dict:
    full_prompt = _build_prompt(md_content)
    client = get_ai_client()
    return client.generate_json(full_prompt, temperature=0.2)
