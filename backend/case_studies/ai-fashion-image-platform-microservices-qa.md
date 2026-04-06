# Case Study: Backend QA & Infrastructure Validation During Microservice Migration for AI Fashion Image Platform (NDA)

## Overview
- **Client type:** AI SaaS startup
- **Industry:** Fashion Technology / AI Image Generation (Sweden)
- **Service provided:** QA Automation Engineer — API automation, load testing, infrastructure validation, microservice integration testing
- **Tags:** TypeScript, Postman, Newman, Playwright, k6, GitLab CI/CD, API Testing, Load Testing, Microservices, FAL API, ComfyUI, RunPod, Google Vertex AI, Qase, Jira, AI Platform QA, Backend Testing

---

## The Challenge
A Swedish AI startup building a fashion image generation platform was undergoing a major backend migration — moving from Supabase to AWS microservices and replacing their RunPod/ComfyUI GPU infrastructure with Google Vertex AI. The platform generates AI product images at scale (face swaps, clothing replacement, prompt-based generation), and the team needed strong backend-focused QA to validate stability, API correctness, and infrastructure readiness before enterprise client rollout.

Key pain points:
- No dedicated QA process for microservices — the platform was being rebuilt from scratch with no test coverage
- AI generation pipelines (FAL API, RunPod, Vertex AI) needed validation without triggering excessive billed API calls
- No comparison data between old (RunPod) and new (Google Vertex AI) infrastructure — scalability unknowns
- Critical backend logic untested: job lifecycle, queue behavior, wallet/billing flows, status transitions
- 8 API contract violations discovered early — including a double-charge risk due to missing idempotency, and incorrect HTTP semantics across multiple endpoints
- No test repository, no CI/CD integration, no documentation

---

## What I Did
- Stood up the **full local development environment from scratch** — database tables, Clerk authentication, user setup, and all microservices — enabling isolated testing without live API costs
- Designed a **dedicated test repository architecture** separating concerns across `/api` (functional), `/load` (k6), `/e2e` (inter-service), `/config`, and `/utils` — built to scale independently from service development
- Built a **Postman → Newman → JavaScript pipeline** for API test execution, enabling CLI and CI integration; planned Playwright integration for E2E and cross-service scenarios
- Implemented **FAL API mock mode** for local testing — disabling real FAL workers to avoid unnecessary billed calls during development and regression runs
- Wrote **191+ API tests** for the Job service: 60 core tests covering job creation, retrieval, cancellation, and status transitions (in_queue → processing → completed/failed); 80+ additional negative scenarios and edge cases
- Applied **matrix testing** to run test suites across different FAL worker types (image generation vs. video generation) — ensuring both pipelines behaved correctly under the same test structure
- Identified and documented **8 critical API issues** with full reproduction steps and expected behavior for Jira:
  - Double charge due to missing idempotency by `referenceId` — critical financial risk
  - 500 error on empty JSON body — should return 400 Bad Request
  - Webhook update returning 200 for non-existent jobs — should return 404
  - Batch balance returning 201 + route collision — incorrect HTTP semantics
  - Insufficient funds returning 400 instead of 402 Payment Required
  - Cancel job returning 201 instead of 200
  - GET with invalid job type returning 200 instead of 400 (missing input validation)
  - Missing `amount` field in Refund DTO — blocking E2E refund flows
- Ran a **controlled load test** comparing old (RunPod) vs. new (Google Vertex AI) infrastructure: 20 concurrent image generation requests in 4 parallel queues of 5
- Maintained **test documentation in Qase** and delivered **daily status reports** to the team; set up GitLab repository for future CI/CD pipeline integration
- Scoped and estimated the full QA engagement: API testing ~176 hours, load testing 40–80 hours, E2E testing 3–4 weeks

---

## Results
- **191+ API tests** written and running across Job service, wallet, and worker modules
- **8 critical bugs identified** — including a double-charge vulnerability from missing idempotency, surfaced before the platform reached enterprise clients
- **Infrastructure comparison validated**: Google Vertex AI (100% success rate, ~111s avg generation time) outperformed RunPod (90% success rate, ~146s avg) — confirmed as the correct migration target
- RunPod retry behavior root cause identified: retries were routing back to the same unavailable GPU instance, causing connection failures
- Isolated test architecture established, decoupled from service code — enabling the team to scale testing independently as new microservices are added
- FAL API mock strategy implemented, reducing test cost and enabling stable, repeatable CI runs without live AI generation calls

---

## What Made the Difference
The decision to isolate the test layer into its own repository from day one — and mock FAL workers for local runs — gave the team a sustainable, cost-controlled foundation for testing a billed, rate-limited AI API. The load test comparison between RunPod and Vertex was a concrete, data-driven input to a major infrastructure decision, not just a stability check. And catching the idempotency gap in the wallet service early prevented a financial bug from reaching production.

---

## Relevant for Jobs With:
- QA for AI-powered platforms (image/video generation, LLM pipelines)
- Microservice API testing and integration validation
- Backend migration QA (AWS, Supabase, serverless)
- Postman / Newman / Playwright automation pipeline setup
- k6 load and stability testing
- FAL API, RunPod, ComfyUI, or Google Vertex AI platform testing
- GitLab CI/CD integration for test automation
- Wallet, billing, and idempotency testing for payment-sensitive systems
- Fashion tech, media, or creative AI platform QA
- Teams transitioning from monolith to microservice architecture
