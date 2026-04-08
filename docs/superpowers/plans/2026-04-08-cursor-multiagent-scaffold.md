# Cursor Multi-Agent System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a complete `.cursor/` multi-agent system for web-cv-converter with 5 rule files, 7 agent skill directories, and memory templates — all production-ready and immediately usable in Cursor.

**Architecture:** Option B (mirrored qa-skills structure). `.cursor/rules/` holds always-apply project conventions. `.cursor/agents/` holds per-agent directories each with `SKILL.md` + `references/`. Memory Keeper state lives in `memory-bank/` (project context) and `docs/qa-memory/` (QA activity log).

**Tech Stack:** Cursor MDC format (YAML frontmatter + Markdown), SKILL.md progressive-loading pattern (L1/L2/L3), qa-project-memory schema from AZANIR/qa-skills.

---

## File Map

**Create (new files):**
- `.cursor/rules/project.mdc`
- `.cursor/rules/git-workflow.mdc`
- `.cursor/rules/project-structure.mdc`
- `.cursor/rules/security.mdc`
- `.cursor/rules/orchestration.mdc`
- `.cursor/agents/orchestrator/SKILL.md`
- `.cursor/agents/orchestrator/references/chains.md`
- `.cursor/agents/orchestrator/references/conflict-rules.md`
- `.cursor/agents/orchestrator/references/task-taxonomy.md`
- `.cursor/agents/document/SKILL.md`
- `.cursor/agents/document/references/doc-templates.md`
- `.cursor/agents/document/references/output-formats.md`
- `.cursor/agents/frontend/SKILL.md`
- `.cursor/agents/frontend/references/nuxt-patterns.md`
- `.cursor/agents/frontend/references/design-system.md`
- `.cursor/agents/frontend/references/component-checklist.md`
- `.cursor/agents/backend/SKILL.md`
- `.cursor/agents/backend/references/fastapi-patterns.md`
- `.cursor/agents/backend/references/supabase-schema.md`
- `.cursor/agents/backend/references/auth0-config.md`
- `.cursor/agents/backend/references/security-self-review.md`
- `.cursor/agents/code-reviewer/SKILL.md`
- `.cursor/agents/code-reviewer/references/severity-matrix.md`
- `.cursor/agents/code-reviewer/references/review-checklist.md`
- `.cursor/agents/code-reviewer/references/style-guide.md`
- `.cursor/agents/tester/SKILL.md`
- `.cursor/agents/tester/references/pytest-patterns.md`
- `.cursor/agents/tester/references/playwright-ts-patterns.md`
- `.cursor/agents/tester/references/vitest-patterns.md`
- `.cursor/agents/tester/references/coverage-targets.md`
- `.cursor/agents/memory-keeper/SKILL.md`
- `.cursor/agents/memory-keeper/references/memory-schema.md`
- `.cursor/agents/memory-keeper/references/memory-bank-schema.md`
- `.cursor/agents/memory-keeper/references/auto-update-protocol.md`
- `.cursor/memory/templates/bugs.md`
- `.cursor/memory/templates/decisions.md`
- `.cursor/memory/templates/test-log.md`
- `.cursor/memory/templates/regressions.md`
- `.cursor/memory/templates/environment.md`
- `memory-bank/projectbrief.md`
- `memory-bank/productContext.md`
- `memory-bank/techContext.md`
- `memory-bank/systemPatterns.md`
- `memory-bank/activeContext.md`
- `memory-bank/progress.md`

---

## Task 1: Create `.cursor/rules/` — Project Conventions

**Files:**
- Create: `.cursor/rules/project.mdc`
- Create: `.cursor/rules/git-workflow.mdc`
- Create: `.cursor/rules/project-structure.mdc`

- [ ] **Step 1: Create `.cursor/rules/project.mdc`**

```markdown
---
description: Global project conventions for web-cv-converter
alwaysApply: true
---

# web-cv-converter Project Conventions

## Stack

| Layer | Technology | Version |
|---|---|---|
| Backend | FastAPI + Python | 3.11+ |
| Schema validation | Pydantic | v2 |
| Database | Supabase (PostgreSQL) | — |
| Auth | Auth0 (JWT RS256) | — |
| Frontend | Nuxt 3 + Vue 3 + TypeScript | — |
| UI library | @nuxt/ui | — |
| Auth (frontend) | nuxt-auth-utils (session) | — |
| Deployment | Docker + Hetzner + Caddy | — |
| Backend tests | pytest | — |
| Frontend tests | vitest | — |
| E2E tests | Playwright (TypeScript) | — |

## Backend Conventions

- Python 3.11+ type hints on all function signatures
- Pydantic v2 for all request/response schemas
- All FastAPI route handlers are `async def`
- Auth guard: `user: dict = Depends(get_current_user)` from `core/auth.py`
- Admin guard: `user: dict = Depends(require_admin)` from `core/auth.py`
- Settings: `get_settings()` from `core/config.py` (pydantic-settings, reads `.env`)
- Supabase client: `get_supabase()` from `core/supabase.py`
- Routers registered in `backend/main.py` under `/api` prefix
- Secrets never in code — always via `get_settings()` attributes
- Migrations: append-only SQL in `backend/supabase/schema.sql`

## API Response Shape

All endpoints return consistent JSON:
```json
{ "data": <payload>, "error": null, "meta": {} }
```
Errors return HTTP 4xx/5xx with `{ "detail": "<message>" }` (FastAPI default).

## HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Success (GET, PUT, PATCH) |
| 201 | Created (POST) |
| 400 | Validation error |
| 401 | Unauthenticated |
| 403 | Forbidden (wrong role or not in allowed_emails) |
| 404 | Not found |
| 500 | Server error |

## Frontend Conventions

- All components use `<script setup lang="ts">` — no Options API
- Composables in `frontend/composables/` — prefix all with `use` (e.g., `useApi.ts`)
- Nuxt 3 auto-imports: do NOT manually import `ref`, `computed`, `useRoute`, etc.
- Layouts in `frontend/layouts/` — default layout wraps all pages
- Middleware in `frontend/middleware/` — `auth.ts` protects authenticated routes
- CSS: global styles only in `frontend/assets/css/main.css`; component styles scoped

## File Organization

| Domain | Write to |
|---|---|
| API routes | `backend/routers/` |
| Business logic | `backend/services/` |
| Auth / config / deps | `backend/core/` |
| DB migrations | `backend/supabase/schema.sql` |
| Pages | `frontend/pages/` |
| Components | `frontend/components/` |
| Composables | `frontend/composables/` |
| Layouts | `frontend/layouts/` |
| Middleware | `frontend/middleware/` |
| Backend tests | `backend/tests/` |
| Frontend unit tests | `frontend/tests/` |
| E2E tests | `tests/e2e/` |
| Documentation | `docs/` |
| QA memory | `docs/qa-memory/` |
| Project context | `memory-bank/` |
```

- [ ] **Step 2: Create `.cursor/rules/git-workflow.mdc`**

```markdown
---
description: Git branching strategy and Conventional Commits for web-cv-converter
alwaysApply: true
---

# Git Workflow

## Branch Policy

**NEVER commit directly to `master`.** All work happens on feature branches.

### Branch Naming

| Type | Pattern | Example |
|---|---|---|
| Feature | `feat/{short-description}` | `feat/add-vacancy-parser` |
| Bug fix | `fix/{short-description}` | `fix/auth-token-expiry` |
| Frontend | `feat/frontend/{description}` | `feat/frontend/upload-form-a11y` |
| Backend | `feat/backend/{description}` | `feat/backend/rate-limit` |
| Tests | `test/{description}` | `test/e2e-login-flow` |
| Docs | `docs/{description}` | `docs/api-contract-update` |
| Refactor | `refactor/{description}` | `refactor/service-layer` |
| CI/CD | `ci/{description}` | `ci/docker-build-cache` |

Use lowercase, hyphens as separators, max 4 words after the type prefix.

### Before Starting Work

1. `git branch --show-current` — confirm you are NOT on master
2. `git pull origin master` — sync with latest
3. `git checkout -b feat/{description}` — create branch

## Conventional Commits

Format: `<type>(<scope>): <description>`

### Types

| Type | When |
|---|---|
| `feat` | New feature or endpoint |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | CSS, formatting, no logic change |
| `refactor` | Code restructuring, no feature/fix |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `ci` | CI/CD pipeline changes |
| `chore` | Deps update, config, maintenance |

### Scopes

| Scope | Applies to |
|---|---|
| `backend` | FastAPI routes, services, core |
| `frontend` | Nuxt pages, components, composables |
| `auth` | Auth0 integration, middleware |
| `db` | Supabase schema, migrations |
| `e2e` | Playwright tests |
| `docs` | Documentation |
| `docker` | Docker/deploy config |
| `deps` | Dependency updates |

### Examples

```
feat(backend): add rate limiting to convert endpoint
fix(auth): handle missing email in Auth0 access token
feat(frontend): add WCAG-compliant upload form
test(e2e): add login flow Playwright spec
docs(db): document Supabase RLS policies
```

### Rules

- Description starts with lowercase verb (add, fix, update, remove)
- Max 72 characters on first line
- No period at end
- Body explains WHY, not what (the diff shows what)
```

- [ ] **Step 3: Create `.cursor/rules/project-structure.mdc`**

```markdown
---
description: Artifact routing — maps each agent to its output directory
globs: "**"
alwaysApply: true
---

# Project Structure — Artifact Routing

When generating project artifacts, save outputs to these directories.
Create the directory on first use if it does not exist.

## Agent Output Directories

| Agent | Output Directory | File Pattern |
|---|---|---|
| document (specs) | `docs/specs/` | `SPEC-{feature}.md` |
| document (API contracts) | `docs/api-contracts/` | `{service}.openapi.yaml` |
| document (ADRs) | `docs/decisions/` | `ADR-{NNN}-{title}.md` |
| document (deployment) | `docs/deployment/` | `{topic}.md` |
| backend (routers) | `backend/routers/` | `{resource}.py` |
| backend (services) | `backend/services/` | `{resource}_service.py` |
| backend (migrations) | `backend/supabase/schema.sql` | append-only SQL |
| backend (core) | `backend/core/` | `{module}.py` |
| frontend (pages) | `frontend/pages/` | `{page}.vue` |
| frontend (components) | `frontend/components/` | `{Component}.vue` |
| frontend (composables) | `frontend/composables/` | `use{Name}.ts` |
| frontend (layouts) | `frontend/layouts/` | `{name}.vue` |
| frontend (middleware) | `frontend/middleware/` | `{name}.ts` |
| tester (backend unit) | `backend/tests/` | `test_{module}.py` |
| tester (frontend unit) | `frontend/tests/` | `{component}.test.ts` |
| tester (E2E) | `tests/e2e/` | `{flow}.spec.ts` |
| tester (coverage report) | `reports/coverage/` | `coverage-{date}.md` |
| code-reviewer (report) | `reports/reviews/` | `review-{date}-{feature}.md` |
| memory-keeper (QA log) | `docs/qa-memory/` | see memory schema |
| memory-keeper (context) | `memory-bank/` | see memory-bank schema |

## Conventions

- All paths are relative to the project root.
- Never pre-create empty directories — create on first artifact write.
- Backend test files follow pytest naming: `test_{module}.py`.
- Frontend test files follow vitest naming: `{Component}.test.ts`.
- E2E spec files follow Playwright naming: `{flow}.spec.ts`.
- Migration SQL is append-only in `backend/supabase/schema.sql` — never drop.
- ADR numbers are sequential zero-padded to 3 digits (ADR-001, ADR-002, ...).
```

- [ ] **Step 4: Verify files exist**

```bash
ls .cursor/rules/
```
Expected output: `git-workflow.mdc  project-structure.mdc  project.mdc`

- [ ] **Step 5: Commit**

```bash
git add .cursor/rules/project.mdc .cursor/rules/git-workflow.mdc .cursor/rules/project-structure.mdc
git commit -m "feat(docs): add cursor project conventions and structure rules"
```

---

## Task 2: Create `.cursor/rules/security.mdc` and `orchestration.mdc`

**Files:**
- Create: `.cursor/rules/security.mdc`
- Create: `.cursor/rules/orchestration.mdc`

- [ ] **Step 1: Create `.cursor/rules/security.mdc`**

```markdown
---
description: OWASP security guardrails for web-cv-converter (FastAPI + Nuxt 3)
globs: "backend/**,frontend/**"
alwaysApply: false
---

# Security Guardrails

## Secrets Policy

- NEVER hardcode secrets, API keys, or tokens in any file.
- Read all secrets via `get_settings()` (backend) or `useRuntimeConfig()` (frontend).
- Add `.env`, `.env.local`, `.env.production` to `.gitignore`.
- Environment variable names are safe to document; their values are not.

## Backend — FastAPI / Auth0 / Supabase

### Authentication
- Every non-public endpoint MUST use `Depends(get_current_user)` from `core/auth.py`.
- Admin endpoints MUST use `Depends(require_admin)` from `core/auth.py`.
- Never bypass auth by checking `user_id` inline — always use the dependency.
- Auth0 JWT validated with RS256 against `https://{domain}/.well-known/jwks.json`.

