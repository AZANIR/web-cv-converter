# Case Study: 850+ Automated API Tests for Hotel Booking SaaS (CultBooking)

## Overview
- **Client type:** SaaS product company
- **Industry:** Hospitality / Hotel Tech (Germany)
- **Service provided:** Test automation — API & integration testing
- **Duration:** Ongoing engagement (published Nov 2023)
- **Tags:** API Testing, Test Automation, JavaScript, Postman, Newman, Allure, CI/CD, SaaS, QA

---

## The Challenge
CultBooking provides a turnkey hotel booking engine for hotels across Europe, handling reservations, room presentation, and the full booking flow. As the platform scaled, the team needed robust, automated API coverage across staging and production environments — with clear reporting for both developers and stakeholders.

Key pain points:
- Incomplete and unclear API documentation slowing down testing
- No centralized API reference (Swagger was outdated)
- Tests needed to run across multiple environments with isolated, readable results
- Manual testing was not sustainable at this scale

---

## What I Did
- Designed and implemented 850+ automated API test cases using **JavaScript, Postman, and Newman**
- Integrated **Allure** for structured, stakeholder-friendly test reporting — linked via dashboards and README
- Built environment-specific smoke test suites (staging + production) with isolated Allure reports per environment
- Implemented automated **setup and teardown** for integration tests to eliminate false positives and keep environments clean
- Integrated **Gmail and Outlook** environments for email-based feature testing
- Opened detailed GitLab issues for API documentation gaps, with endpoint-specific breakdowns
- Updated Swagger docs and ran regular syncs with the dev team to close knowledge gaps
- Set up **weekly regression suites** in the CI/CD pipeline

---

## Results
- **850+ automated test cases** executed, covering all key functional endpoints
- **320+ high- and medium-severity bugs** reported, accelerating resolution and raising product quality
- Automated setup/teardown reduced false positives and ensured environment cleanliness
- Allure reports integrated into CI/CD — full test visibility and traceability for the team
- Zero critical bugs in production across multiple release cycles thanks to weekly regression suites

---

## What Made the Difference
Starting with documentation — filing detailed GitLab issues and updating Swagger — created a shared source of truth that made every subsequent test more accurate. Once documentation and environments were stable, automation compounded quickly in coverage and reliability.

---

## Relevant for Jobs With:
- API test automation
- QA for SaaS products
- Postman / Newman / Allure setups
- CI/CD integration for testing
- JavaScript-based test frameworks
- Bug reporting and quality improvement engagements
- European or hospitality-sector clients
