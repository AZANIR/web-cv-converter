# web-cv-converter

Повноцінний застосунок: **`backend/`** (FastAPI), **`frontend/`** (Nuxt). Локально: **`docker-compose.yml`** у корені репо.

**Прод на Hetzner + Caddy (`cvc.valtive.io`):** [docs/DEPLOY_HETZNER.md](docs/DEPLOY_HETZNER.md) · GitHub Actions: `.github/workflows/deploy-production.yml`.

---

# Plan B — CV Generator (ReportLab)

Pure Python approach: ReportLab builds the PDF directly using Platypus layout engine and custom Flowable components. No system dependencies required.

---

## Prerequisites

- **Python 3.9+** installed and available in PATH
- No additional system libraries needed

---

## Step 1 — Create and Activate a Virtual Environment

### Windows (PowerShell)

```powershell
cd plan_b_reportlab
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If you get an execution policy error, run first:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### Windows (cmd.exe)

```cmd
cd plan_b_reportlab
python -m venv venv
venv\Scripts\activate.bat
```

### Windows (Git Bash / MSYS2)

```bash
cd plan_b_reportlab
python -m venv venv
source venv/Scripts/activate
```

### macOS / Linux

```bash
cd plan_b_reportlab
python3 -m venv venv
source venv/bin/activate
```

---

## Step 2 — Install Python Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs:
- `reportlab` — PDF generation library (Platypus + Canvas)

---

## Step 3 — Generate the PDF

```bash
python generate.py
```

The PDF appears at `output/CV_Generated.pdf`.

### Custom paths

```bash
python generate.py <styles.json> <data.json> <output_path>
```

Example:

```bash
python generate.py styles.json data.json output/My_CV.pdf
```

---

## Step 4 — Deactivate the Virtual Environment

When done:

```bash
deactivate
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'reportlab'` | Virtual environment not activated, or dependencies not installed — re-do Steps 1–2 |
| `TTFError: Can't open file` | Ensure `fonts/` folder contains all three `.ttf` files |
| `LayoutError: ... too large on page` | Content overflows the frame; check that `data.json` isn't adding unexpected extra content |
| `PermissionError` on output file | Close the PDF if it's open in a viewer, then retry |
| PDF text looks garbled | Font registration failed; verify font file names match those in `generate.py` |

---

## File Overview

```
plan_b_reportlab/
├── generate.py          — Main script: register fonts, build story, render PDF
├── components.py        — Custom Flowable classes:
│                            HeaderBlock  — dark header with name/title/contacts
│                            SectionDivider — two-color horizontal line
│                            TechTagRow   — inline tech badges with auto-wrap
├── styles.json          — Colors, font sizes, spacing configuration
├── data.json            — CV content (name, skills, experience, etc.)
├── requirements.txt     — Python dependencies
├── fonts/
│   ├── LiberationSans-Regular.ttf
│   ├── LiberationSans-Bold.ttf
│   └── LiberationSans-Italic.ttf
└── output/
    └── CV_Generated.pdf — Generated PDF output
```
