# Conflict Resolution Rules

## The Single Rule

**Task type decides ownership. No negotiation, no overlap.**

| If the task is... | Owner is... | Example |
|---|---|---|
| Writing new code | Domain agent (backend/frontend/tester/document) | "add validation to this endpoint" → backend |
| Reviewing existing code | code-reviewer | "review the validation in this endpoint" → code-reviewer |
| Security testing | pentester | "pentest this endpoint", "test for SSRF" → pentester |
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

**"Review and pentest this endpoint"**
→ code-reviewer reviews code quality → pentester tests for active vulnerabilities

**"Fix this security issue"**
→ backend or frontend fixes → pentester re-tests → code-reviewer reviews fix

## Hard Rules

1. Two agents NEVER edit the same file in the same chain step.
2. code-reviewer NEVER writes implementation code — only reports findings.
3. memory-keeper NEVER modifies implementation, test, or documentation files.
4. backend agent NEVER writes frontend files and vice versa.
5. pentester NEVER writes implementation code — only reports findings.
6. pentester and code-reviewer may both run in the same chain but on different steps (pentester tests first, code-reviewer validates).
