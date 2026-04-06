# Case Study: 68 Bugs Found in Full-Site Testing of Dutch Holiday Rental Marketplace (NDA)

## Overview
- **Client type:** Online holiday rental marketplace
- **Industry:** Travel & Hospitality (Netherlands)
- **Service provided:** Manual QA — full-site compatibility, functional, and UI testing on a live platform
- **Tags:** Manual Testing, Functional Testing, UI Testing, Compatibility Testing, Cross-Browser Testing, Cross-Device Testing, Live Environment Testing, Google Spreadsheet Bug Reporting, Web Testing, Travel Platform QA

---

## The Challenge
A large Dutch holiday rental marketplace — operating across 50+ countries and connecting property owners with travellers — requested a full round of website QA on their live production platform. The site had been running since 2010, and the primary goal was to validate look, functionality, and consistency across devices and browsers without disrupting real users or active bookings.

Key pain points:
- Testing had to be conducted on a live platform with real users — any test actions risked interfering with actual property owners and guests
- Geographic access restriction (Netherlands only) required a VPN-based testing setup
- No existing bug tracking system — defect reporting needed a custom solution
- Large site scope required upfront alignment on what could and could not be tested in a live environment
- Booking and owner interaction flows needed validation without creating noise for real platform participants

---

## What I Did
- Coordinated with the client to define scope upfront — agreeing on which pages and functionalities to include and explicitly excluding those not suitable for live testing
- Requested a **dedicated test booking entity** (a test user with a real property listing) to safely test booking flows, feedback submission, owner messaging, and rental features without affecting real users
- Configured **VPN access** to simulate Netherlands-based browsing and ensure accurate rendering and geo-restricted feature coverage
- Prepared **structured test documentation** — a detailed checklist covering all agreed functionality across required devices and browsers
- Assigned three QA engineers to execute **cross-browser and cross-device testing** in parallel, ensuring efficient full-site coverage
- Reported all **68 bugs in a Google Spreadsheet** (the client's preferred format) alongside the testing checklist — with severity classification, reproduction steps, and prioritisation guidance
- Provided recommendations on fix prioritisation: all critical and major bugs flagged for immediate action, with guidance to address the most user-noticeable minor bugs first

---

## Results
- **68 bugs identified** on a live platform — the majority Minor or Trivial, but collectively significant for user experience and platform trust
- All defects reported with severity classification, enabling the client to prioritise fixes by user impact
- **Nearly all recommendations implemented** by the client team within weeks of delivery
- Client expressed high satisfaction with the thoroughness and structure of the QA output
- Full-site coverage completed without any disruption to real users, bookings, or property owner accounts

---

## What Made the Difference
Setting up a dedicated test account before touching any live functionality was essential — it meant the QA team could test booking flows, owner messaging, and feedback submission with full confidence, without risking confusion for real platform users. The upfront scoping conversation also saved time by drawing a clear line between what could and couldn't be tested safely in a live environment.

---

## Relevant for Jobs With:
- Live environment / production testing
- Travel, hospitality, or rental marketplace platform QA
- Cross-browser and cross-device compatibility testing
- Full-site manual QA audits (one-time or by estimate)
- Functional and UI testing for web applications
- Testing without a bug tracker (Google Spreadsheet reporting)
- Geo-restricted platform testing (VPN setup)
- Booking, payment, and marketplace flow validation
