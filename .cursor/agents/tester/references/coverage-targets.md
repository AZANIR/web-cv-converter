# Coverage Targets

## Thresholds

| Layer | Minimum Coverage | Measured by |
|---|---|---|
| Backend (Python) | 80% line coverage | `pytest --cov` |
| Frontend (TypeScript/Vue) | 70% line coverage | `vitest --coverage` |

These thresholds are enforced by Code Reviewer as a Critical (blocking) finding.

## What Counts

**Backend coverage includes:**
- All files in `backend/routers/`
- All files in `backend/services/`
- All files in `backend/core/` (excluding `__init__.py`)

**Backend coverage excludes:**
- `backend/main.py` (boilerplate)
- Migration files
- `__pycache__` directories

**Frontend coverage includes:**
- All files in `frontend/components/`
- All files in `frontend/composables/`
- All files in `frontend/pages/` (where logic exists)

**Frontend coverage excludes:**
- `frontend/layouts/` (minimal logic)
- `frontend/middleware/` (tested via E2E)
- Type-only files

## Running Coverage Reports

```bash
# Backend
cd backend && pytest --cov=. --cov-report=html --cov-report=term-missing
# Report at: backend/htmlcov/index.html

# Frontend
cd frontend && npx vitest run --coverage
# Report at: frontend/coverage/index.html
```

## Coverage Report Output

Save coverage reports to `reports/coverage/` after each major test run:

```
reports/coverage/
  coverage-{YYYY-MM-DD}-backend.md
  coverage-{YYYY-MM-DD}-frontend.md
```

## Improving Coverage

When coverage is below threshold:
1. Identify uncovered lines with `pytest --cov --cov-report=term-missing`
2. Prioritize: service methods > router handlers > utility functions
3. Focus on behavior, not line count — test meaningful paths
4. A test that only covers a line without asserting behavior is not useful
