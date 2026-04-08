# Design Spec: Cursor Multi-Agent System for web-cv-converter

**Date:** 2026-04-08  
**Status:** Approved  
**Author:** AZANIR + Claude Code  
**Scope:** `.cursor/` directory scaffolding — project-specific for web-cv-converter

---

## 1. Context

**Project:** web-cv-converter — FastAPI backend, Nuxt 3 frontend, Supabase DB, Auth0 auth, Docker + Hetzner deployment.

**Goal:** Design and scaffold a complete multi-agent system inside `.cursor/` that coordinates 7 specialized agents through an orchestrator, using skills extracted from [AZANIR/qa-skills](https://github.com/AZANIR/qa-skills) and authored for this project's specific stack.

**Source of truth for skill patterns:** AZANIR/qa-skills — 57 agent skills following progressive-loading (SKILL.md + references/), `.cursor/rules/` for project conventions, `qa-project-memory` for memory schema.

---

## 2. Directory Structure

```
.cursor/
├── rules/
│   ├── project.mdc              ← stack conventions (alwaysApply: true)
│   ├── git-workflow.mdc         ← branch naming + Conventional Commits
│   ├── project-structure.mdc   ← artifact routing table per agent
│   ├── security.mdc            ← OWASP guardrails, secrets policy
│   └── orchestration.mdc       ← inter-agent routing, chains, conflict rules
│
├── agents/
│   ├── orchestrator/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── chains.md
│   │       ├── conflict-rules.md
│   │       └── task-taxonomy.md
│   │
│   ├── document/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── doc-templates.md
│   │       └── output-formats.md
│   │
│   ├── frontend/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── nuxt-patterns.md
│   │       ├── design-system.md
│   │       └── component-checklist.md
│   │
│   ├── backend/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── fastapi-patterns.md
│   │       ├── supabase-schema.md
│   │       ├── auth0-config.md
│   │       └── security-self-review.md
│   │
│   ├── code-reviewer/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── severity-matrix.md
│   │       ├── review-checklist.md
│   │       └── style-guide.md
│   │
│   ├── tester/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── pytest-patterns.md
│   │       ├── playwright-ts-patterns.md
│   │       ├── vitest-patterns.md
│   │       └── coverage-targets.md
│   │
│   └── memory-keeper/
│       ├── SKILL.md
│       └── references/
│           ├── memory-schema.md
│           ├── memory-bank-schema.md
│           └── auto-update-protocol.md
│
└── memory/
    └── templates/
        ├── bugs.md
        ├── decisions.md
        ├── test-log.md
        ├── regressions.md
        └── environment.md
```

---

## 3. Agent Roles & Responsibilities

### Orchestrator
- **Role:** Router and chain coordinator. Receives every task, classifies it, delegates to the correct agent, monitors handoff objects for blocking issues.
- **Inputs:** Natural language requests or explicit `@orchestrator chain:<name>` commands.
- **Outputs:** Delegation instructions + chain execution log.
- **Never produces:** Implementation artifacts, test files, or documentation.

### Document Agent
- **Role:** Owns all written project knowledge.
- **Produces:** OpenAPI YAML contracts, feature specs, ADRs, deployment docs, README updates.
- **Output path:** `docs/`
- **Triggers:** Requirement changes, new features, ADR decisions from any agent.

### Frontend Agent
- **Role:** Owns the Nuxt 3 UI layer.
- **Produces:** Pages, components, composables, layouts, middleware.
- **Enforces:** Design system (spacing, component reuse, WCAG 2.2 color contrast + keyboard navigation).
- **Does not own:** E2E tests (Tester Agent), backend API contracts.
- **Output paths:** `frontend/pages/`, `frontend/components/`, `frontend/composables/`, `frontend/layouts/`

### Backend Agent
- **Role:** Owns the full FastAPI stack.
- **Produces:** Routes, services, Pydantic schemas, Supabase migrations, Auth0 configuration.
- **Self-review:** Runs `security-self-review.md` checklist (OWASP Top 10 for FastAPI) before every handoff.
- **Output paths:** `backend/routers/`, `backend/services/`, `backend/core/`, `backend/supabase/`

### Code Reviewer Agent
- **Role:** Tiered quality gate. Activated after every "write" task.
- **Critical (blocking):** Security vulnerabilities, broken imports, missing auth guards, test coverage below threshold.
- **Advisory:** Naming conventions, docstring gaps, component size, unused imports.
- **Produces:** Structured review report with severity-tagged findings.
- **Orchestrator behavior:** Halts chain on any critical finding until resolved.

### Tester Agent
- **Role:** Owns all test types for this project.
- **Frameworks:** `pytest` (backend unit/integration), `vitest` (frontend unit), `playwright-ts` (E2E).
- **Coverage targets:** 80% backend, 70% frontend.
- **Output paths:** `backend/tests/`, `frontend/tests/`, `tests/e2e/`
- **Produces:** Test files + coverage reports.

### Memory Keeper Agent
- **Role:** Final step in every chain. Logs activity, maintains cross-session context.
- **Writes to:** `docs/qa-memory/` (activity log) + `memory-bank/` (project context).
- **Never modifies:** Implementation files, test files, or documentation content.

---

## 4. Orchestration Logic

### Task Classification Table

| Task Type | Owner | Example Natural Language |
|---|---|---|
| `write:frontend` | Frontend Agent | "add a login page", "fix the CV upload component" |
| `write:backend` | Backend Agent | "add an endpoint", "update the Supabase schema" |
| `write:docs` | Document Agent | "update the API contract", "write an ADR" |
| `write:tests` | Tester Agent | "write tests for the converter service" |
| `review` | Code Reviewer | "review my changes", "audit this file" |
| `chain:*` | Orchestrator routes | explicit chain commands |
| `memory:*` | Memory Keeper | "what bugs do we know", "init qa memory" |

### Predefined Chains

| Chain | Command | Agent Flow |
|---|---|---|
| **feature** | `@orchestrator chain:feature` | Document → Backend → Frontend (sequential, different file trees) → Code Reviewer → Tester → Memory Keeper |
| **api-feature** | `@orchestrator chain:api-feature` | Document → Backend → Code Reviewer → Tester (API) → Memory Keeper |
| **ui-feature** | `@orchestrator chain:ui-feature` | Document → Frontend → Code Reviewer → Tester (E2E) → Memory Keeper |
| **review-only** | `@orchestrator chain:review` | Code Reviewer → Memory Keeper |
| **stabilize** | `@orchestrator chain:stabilize` | Tester (flaky detection) → Code Reviewer → Memory Keeper |

### Handoff Object Schema

```yaml
handoff:
  from: <agent-name>
  to: <agent-name>
  artifacts:
    - path: <file-path>
      type: implementation | spec | test | report
  context:
    feature: <feature-name>
    chain: <chain-name>
    blocking_issues: []   # non-empty = Orchestrator halts chain
```

### Conflict Resolution Rule

**Single rule:** Task type decides ownership.
- "write" tasks → domain agent (Backend/Frontend/Document/Tester)
- "review/audit" tasks → Code Reviewer
- Two agents never run in parallel on the same file

---

## 5. Memory Schema

### Layer 1: `memory-bank/` (project context, rarely changes)

| File | Purpose |
|---|---|
| `projectbrief.md` | Goals, scope, success criteria |
| `productContext.md` | Why it exists, users, problems solved |
| `techContext.md` | Full stack: FastAPI, Nuxt 3, Supabase, Auth0, Docker, Hetzner |
| `systemPatterns.md` | Architectural decisions, coding conventions |
| `activeContext.md` | Current sprint focus, in-progress work |
| `progress.md` | Done, pending, known blockers |

### Layer 2: `docs/qa-memory/` (QA activity log, append-only)

| File | Updated by | Content |
|---|---|---|
| `bugs.md` | Code Reviewer, Tester | Active bugs + resolution status |
| `decisions.md` | All agents | ADR-format: context, decision, consequences |
| `test-log.md` | Tester | Tests written, results, coverage per run |
| `regressions.md` | Tester, Code Reviewer | Regression patterns + root causes |
| `environment.md` | Backend Agent | Env var names, Supabase URLs, Auth0 tenant (no values) |
| `_index.md` | Memory Keeper | Cross-reference by entry ID + keyword |
| `_archive/` | Memory Keeper | Entries rotated when file exceeds 200 entries |

### Entry ID Format

```
BUG-YYYY-MM-DD-NNN   ← bugs.md
DEC-YYYY-MM-DD-NNN   ← decisions.md
TST-YYYY-MM-DD-NNN   ← test-log.md
REG-YYYY-MM-DD-NNN   ← regressions.md
```

---

## 6. Skill File Authoring Standard

All agent `SKILL.md` files follow the qa-skills progressive-loading pattern:

- **L1 (SKILL.md):** Trigger phrases, scope summary, can/cannot/will-not-do
- **L2 (SKILL.md continued):** Workflow steps, decision logic, quality checklist
- **L3 (references/*.md):** Detailed patterns, examples, framework-specific content

SKILL.md must stay under 500 lines. Overflow goes to `references/`.

YAML frontmatter required on every SKILL.md:
```yaml
---
name: <agent-name>
description: One-line purpose for agent discovery
---
```

---

## 7. Implementation Notes

- All `.mdc` rule files in `.cursor/rules/` use YAML frontmatter with `description`, `globs`, and `alwaysApply` fields per Cursor MDC format.
- `project.mdc` and `git-workflow.mdc` use `alwaysApply: true` — loaded in every session.
- `orchestration.mdc` uses `alwaysApply: true` — the routing brain must always be active.
- Agent `SKILL.md` files are invoked on demand via `@agent-name` in Cursor — not always-apply.
- The `memory/templates/` files are blank starters; Memory Keeper copies them to `docs/qa-memory/` on first `init` command.
- `memory-bank/` already exists at project root — Memory Keeper will populate/update it, not recreate it.
