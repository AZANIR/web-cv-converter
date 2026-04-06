# Case Study: Robust Manual API Testing for GreenTech IoT Platform (NDA)

## Overview
- **Client type:** GreenTech SaaS platform
- **Industry:** Renewable Energy / IoT / Green Technology
- **Service provided:** Lead API QA Engineer — manual API testing, OWASP security testing, performance validation
- **Tags:** Manual Testing, API Testing, Postman, OWASP, IoT, Security Testing, CRUD Validation, Performance Testing, GreenTech

---

## The Challenge
A GreenTech platform providing real-time monitoring and analytics for renewable energy infrastructure — integrating IoT sensors and IoT devices through API endpoints — needed thorough manual API validation before deployment. The APIs handled sensitive IoT data, making security and reliability critical requirements.

Key pain points:
- Complex IoT data flows requiring precision validation across all CRUD operations
- Potential security vulnerabilities in APIs handling sensitive energy infrastructure data
- No systematic OWASP coverage — known vulnerability classes untested
- API response times weren't benchmarked or optimized for real-world load

---

## What I Did
- Led manual API testing using **Postman**, systematically validating **425+ CRUD operations** across all key endpoints
- Applied **boundary value analysis and equivalence partitioning** to cover all input scenarios for IoT data flows
- Executed full **OWASP Top 10 security test coverage** — identified and resolved 4 major vulnerabilities:
  - SQL Injection
  - Broken Authentication
  - Improper Access Control
- Performed **stress and load testing** to identify performance bottlenecks under heavy traffic
- Worked directly with developers on optimization — improved endpoint response times by 25%
- Delivered structured **Postman collection-based test reports** for developer collaboration and audit trails
- Logged **120+ actionable issues** with clear reproduction steps and severity classification

---

## Results
- **425+ CRUD operations validated** across all API endpoints
- **4 critical OWASP Top 10 vulnerabilities resolved** before production deployment
- **25% improvement in API response times** through performance testing and dev collaboration
- **120+ bugs documented** with clear, actionable reproduction steps
- Platform declared deployment-ready for real-world, large-scale IoT integration

---

## What Made the Difference
Treating security testing as a first-class citizen alongside functional testing — not an afterthought — caught SQL injection and broken authentication issues before they could reach production in a sensitive infrastructure context. The structured Postman collections also became living documentation the dev team continued using after the engagement.

---

## Relevant for Jobs With:
- Manual API testing (Postman)
- OWASP security testing
- IoT platform QA
- GreenTech, energy, or infrastructure SaaS
- API performance and load testing
- Security-sensitive or compliance-focused projects
- CRUD endpoint validation
- Lead / senior API QA roles