### Input Validation
- All request bodies validated via Pydantic v2 models — never accept raw `dict`.
- Path and query parameters use FastAPI type annotations with constraints where applicable.
- File uploads: validate MIME type and size before processing.

### SQL / Supabase
- All DB access via `get_supabase()` — use parameterized Supabase SDK calls only.
- Never construct SQL strings with f-strings or `.format()`.
- RLS policies required on every table — document in `backend/supabase/schema.sql`.
- Service role key only used server-side via `get_supabase()` — never expose to client.

### OWASP Top 10 Checklist (FastAPI context)
- [ ] A01 Broken Access Control — auth dependency on every protected route
- [ ] A02 Cryptographic Failures — no secrets in code; HTTPS enforced by Caddy
- [ ] A03 Injection — Supabase SDK parameterized calls only; no raw SQL
- [ ] A04 Insecure Design — rate limiting on AI-heavy endpoints via `services/rate_limit.py`
- [ ] A05 Security Misconfiguration — CORS origins restricted in `main.py`
- [ ] A06 Vulnerable Components — check `requirements.txt` for known CVEs before release
- [ ] A07 Auth Failures — JWT RS256, audience + issuer validated in `core/auth.py`
- [ ] A08 Software Integrity — no unverified npm/pip packages
- [ ] A09 Logging — `logging.basicConfig` in `main.py`; never log JWT tokens or PII
- [ ] A10 SSRF — validate all URLs before making outbound HTTP calls

## Frontend — Nuxt 3

### Auth
- Session managed by `nuxt-auth-utils` — never store tokens in `localStorage`.
- Use `useUserSession()` composable to check auth state.
- Protect routes via `frontend/middleware/auth.ts`.

### XSS Prevention
- Never use `v-html` with user-supplied content.
- All user-provided text rendered via template interpolation `{{ }}` (auto-escaped by Vue).
- Content Security Policy headers set by Caddy — do not override.

### API Calls
- Always use `useApi.ts` composable for backend calls — it attaches auth headers.
- Never call the backend directly with `fetch()` or `$fetch()` in components.
- Never expose `NUXT_OAUTH_*` secrets in public runtime config.
```

- [ ] **Step 2: Create `.cursor/rules/orchestration.mdc`**

```markdown
---
description: Multi-agent routing, task chains, handoff protocol, and conflict rules
alwaysApply: true
---

# Agent Orchestration

## Task Classification

The Orchestrator classifies every incoming request before routing. Task type is the single source of truth for ownership.

| Task Type | Owner Agent | Natural Language Examples |
|---|---|---|
| `write:frontend` | frontend | "add a page", "fix this component", "update the nav" |
| `write:backend` | backend | "add an endpoint", "update the schema", "add a service" |
| `write:docs` | document | "update the API contract", "write an ADR", "document this" |
| `write:tests` | tester | "write tests for", "add coverage for", "test this" |
| `review` | code-reviewer | "review my changes", "audit this file", "check for issues" |
| `chain:*` | orchestrator (routes) | `@orchestrator chain:<name>` |
| `memory:*` | memory-keeper | "what bugs do we know", "init qa memory", "log this decision" |

**Rule:** "write" tasks → domain agent first, then code-reviewer. "review/audit" tasks → code-reviewer only. Two agents never run in parallel on the same file.

## Explicit Agent Invocation

Use `@<agent-name>` to invoke a specific agent directly:
- `@orchestrator chain:api-feature` — run the api-feature chain
- `@backend add a rate-limit endpoint` — route directly to backend agent
- `@tester write pytest for convert router` — route directly to tester agent
- `@memory-keeper init` — initialize QA memory
- `@code-reviewer audit backend/routers/convert.py` — direct review

## Predefined Chains

| Chain | Command | Flow |
|---|---|---|
| **feature** | `@orchestrator chain:feature` | document → backend → frontend → code-reviewer → tester → memory-keeper |
| **api-feature** | `@orchestrator chain:api-feature` | document → backend → code-reviewer → tester (pytest + supertest) → memory-keeper |
| **ui-feature** | `@orchestrator chain:ui-feature` | document → frontend → code-reviewer → tester (vitest + playwright) → memory-keeper |
| **review-only** | `@orchestrator chain:review` | code-reviewer → memory-keeper |
| **stabilize** | `@orchestrator chain:stabilize` | tester (flaky detection) → code-reviewer → memory-keeper |

See `.cursor/agents/orchestrator/references/chains.md` for per-chain input/output contracts.

## Handoff Protocol

Each agent passes a structured handoff object to the next agent in the chain:

```yaml
handoff:
  from: <agent-name>          # who produced this
  to: <agent-name>            # who receives it next
  artifacts:
    - path: <file-path>
      type: implementation | spec | test | report | migration
  context:
    feature: <feature-name>
    chain: <chain-name>
    blocking_issues: []       # non-empty = Orchestrator halts chain
```

**Blocking behavior:** If `blocking_issues` is non-empty after code-reviewer runs, the Orchestrator surfaces the issues to the user and halts the chain. The user must resolve and re-run from the blocking step.

## Conflict Resolution

Single rule — task type decides:
- "write endpoint validation" → `write:backend` → backend implements → code-reviewer audits
- "review the validation" → `review` → code-reviewer only

Memory Keeper always runs last in every chain, never skipped.

## Memory Keeper Auto-Trigger

After every completed chain, Memory Keeper receives the chain summary and:
1. Classifies entries (bugs found, decisions made, tests written)
2. Appends to the relevant `docs/qa-memory/*.md` file
3. Updates `_index.md`
4. Updates `memory-bank/activeContext.md` and `memory-bank/progress.md`

See `.cursor/agents/memory-keeper/references/auto-update-protocol.md` for the full protocol.
```

- [ ] **Step 3: Verify**

```bash
ls .cursor/rules/
```
Expected: `git-workflow.mdc  orchestration.mdc  project-structure.mdc  project.mdc  security.mdc`

- [ ] **Step 4: Commit**

```bash
git add .cursor/rules/security.mdc .cursor/rules/orchestration.mdc
git commit -m "feat(docs): add security guardrails and orchestration rules"
```

---

## Task 3: Create Orchestrator Agent

**Files:**
- Create: `.cursor/agents/orchestrator/SKILL.md`
- Create: `.cursor/agents/orchestrator/references/chains.md`
- Create: `.cursor/agents/orchestrator/references/conflict-rules.md`
- Create: `.cursor/agents/orchestrator/references/task-taxonomy.md`

- [ ] **Step 1: Create `.cursor/agents/orchestrator/SKILL.md`**

```markdown
---
name: orchestrator
description: Master coordinator for web-cv-converter agents. Routes tasks, executes chains, monitors handoffs for blocking issues, resolves ownership conflicts.
---

# Orchestrator Agent

## Purpose

Receives every task, classifies it by type, delegates to the correct agent or chain, monitors handoff objects for blocking issues, and ensures Memory Keeper runs at chain end. Never produces implementation artifacts itself.

## Trigger Phrases

- "run full feature" / `@orchestrator chain:feature`
- "api feature" / `@orchestrator chain:api-feature`
- "ui feature" / `@orchestrator chain:ui-feature`
- "review only" / `@orchestrator chain:review`
- "stabilize tests" / `@orchestrator chain:stabilize`
- Any ambiguous task that spans multiple agents

## Decision Logic

1. **Classify the task** — use `references/task-taxonomy.md` to determine task type
2. **Single agent?** — delegate directly with context
3. **Multi-step?** — select the appropriate chain from `references/chains.md`
4. **Conflict?** — apply rule from `references/conflict-rules.md`
5. **After each agent completes** — check handoff object for `blocking_issues`
6. **End of chain** — trigger Memory Keeper with chain summary

## Can Do

- Classify any incoming task by type
- Route to any agent with full context
- Execute any predefined chain end-to-end
- Halt chain and surface blocking issues to user
- Trigger Memory Keeper at chain end

## Cannot Do

- Produce implementation artifacts (code, specs, tests)
- Override a blocking issue raised by Code Reviewer
- Execute chains in parallel on the same file

## Will Not Do

- Modify production configurations
- Skip the Memory Keeper step at chain end
- Route security-critical tasks without Code Reviewer involvement

## Workflow

1. Receive user request (natural language or explicit command)
2. Classify task type using taxonomy
3. If single-agent task: delegate with context object
4. If chain: execute agents in sequence per chain definition
5. After each step: read handoff object — if `blocking_issues` non-empty, halt and surface to user
6. Final step: invoke Memory Keeper with full chain artifact list

## Quality Checklist

- [ ] Task type classified correctly before routing
- [ ] Correct chain selected for multi-step tasks
- [ ] Handoff object passed between each agent
- [ ] Blocking issues surfaced before proceeding
- [ ] Memory Keeper invoked as final step
```

- [ ] **Step 2: Create `.cursor/agents/orchestrator/references/chains.md`**

```markdown
# Predefined Chains — Input/Output Contracts

## Chain: feature

**Command:** `@orchestrator chain:feature`
**Use when:** Adding a complete feature that requires both backend and frontend changes.

```
document → backend → frontend → code-reviewer → tester → memory-keeper
```

| Step | Input | Output |
|---|---|---|
| document | feature description | `docs/specs/SPEC-{feature}.md` |
| backend | spec file path | router + service files in `backend/` |
| frontend | spec + backend API shape | page/component files in `frontend/` |
| code-reviewer | all changed files | review report + handoff with `blocking_issues` |
| tester | spec + implementation files | pytest + vitest + playwright specs |
| memory-keeper | chain summary | updated `docs/qa-memory/` + `memory-bank/` |

---

## Chain: api-feature

**Command:** `@orchestrator chain:api-feature`
**Use when:** Adding or modifying backend API only (no frontend changes).

```
document → backend → code-reviewer → tester → memory-keeper
```

| Step | Input | Output |
|---|---|---|
| document | feature description | `docs/specs/SPEC-{feature}.md` + `docs/api-contracts/{service}.openapi.yaml` |
| backend | spec + OpenAPI contract | router in `backend/routers/` + service in `backend/services/` |
| code-reviewer | changed backend files | review report |
| tester | router + service files | `backend/tests/test_{module}.py` (pytest) |
| memory-keeper | chain summary | updated qa-memory + memory-bank |

---

## Chain: ui-feature

**Command:** `@orchestrator chain:ui-feature`
**Use when:** Adding or modifying frontend UI only (backend API already exists).

```
document → frontend → code-reviewer → tester → memory-keeper
```

| Step | Input | Output |
|---|---|---|
| document | feature description | `docs/specs/SPEC-{feature}.md` |
| frontend | spec | pages/components in `frontend/` |
| code-reviewer | changed frontend files | review report |
| tester | component files | `frontend/tests/*.test.ts` (vitest) + `tests/e2e/*.spec.ts` (playwright) |
| memory-keeper | chain summary | updated qa-memory + memory-bank |

---

## Chain: review-only

**Command:** `@orchestrator chain:review`
**Use when:** Reviewing existing code without adding features.

```
code-reviewer → memory-keeper
```

| Step | Input | Output |
|---|---|---|
| code-reviewer | file path(s) or diff | review report with severity-tagged findings |
| memory-keeper | review report | log to `docs/qa-memory/decisions.md` if ADR decisions made |

---

## Chain: stabilize

**Command:** `@orchestrator chain:stabilize`
**Use when:** Fixing flaky or failing tests.

```
tester (flaky detection) → code-reviewer → memory-keeper
```

| Step | Input | Output |
|---|---|---|
| tester | test run results / specific test files | flaky test analysis + fixed test files |
| code-reviewer | fixed test files | review report |
| memory-keeper | chain summary | log to `docs/qa-memory/regressions.md` |
```

- [ ] **Step 3: Create `.cursor/agents/orchestrator/references/conflict-rules.md`**

```markdown
# Conflict Resolution Rules

## The Single Rule

**Task type decides ownership. No negotiation, no overlap.**

| If the task is... | Owner is... | Example |
|---|---|---|
| Writing new code | Domain agent (backend/frontend/tester/document) | "add validation to this endpoint" → backend |
| Reviewing existing code | code-reviewer | "review the validation in this endpoint" → code-reviewer |
| Writing tests | tester | "write tests for the validation" → tester |
| Writing docs | document | "document the validation schema" → document |

## Edge Cases

**"Refactor and review this endpoint"**
→ backend writes the refactor → code-reviewer reviews → tester verifies tests still pass

**"Add tests and review coverage"**
→ tester writes tests → code-reviewer reviews coverage threshold

**"Update the schema and document it"**
→ backend updates `schema.sql` → document updates `docs/api-contracts/`

**"Fix this bug"**
→ Classify: is this a backend or frontend bug?
→ backend or frontend fixes → code-reviewer verifies fix is not introducing new issues

## Hard Rules

1. Two agents NEVER edit the same file in the same chain step.
2. code-reviewer NEVER writes implementation code — only reports findings.
3. memory-keeper NEVER modifies implementation, test, or documentation files.
4. backend agent NEVER writes frontend files and vice versa.
```

- [ ] **Step 4: Create `.cursor/agents/orchestrator/references/task-taxonomy.md`**

```markdown
# Task Taxonomy

