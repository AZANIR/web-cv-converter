# Review Checklist

Apply this checklist to every file in the handoff object.

## Python / FastAPI

### Security (Critical)
- [ ] Every non-public route has `Depends(get_current_user)` or `Depends(require_admin)`
- [ ] No hardcoded secrets, keys, or passwords
- [ ] No f-string SQL construction
- [ ] No `except: pass` swallowing errors silently
- [ ] `get_supabase()` used for all DB access — not direct psycopg2

### Correctness
- [ ] All route handlers are `async def`
- [ ] Pydantic v2 models for all request/response bodies (no `dict` or `Any`)
- [ ] Router registered in `main.py`
- [ ] All imports resolve (no broken import paths)

### Style (Advisory)
- [ ] Functions have type annotations
- [ ] Public functions have docstrings
- [ ] No unused imports
- [ ] Variable names are `snake_case`
- [ ] File is under 300 lines (if larger, consider splitting)

## TypeScript / Vue / Nuxt 3

### Security (Critical)
- [ ] No `v-html` with user-supplied content
- [ ] No secrets in component code or composables
- [ ] No `localStorage` usage for auth tokens
- [ ] Direct `$fetch()` not used in components (must use `useApi.ts`)

### Correctness
- [ ] `<script setup lang="ts">` on all components
- [ ] No manual Vue imports
- [ ] Protected pages have `definePageMeta({ middleware: ['auth'] })`
- [ ] Props typed with `defineProps<Props>()`
- [ ] All imports resolve

### Accessibility (Critical if WCAG violation)
- [ ] All `<img>` have `alt` attribute
- [ ] Icon-only buttons have `aria-label`
- [ ] No `outline-none` without visible focus replacement
- [ ] Form inputs have associated labels

### Style (Advisory)
- [ ] Composables prefixed with `use`
- [ ] Component names are PascalCase
- [ ] No `console.log` in production paths
- [ ] Component under 300 lines

## SQL / Migrations

### Critical
- [ ] No DROP TABLE or DROP COLUMN statements
- [ ] RLS enabled on new tables
- [ ] Policies created for SELECT, INSERT, UPDATE, DELETE
- [ ] No raw user input interpolated into SQL

### Correctness
- [ ] Migration is append-only (added to end of `schema.sql`)
- [ ] Table names follow `snake_case` plural convention
- [ ] Comment block added with date and purpose

## Test Files

### Coverage (Critical)
- [ ] Backend test coverage >= 80% (check via `pytest --cov`)
- [ ] Frontend test coverage >= 70% (check via `vitest --coverage`)

### Correctness
- [ ] Tests cover happy path + at least one error/edge case
- [ ] No hardcoded credentials in test fixtures
- [ ] Tests are deterministic (no `time.sleep` or random without seed)

## Post-Pentest Validation

When running after pentester in the `security-audit` or `security-fix` chain:
- [ ] Cross-reference pentester findings with actual code patterns
- [ ] Verify that flagged files match the reported vulnerability type
- [ ] Flag any additional related vulnerabilities in the same files
- [ ] Confirm remediation guidance is actionable and specific
