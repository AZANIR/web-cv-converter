# Case Study: QA Strategy & LLM Accuracy Program for AI Financial Document Processing Pipeline (NDA)

## Overview
- **Client type:** AI SaaS startup
- **Industry:** Financial Technology / Private Equity (USA)
- **Service provided:** QA Automation Engineer / Data Quality Analyst — full QA strategy setup, LLM accuracy testing, CI/CD integration, pipeline defect tracking
- **Tags:** TypeScript, Python, LLM Testing, AI Pipeline QA, Document Processing, CI/CD, Accuracy Testing, Data Validation, Qase, Jira, Fintech, OCR Testing, Table Extraction, Chart Extraction, KPI Extraction

---

## The Challenge
A US-based AI fintech startup was building an LLM-powered document preprocessing pipeline that extracts structured financial data (tables, charts, KPIs, metadata) from PDFs, PowerPoints, and Excel files for private equity reporting. The system had no QA process, no automation, and no way to measure or track accuracy regressions across LLM/prompt changes.

Key pain points:
- No test coverage for the preprocessing pipeline — broken changes went undetected after LLM or prompt updates
- No accuracy measurement program — the team had no visibility into how correctly the LLM was extracting tables, charts, and KPIs
- Complex, multi-stage pipeline (OCR → Markdown → Table extraction → Chart extraction → KPI extraction → Excel agent) with no stage-level validation
- LLM outputs were non-deterministic — traditional test assertions didn't apply
- No CI/CD integration for test execution
- Critical extraction bugs present but undocumented: repeated table rows (4000+ duplicate lines), missed charts, hallucinated column names, numerical OCR errors

---

## What I Did
- Designed and implemented a comprehensive **QA and accuracy strategy** covering two tracks: operational reliability ("does it run?") and accuracy ("how correct is it?")
- Built smoke and integration tests to validate the full preprocessor green-path — asserting pipeline completion and artifact output for PDF, PowerPoint, and Excel inputs
- Developed a **golden corpus** of 10–20 ground-truth documents (PDFs, Decks, Excel files) with cell-level truth data for regression detection across table matrices, chart series, KPI lists, and metadata
- Implemented **accuracy metrics**: cell accuracy (numeric match with tolerance), row coverage, date alignment (month/quarter/year), chart series similarity, and KPI F1 score
- Introduced a **judge LLM** for sanity-checking markdown integrity and image-to-data consistency in chart extraction — flagging garbled or deformed outputs automatically
- Integrated test execution into **CI/CD pipelines**: every PR triggers smoke tests + mini-golden (2 docs); nightly runs execute the full golden corpus with cost and runtime budget checks
- Documented and categorised extraction defects found in the pipeline, including: repeated table blocks spanning thousands of lines, completely missed circular/overlay charts, OCR number confusion (e.g. 5/6/9 misread as 8), hallucinated column names from background images, and truncated table rows
- Used **Cursor (AI-assisted development)** to accelerate test writing and pipeline improvement — contributing directly to code changes in the preprocessing pipeline, not just writing test scripts

---

## Results
- Full **smoke and integration coverage** established — broken pipeline states caught immediately after any LLM, prompt, or dependency change
- **Accuracy metrics and regression gating** in place — any prompt or code change is blocked from deploy if accuracy drops beyond defined thresholds
- Critical extraction bugs documented with reproducible examples, enabling the dev team to prioritize and resolve high-impact LLM failures before client demos
- **CI/CD-integrated test pipeline** running on every PR and nightly, with cost and runtime alerting
- Accuracy and quality became measurable and visible to the full team — shifting QA from reactive bug-finding to a data-driven accuracy improvement program

---

## What Made the Difference
Treating LLM output testing as a data quality problem — not a traditional pass/fail assertion problem — was the key shift. Building a ground-truth corpus and computing cell-level accuracy metrics gave the team a way to track quality as a number over time, not just a gut feeling. That foundation, combined with a judge LLM for subjective checks, made it possible to gate deploys on quality for the first time.

---

## Relevant for Jobs With:
- QA for AI/LLM-powered pipelines or data extraction systems
- Document processing, OCR, or NLP pipeline testing
- Accuracy testing and ground-truth corpus development
- Fintech, private equity, or financial data platforms
- CI/CD integration for non-deterministic system testing
- Data validation and regression detection for ML outputs
- TypeScript or Python test frameworks
- Senior QA / SDET roles requiring both testing and code contribution
- AI-native teams using Cursor, Claude, or similar tools in development workflows