Complete classification of task types with decision criteria.

## write:backend

**Triggers:**
- "add endpoint / route / API"
- "update Supabase schema / migration"
- "add service / business logic"
- "configure Auth0"
- "add Pydantic model / schema"
- "update core config"

**Files touched:** `backend/routers/`, `backend/services/`, `backend/core/`, `backend/supabase/schema.sql`

---

## write:frontend

**Triggers:**
- "add page / component / layout"
- "update composable / middleware"
- "fix UI / style / accessibility issue"
- "add form / upload / modal"

**Files touched:** `frontend/pages/`, `frontend/components/`, `frontend/composables/`, `frontend/layouts/`, `frontend/middleware/`

---

## write:docs

**Triggers:**
- "write spec / ADR / decision record"
- "update API contract / OpenAPI"
- "document this feature / endpoint"
- "update README / deployment doc"

**Files touched:** `docs/specs/`, `docs/api-contracts/`, `docs/decisions/`, `docs/deployment/`

---

## write:tests

**Triggers:**
- "write tests / add test coverage"
- "add pytest / vitest / playwright tests"
- "test this endpoint / component / flow"
- "improve coverage"

**Files touched:** `backend/tests/`, `frontend/tests/`, `tests/e2e/`

---

## review

**Triggers:**
- "review this / review my changes"
- "audit / check for issues"
- "is this secure / correct / clean?"
- "code review"

**Files touched:** code-reviewer reads files, writes report to `reports/reviews/`

---

## chain:*

**Triggers:** Explicit `@orchestrator chain:<name>` command.
**See:** `references/chains.md`

---

## memory:*

**Triggers:**
- "what bugs do we know / search memory"
- "init qa memory / initialize memory"
- "log this bug / add this decision"
- "what was done / memory status"
- "memory summary"

**Routed to:** memory-keeper directly

---

## Ambiguous Task Handling

If a task could be `write:backend` OR `write:frontend`:
1. Ask one clarifying question: "Is this change to the API or the UI?"
2. Route based on answer.

If a task is clearly both (full feature), default to `@orchestrator chain:feature`.
```

- [ ] **Step 5: Verify**

```bash
ls .cursor/agents/orchestrator/ && ls .cursor/agents/orchestrator/references/
```
Expected: `SKILL.md  references/` and `chains.md  conflict-rules.md  task-taxonomy.md`

- [ ] **Step 6: Commit**

```bash
git add .cursor/agents/orchestrator/
git commit -m "feat(docs): add orchestrator agent skill and references"
```

---

## Task 4: Create Document Agent

**Files:**
- Create: `.cursor/agents/document/SKILL.md`
- Create: `.cursor/agents/document/references/doc-templates.md`
- Create: `.cursor/agents/document/references/output-formats.md`

- [ ] **Step 1: Create `.cursor/agents/document/SKILL.md`**

```markdown
---
name: document
description: Generates and maintains all project documentation — specs, ADRs, OpenAPI contracts, deployment docs, README updates — for web-cv-converter.
---

# Document Agent

## Purpose

Owns all written project knowledge for web-cv-converter. Generates structured documentation from requirements and feature descriptions. Keeps docs synchronized with implementation.

## Trigger Phrases

- "write a spec for" / "create a feature spec"
- "write an ADR" / "record this decision" / "architecture decision"
- "update the API contract" / "generate OpenAPI for"
- "document this endpoint / feature / change"
- "update the README" / "update deployment docs"
- Invoked by Orchestrator at the start of every `feature`, `api-feature`, or `ui-feature` chain

## Workflow

1. Receive feature description or task context
2. Identify document type (spec, ADR, OpenAPI, deployment, README)
3. Load the correct template from `references/doc-templates.md`
4. Generate document using project context from `memory-bank/`
5. Write to the correct output directory per `project-structure.mdc`
6. Return handoff object with artifact path

## Can Do

- Generate feature specs from natural language descriptions
- Generate OpenAPI YAML contracts from endpoint descriptions
- Write ADRs with context, decision, and consequences
- Update existing docs when features change
- Write deployment documentation

## Cannot Do

- Generate test cases (Tester Agent owns this)
- Write implementation code (Backend/Frontend Agents own this)
- Make architectural decisions (record decisions, do not make them)

## Will Not Do

- Delete existing documentation without explicit instruction
- Override decisions recorded in `docs/decisions/`

## Output Paths

| Document Type | Path | Naming |
|---|---|---|
| Feature spec | `docs/specs/` | `SPEC-{feature}.md` |
| ADR | `docs/decisions/` | `ADR-{NNN}-{title}.md` |
| OpenAPI contract | `docs/api-contracts/` | `{service}.openapi.yaml` |
| Deployment docs | `docs/deployment/` | `{topic}.md` |
| README update | project root | `README.md` |

## Quality Checklist

- [ ] Document uses the correct template from `references/doc-templates.md`
- [ ] All section headers present (no empty sections)
- [ ] ADR number is sequential with existing ADRs in `docs/decisions/`
- [ ] OpenAPI contract validates against OpenAPI 3.0 schema
- [ ] No secrets or credentials in any document
```

- [ ] **Step 2: Create `.cursor/agents/document/references/doc-templates.md`**

````markdown
# Document Templates

## Feature Spec Template (`SPEC-{feature}.md`)

```markdown
# SPEC-{feature}: {Feature Title}

**Date:** YYYY-MM-DD
**Status:** Draft | Approved | Implemented
**Author:** {agent or user}
**Related ADR:** ADR-{NNN} (if applicable)

---

## Overview

{1-3 sentences describing the feature and why it exists}

## Requirements

| ID | Requirement | Priority |
|---|---|---|
| REQ-001 | {requirement text} | Must / Should / Could |

## API Changes

{Describe new or modified endpoints. Link to OpenAPI contract if generated.}

| Method | Path | Auth Required | Description |
|---|---|---|---|
| POST | `/api/{resource}` | Yes | {description} |

## Data Model Changes

{Describe any new tables, columns, or migrations in `backend/supabase/schema.sql`}

## Frontend Changes

{Describe new pages, components, or composables}

## Acceptance Criteria

- [ ] {Criterion 1}
- [ ] {Criterion 2}

## Out of Scope

- {What this spec explicitly does NOT cover}
```

---

## ADR Template (`ADR-{NNN}-{title}.md`)

```markdown
# ADR-{NNN}: {Title}

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-{NNN}
**Deciders:** {who made this decision}

---

## Context

{Describe the situation that forces this decision. What is the problem?}

## Decision

{State the decision clearly. What was chosen?}

## Consequences

**Positive:**
- {What improves}

**Negative / Trade-offs:**
- {What gets harder or what we give up}

**Neutral:**
- {Side effects that are neither good nor bad}
```

---

## OpenAPI Contract Template (`{service}.openapi.yaml`)

```yaml
openapi: "3.0.3"
info:
  title: "{Service} API"
  version: "1.0.0"
  description: "{Service description}"

servers:
  - url: "http://localhost:8000/api"
    description: Local development
  - url: "https://{domain}/api"
    description: Production

paths:
  /{resource}:
    post:
      summary: "{Action description}"
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/{RequestSchema}"
      responses:
        "200":
          description: Success
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/{ResponseSchema}"
        "401":
          description: Unauthenticated
        "403":
          description: Forbidden

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    {RequestSchema}:
      type: object
      required:
        - {field}
      properties:
        {field}:
          type: string
          description: "{field description}"
```
````

- [ ] **Step 3: Create `.cursor/agents/document/references/output-formats.md`**

```markdown
# Output Formats

## Markdown Conventions

All Markdown documents follow these conventions:

- H1 (`#`) for document title only — one per file
- H2 (`##`) for major sections
- H3 (`###`) for subsections
- Tables use GFM pipe syntax with header separator row
- Code blocks use fenced triple backtick with language identifier
- Checklists use `- [ ]` syntax (GitHub-compatible)
- No trailing whitespace; single blank line between sections

## Status Labels

Use consistent status labels across all documents:

| Document Type | Valid Statuses |
|---|---|
| Spec | Draft, Approved, Implemented, Deprecated |
| ADR | Proposed, Accepted, Deprecated, Superseded |
| API Contract | Draft, Stable, Deprecated |

## ADR Numbering

ADRs are numbered sequentially. Before writing a new ADR:
1. `ls docs/decisions/` to find the highest existing number
2. Increment by 1 (zero-pad to 3 digits: ADR-001, ADR-002, ...)

## OpenAPI Validation

Before finalizing an OpenAPI contract:
- All `$ref` values resolve to defined schemas in `components/schemas`
- All paths have at least one response defined
- All request bodies have a schema
- Security schemes match those defined in `components/securitySchemes`

## File Encoding

- UTF-8, LF line endings
- No BOM
```

- [ ] **Step 4: Commit**

```bash
git add .cursor/agents/document/
git commit -m "feat(docs): add document agent skill and references"
```

---

## Task 5: Create Frontend Agent

**Files:**
- Create: `.cursor/agents/frontend/SKILL.md`
- Create: `.cursor/agents/frontend/references/nuxt-patterns.md`
- Create: `.cursor/agents/frontend/references/design-system.md`
- Create: `.cursor/agents/frontend/references/component-checklist.md`

- [ ] **Step 1: Create `.cursor/agents/frontend/SKILL.md`**

```markdown
---
name: frontend
description: Owns the Nuxt 3 UI layer for web-cv-converter. Implements pages, components, composables, and layouts. Enforces design system rules and WCAG 2.2 accessibility.
---

# Frontend Agent

## Purpose

Implements all Nuxt 3 UI for web-cv-converter. Follows design system conventions, enforces WCAG 2.2 accessibility, and flags (but does not block) design deviations for Code Reviewer.

## Tech Context

- Framework: Nuxt 3, Vue 3 Composition API, TypeScript
- UI library: @nuxt/ui (Tailwind-based)
- Auth: `nuxt-auth-utils` — use `useUserSession()` to check auth state
- API calls: `useApi.ts` composable — never call `$fetch` directly in components
- Composables: `useApi.ts` (API calls), `useAuthApiHeaders.ts` (auth headers)
- Existing pages: index, login, dashboard, history, generate-history, access-denied, admin/, generate/
- Existing components: AppNav, ConversionCard, GeneratedCvResult, MdEditor, StatusBadge, UploadForm, VacancyInputForm

## Trigger Phrases

- "add a page / component / layout"
- "fix the UI / style"
- "update the upload form / nav / card"
- "add accessibility / WCAG fix"
- "fix composable / middleware"
- Invoked by Orchestrator in `feature` and `ui-feature` chains

## Workflow

1. Read the feature spec from `docs/specs/`
2. Identify what needs to change: page, component, composable, layout, or middleware
3. Check existing components in `frontend/components/` before creating new ones
4. Implement using patterns from `references/nuxt-patterns.md`
5. Apply design system rules from `references/design-system.md`
6. Run self-check against `references/component-checklist.md`
7. Return handoff object with changed file paths

## Can Do

- Create and modify Vue 3 SFC pages and components
- Create and modify TypeScript composables with `use` prefix
- Update layouts and middleware
- Enforce WCAG 2.2 color contrast, keyboard navigation, ARIA labels
- Flag design deviations in handoff object as advisory issues

## Cannot Do

- Write backend API endpoints
- Write E2E Playwright tests (Tester Agent owns this)
- Make API contract decisions

## Will Not Do

- Use Options API — always `<script setup lang="ts">`
- Use `v-html` with user-supplied content
- Store auth tokens in `localStorage`
- Call backend directly with `fetch()` — always use `useApi.ts`

## Quality Checklist

- [ ] `<script setup lang="ts">` used in all components
- [ ] No manual Vue imports (Nuxt auto-imports)
- [ ] Auth state via `useUserSession()` — not hardcoded
- [ ] All API calls via `useApi.ts` composable
- [ ] WCAG 2.2: all interactive elements keyboard accessible
- [ ] WCAG 2.2: color contrast ratio ≥ 4.5:1 for normal text
- [ ] WCAG 2.2: all images have `alt` attribute
- [ ] No `v-html` with user content
- [ ] Component passes `references/component-checklist.md`
```

- [ ] **Step 2: Create `.cursor/agents/frontend/references/nuxt-patterns.md`**

````markdown
# Nuxt 3 Patterns

## Page Structure

```vue
<!-- frontend/pages/example.vue -->
<template>
  <div>
    <h1>Page Title</h1>
    <!-- content -->
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ['auth'],  // add if page requires login
})

const { data, error } = await useApi('/api/resource')
</script>
```

## Component Structure

```vue
<!-- frontend/components/ExampleCard.vue -->
<template>
  <div class="...">
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  status?: 'pending' | 'done' | 'error'
}
const props = withDefaults(defineProps<Props>(), {
  status: 'pending',
})
const emit = defineEmits<{
  (e: 'action', id: string): void
}>()
</script>
```

## Composable Pattern

```typescript
// frontend/composables/useResourceName.ts
export function useResourceName() {
  const state = ref<ResourceType | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchResource(id: string) {
    loading.value = true
    error.value = null
    try {
      const { data } = await useApi(`/api/resource/${id}`)
      state.value = data
    } catch (e) {
      error.value = 'Failed to load resource'
    } finally {
      loading.value = false
    }
  }

  return { state, loading, error, fetchResource }
}
```

## Auth Check Pattern

```vue
<script setup lang="ts">
const { user, loggedIn } = useUserSession()

