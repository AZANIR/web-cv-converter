# Case Study: Full-Cycle QA for Multi-Tenant Marketplace SaaS Platform (NDA)

## Overview
- **Client type:** SaaS product startup
- **Industry:** E-commerce / Marketplace Technology
- **Service provided:** External QA Team — manual testing, API automation, load testing, integration testing, NFR validation
- **Tags:** Playwright, Postman, Portman, Azure DevOps, GitHub Actions, Manual Testing, API Testing, Contract Testing, Load Testing, Security Testing, RLS, Stripe, Multi-tenant, Marketplace, Jira, Confluence

---

## The Challenge
A multi-tenant SaaS marketplace platform (Amazon-model architecture) needed a structured external QA team ahead of its MVP launch. The platform supports multiple stores, vendor roles, Stripe payments, shipping integrations, and a unique "Try-Me" physical booking system — all with strict data isolation between tenants.

Key pain points:
- No dedicated external QA process — development was moving fast with insufficient test coverage
- Multi-tenant architecture required strict Row-Level Security (RLS) validation to prevent cross-tenant data leakage
- Complex role hierarchy (Operator / Vendor / Customer) with no systematic permission boundary testing
- Stripe payment flows, refunds, and edge function resilience untested at depth
- No load or performance testing ahead of launch — scalability risk unquantified
- Third-party integrations (Stripe Connect, Carriyo shipping) had no contract or integration test coverage
- Risk areas across negative flows: missing cancel/refund options, validation gaps, state persistence bugs

---

## What I Did
- Acted as **external QA team lead**, defining and executing the full QA strategy across manual, API, load, and NFR testing tracks
- Delivered comprehensive **manual testing focused on negative flows and functional gaps** — store onboarding wizard, settings, vendor management, catalog, order/return/refund/exchange workflows, and role-based access
- Authored a detailed **test plan and edge case documentation** covering: Stripe payment intents, refund processing, idempotency guards (duplicate refund/launch prevention), session management, shipping integration (Carriyo), Try-Me booking flows, and inventory reservation logic
- Built **API automation using Postman and Portman** for OpenAPI/Swagger contract validation — ensuring API responses match defined contracts across all critical endpoints
- Designed **multi-tenant security tests** validating RLS enforcement across all sensitive tables (orders, returns, payouts, vendor profiles) — confirming zero cross-tenant data exposure
- Defined **NFR test strategy** covering performance targets (p95 < 500ms for edge functions, p95 < 3s storefront page load), load/stress/spike/endurance scenarios, OWASP security coverage, WCAG accessibility baseline, cross-browser/device compatibility, and disaster recovery
- Integrated test reporting into **Azure DevOps and GitHub Actions** CI/CD pipelines with results surfaced in Slack/Google Chat and tracked in Jira/Confluence
- Reported first **26 bugs in the initial 10-day testing window**, identifying key risk categories: permission boundary inconsistencies, navigation/redirect failures post-submission, validation gaps, state persistence issues, and edge-case slug handling

---

## Results
- **26 bugs logged in first 10 days** of engagement — spanning store creation, settings, vendors, and catalog flows
- Key risk areas surfaced pre-launch: permission enforcement gaps, generic error handling, and state persistence inconsistencies that would have caused production incidents
- **Full test plan and edge case documentation** delivered and maintained, giving the dev team a clear, actionable quality gate before each release
- **API contract testing** with Portman established as a regression gate — catching breaking API changes before they reach staging
- **Multi-tenant RLS security coverage** confirmed data isolation between store instances — critical for a marketplace model
- NFR performance baselines and load test scenarios defined, ready for execution ahead of MVP go-live

---

## What Made the Difference
Prioritising negative flows and permission boundaries from day one — not just happy-path coverage — surfaced the bugs that matter most for a marketplace: cases where one tenant could see another's data, or where a missing validation could corrupt an order state. Combined with API contract testing, the team gained confidence that both the UI and backend behave consistently under the same rules.

---

## Relevant for Jobs With:
- Multi-tenant SaaS or marketplace platform QA
- External QA team or Lead QA roles
- Playwright automation (E2E and API)
- API contract testing (Postman, Portman, OpenAPI/Swagger)
- Stripe payment and refund flow testing
- RLS / database security and role-based access testing
- Load and performance testing for pre-launch readiness
- Azure DevOps and GitHub Actions CI/CD integration
- E-commerce platforms (orders, returns, inventory, shipping)
- OWASP security testing and WCAG accessibility validation
