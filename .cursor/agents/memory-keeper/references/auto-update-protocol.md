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
    bugs: []
    decisions: []
    tests_written: []
    regressions: []
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

Only update `techContext.md` and `systemPatterns.md` when significant architectural changes occur.

## Archive Trigger

If any `docs/qa-memory/*.md` file exceeds 200 entries:
1. Create `docs/qa-memory/_archive/{YYYY-Q{N}}.md` with the oldest 150 entries
2. Remove those entries from the active file
3. Update `_index.md` to note that older entries are in archive