// Redirect if not logged in (alternative to middleware for inline checks)
if (!loggedIn.value) {
  await navigateTo('/login')
}
</script>
```

## API Call Pattern

```typescript
// Always use useApi composable — never $fetch directly in components
const { data, error, refresh } = await useApi('/api/convert', {
  method: 'POST',
  body: { markdown, vacancy },
})
```

## Auth Middleware (`frontend/middleware/auth.ts`)

```typescript
export default defineNuxtRouteMiddleware(() => {
  const { loggedIn } = useUserSession()
  if (!loggedIn.value) {
    return navigateTo('/login')
  }
})
```

## Server Route Pattern (`frontend/server/api/`)

```typescript
// frontend/server/api/resource.get.ts
export default defineEventHandler(async (event) => {
  const session = await getUserSession(event)
  if (!session.user) {
    throw createError({ statusCode: 401, message: 'Unauthenticated' })
  }
  // proxy to backend...
})
```
````

- [ ] **Step 3: Create `.cursor/agents/frontend/references/design-system.md`**

```markdown
# Design System

## UI Library

@nuxt/ui (Tailwind CSS-based). Use `UButton`, `UCard`, `UInput`, `UBadge`, `UModal` etc. from the library before creating custom components.

## Spacing Scale (Tailwind)

Use Tailwind spacing classes only. Do NOT use arbitrary values like `p-[13px]`.

| Purpose | Class |
|---|---|
| Page padding | `p-6` or `px-6 py-4` |
| Card padding | `p-4` |
| Section gap | `gap-4` or `gap-6` |
| Inline gap | `gap-2` |
| Form field gap | `space-y-4` |

## Color Usage

Use Tailwind semantic colors via @nuxt/ui tokens. Avoid hardcoded hex values.

| Semantic | Class |
|---|---|
| Primary action | `bg-primary` / `text-primary` |
| Destructive | `bg-red-500` / `text-red-600` |
| Success | `text-green-600` |
| Muted text | `text-gray-500` |
| Card background | `bg-white dark:bg-gray-900` |

## Typography

| Element | Class |
|---|---|
| Page title | `text-2xl font-bold` |
| Section heading | `text-lg font-semibold` |
| Body text | `text-sm` or `text-base` |
| Muted/helper text | `text-sm text-gray-500` |

## WCAG 2.2 Requirements

**Color contrast:** Normal text must have ≥ 4.5:1 contrast ratio. Large text (≥ 18pt or 14pt bold) must have ≥ 3:1.

**Keyboard navigation:**
- All interactive elements (buttons, links, inputs) must be focusable with Tab
- Focus indicators must be visible — do NOT `outline-none` without replacement
- Custom interactive elements must have `tabindex="0"` and keyboard event handlers

**ARIA:**
- All `<img>` tags require `alt` attribute (empty string `alt=""` for decorative images)
- Icon-only buttons require `aria-label`
- Form inputs require associated `<label>` or `aria-label`
- Loading states: use `aria-busy="true"` on container
- Error messages: use `role="alert"` or `aria-live="polite"`

**Forms:**
- Each input has a visible label or `aria-label`
- Validation errors are announced (use `role="alert"` on error container)
- Required fields marked with `aria-required="true"` or `required` attribute

## Existing Component Conventions

Before creating a new component, check if one of these existing components covers the need:
- `ConversionCard.vue` — card for displaying conversion results
- `StatusBadge.vue` — status indicator badge
- `UploadForm.vue` — file/markdown upload form
- `VacancyInputForm.vue` — vacancy URL/text input
- `MdEditor.vue` — Markdown editor
- `GeneratedCvResult.vue` — CV generation result display
- `AppNav.vue` — navigation bar
```

- [ ] **Step 4: Create `.cursor/agents/frontend/references/component-checklist.md`**

```markdown
# Component Checklist

Run this checklist before returning a frontend handoff object.

## Structure
- [ ] File is in the correct directory (`pages/`, `components/`, `composables/`, `layouts/`, `middleware/`)
- [ ] Component file uses `<script setup lang="ts">` — no Options API
- [ ] No manual imports of Vue primitives (Nuxt auto-imports `ref`, `computed`, `watch`, etc.)
- [ ] Props typed with TypeScript interface and `defineProps<Props>()`
- [ ] Emits typed with `defineEmits<{...}>()`

## Auth & API
- [ ] Auth state uses `useUserSession()` — not hardcoded checks
- [ ] All API calls go through `useApi.ts` — no direct `$fetch()` in components
- [ ] Protected pages have `definePageMeta({ middleware: ['auth'] })`

## Security
- [ ] No `v-html` with user-provided content
- [ ] No secrets or API keys in component code
- [ ] No `localStorage` usage for auth tokens

## Accessibility (WCAG 2.2)
- [ ] All `<img>` have `alt` attribute
- [ ] Icon-only buttons have `aria-label`
- [ ] All form inputs have visible label or `aria-label`
- [ ] Focus outline is visible (no bare `outline-none`)
- [ ] Interactive elements are keyboard-accessible (Tab + Enter/Space)
- [ ] Error messages use `role="alert"` or `aria-live`

## Design System
- [ ] Uses @nuxt/ui components (`UButton`, `UCard`, `UInput`, etc.) where applicable
- [ ] Spacing uses Tailwind scale — no arbitrary values
- [ ] Colors use semantic Tailwind/nuxt-ui tokens — no hardcoded hex
```

- [ ] **Step 5: Commit**

```bash
git add .cursor/agents/frontend/
git commit -m "feat(docs): add frontend agent skill and references"
```

---

## Task 6: Create Backend Agent

**Files:**
- Create: `.cursor/agents/backend/SKILL.md`
- Create: `.cursor/agents/backend/references/fastapi-patterns.md`
- Create: `.cursor/agents/backend/references/supabase-schema.md`
- Create: `.cursor/agents/backend/references/auth0-config.md`
- Create: `.cursor/agents/backend/references/security-self-review.md`

- [ ] **Step 1: Create `.cursor/agents/backend/SKILL.md`**

```markdown
---
name: backend
description: Owns the full FastAPI stack for web-cv-converter — routes, services, Pydantic schemas, Supabase migrations, Auth0 configuration. Performs OWASP self-review before every handoff.
---

# Backend Agent

## Purpose

Implements all FastAPI backend for web-cv-converter. Owns the full stack: routes in `backend/routers/`, business logic in `backend/services/`, configuration in `backend/core/`, and database migrations in `backend/supabase/schema.sql`. Performs a security self-review before every handoff to Code Reviewer.

## Tech Context

- FastAPI with Python 3.11+, Pydantic v2
- Auth: `Depends(get_current_user)` or `Depends(require_admin)` from `core/auth.py`
- Config: `get_settings()` from `core/config.py` (reads `.env` via pydantic-settings)
- DB: `get_supabase()` from `core/supabase.py` (Supabase Python SDK)
- Existing routers: admin, convert, generate, history, me, prompts
- Existing services: ai_service, conversion_runner, generation_runner, pdf_service, prompt_service, rate_limit, storage_service, vacancy_parser, embedding_service, case_study_loader

## Trigger Phrases

- "add endpoint / route / API"
- "update Supabase schema / migration"
- "add/update service / business logic"
- "configure Auth0 / update auth"
- "add Pydantic model / schema"
- Invoked by Orchestrator in `feature` and `api-feature` chains

## Workflow

1. Read the feature spec from `docs/specs/`
2. Determine what needs to change: router, service, schema, migration, or core config
3. Check existing routers and services before creating new ones
4. Implement using patterns from `references/fastapi-patterns.md`
5. Add migration to `backend/supabase/schema.sql` if DB changes needed
6. Run self-review against `references/security-self-review.md`
7. Return handoff object with changed file paths and empty `blocking_issues`

## Can Do

- Create and modify FastAPI routers with typed Pydantic v2 schemas
- Create and modify service modules with async business logic
- Append migration SQL to `backend/supabase/schema.sql`
- Update Auth0 configuration in `core/auth.py` or `core/config.py`
- Update environment variable definitions in `core/config.py`

## Cannot Do

- Write frontend Vue components
- Write test files (Tester Agent owns this)
- Make Auth0 tenant configuration changes in the Auth0 dashboard

## Will Not Do

- Commit secrets, API keys, or tokens to any file
- Bypass auth dependencies (`get_current_user`, `require_admin`)
- Use raw f-string SQL — always use Supabase SDK parameterized calls
- Drop existing database tables or columns

## Quality Checklist

- [ ] All route handlers are `async def`
- [ ] All request/response bodies use Pydantic v2 models
- [ ] Protected routes use `Depends(get_current_user)` or `Depends(require_admin)`
- [ ] All DB calls use `get_supabase()` SDK — no raw SQL strings
- [ ] New settings added to `Settings` class in `core/config.py`
- [ ] Migration SQL appended to `backend/supabase/schema.sql` (append-only)
- [ ] Security self-review checklist passed (see `references/security-self-review.md`)
- [ ] No secrets hardcoded
```

- [ ] **Step 2: Create `.cursor/agents/backend/references/fastapi-patterns.md`**

````markdown
# FastAPI Patterns

## Router Pattern

```python
# backend/routers/{resource}.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.auth import get_current_user
from services.{resource}_service import {Resource}Service

router = APIRouter(prefix="/{resource}s", tags=["{resource}"])


class {Resource}Request(BaseModel):
    field: str
    # add fields here


class {Resource}Response(BaseModel):
    id: str
    field: str
    # add fields here


@router.post("/", response_model={Resource}Response, status_code=201)
async def create_{resource}(
    body: {Resource}Request,
    user: dict = Depends(get_current_user),
) -> {Resource}Response:
    service = {Resource}Service()
    result = await service.create(user["user_id"], body)
    return result


@router.get("/{id}", response_model={Resource}Response)
async def get_{resource}(
    id: str,
    user: dict = Depends(get_current_user),
) -> {Resource}Response:
    service = {Resource}Service()
    result = await service.get(id, user["user_id"])
    if not result:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    return result
```

## Service Pattern

```python
# backend/services/{resource}_service.py
from core.supabase import get_supabase


