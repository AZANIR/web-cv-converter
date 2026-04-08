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
