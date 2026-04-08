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