class {Resource}Service:
    def __init__(self):
        self.sb = get_supabase()
        self.table = "{resource}s"

    async def create(self, user_id: str, data: dict) -> dict:
        result = self.sb.table(self.table).insert({
            "user_id": user_id,
            **data,
        }).execute()
        return result.data[0]

    async def get(self, id: str, user_id: str) -> dict | None:
        result = (
            self.sb.table(self.table)
            .select("*")
            .eq("id", id)
            .eq("user_id", user_id)  # row-level ownership check
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    async def list_for_user(self, user_id: str) -> list[dict]:
        result = (
            self.sb.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data
```

## Register Router in main.py

```python
# backend/main.py — add to existing imports and router registrations
from routers import {resource}
app.include_router({resource}.router, prefix="/api")
```

## Settings Pattern (adding new env var)

```python
# backend/core/config.py — add to Settings class
class Settings(BaseSettings):
    # ... existing fields ...
    new_service_api_key: str = ""
    new_service_base_url: str = "https://api.example.com"
```

## Error Handling Pattern

```python
from fastapi import HTTPException

# 400 — validation / bad request
raise HTTPException(status_code=400, detail="Invalid input: {reason}")

# 404 — not found
raise HTTPException(status_code=404, detail="{Resource} not found")

# 403 — forbidden (wrong owner)
raise HTTPException(status_code=403, detail="Access denied")

# 500 — unexpected (log it first)
import logging
logger = logging.getLogger(__name__)
logger.exception("Unexpected error in {endpoint}")
raise HTTPException(status_code=500, detail="Internal server error")
```
````

- [ ] **Step 3: Create `.cursor/agents/backend/references/supabase-schema.md`**

```markdown
# Supabase Schema Conventions

## Migration File

All migrations are append-only SQL in `backend/supabase/schema.sql`.

Rules:
- NEVER drop tables or columns
- NEVER remove RLS policies
- Append new `CREATE TABLE`, `ALTER TABLE`, or `CREATE POLICY` statements at the end
- Comment each migration block with date and purpose

```sql
-- 2026-04-08: Add {feature} table
CREATE TABLE IF NOT EXISTS {table_name} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS: users can only access their own rows
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;

CREATE POLICY "{table_name}_user_select"
    ON {table_name} FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "{table_name}_user_insert"
    ON {table_name} FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "{table_name}_user_update"
    ON {table_name} FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "{table_name}_user_delete"
    ON {table_name} FOR DELETE
    USING (auth.uid() = user_id);
```

## Naming Conventions

| Object | Convention | Example |
|---|---|---|
| Tables | `snake_case`, plural | `cv_conversions` |
| Columns | `snake_case` | `user_id`, `created_at` |
| Foreign keys | `{table}_id` | `profile_id` |
| Indexes | `idx_{table}_{column}` | `idx_cv_conversions_user_id` |
| RLS Policies | `"{table}_{role}_{action}"` | `"cv_conversions_user_select"` |

## Existing Tables (from schema.sql)

- `profiles` — user profiles (id, email, full_name, avatar_url, role)
- `allowed_emails` — email allowlist for access control
- Check `backend/supabase/schema.sql` for the full current schema before adding tables.

## RLS Requirement

Every new table MUST have RLS enabled and appropriate policies. Minimum: SELECT, INSERT, UPDATE, DELETE policies for the owning user.
```

- [ ] **Step 4: Create `.cursor/agents/backend/references/auth0-config.md`**

```markdown
# Auth0 Configuration

## How Auth Works in this Project

1. Frontend authenticates via Auth0 OAuth2 flow using `nuxt-auth-utils`
2. Frontend stores session server-side (not in localStorage)
3. Frontend server routes proxy calls to FastAPI with Bearer token
4. FastAPI validates JWT RS256 via Auth0 JWKS endpoint in `core/auth.py`
5. Email verified against `allowed_emails` Supabase table
6. User profile upserted to `profiles` table on each valid request

## Key Functions in `core/auth.py`

| Function | Purpose |
|---|---|
| `get_current_user(credentials, id_token_header)` | FastAPI dependency — validates JWT, checks email allowlist, upserts profile. Returns `{"user_id": str, "email": str}` |
| `require_admin(user)` | FastAPI dependency — wraps `get_current_user`, checks `admin_emails` config or `profiles.role = "admin"` |
| `decode_auth0_token(token)` | Internal — validates RS256 JWT against Auth0 JWKS |
| `check_allowed_email(email)` | Internal — checks `allowed_emails` table |

## Required Environment Variables

| Variable | Description |
|---|---|
| `AUTH0_DOMAIN` | Auth0 domain (e.g. `dev-xxx.us.auth0.com`) |
| `AUTH0_API_AUDIENCE` | API audience identifier |
| `AUTH0_CLIENT_ID` | SPA client ID (optional, for ID token email fallback) |
| `ADMIN_EMAILS` | Comma-separated admin email list |

## Adding New Auth0 Settings

If a new Auth0 setting is needed, add it to `Settings` in `core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing ...
    auth0_new_setting: str = ""
```

Then read it via `get_settings().auth0_new_setting`.

## Auth Dependency Usage

```python
# Standard protected endpoint
@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user  # {"user_id": "auth0|...", "email": "user@example.com"}

# Admin-only endpoint
@router.delete("/{id}")
async def delete_item(id: str, user: dict = Depends(require_admin)):
    ...
```

## X-Auth0-ID-Token Header

When the Auth0 API access token does not contain an email claim, the frontend can send the ID token in the `X-Auth0-ID-Token` header. `get_current_user` will decode it to extract the email. This is already handled in `core/auth.py`.
```

- [ ] **Step 5: Create `.cursor/agents/backend/references/security-self-review.md`**

```markdown
# Security Self-Review Checklist

Run this checklist before returning a backend handoff object. All items must pass. Add failing items to `blocking_issues` in the handoff object.

## Authentication & Authorization

- [ ] Every non-public endpoint has `Depends(get_current_user)` or `Depends(require_admin)`
- [ ] No endpoint checks `user_id` inline without using the dependency
- [ ] Admin endpoints use `Depends(require_admin)`, not manual role checks
- [ ] No JWT tokens logged or returned in error messages

## Input Validation

- [ ] All request bodies are Pydantic v2 models — no raw `dict` or `Any`
- [ ] File uploads validate MIME type before processing
- [ ] Numeric fields have min/max constraints where appropriate (e.g., `Field(ge=1, le=100)`)
- [ ] URL fields validated with `AnyHttpUrl` type where used

## Database / Supabase

- [ ] All DB queries use Supabase SDK parameterized calls — no f-string SQL
- [ ] New tables have RLS enabled per `supabase-schema.md` template
- [ ] Data returned to the user belongs to them (`.eq("user_id", user["user_id"])` or equivalent)
- [ ] Supabase service role key not exposed outside `core/supabase.py`

## Secrets & Configuration

- [ ] No hardcoded secrets, API keys, or connection strings in any file
- [ ] All secrets read via `get_settings()` attributes
- [ ] No secrets logged at any log level

## Error Handling

- [ ] No stack traces or internal details in HTTP error responses
- [ ] 404 responses do not reveal whether a resource exists (for non-owner requests)
- [ ] 500 errors logged before returning generic message

## CORS

- [ ] `allowed_origins` read from `get_settings()` — not hardcoded in `main.py`
- [ ] No wildcard `*` CORS origin in production config

## Rate Limiting

- [ ] AI-heavy endpoints (convert, generate) use `rate_limit.py` service
- [ ] Rate limit errors return 429 with `Retry-After` header where applicable
```

- [ ] **Step 6: Commit**

```bash
git add .cursor/agents/backend/
git commit -m "feat(docs): add backend agent skill and references"
```

---

## Task 7: Create Code Reviewer Agent

**Files:**
- Create: `.cursor/agents/code-reviewer/SKILL.md`
- Create: `.cursor/agents/code-reviewer/references/severity-matrix.md`
- Create: `.cursor/agents/code-reviewer/references/review-checklist.md`
- Create: `.cursor/agents/code-reviewer/references/style-guide.md`

- [ ] **Step 1: Create `.cursor/agents/code-reviewer/SKILL.md`**

```markdown
---
name: code-reviewer
description: Tiered quality gate for web-cv-converter. Critical findings (security, broken tests, missing auth) are blocking. Style and convention findings are advisory.
---

# Code Reviewer Agent

## Purpose

Enforces code quality, security, and convention standards across the entire codebase. Activated after every "write" task. Produces a structured review report with severity-tagged findings. Critical findings halt the chain.

## Trigger Phrases

- "review my changes" / "code review" / "audit this"
- "check for issues / security issues / style issues"
- "is this correct / secure / clean?"
- Invoked automatically by Orchestrator after every Backend, Frontend, or Tester output

## Tier Definitions

### Critical (Blocking)
Chain halts until resolved. User must fix before proceeding.
- Security vulnerabilities (auth bypass, SQL injection, XSS, exposed secrets)
- Missing auth dependency on protected endpoint
- Broken imports or syntax errors
- Test coverage below threshold (< 80% backend, < 70% frontend)
- Hardcoded secrets or credentials in code

### Advisory (Non-Blocking)
Logged in review report. User can proceed but should address.
- Naming convention violations
- Missing type annotations on new functions
- Unused imports or variables
- Missing docstrings on public functions
- Component size > 300 lines (suggest splitting)
- Missing error handling in non-critical paths

## Workflow

1. Receive handoff object with list of changed file paths
2. Read each file
3. Apply `references/review-checklist.md` systematically
4. Classify each finding by severity using `references/severity-matrix.md`
5. Write review report to `reports/reviews/review-{date}-{feature}.md`
6. Return handoff object:
   - `blocking_issues`: list of critical findings
   - `advisory_issues`: list of advisory findings

## Can Do

- Review any Python, TypeScript, Vue, SQL, or YAML file
- Identify security vulnerabilities per OWASP Top 10 (FastAPI context)
- Check WCAG 2.2 compliance in Vue components
- Verify test coverage thresholds are met
- Flag style and convention violations

## Cannot Do

- Fix code — only reports findings
- Write implementation code or tests
- Override a blocking finding

## Will Not Do

- Approve code with critical findings
- Skip security checks for "small" changes

## Quality Checklist

- [ ] All changed files reviewed (not sampled)
- [ ] Every finding classified as critical or advisory
- [ ] Review report written to `reports/reviews/`
- [ ] Handoff `blocking_issues` populated for critical findings
- [ ] Handoff `advisory_issues` populated for advisory findings
```

- [ ] **Step 2: Create `.cursor/agents/code-reviewer/references/severity-matrix.md`**

```markdown
# Severity Matrix

## Critical (Blocking)

These findings MUST be resolved before the chain proceeds.

| Finding | Example | Why Critical |
|---|---|---|
| Missing auth dependency | `@router.get("/data")` with no `Depends(get_current_user)` | Any user can access protected data |
| Hardcoded secret | `api_key = "sk-..."` in source file | Secret exposure in git history |
| SQL injection vector | `f"SELECT * WHERE id = {user_input}"` | Data exfiltration or destruction |
| Broken import | `from services.nonexistent import Foo` | Runtime crash |
| Syntax error | Unparseable Python or TypeScript | Code does not run |
| Auth bypass | Checking `user_id` inline instead of via dependency | Exploitable by token manipulation |
| XSS vector | `v-html="userInput"` in Vue component | Script injection |
| Coverage below threshold | Backend < 80% or frontend < 70% | Untested code ships |
| Missing Pydantic model | `body: dict` instead of typed Pydantic model | No input validation |
| Exposed service role key | `SUPABASE_SERVICE_ROLE_KEY` in frontend code | Full DB access from client |

## Advisory (Non-Blocking)

These findings are logged and should be addressed but do not halt the chain.

| Finding | Example | Guidance |
|---|---|---|
| Missing type annotation | `def func(x):` in Python | Add `: type` annotation |
| Naming convention | `getUserData()` in Python | Use `get_user_data()` |
| Unused import | `import os` never used | Remove |
| Missing docstring | Public function with no docstring | Add one-line description |
| Component too large | Vue SFC > 300 lines | Consider splitting |
| Magic number | `if count > 47:` | Extract to named constant |
| Missing error handling | `result.data[0]` without checking `result.data` | Add guard |
| Deprecated API | Using `@nuxt/bridge` patterns | Update to Nuxt 3 native |
| Missing ARIA label | `<button><icon /></button>` with no label | Add `aria-label` |
| Console.log in production | `console.log(userData)` | Remove or replace with logger |
```

- [ ] **Step 3: Create `.cursor/agents/code-reviewer/references/review-checklist.md`**

```markdown
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
- [ ] Backend test coverage ≥ 80% (check via `pytest --cov`)
- [ ] Frontend test coverage ≥ 70% (check via `vitest --coverage`)

### Correctness
- [ ] Tests cover happy path + at least one error/edge case
- [ ] No hardcoded credentials in test fixtures
- [ ] Tests are deterministic (no `time.sleep` or random without seed)
```

- [ ] **Step 4: Create `.cursor/agents/code-reviewer/references/style-guide.md`**

```markdown
# Style Guide

## Python

Follows PEP 8 with project-specific additions.

| Rule | Standard | Example |
|---|---|---|
| Functions / methods | `snake_case` | `get_user_data()` |
| Classes | `PascalCase` | `ConversionService` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_FILE_SIZE_MB = 10` |
| Private functions | `_snake_case` prefix | `_validate_token()` |
| Type hints | Required on all public functions | `def create(self, user_id: str) -> dict:` |
| Max line length | 100 characters | — |
| Imports | stdlib → third-party → local, separated by blank lines | — |

## TypeScript / Vue

Follows Vue 3 Composition API conventions.

| Rule | Standard | Example |
|---|---|---|
| Components | PascalCase file + component name | `UploadForm.vue` |
| Composables | `use` prefix, camelCase | `useApi.ts` |
| Pages | kebab-case or Nuxt route convention | `generate-history.vue` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES = 3` |
| Interfaces | PascalCase with `I` prefix optional | `interface Props { ... }` |
| Reactive variables | Descriptive, no `val` / `data` suffix | `isLoading`, `conversions` |

## Commit Messages

Follow Conventional Commits as defined in `.cursor/rules/git-workflow.mdc`.

| Violation | Advisory Note |
|---|---|
| Message in past tense | Use present tense: "add" not "added" |
| Message > 72 chars | Shorten or move detail to body |
| Missing type prefix | Add `feat:`, `fix:`, `docs:` etc. |
| Generic message | "fix bug" is not useful — describe what bug |
```

- [ ] **Step 5: Commit**

```bash
git add .cursor/agents/code-reviewer/
git commit -m "feat(docs): add code-reviewer agent skill and references"
```

---

## Task 8: Create Tester Agent

**Files:**
- Create: `.cursor/agents/tester/SKILL.md`
- Create: `.cursor/agents/tester/references/pytest-patterns.md`
- Create: `.cursor/agents/tester/references/playwright-ts-patterns.md`
- Create: `.cursor/agents/tester/references/vitest-patterns.md`
- Create: `.cursor/agents/tester/references/coverage-targets.md`

- [ ] **Step 1: Create `.cursor/agents/tester/SKILL.md`**

```markdown
---
name: tester
description: Owns all test types for web-cv-converter — pytest (backend), vitest (frontend), Playwright TypeScript (E2E). Writes tests, runs them, and produces coverage reports.
---

# Tester Agent

## Purpose

Writes and maintains all test types for web-cv-converter. Selects the correct framework based on what's being tested, follows TDD where possible, and produces coverage reports after every run.

## Frameworks by Test Type

| Test Type | Framework | Output Directory |
|---|---|---|
| Backend unit + integration | pytest | `backend/tests/test_{module}.py` |
| Frontend unit + component | vitest | `frontend/tests/{Component}.test.ts` |
| E2E flows | Playwright (TypeScript) | `tests/e2e/{flow}.spec.ts` |
| Coverage reports | pytest-cov / vitest --coverage | `reports/coverage/` |

## Trigger Phrases

- "write tests for" / "add test coverage"
- "write pytest / vitest / playwright tests"
- "test this endpoint / component / flow"
- "check test coverage"
- "fix flaky tests" / "stabilize tests"
- Invoked by Orchestrator in all chains as the final write step

## Workflow

1. Read the spec and/or implementation files to understand what to test
2. Determine test type: backend unit, frontend unit, or E2E
3. Write tests following patterns in `references/` for the relevant framework
4. Include: happy path, at least one error case, one edge case per test suite
5. Run tests and verify they pass
6. Produce coverage report
7. Return handoff with test file paths and coverage metrics

## Can Do

- Write pytest tests for any FastAPI router or service
- Write vitest tests for Vue components and composables
- Write Playwright E2E specs for user flows
- Run test suites and report results
- Detect and fix flaky tests (chain:stabilize)

## Cannot Do

- Write implementation code (Backend/Frontend Agents own this)
- Change test coverage thresholds without explicit instruction

## Will Not Do

- Write tests that hardcode production credentials
- Skip error case coverage
- Mark tests as passing without running them

## Quality Checklist

- [ ] Tests cover happy path + error case + edge case
- [ ] No hardcoded credentials or tokens in test fixtures
- [ ] Tests are deterministic (no `time.sleep` without good reason)
- [ ] Backend coverage ≥ 80% after new tests
- [ ] Frontend coverage ≥ 70% after new tests
- [ ] All tests pass before returning handoff
```

- [ ] **Step 2: Create `.cursor/agents/tester/references/pytest-patterns.md`**

````markdown
# pytest Patterns

## Test File Structure

```python
# backend/tests/test_{module}.py
import pytest
from httpx import AsyncClient
from main import app
from core.config import get_settings


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.fixture
def auth_headers():
    """Return mock auth headers for tests. Override get_current_user dependency."""
    return {"Authorization": "Bearer test-token"}
```

## Overriding Auth Dependency in Tests

```python
from fastapi.testclient import TestClient
from main import app
from core.auth import get_current_user

MOCK_USER = {"user_id": "test-user-123", "email": "test@example.com"}

def override_get_current_user():
    return MOCK_USER

app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)
```

## Router Test Pattern

```python
# backend/tests/test_convert_router.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from core.auth import get_current_user

MOCK_USER = {"user_id": "user-123", "email": "test@example.com"}
app.dependency_overrides[get_current_user] = lambda: MOCK_USER
client = TestClient(app)


def test_convert_success():
    with patch("routers.convert.ConversionService.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = {"id": "conv-1", "status": "done"}
        response = client.post("/api/convert", json={"markdown": "# Hello", "vacancy": "..."})
    assert response.status_code == 200
    assert response.json()["id"] == "conv-1"


def test_convert_unauthenticated():
    # Remove the override temporarily
    app.dependency_overrides.clear()
    response = client.post("/api/convert", json={"markdown": "# Hello"})
    assert response.status_code == 401
    # Restore
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER


def test_convert_missing_body():
    response = client.post("/api/convert", json={})
    assert response.status_code == 422  # Pydantic validation error
```

## Service Test Pattern

```python
# backend/tests/test_{resource}_service.py
import pytest
from unittest.mock import MagicMock, patch
from services.{resource}_service import {Resource}Service


@pytest.fixture
def mock_supabase():
    with patch("services.{resource}_service.get_supabase") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


def test_create_success(mock_supabase):
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "row-1", "user_id": "user-1"}
    ]
    service = {Resource}Service()
    result = service.create("user-1", {"field": "value"})
    assert result["id"] == "row-1"


