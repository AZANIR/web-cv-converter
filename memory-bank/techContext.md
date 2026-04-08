# Technical Context

## Stack

| Layer | Technology | Key Files |
|---|---|---|
| Backend framework | FastAPI (Python 3.11+) | `backend/main.py` |
| Schema validation | Pydantic v2 | All `backend/routers/`, `backend/services/` |
| Auth | Auth0 (RS256 JWT) | `backend/core/auth.py` |
| Database | Supabase (PostgreSQL) | `backend/core/supabase.py`, `backend/supabase/schema.sql` |
| AI provider | Gemini (default) or Anthropic | `backend/services/ai_service.py` |
| PDF generation | WeasyPrint | `backend/services/pdf_service.py` |
| Frontend framework | Nuxt 3 + Vue 3 + TypeScript | `frontend/nuxt.config.ts` |
| UI library | @nuxt/ui (Tailwind) | All frontend components |
| Frontend auth | nuxt-auth-utils (session) | `frontend/middleware/auth.ts` |
| Deployment | Docker Compose | `docker-compose.yml` |
| Reverse proxy | Caddy | `Caddyfile.example` |
| Hosting | Hetzner VPS | `docs/DEPLOY_HETZNER.md` |

## Backend Routers

| Router | Prefix | Purpose |
|---|---|---|
| `routers/me.py` | `/api/me` | User profile |
| `routers/convert.py` | `/api/convert` | CV conversion |
| `routers/generate.py` | `/api/generate` | CV generation |
| `routers/history.py` | `/api/history` | Conversion history |
| `routers/admin.py` | `/api/admin` | Admin panel |
| `routers/prompts.py` | `/api/prompts` | Prompt management |

## Backend Services

| Service | Purpose |
|---|---|
| `ai_service.py` | AI provider abstraction (Gemini/Anthropic) |
| `conversion_runner.py` | Orchestrates conversion flow |
| `generation_runner.py` | Orchestrates generation flow |
| `pdf_service.py` | Renders HTML to PDF |
| `prompt_service.py` | Loads and manages prompts |
| `rate_limit.py` | Rate limiting for AI endpoints |
| `storage_service.py` | File storage operations |
| `vacancy_parser.py` | Parses job vacancy from URL or text |
| `embedding_service.py` | Vector embeddings for similarity |
| `case_study_loader.py` | Loads case study templates |

## Environment Variables

| Variable | Layer | Purpose |
|---|---|---|
| `AUTH0_DOMAIN` | Backend | Auth0 tenant domain |
| `AUTH0_API_AUDIENCE` | Backend | API identifier |
| `AUTH0_CLIENT_ID` | Backend | SPA client ID (optional) |
| `ADMIN_EMAILS` | Backend | Comma-separated admin emails |
| `SUPABASE_URL` | Backend | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend | DB service role key |
| `AI_PROVIDER` | Backend | `gemini` or `anthropic` |
| `GEMINI_API_KEY` | Backend | Gemini API key |
| `ANTHROPIC_API_KEY` | Backend | Anthropic API key (if used) |
| `ALLOWED_ORIGINS` | Backend | CORS allowed origins |
| `NUXT_PUBLIC_API_URL` | Frontend | Backend API base URL |
| `NUXT_SESSION_PASSWORD` | Frontend | Session cookie encryption |
| `NUXT_API_BASE_SERVER` | Frontend | Internal backend URL (Docker) |
| `NUXT_OAUTH_AUTH0_DOMAIN` | Frontend | Auth0 domain |
| `NUXT_OAUTH_AUTH0_CLIENT_ID` | Frontend | Auth0 SPA client ID |
| `NUXT_OAUTH_AUTH0_CLIENT_SECRET` | Frontend | Auth0 client secret |
| `NUXT_OAUTH_AUTH0_AUDIENCE` | Frontend | Auth0 API audience |
