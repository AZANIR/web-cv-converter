# Progress

_Last updated: 2026-04-08_

## Done

- [x] Initial project setup and Docker compose
- [x] FastAPI backend structure (routers, services, core)
- [x] Supabase schema with RLS
- [x] Auth0 integration (JWT RS256, allowed_emails, profiles)
- [x] CV conversion endpoint (`/api/convert`)
- [x] CV generation endpoint (`/api/generate`)
- [x] PDF generation service (WeasyPrint)
- [x] Vacancy URL parser
- [x] Nuxt 3 frontend with Auth0 login
- [x] Conversion history page
- [x] Admin panel
- [x] Case study templates for QA
- [x] Backend tests (pytest infrastructure)
- [x] Frontend tests (vitest infrastructure)
- [x] Hetzner deployment setup (Caddy + Docker)
- [x] `.cursor/` multi-agent system scaffold

## In Progress

- [ ] Expanding test coverage to >= 80% backend / >= 70% frontend

## Pending

- [ ] E2E Playwright tests for critical flows (login, convert, generate)
- [ ] CI/CD pipeline test integration
- [ ] Performance optimization for AI endpoints

## Known Issues

None currently. See `docs/qa-memory/bugs.md` after first `@memory-keeper init`.
