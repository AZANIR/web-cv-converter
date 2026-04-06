"""CLI: seed initial prompts into the prompts table.

Usage:
    cd backend && python -m scripts.seed_prompts
"""

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

from core.supabase import get_supabase  # noqa: E402

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

PROMPT_DEFINITIONS = [
    {
        "slug": "vacancy_to_case_study",
        "name": "Vacancy → Case Study",
        "description": "Templatize a raw job vacancy into structured case study JSON",
        "file": "vacancy_to_case_study.md",
    },
    {
        "slug": "cv_generation",
        "name": "CV Generation",
        "description": "Generate a full QA CV in Markdown from a vacancy case study + reference context",
        "file": "cv_generation.md",
    },
    {
        "slug": "cv_to_json",
        "name": "CV Markdown → JSON",
        "description": "Convert CV Markdown to structured JSON for PDF rendering",
        "file": "cv_to_json.md",
    },
]


def main() -> None:
    sb = get_supabase()
    created = 0

    for defn in PROMPT_DEFINITIONS:
        existing = sb.table("prompts").select("id").eq("slug", defn["slug"]).limit(1).execute()
        if existing.data:
            logging.info("Skipping existing prompt: %s", defn["slug"])
            continue

        file_path = PROMPTS_DIR / defn["file"]
        if not file_path.exists():
            # For cv_to_json, fall back to the existing prompt file
            if defn["slug"] == "cv_to_json":
                alt = Path(__file__).resolve().parent.parent / "cv_to_json_prompt.md"
                if alt.exists():
                    file_path = alt
                else:
                    logging.warning("No file for %s, skipping", defn["slug"])
                    continue
            else:
                logging.warning("File not found: %s, skipping", file_path)
                continue

        content = file_path.read_text(encoding="utf-8")
        sb.table("prompts").insert({
            "slug": defn["slug"],
            "name": defn["name"],
            "description": defn["description"],
            "content": content,
        }).execute()
        created += 1
        logging.info("Seeded prompt: %s", defn["slug"])

    print(f"Done. Created {created} prompt(s).")


if __name__ == "__main__":
    main()
    sys.exit(0)
