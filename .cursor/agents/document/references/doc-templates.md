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
