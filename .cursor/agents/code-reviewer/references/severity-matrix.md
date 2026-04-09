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
| Missing ARIA label | `<button><icon /></button>` with no label | Add `aria-label` |
| Console.log in production | `console.log(userData)` | Remove or replace with logger |
