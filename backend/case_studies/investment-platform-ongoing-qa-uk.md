# Case Study: QA Process Setup & Ongoing Testing for UK Investment Management Platform (NDA)

## Overview
- **Client type:** Two-sided SaaS investment platform
- **Industry:** Investment Management / Fintech (UK)
- **Service provided:** Manual QA Engineer — QA process setup, ongoing sprint testing, exploratory testing, compatibility and accessibility testing
- **Tags:** Manual Testing, Exploratory Testing, Functional Testing, UI Testing, Regression Testing, Accessibility Testing, Compatibility Testing, Smoke Testing, Fintech QA, Agile QA, Web Testing

---

## The Challenge
A UK-based investment management platform connecting investors and SMEs — covering deal tracking, investor relationship management, document management, and fundraising materials — was live but lacked a dedicated QA function. The development pace was fast, the team was small, and the platform's domain complexity (financial metrics, investment flows, two-sided user roles) made ad hoc testing insufficient.

Key pain points:
- No dedicated QA engineer or structured testing process in a live, fast-moving product
- Highly dynamic development with new features shipping continuously — no stable regression baseline
- Complex domain requiring deep understanding before effective testing (investment terminology, two-sided user roles, calculation logic)
- Emergency production rollouts with no safety net
- No testing strategy document or formal QA documentation to guide coverage decisions
- Risk of reputational and financial damage if core investment flows reached users broken

---

## What I Did
- Joined an active, live product and completed structured **onboarding and exploratory testing** to map the platform's full functionality, terminology, and user flows before writing a single formal test
- Logged all defects discovered during the exploratory phase with detailed reproduction steps and business-impact context
- Authored a **testing strategy document** that became the team's core QA reference — defining coverage priorities, testing types, and escalation rules for emergency rollouts
- Established an **ongoing sprint-based QA cadence**: inspecting all new features as soon as they appeared in the test build, prioritising bugs by business impact
- Covered **production testing** for emergency rollouts — running critical flow checks directly on live environments when sprint timelines required it
- Validated **calculation correctness** for financial input scenarios in production — ensuring investment metrics, deal tracking data, and fundraising outputs were numerically accurate
- Applied a full suite of testing types across every sprint cycle: exploratory, functional, UI, compatibility, accessibility, smoke, regression, and retesting after bug fixes
- Delivered **cross-platform compatibility testing** across 10 OS and browser combinations, plus dedicated iOS and Android device rounds
- Maintained **constant collaboration** with the development team through planning meetings, daily standups, sync calls, and async communication — acting as an embedded QA partner rather than an external reviewer

---

## Results
- **Critical defects detected** across core platform functionality — several features would have been unusable in production without QA intervention
- Platform tested across **10 OS and browser combinations**, plus iOS and Android coverage — ensuring reliability regardless of user environment
- Bug prioritisation by business impact prevented user-facing failures, protecting the platform's financial and reputational standing
- Testing strategy document established a sustainable, scalable QA foundation the team could build on as the product grew
- Zero user complaints related to tested feature areas during the engagement

---

## What Made the Difference
Starting with deep exploratory testing — before any documentation or formal cases — was the right call for a live, complex fintech product with no QA history. Understanding the domain (investment flows, two-sided roles, calculation logic) made every subsequent test more targeted and every bug report more actionable. The testing strategy document then gave the team a shared language for quality that outlasted any individual sprint.

---

## Relevant for Jobs With:
- Ongoing QA for live SaaS products in fast-moving teams
- Fintech, investment management, or two-sided marketplace QA
- QA process setup from scratch on an existing product
- Exploratory and functional testing for complex domain applications
- Agile / sprint-based QA with direct dev team collaboration
- Accessibility and compatibility testing (cross-browser, cross-device)
- Production testing and emergency rollout support
- Financial calculation and data accuracy validation
- Small-team or part-time embedded QA roles
