# memory-bank/ Schema

Files in `memory-bank/` describe WHAT THE PROJECT IS (static context).
Files in `docs/qa-memory/` describe WHAT QA HAS DONE (activity log).

Memory Keeper updates `memory-bank/` when significant changes occur — not after every chain.

## Files and Update Triggers

| File | Purpose | Update when |
|---|---|---|
| `projectbrief.md` | Goals, scope, success criteria | Project scope changes |
| `productContext.md` | Why it exists, users, problems | Product direction changes |
| `techContext.md` | Full stack, env vars, services | New service or tech added |
| `systemPatterns.md` | Architecture, coding conventions | Pattern or architecture changes |
| `activeContext.md` | Current sprint focus, in-progress work | After every chain |
| `progress.md` | Done, pending, known blockers | When features complete or blockers change |

## activeContext.md Template

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

## progress.md Template

```markdown
# Progress

_Last updated: YYYY-MM-DD_

## Done

- [x] {Completed feature}

## In Progress

- [ ] {Current feature}

## Pending

- [ ] {Future feature}

## Known Issues

- {Issue description} — see BUG-YYYY-MM-DD-NNN in docs/qa-memory/bugs.md
```
