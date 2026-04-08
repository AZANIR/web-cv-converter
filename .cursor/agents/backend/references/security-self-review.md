# Security Self-Review Checklist

Run this checklist before returning a backend handoff object. All items must pass. Add failing items to `blocking_issues` in the handoff object.

## Authentication & Authorization

- [ ] Every non-public endpoint has `Depends(get_current_user)` or `Depends(require_admin)`
- [ ] No endpoint checks `user_id` inline without using the dependency
- [ ] Admin endpoints use `Depends(require_admin)`, not manual role checks
- [ ] No JWT tokens logged or returned in error messages

## Input Validation

- [ ] All request bodies are Pydantic v2 models — no raw `dict` or `Any`
- [ ] File uploads validate MIME type before processing
- [ ] Numeric fields have min/max constraints where appropriate (e.g., `Field(ge=1, le=100)`)
- [ ] URL fields validated with `AnyHttpUrl` type where used

## Database / Supabase

- [ ] All DB queries use Supabase SDK parameterized calls — no f-string SQL
- [ ] New tables have RLS enabled per `supabase-schema.md` template
- [ ] Data returned to the user belongs to them (`.eq("user_id", user["user_id"])` or equivalent)
- [ ] Supabase service role key not exposed outside `core/supabase.py`

## Secrets & Configuration

- [ ] No hardcoded secrets, API keys, or connection strings in any file
- [ ] All secrets read via `get_settings()` attributes
- [ ] No secrets logged at any log level

## Error Handling

- [ ] No stack traces or internal details in HTTP error responses
- [ ] 404 responses do not reveal whether a resource exists (for non-owner requests)
- [ ] 500 errors logged before returning generic message

## CORS

- [ ] `allowed_origins` read from `get_settings()` — not hardcoded in `main.py`
- [ ] No wildcard `*` CORS origin in production config

## Rate Limiting

- [ ] AI-heavy endpoints (convert, generate) use `rate_limit.py` service
- [ ] Rate limit errors return 429 with `Retry-After` header where applicable
