# System Patterns

## Architecture Overview

Single FastAPI service + Nuxt 3 SSR frontend. Frontend server routes proxy authenticated requests to the FastAPI backend. No direct browser-to-backend calls (CORS restricted).

```
Browser → Nuxt 3 SSR (frontend/server/api/) → FastAPI backend → Supabase
                              |
                        Auth0 (JWT validation)
```

## Auth Pattern

```
1. User logs in via Auth0 OAuth2 (nuxt-auth-utils)
2. Session stored server-side (nuxt-auth-utils)
3. Frontend server route attaches Bearer token from session
4. FastAPI validates RS256 JWT → checks allowed_emails → upserts profile
5. get_current_user() dependency returns {"user_id": str, "email": str}
```

## API Call Pattern (Frontend → Backend)

```
Component → useApi(path, options) composable
          → frontend/server/api/[...path].ts (server proxy)
          → FastAPI endpoint with Authorization header
          → returns data to component
```

## Data Access Pattern (Backend)

```
Router handler (routers/) → Service method (services/)
                           → Supabase SDK (core/supabase.py)
                           → Returns typed Pydantic model
```

## Migration Pattern

All database changes are append-only SQL blocks in `backend/supabase/schema.sql`.

```sql
-- YYYY-MM-DD: Description of change
CREATE TABLE IF NOT EXISTS ...
ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...
```

Never drop, truncate, or alter existing column types.

## Key Conventions

| Convention | Rule |
|---|---|
| Route auth | Every protected route: `Depends(get_current_user)` |
| Admin routes | `Depends(require_admin)` |
| DB access | `get_supabase()` SDK only, no raw SQL |
| Config | `get_settings()` for all env vars |
| Vue components | `<script setup lang="ts">` always |
| API calls | `useApi.ts` composable always |
| Composables | `use` prefix always |