def test_get_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value.data = []
    service = {Resource}Service()
    result = service.get("nonexistent", "user-1")
    assert result is None
```

## Run Commands

```bash
# Run all tests
cd backend && pytest

# Run with coverage
cd backend && pytest --cov=. --cov-report=term-missing

# Run specific test file
cd backend && pytest tests/test_convert_router.py -v

# Run specific test
cd backend && pytest tests/test_convert_router.py::test_convert_success -v
```
````

- [ ] **Step 3: Create `.cursor/agents/tester/references/playwright-ts-patterns.md`**

````markdown
# Playwright TypeScript Patterns

## Test File Structure

```typescript
// tests/e2e/{flow}.spec.ts
import { test, expect } from '@playwright/test'

test.describe('{Feature} flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to starting page
    await page.goto('/')
  })

  test('happy path: user can {action}', async ({ page }) => {
    // Arrange
    await page.goto('/login')
    
    // Act
    await page.getByLabel('Email').fill('test@example.com')
    await page.getByRole('button', { name: 'Log in' }).click()
    
    // Assert
    await expect(page).toHaveURL('/dashboard')
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
  })

  test('error case: {condition} shows error message', async ({ page }) => {
    await page.goto('/generate')
    await page.getByRole('button', { name: 'Generate' }).click()
    await expect(page.getByRole('alert')).toContainText('required')
  })
})
```

## Auth Setup (Authenticated Tests)

```typescript
// tests/e2e/auth.setup.ts
import { test as setup } from '@playwright/test'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  // Complete Auth0 login flow
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!)
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!)
  await page.getByRole('button', { name: 'Continue' }).click()
  await page.waitForURL('/dashboard')
  // Save session state
  await page.context().storageState({ path: 'tests/e2e/.auth/user.json' })
})
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:3000',
    storageState: 'tests/e2e/.auth/user.json',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'e2e',
      dependencies: ['setup'],
    },
  ],
})
```

## Common Locators (prefer role/label over CSS)

```typescript
// By role
page.getByRole('button', { name: 'Submit' })
page.getByRole('heading', { name: 'Dashboard' })
page.getByRole('link', { name: 'History' })
page.getByRole('alert')

// By label
page.getByLabel('Email')
page.getByLabel('Vacancy URL')

// By test ID (last resort)
page.getByTestId('upload-form')
```

## Run Commands

```bash
# Run all E2E tests
npx playwright test

# Run specific spec
npx playwright test tests/e2e/login.spec.ts

# Run with UI
npx playwright test --ui

# Show last report
npx playwright show-report
```
````

- [ ] **Step 4: Create `.cursor/agents/tester/references/vitest-patterns.md`**

````markdown
# Vitest Patterns

## Component Test Structure

```typescript
// frontend/tests/{Component}.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import {Component} from '~/components/{Component}.vue'

describe('{Component}', () => {
  it('renders with required props', () => {
    const wrapper = mount({Component}, {
      props: { title: 'Test Title' },
    })
    expect(wrapper.text()).toContain('Test Title')
  })

  it('emits action event when button clicked', async () => {
    const wrapper = mount({Component}, {
      props: { id: 'item-1', title: 'Test' },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('action')).toBeTruthy()
    expect(wrapper.emitted('action')![0]).toEqual(['item-1'])
  })

  it('shows error state when status is error', () => {
    const wrapper = mount({Component}, {
      props: { title: 'Test', status: 'error' },
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(true)
  })
})
```

## Composable Test Structure

```typescript
// frontend/tests/use{Name}.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { use{Name} } from '~/composables/use{Name}'

// Mock useApi
vi.mock('~/composables/useApi', () => ({
  useApi: vi.fn().mockResolvedValue({ data: { id: '1' } }),
}))

describe('use{Name}', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with null state', () => {
    const { state, loading, error } = use{Name}()
    expect(state.value).toBeNull()
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('fetches data and updates state', async () => {
    const { state, fetchResource } = use{Name}()
    await fetchResource('test-id')
    expect(state.value).toEqual({ id: '1' })
  })
})
```

## Run Commands

```bash
# Run all frontend unit tests
cd frontend && npx vitest run

# Run with coverage
cd frontend && npx vitest run --coverage

# Run in watch mode
cd frontend && npx vitest

# Run specific test file
cd frontend && npx vitest run tests/UploadForm.test.ts
```

## vitest.config.ts (reference — already exists in project)

```typescript
// frontend/vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      reporter: ['text', 'json', 'html'],
      threshold: {
        lines: 70,
        functions: 70,
        branches: 70,
      },
    },
  },
})
```
````

- [ ] **Step 5: Create `.cursor/agents/tester/references/coverage-targets.md`**

```markdown
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
```

- [ ] **Step 6: Commit**

```bash
git add .cursor/agents/tester/
git commit -m "feat(docs): add tester agent skill and references"
```

---

## Task 9: Create Memory Keeper Agent

**Files:**
- Create: `.cursor/agents/memory-keeper/SKILL.md`
- Create: `.cursor/agents/memory-keeper/references/memory-schema.md`
- Create: `.cursor/agents/memory-keeper/references/memory-bank-schema.md`
- Create: `.cursor/agents/memory-keeper/references/auto-update-protocol.md`

- [ ] **Step 1: Create `.cursor/agents/memory-keeper/SKILL.md`**

```markdown
---
name: memory-keeper
description: Maintains cross-session project memory for web-cv-converter. Logs QA activity to docs/qa-memory/ and keeps memory-bank/ context current. Runs as the final step of every agent chain.
---

# Memory Keeper Agent

## Purpose

Persists project state across sessions. Logs all QA activity to `docs/qa-memory/` and maintains the project context files in `memory-bank/`. Runs automatically as the final step of every orchestrated chain. Supports direct invocation for memory search, initialization, and manual entries.

## Commands

| Command (EN) | Action |
|---|---|
| `init` | Create `docs/qa-memory/` structure from `.cursor/memory/templates/` |
| `update` | Auto-record after a chain (called automatically) |
| `search <query>` | Search across all `docs/qa-memory/` files and `_index.md` |
| `status` | Show memory health: entry count, last update |
| `log bug` | Manually add a bug entry |
| `add decision` | Manually add an ADR entry to `docs/qa-memory/decisions.md` |
| `summary` | Summary of recent activity |

## Trigger Phrases

- "init qa memory" / "initialize memory"
- "what bugs do we know" / "search memory for"
- "log this bug / decision / regression"
- "memory status" / "memory summary"
- "what was done recently"
- Invoked automatically by Orchestrator at end of every chain

## Workflow

### Auto-Update (Post-Chain)

1. Receive chain summary from Orchestrator (list of artifacts + chain type)
2. Classify entries: bugs found, decisions made, tests written, regressions
3. Check `_index.md` for duplicate entries
4. Append new entries to correct `docs/qa-memory/` files
5. Update `_index.md` with new entry IDs and keywords
6. Update `memory-bank/activeContext.md` with latest work
7. Update `memory-bank/progress.md` if features completed or blockers resolved

### Init

1. Check if `docs/qa-memory/` exists
2. If not, copy templates from `.cursor/memory/templates/` to `docs/qa-memory/`
3. Create `_index.md` with header
4. Create `_archive/` subdirectory
5. Confirm with entry count (6 files created)

## Can Do

- Initialize `docs/qa-memory/` structure
- Append entries to any `docs/qa-memory/` file
- Update `memory-bank/` context files
- Search across all memory files
- Archive entries when files exceed 200 entries

## Cannot Do

- Modify implementation files, test files, or specification documents
- Delete entries (only archives)
- Create new memory file types beyond the defined schema

## Will Not Do

- Store secrets or credentials in any memory file
- Overwrite existing memory entries (only append)

## Quality Checklist

- [ ] Entry ID generated using correct format (BUG/DEC/TST/REG-YYYY-MM-DD-NNN)
- [ ] Duplicate check performed before appending
- [ ] `_index.md` updated with new entry
- [ ] `memory-bank/activeContext.md` updated
- [ ] No secrets or credentials in any entry
```

- [ ] **Step 2: Create `.cursor/agents/memory-keeper/references/memory-schema.md`**

```markdown
# docs/qa-memory/ Schema

All files live in `docs/qa-memory/`. Entries are append-only.

## bugs.md — Bug Log

```markdown
## BUG-YYYY-MM-DD-NNN

**Title:** {Brief bug description}
**Status:** Open | Resolved | Won't Fix
**Severity:** Critical | High | Medium | Low
**Found by:** {agent or user}
**Date found:** YYYY-MM-DD
**Date resolved:** YYYY-MM-DD (if applicable)

**Description:**
{What the bug is, where it occurs}

**Reproduction steps:**
1. {Step 1}
2. {Step 2}

**Root cause:** {What caused it}

**Resolution:** {How it was fixed, or why it won't be fixed}

**Related:** {TST-YYYY-MM-DD-NNN, PR link, etc.}

---
```

## decisions.md — Architecture Decision Log

```markdown
## DEC-YYYY-MM-DD-NNN

**Title:** {Decision title}
**Date:** YYYY-MM-DD
**Status:** Accepted | Proposed | Deprecated
**Decided by:** {agent or user}

**Context:** {Why this decision was needed}

**Decision:** {What was decided}

**Consequences:**
- {Impact 1}
- {Impact 2}

---
```

## test-log.md — Test Execution Log

