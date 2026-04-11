# CLAUDE.md — web-cv-converter

## Stack

- **Backend:** FastAPI (Python 3.11+), Pydantic v2, Supabase (PostgreSQL), Auth0 (JWT RS256)
- **Frontend:** Nuxt 3 + Vue 3 + TypeScript, @nuxt/ui, nuxt-auth-utils
- **Tests:** pytest (backend), vitest (frontend), Playwright (e2e)
- **Deploy:** Docker + Hetzner + Caddy

## Git Workflow (MANDATORY)

- **NEVER commit directly to `master`** — always create a feature branch first
- Before starting work: `git checkout -b <type>/<description>` from up-to-date master
- Branch naming: `feat/`, `fix/`, `test/`, `refactor/`, `docs/`, `ci/`, `chore/` — lowercase, hyphens, max 4 words
- Conventional Commits: `<type>(<scope>): <description>` — lowercase verb, max 72 chars, no period
- Scopes: `backend`, `frontend`, `auth`, `db`, `e2e`, `docs`, `docker`, `deps`
- **NEVER include `Co-Authored-By` lines or AI model names in commits or PRs**
- PR descriptions: plain professional language, no AI attribution

## Backend Conventions

- Type hints on all function signatures
- Auth guard: `Depends(get_current_user)` or `Depends(require_admin)` from `core/auth.py`
- Settings: `get_settings()` from `core/config.py`
- Supabase: `get_supabase()` from `core/supabase.py`
- Routers under `/api` prefix, registered in `backend/main.py`
- Secrets via `get_settings()` only — never hardcode

## Frontend Conventions

- `<script setup lang="ts">` — no Options API
- Use `useApiRequest()` composable for all backend calls — never raw `$fetch()`
- Nuxt auto-imports: don't manually import `ref`, `computed`, `useRoute`, etc.
- No `v-html` with unsanitized user content
- No tokens in `localStorage`

## Security Rules

- Validate all user-supplied URLs before fetching (SSRF prevention)
- Supabase SDK parameterized calls only — no raw SQL
- Never log JWT tokens or PII
- File uploads: validate MIME type and size

## File Organization

| Domain | Path |
|---|---|
| API routes | `backend/routers/` |
| Business logic | `backend/services/` |
| Auth/config | `backend/core/` |
| Backend tests | `backend/tests/` |
| Pages | `frontend/pages/` |
| Components | `frontend/components/` |
| Composables | `frontend/composables/` |
| Frontend tests | `frontend/tests/` |
| E2E tests | `tests/e2e/` |
| Docs | `docs/` |

## Commands

```bash
# Backend
cd backend && pip install -r requirements.txt
cd backend && python -m pytest

# Frontend
cd frontend && npm install
cd frontend && npm run dev
cd frontend && npx vitest run

# E2E
cd frontend && npx playwright test
```
