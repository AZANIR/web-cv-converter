# Case Study: Boosted QA Efficiency by 64% in EdTech Automation Project (Schoolio)

## Overview
- **Client type:** EdTech SaaS platform
- **Industry:** Education / K-8 Online Learning (Canada)
- **Service provided:** SDET Lead — test automation architecture, QA process setup
- **Tags:** TypeScript, WebdriverIO, Page Object Model, GitHub Actions, Jira, Automated Testing, SDET, EdTech, Regression Testing, CI/CD

---

## The Challenge
Schoolio is a K–8 EdTech platform where users build interactive courses, lessons, quizzes, and assessments. The platform had a growing test suite but lacked automation coverage, structured QA processes, and CI/CD integration — making releases slow and risky.

Key pain points:
- Large manual test suite with no scalable automation strategy
- Complex dynamic quiz flows that were hard to automate reliably
- Media stream validation (video/audio) failing inconsistently in automated environments
- No GitHub Actions pipeline to give developers fast QA feedback

---

## What I Did
- Led automation using **TypeScript + WebdriverIO**, structured via **Page Object Model** for maintainability
- Automated **116 of 181 test cases (64%)** — regression and smoke suites run on every push
- Set up **GitHub Actions** CI/CD pipelines for automated test execution and dev feedback loops
- Co-developed modular quiz interaction helpers with the dev team to handle dynamic user inputs
- Introduced **randomized data testing** to simulate diverse real-world user behaviors across quiz types
- Covered video/audio stream validation through high-precision **manual testing** (too resource-heavy for automation)
- Logged **200+ detailed bugs in Jira**, directly contributing to platform stability
- Conducted hands-on usability testing, surfacing UI/UX blockers automation couldn't catch
- Maintained test documentation and coverage tracking in Google Sheets

---

## Results
- **64% automation coverage** achieved (116 of 181 test cases), cutting manual QA time by nearly half
- **200+ bugs logged** in Jira with structured detail, accelerating resolution
- **15+ critical pre-release bugs** caught and resolved — including edge cases in video rendering and quiz flows
- Faster, more reliable release cycles through CI/CD-integrated smoke and regression testing
- QA established as a core product enabler, not a bottleneck

---

## What Made the Difference
Collaborating directly with developers to build extensible quiz automation helpers was the key unlock. Instead of fighting the dynamic logic, we made it testable by design — and the randomized data layer ensured we were testing real user behavior, not just happy paths.

---

## Relevant for Jobs With:
- WebdriverIO or TypeScript-based test automation
- SDET / QA Lead roles
- EdTech or e-learning platforms
- GitHub Actions CI/CD setup for testing
- End-to-end and regression test suite development
- Bug tracking and QA process improvement
- Platforms with complex dynamic UI (quizzes, forms, media)