```markdown
## TST-YYYY-MM-DD-NNN

**Feature:** {Feature tested}
**Date:** YYYY-MM-DD
**Agent:** tester
**Chain:** {chain name}

**Tests written:**
- `{file path}` — {N} tests ({framework})

**Results:** {N} passed, {N} failed, {N} skipped

**Coverage:** Backend {N}% | Frontend {N}%

**Notes:** {Any notable findings}

---
```

## regressions.md — Regression Log

```markdown
## REG-YYYY-MM-DD-NNN

**Description:** {What regressed}
**Date detected:** YYYY-MM-DD
**Status:** Active | Fixed
**Affected tests:** {test file paths}

**Pattern:** {What kind of regression: flaky, broken by change, environment-specific}

**Root cause:** {What caused the regression}

**Fix applied:** {What was changed to fix it}

---
```

## environment.md — Environment Reference

```markdown
## {Environment Name}

**Last updated:** YYYY-MM-DD

| Variable | Purpose | Set in |
|---|---|---|
| `AUTH0_DOMAIN` | Auth0 tenant domain | `.env` |
| `AUTH0_API_AUDIENCE` | API identifier | `.env` |
| `SUPABASE_URL` | Supabase project URL | `.env` |
| `NUXT_PUBLIC_API_URL` | Backend URL for frontend | `.env` (frontend) |

**Supabase:** Project URL documented here (no credentials)
**Auth0:** Tenant name documented here (no secrets)

---
```

## _index.md — Search Index

```markdown
# QA Memory Index

_Last updated: YYYY-MM-DD_

## Quick Reference

| ID | Type | Title | Date | Status |
|---|---|---|---|---|
| BUG-YYYY-MM-DD-001 | Bug | {title} | YYYY-MM-DD | Open |
| DEC-YYYY-MM-DD-001 | Decision | {title} | YYYY-MM-DD | Accepted |
| TST-YYYY-MM-DD-001 | Test run | {feature} | YYYY-MM-DD | — |

## Keyword Index

- **auth**: BUG-..., DEC-..., TST-...
- **supabase**: BUG-..., DEC-...
- **convert**: TST-..., REG-...
```
```

- [ ] **Step 3: Create `.cursor/agents/memory-keeper/references/memory-bank-schema.md`**

```markdown
# memory-bank/ Schema

Files in `memory-bank/` describe WHAT THE PROJECT IS (static context).
Files in `docs/qa-memory/` describe WHAT QA HAS DONE (activity log).

Memory Keeper updates `memory-bank/` when significant changes occur — not after every chain.

## projectbrief.md

```markdown
# Project Brief: web-cv-converter

## Overview

**Project:** web-cv-converter
**Type:** Web application — CV/resume conversion to PDF with AI
**Status:** Active development

## Goal

Convert Markdown CVs to polished PDFs using AI assistance. Users paste their Markdown CV and a job vacancy, the AI optimizes the CV for the vacancy, and the result is rendered as a professional PDF.

## Core Features

- Markdown CV → AI-optimized → PDF conversion
- Vacancy URL/text parsing for job-specific optimization
- Conversion history and management
- Admin panel for user management
- Multiple case study templates for QA

## Success Criteria

- Users can convert a CV end-to-end in under 60 seconds
- Generated PDFs are professionally formatted
- Auth-protected — only allowed emails can access
```

## productContext.md

```markdown
# Product Context

## Why It Exists

Manual CV tailoring for each job application is time-consuming. This tool automates CV optimization for specific vacancies using AI, producing a professional PDF output.

## Target Users

- QA engineers and professionals customizing CVs for job applications
- Internal users (access controlled via allowed_emails table)

## Problems Solved

- Time spent manually tailoring CV content for each vacancy
- Formatting inconsistency in self-produced PDFs
- Context-switching between writing tools and design tools

## User Journey

1. Log in via Auth0
2. Paste or upload Markdown CV
3. Input vacancy URL or text
4. AI analyzes and optimizes CV for vacancy
5. Download PDF or view in browser
6. Access history of past conversions
```

## techContext.md

```markdown
# Technical Context

## Stack

| Layer | Technology | Notes |
|---|---|---|
| Backend | FastAPI (Python 3.11+) | Async, Pydantic v2 |
| Auth | Auth0 (RS256 JWT) | `core/auth.py`, allowed_emails table |
| Database | Supabase (PostgreSQL) | RLS enforced, `core/supabase.py` |
| AI | Gemini (default) or Anthropic | Configurable via `AI_PROVIDER` env var |
| Frontend | Nuxt 3 + Vue 3 + TypeScript | `@nuxt/ui`, `nuxt-auth-utils` |
| Deployment | Docker Compose + Hetzner VPS | Caddy reverse proxy |
| PDF generation | WeasyPrint / internal service | `services/pdf_service.py` |

## Key Environment Variables

| Variable | Service | Purpose |
|---|---|---|
| `AUTH0_DOMAIN` | Backend | Auth0 tenant domain |
| `AUTH0_API_AUDIENCE` | Backend | API identifier |
| `SUPABASE_URL` | Backend | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend | DB access (server-side only) |
| `GEMINI_API_KEY` | Backend | Gemini AI API key |
| `NUXT_PUBLIC_API_URL` | Frontend | Backend API URL |
| `NUXT_SESSION_PASSWORD` | Frontend | Session encryption key |
| `NUXT_OAUTH_AUTH0_*` | Frontend | Auth0 OAuth config |

## Service Dependencies

- Auth0 tenant: documented in environment.md
- Supabase project: documented in environment.md
```

## systemPatterns.md

```markdown
# System Patterns

## Architecture

Single-service backend (FastAPI) + Single-page frontend (Nuxt 3 SSR). Communication via REST API with JWT auth.

## Key Patterns

**Auth pattern:** Auth0 JWT RS256 → `get_current_user` dependency → allowed_emails check → profile upsert

**API pattern:** Router (`routers/`) delegates to Service (`services/`) which uses Supabase SDK (`core/supabase.py`). Routes return Pydantic models.

**Frontend data pattern:** Server route in `frontend/server/api/` proxies to backend with auth headers from session. Components call via `useApi.ts` composable.

**Migration pattern:** Append-only SQL in `backend/supabase/schema.sql`. RLS required on every table.

## Coding Conventions

- Python: async/await everywhere, Pydantic v2 strict typing, `snake_case`
- TypeScript/Vue: `<script setup lang="ts">`, Nuxt auto-imports, composables prefixed `use`
- No raw SQL — Supabase SDK only
- No secrets in code — `get_settings()` or `useRuntimeConfig()` only

## Test Strategy

- Backend: pytest with dependency overrides for auth
- Frontend: vitest for components and composables
- E2E: Playwright TypeScript for critical user flows
```

## activeContext.md

Updated by Memory Keeper after each chain. Contains current sprint focus.

```markdown
# Active Context

_Last updated: YYYY-MM-DD_

## Current Focus

{What is currently being worked on}

## Recently Completed

- {Feature 1} — {date}
- {Feature 2} — {date}

## In Progress

- {Item being worked on}

## Known Blockers

- {Blocker description} — {who needs to resolve}
```

## progress.md

Updated by Memory Keeper when features complete or blockers change.

```markdown
# Progress

_Last updated: YYYY-MM-DD_

## Done

- [x] Initial project setup
- [x] Auth0 integration
- [x] Supabase schema
- [x] CV conversion endpoint
- [x] PDF generation service
- [x] Nuxt 3 frontend with Auth0 login
- [x] Admin panel
- [x] Conversion history

## In Progress

- [ ] {Current feature}

## Pending

- [ ] {Future feature}

## Known Issues

- {Issue description} — see BUG-YYYY-MM-DD-NNN in docs/qa-memory/bugs.md
```
```

- [ ] **Step 4: Create `.cursor/agents/memory-keeper/references/auto-update-protocol.md`**

```markdown
# Auto-Update Protocol

This protocol runs automatically after every agent chain completes.

## Input

Memory Keeper receives from Orchestrator:

```yaml
chain_summary:
  chain: <chain-name>
  feature: <feature-name>
  date: YYYY-MM-DD
  artifacts:
    - path: <file-path>
      type: implementation | spec | test | review | migration
  findings:
    bugs: []          # bugs found by code-reviewer
    decisions: []     # decisions made during chain
    tests_written: [] # test files created by tester
    regressions: []   # regressions found
  coverage:
    backend: <N>%
    frontend: <N>%
```

## Step 1: Classify Entries

| If chain_summary contains | Write to |
|---|---|
| `findings.bugs` non-empty | `docs/qa-memory/bugs.md` |
| `findings.decisions` non-empty | `docs/qa-memory/decisions.md` |
| `findings.tests_written` non-empty | `docs/qa-memory/test-log.md` |
| `findings.regressions` non-empty | `docs/qa-memory/regressions.md` |
| Backend artifacts with migrations | `docs/qa-memory/environment.md` (if env vars changed) |

## Step 2: Duplicate Check

Before appending:
1. Read `_index.md`
2. Search for entries with same feature name and same date
3. If duplicate found: skip (do not duplicate entries)

## Step 3: Generate Entry IDs

For each entry:
1. Read current max ID from `_index.md` for the type
2. Increment by 1
3. Format: `{TYPE}-{YYYY}-{MM}-{DD}-{NNN}` (zero-padded to 3 digits)

## Step 4: Append Entries

Append formatted entries (per `memory-schema.md`) to the correct files.
Each entry ends with `---` separator.

## Step 5: Update _index.md

Add rows to the Quick Reference table and update the Keyword Index.
Update the `_Last updated` timestamp.

## Step 6: Update memory-bank/

After every chain:
- `activeContext.md`: Update "Recently Completed" with the feature name and date
- `progress.md`: If the chain completed a feature, move it to the Done list

Only update `techContext.md` and `systemPatterns.md` when significant architectural changes occur (new service added, auth pattern changed, etc.).

## Archive Trigger

If any `docs/qa-memory/*.md` file exceeds 200 entries:
1. Create `docs/qa-memory/_archive/{YYYY-Q{N}}.md` with the oldest 150 entries
2. Remove those entries from the active file
3. Update `_index.md` to note that older entries are in archive
```

- [ ] **Step 5: Commit**

```bash
git add .cursor/agents/memory-keeper/
git commit -m "feat(docs): add memory-keeper agent skill and references"
```

---

## Task 10: Create Memory Templates and memory-bank/

**Files:**
- Create: `.cursor/memory/templates/bugs.md`
- Create: `.cursor/memory/templates/decisions.md`
- Create: `.cursor/memory/templates/test-log.md`
- Create: `.cursor/memory/templates/regressions.md`
- Create: `.cursor/memory/templates/environment.md`
- Create: `memory-bank/projectbrief.md`
- Create: `memory-bank/productContext.md`
- Create: `memory-bank/techContext.md`
- Create: `memory-bank/systemPatterns.md`
- Create: `memory-bank/activeContext.md`
- Create: `memory-bank/progress.md`

- [ ] **Step 1: Create `.cursor/memory/templates/bugs.md`**

```markdown
# Bug Log

_Maintained by Memory Keeper Agent. See .cursor/agents/memory-keeper/references/memory-schema.md for entry format._

<!-- Append new entries below using format: BUG-YYYY-MM-DD-NNN -->
```

- [ ] **Step 2: Create `.cursor/memory/templates/decisions.md`**

```markdown
# Architecture Decision Log

_Maintained by Memory Keeper Agent. See .cursor/agents/memory-keeper/references/memory-schema.md for entry format._

<!-- Append new entries below using format: DEC-YYYY-MM-DD-NNN -->
```

- [ ] **Step 3: Create `.cursor/memory/templates/test-log.md`**

```markdown
# Test Execution Log

_Maintained by Memory Keeper Agent. See .cursor/agents/memory-keeper/references/memory-schema.md for entry format._

<!-- Append new entries below using format: TST-YYYY-MM-DD-NNN -->
```

- [ ] **Step 4: Create `.cursor/memory/templates/regressions.md`**

```markdown
# Regression Log

_Maintained by Memory Keeper Agent. See .cursor/agents/memory-keeper/references/memory-schema.md for entry format._

<!-- Append new entries below using format: REG-YYYY-MM-DD-NNN -->
```

- [ ] **Step 5: Create `.cursor/memory/templates/environment.md`**

```markdown
# Environment Reference

_Maintained by Memory Keeper Agent. Contains env var names and service references. Never contains secret values._

<!-- Add environment sections below -->
```

- [ ] **Step 6: Create `memory-bank/projectbrief.md`**

```markdown
# Project Brief: web-cv-converter

## Overview

**Project:** web-cv-converter
**Type:** Web application — AI-powered CV/resume conversion to PDF
**Status:** Active development
**Repository:** AZANIR/web-cv-converter

## Goal

Convert Markdown CVs to polished PDFs using AI assistance. Users paste their Markdown CV and a job vacancy URL or text, the AI optimizes the CV content for the vacancy, and the result is rendered as a professional PDF for download.

## Core Features

- Markdown CV + vacancy input → AI optimization → PDF output
- Vacancy URL parsing (extracts job requirements)
- Conversion history and management per user
- Multiple professional CV templates
- Admin panel for user and email allowlist management
- Auth-gated: only approved emails can access

## Success Criteria

