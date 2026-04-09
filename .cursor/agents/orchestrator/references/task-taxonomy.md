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
