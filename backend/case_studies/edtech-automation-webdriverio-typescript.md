# Case Study: 63% Regression Automated & 200+ Bugs Logged in US EdTech Platform (NDA)

## Overview
- **Client type:** EdTech SaaS startup
- **Industry:** Education / E-learning (Elementary, USA)
- **Service provided:** QA Automation Engineer — hybrid QA setup, automation framework, CI/CD integration
- **Tags:** TypeScript, WebdriverIO, Page Object Model, GitHub Actions, Jira, Manual Testing, Automated Testing, Regression Testing, EdTech, UI/UX Testing, CI/CD

---

## The Challenge
A US-based EdTech platform for elementary learning was live but had no structured QA process. Testing was limited to basic smoke checks by the project manager and occasional unit/integration tests by developers — with no automation, no regression coverage, and no formal bug tracking.

Key pain points:
- No QA framework or structured testing process
- Complex interactive features (quizzes, drag-and-drop, multimedia) left untested
- Audio and video stream validation was inconsistent and resource-heavy under automation
- No CI/CD integration for test execution
- No visibility into regression health between releases

---

## What I Did
- Established a hybrid QA approach: **automated testing for quiz logic and regressions**, manual validation for media-rich and audio/video content where automation was unreliable
- Collaborated with the dev team to design a **custom modular method stack** for complex quiz interactions — drag and drop, line drawing, multiple-choice, and open-text questions
- Introduced **randomized data generation** to simulate real user behavior and improve edge case coverage
- Built the automation framework using **TypeScript + WebdriverIO** with a **Page Object Model** architecture for maintainability and scalability
- Integrated test execution into **GitHub Actions CI/CD**, synchronizing automated runs with dev workflows
- Documented regression test cases in **Google Sheets** and logged all bugs in **Jira**
- Conducted **usability testing** to surface UX friction points and drive iterative improvements

---

## Results
- **200 test cases created**, 126 automated — achieving **63% regression automation coverage** in 3 months
- **200+ bugs logged in Jira**, directly improving platform stability
- **10–15 non-critical issues** (UI glitches, security flaws) resolved pre-release
- Reduced post-release issues and improved overall product reliability
- Noticeable boost in user satisfaction through iterative UX improvements

---

## What Made the Difference
The decision to go hybrid — automating structured logic while keeping media validation manual — prevented the team from wasting time on flaky, resource-heavy tests. The modular quiz helper stack, built together with developers, made complex interactions reliably testable and gave the team a reusable foundation to scale from.

---

## Relevant for Jobs With:
- WebdriverIO / TypeScript test automation
- EdTech or e-learning platform QA
- Hybrid manual + automated testing strategies
- GitHub Actions CI/CD setup for testing
- Complex UI automation (drag-and-drop, dynamic forms, quiz flows)
- QA framework setup from scratch
- Bug tracking and regression management (Jira, Google Sheets)
- Usability and UX testing
