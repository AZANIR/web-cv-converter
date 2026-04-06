"""CLI: seed QA case studies into document_embeddings with vectors.

Usage:
    cd backend && python -m scripts.seed_case_studies
"""

import logging
import sys

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

from services.case_study_loader import seed_embeddings  # noqa: E402

if __name__ == "__main__":
    count = seed_embeddings()
    print(f"Done. Embedded {count} new case study(ies).")
    sys.exit(0)
