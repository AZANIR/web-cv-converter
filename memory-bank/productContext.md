# Product Context

## Why It Exists

Tailoring a CV for each job application is time-consuming. This tool automates the analysis and optimization of CV content against a specific job vacancy using AI, then produces a properly formatted PDF — eliminating the need for manual editing and layout work.

## Target Users

- QA engineers and tech professionals applying for new roles
- Internal users only (access controlled via `allowed_emails` Supabase table)

## Problems Solved

| Problem | Solution |
|---|---|
| Manual CV tailoring for each vacancy | AI analyzes vacancy and rewrites CV sections |
| Formatting inconsistency | Standardized PDF templates with professional layout |
| Context switching (writing + design) | Single tool handles content + output |
| Storing and re-using past CVs | Conversion history per user |

## User Journey

1. Log in via Auth0 (Google or email)
2. Navigate to Convert page
3. Paste Markdown CV and vacancy URL or text
4. Submit — AI processes and optimizes
5. View generated CV result
6. Download as PDF or copy Markdown
7. Access history of past conversions at any time