- End-to-end conversion completes in < 60 seconds
- Generated PDFs are professionally formatted
- Auth-protected: only `allowed_emails` table entries can log in
- System handles concurrent users without rate-limit errors
```

- [ ] **Step 7: Create `memory-bank/productContext.md`**

```markdown
# Product Context

## Why It Exists

Tailoring a CV for each job application is time-consuming. This tool automates the analysis and optimization of CV content against a specific job vacancy using AI, then produces a properly formatted PDF — eliminating the need for manual editing and layout work.

## Target Users

- QA engineers and tech professionals applying for new roles
- Internal users only (access controlled via `allowed_emails` Supabase table)

## Problems Solved

| Problem | Solution |
|---|---|
| Manual CV tailoring for each vacancy | AI analyzes vacancy and rewrites CV sections |
| Formatting inconsistency | Standardized PDF templates with professional layout |
| Context switching (writing + design) | Single tool handles content + output |
| Storing and re-using past CVs | Conversion history per user |

## User Journey

1. Log in via Auth0 (Google or email)
2. Navigate to Convert page
3. Paste Markdown CV and vacancy URL or text
4. Submit — AI processes and optimizes
5. View generated CV result
6. Download as PDF or copy Markdown
7. Access history of past conversions at any time
```

- [ ] **Step 8: Create `memory-bank/techContext.md`**

```markdown
# Technical Context

## Stack

| Layer | Technology | Key Files |
|---|---|---|
| Backend framework | FastAPI (Python 3.11+) | `backend/main.py` |
| Schema validation | Pydantic v2 | All `backend/routers/`, `backend/services/` |
| Auth | Auth0 (RS256 JWT) | `backend/core/auth.py` |
| Database | Supabase (PostgreSQL) | `backend/core/supabase.py`, `backend/supabase/schema.sql` |
| AI provider | Gemini (default) or Anthropic | `backend/services/ai_service.py` |
| PDF generation | WeasyPrint | `backend/services/pdf_service.py` |
| Frontend framework | Nuxt 3 + Vue 3 + TypeScript | `frontend/nuxt.config.ts` |
| UI library | @nuxt/ui (Tailwind) | All frontend components |
| Frontend auth | nuxt-auth-utils (session) | `frontend/middleware/auth.ts` |
| Deployment | Docker Compose | `docker-compose.yml` |
| Reverse proxy | Caddy | `Caddyfile.example` |
| Hosting | Hetzner VPS | `docs/DEPLOY_HETZNER.md` |

## Backend Routers

| Router | Prefix | Purpose |
|---|---|---|
| `routers/me.py` | `/api/me` | User profile |
| `routers/convert.py` | `/api/convert` | CV conversion |
| `routers/generate.py` | `/api/generate` | CV generation |
| `routers/history.py` | `/api/history` | Conversion history |
| `routers/admin.py` | `/api/admin` | Admin panel |
| `routers/prompts.py` | `/api/prompts` | Prompt management |

## Backend Services

| Service | Purpose |
|---|---|
| `ai_service.py` | AI provider abstraction (Gemini/Anthropic) |
| `conversion_runner.py` | Orchestrates conversion flow |
| `generation_runner.py` | Orchestrates generation flow |
| `pdf_service.py` | Renders HTML to PDF |
| `prompt_service.py` | Loads and manages prompts |
| `rate_limit.py` | Rate limiting for AI endpoints |
| `storage_service.py` | File storage operations |
| `vacancy_parser.py` | Parses job vacancy from URL or text |
| `embedding_service.py` | Vector embeddings for similarity |
| `case_study_loader.py` | Loads case study templates |

## Environment Variables

| Variable | Layer | Purpose |
|---|---|---|
| `AUTH0_DOMAIN` | Backend | Auth0 tenant domain |
| `AUTH0_API_AUDIENCE` | Backend | API identifier |
| `AUTH0_CLIENT_ID` | Backend | SPA client ID (optional) |
| `ADMIN_EMAILS` | Backend | Comma-separated admin emails |
| `SUPABASE_URL` | Backend | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend | DB service role key |
| `AI_PROVIDER` | Backend | `gemini` or `anthropic` |
| `GEMINI_API_KEY` | Backend | Gemini API key |
| `ANTHROPIC_API_KEY` | Backend | Anthropic API key (if used) |
| `ALLOWED_ORIGINS` | Backend | CORS allowed origins |
| `NUXT_PUBLIC_API_URL` | Frontend | Backend API base URL |
| `NUXT_SESSION_PASSWORD` | Frontend | Session cookie encryption |
| `NUXT_API_BASE_SERVER` | Frontend | Internal backend URL (Docker) |
| `NUXT_OAUTH_AUTH0_DOMAIN` | Frontend | Auth0 domain |
| `NUXT_OAUTH_AUTH0_CLIENT_ID` | Frontend | Auth0 SPA client ID |
| `NUXT_OAUTH_AUTH0_CLIENT_SECRET` | Frontend | Auth0 client secret |
| `NUXT_OAUTH_AUTH0_AUDIENCE` | Frontend | Auth0 API audience |
```

- [ ] **Step 9: Create `memory-bank/systemPatterns.md`**

```markdown
# System Patterns

## Architecture Overview

Single FastAPI service + Nuxt 3 SSR frontend. Frontend server routes proxy authenticated requests to the FastAPI backend. No direct browser-to-backend calls (CORS restricted).

```
Browser → Nuxt 3 SSR (frontend/server/api/) → FastAPI backend → Supabase
                              ↕
                        Auth0 (JWT validation)
```

## Auth Pattern

```
1. User logs in via Auth0 OAuth2 (nuxt-auth-utils)
2. Session stored server-side (nuxt-auth-utils)
3. Frontend server route attaches Bearer token from session
4. FastAPI validates RS256 JWT → checks allowed_emails → upserts profile
5. get_current_user() dependency returns {"user_id": str, "email": str}
```

## API Call Pattern (Frontend → Backend)

```
Component → useApi(path, options) composable
          → frontend/server/api/[...path].ts (server proxy)
          → FastAPI endpoint with Authorization header
          → returns data to component
```

## Data Access Pattern (Backend)

```
Router handler (routers/) → Service method (services/)
                           → Supabase SDK (core/supabase.py)
                           → Returns typed Pydantic model
```

## Migration Pattern

All database changes are append-only SQL blocks in `backend/supabase/schema.sql`.
Format:
```sql
-- YYYY-MM-DD: Description of change
CREATE TABLE IF NOT EXISTS ...
ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...
```

Never drop, truncate, or alter existing column types.

## Key Conventions

| Convention | Rule |
|---|---|
| Route auth | Every protected route: `Depends(get_current_user)` |
| Admin routes | `Depends(require_admin)` |
| DB access | `get_supabase()` SDK only, no raw SQL |
| Config | `get_settings()` for all env vars |
| Vue components | `<script setup lang="ts">` always |
| API calls | `useApi.ts` composable always |
| Composables | `use` prefix always |
```

- [ ] **Step 10: Create `memory-bank/activeContext.md`**

```markdown
# Active Context

_Last updated: 2026-04-08_

## Current Focus

Setting up the `.cursor/` multi-agent system (Orchestrator, Document, Frontend, Backend, Code Reviewer, Tester, Memory Keeper).

## Recently Completed

- Auth0 login flow with middleware enhancements (feat/fix-logout-user)
- MD template creation and content quality rules for CV conversion
- Testing infrastructure setup (pytest + vitest)
- Initial project structure and Docker deployment

## In Progress

- `.cursor/` multi-agent system scaffolding

## Known Blockers

None currently.
```

- [ ] **Step 11: Create `memory-bank/progress.md`**

```markdown
# Progress

_Last updated: 2026-04-08_

## Done

- [x] Initial project setup and Docker compose
- [x] FastAPI backend structure (routers, services, core)
- [x] Supabase schema with RLS
- [x] Auth0 integration (JWT RS256, allowed_emails, profiles)
- [x] CV conversion endpoint (`/api/convert`)
- [x] CV generation endpoint (`/api/generate`)
- [x] PDF generation service (WeasyPrint)
- [x] Vacancy URL parser
- [x] Nuxt 3 frontend with Auth0 login
- [x] Conversion history page
- [x] Admin panel
- [x] Case study templates for QA
- [x] Backend tests (pytest infrastructure)
- [x] Frontend tests (vitest infrastructure)
- [x] Hetzner deployment setup (Caddy + Docker)
- [x] .cursor/ multi-agent system scaffold

## In Progress

- [ ] Expanding test coverage to ≥ 80% backend / ≥ 70% frontend

## Pending

- [ ] E2E Playwright tests for critical flows (login, convert, generate)
- [ ] CI/CD pipeline test integration
- [ ] Performance optimization for AI endpoints

## Known Issues

None currently. See `docs/qa-memory/bugs.md` after first init.
```

- [ ] **Step 12: Verify all files**

```bash
ls .cursor/memory/templates/ && ls memory-bank/
```
Expected:
```
bugs.md  decisions.md  environment.md  regressions.md  test-log.md
activeContext.md  productContext.md  progress.md  projectbrief.md  systemPatterns.md  techContext.md
```

- [ ] **Step 13: Commit**

```bash
git add .cursor/memory/ memory-bank/
git commit -m "feat(docs): add memory templates and initialize memory-bank"
```

---

## Task 11: Final Verification

- [ ] **Step 1: Verify complete directory tree**

```bash
find .cursor -type f | sort
```

Expected output (43 files):
```
.cursor/agents/backend/SKILL.md
.cursor/agents/backend/references/auth0-config.md
.cursor/agents/backend/references/fastapi-patterns.md
.cursor/agents/backend/references/security-self-review.md
.cursor/agents/backend/references/supabase-schema.md
.cursor/agents/code-reviewer/SKILL.md
.cursor/agents/code-reviewer/references/review-checklist.md
.cursor/agents/code-reviewer/references/severity-matrix.md
.cursor/agents/code-reviewer/references/style-guide.md
.cursor/agents/document/SKILL.md
.cursor/agents/document/references/doc-templates.md
.cursor/agents/document/references/output-formats.md
.cursor/agents/frontend/SKILL.md
.cursor/agents/frontend/references/component-checklist.md
.cursor/agents/frontend/references/design-system.md
.cursor/agents/frontend/references/nuxt-patterns.md
.cursor/agents/memory-keeper/SKILL.md
.cursor/agents/memory-keeper/references/auto-update-protocol.md
.cursor/agents/memory-keeper/references/memory-bank-schema.md
.cursor/agents/memory-keeper/references/memory-schema.md
.cursor/agents/orchestrator/SKILL.md
.cursor/agents/orchestrator/references/chains.md
.cursor/agents/orchestrator/references/conflict-rules.md
.cursor/agents/orchestrator/references/task-taxonomy.md
.cursor/agents/tester/SKILL.md
.cursor/agents/tester/references/coverage-targets.md
.cursor/agents/tester/references/playwright-ts-patterns.md
.cursor/agents/tester/references/pytest-patterns.md
.cursor/agents/tester/references/vitest-patterns.md
.cursor/memory/templates/bugs.md
.cursor/memory/templates/decisions.md
.cursor/memory/templates/environment.md
.cursor/memory/templates/regressions.md
.cursor/memory/templates/test-log.md
.cursor/rules/git-workflow.mdc
.cursor/rules/orchestration.mdc
.cursor/rules/project-structure.mdc
.cursor/rules/project.mdc
.cursor/rules/security.mdc
```

- [ ] **Step 2: Verify memory-bank**

```bash
ls memory-bank/
```
Expected: `activeContext.md  productContext.md  progress.md  projectbrief.md  systemPatterns.md  techContext.md`

- [ ] **Step 3: Spot-check a rule file is valid MDC (has YAML frontmatter)**

```bash
head -5 .cursor/rules/orchestration.mdc
```
Expected:
```
---
description: Multi-agent routing, task chains, handoff protocol, and conflict rules
alwaysApply: true
---
```

- [ ] **Step 4: Final commit**

```bash
git add .cursor/ memory-bank/
git commit -m "feat(docs): complete .cursor/ multi-agent system scaffold

7 agents (orchestrator, document, frontend, backend, code-reviewer,
tester, memory-keeper), 5 always-apply rules, memory templates, and
memory-bank context files for web-cv-converter.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Self-Review Notes

**Spec coverage check:**
- ✅ Section 2 (Directory Structure) — covered by Tasks 1-10
- ✅ Section 3 (Agent Roles) — covered in each agent's SKILL.md
- ✅ Section 4 (Orchestration Logic) — covered in orchestration.mdc + orchestrator references
- ✅ Section 5 (Memory Schema) — covered in memory-keeper references + templates
- ✅ Section 6 (Skill Authoring Standard) — all SKILL.md files follow YAML frontmatter + L1/L2/L3 progressive loading
- ✅ Section 7 (Implementation Notes) — alwaysApply fields set correctly, agent SKILL.md files documented as on-demand

**No placeholders found.** All file contents are complete and production-ready.

**Type consistency:** Handoff object schema used consistently across orchestration.mdc and chains.md. Entry ID format consistent across memory-schema.md and auto-update-protocol.md.
