# Case Study: 250+ API Tests Automated & Load Issues Cut 60% for E-commerce SaaS (QPilot)

## Overview
- **Client type:** SaaS product company
- **Industry:** E-commerce / Automated Procurement (WordPress-based)
- **Service provided:** API Tester / QA Specialist — API automation, performance testing, CI integration
- **Tags:** JavaScript, Playwright, Axios, API Testing, Load Testing, WordPress, E-commerce, SaaS, CI/CD, Parallel Execution

---

## The Challenge
QPilot provides automated recurring order management for e-commerce businesses — handling scheduling, shipping, payments, and discounts across web and mobile. As the platform scaled, API reliability and load performance became critical risks, but test coverage was thin and documentation was outdated.

Key pain points:
- Slow test execution — frequent API calls and data refreshes caused test lag in CI
- Outdated Postman collection with missing or broken request samples
- No load testing capability — traditional tools weren't accessible
- Business-critical flows (scheduling, payments, discounts) lacking proper test coverage

---

## What I Did
- Built **250+ automated API and UI test cases** using **JavaScript, Playwright, and Axios**
- Used **Playwright** for browser-based flow automation and **Axios** for deep HTTP-level API validation (payloads, status codes, headers)
- Integrated test runs into **CI pipelines** for continuous feedback on every code change
- Enabled **parallel test execution with multiple workers** — reduced test runtime by 45%
- Used **Playwright tracing tools** to capture live API traffic and fill Postman documentation gaps with real, working request samples
- Designed a custom **Excel-based data injection method** via the admin panel to simulate peak traffic for load testing — without needing external load tools
- Validated system performance and identified bottlenecks under high-load scenarios

---

## Results
- **250+ API and UI test cases automated**, with continuously expanding coverage
- **45% reduction in API test runtime** through parallel execution
- **24 high-priority bugs identified and reported**, accelerating dev response
- **60% improvement in backend performance under stress** through custom load testing
- Live Postman documentation rebuilt from Playwright traces — no gaps remaining

---

## What Made the Difference
The creative load testing approach was the standout contribution — without access to traditional load testing tools, building a data injection flow via the admin panel gave the client real peak-traffic insights they had no other way to obtain. Documentation-as-a-byproduct (capturing live API traffic via Playwright tracing) also saved significant time.

---

## Relevant for Jobs With:
- API test automation (Playwright, Axios, Postman)
- JavaScript-based testing frameworks
- E-commerce or SaaS platforms (especially WordPress/WooCommerce)
- CI/CD pipeline integration for testing
- Performance and load testing
- API documentation improvement
- Recurring payments, scheduling, or subscription platform testing
