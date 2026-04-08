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
