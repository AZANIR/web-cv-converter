# Vacancy to Case Study — Templatization Prompt

## Task

You receive raw text from a job vacancy / job posting. Parse it and return a single valid JSON object that captures the structured requirements in a case-study-like format. Follow the schema below precisely.

---

## Output JSON Schema

```json
{
  "title": "",
  "client_type": "",
  "industry": "",
  "tags": [],
  "requirements": [],
  "responsibilities": [],
  "tech_stack": [],
  "seniority_level": "",
  "experience_years": "",
  "domain_keywords": [],
  "language_requirements": []
}
```

## Field Rules

### `title`
Short descriptive title for this vacancy. Example: "Senior QA Automation Engineer — Fintech SaaS"

### `client_type`
Type of company. Examples: "SaaS startup", "Enterprise", "Agency", "Product company"

### `industry`
Domain or vertical. Examples: "Fintech", "Healthcare", "E-commerce", "EdTech", "AI/ML"

### `tags`
Array of technology and skill tags extracted from the vacancy. Include tools, frameworks, methodologies, and testing types. Example: ["Playwright", "TypeScript", "CI/CD", "API Testing", "Performance Testing"]

### `requirements`
Array of key requirements from the vacancy (skills, qualifications, certifications). Copy or lightly rephrase from the source.

### `responsibilities`
Array of key responsibilities described in the vacancy.

### `tech_stack`
Array of specific tools and technologies mentioned. Example: ["Playwright", "Cypress", "Postman", "Jenkins", "Docker", "PostgreSQL"]

### `seniority_level`
Inferred seniority: "Junior", "Middle", "Senior", "Lead", "Principal". If unclear, use "Middle".

### `experience_years`
Required years of experience as stated or inferred. Example: "5+", "3-5", "2+"

### `domain_keywords`
Array of domain-specific keywords for semantic matching. Include industry terms, compliance standards, product types. Example: ["payments", "PSD2", "SEPA", "mobile banking"]

### `language_requirements`
Array of objects with language and level extracted from vacancy. Each object: `{"language": "English", "level": "B2"}`. Use CEFR levels (A1, A2, B1, B2, C1, C2) or descriptive levels (Fluent, Native, Conversational, Intermediate, Upper-Intermediate). If the vacancy mentions a language but not the level, set level to "". If no languages are mentioned at all, return an empty array `[]`.

---

## General Rules

1. Extract information only from the provided text. Do not invent data.
2. If a field has no matching information, use `""` for strings or `[]` for arrays.
3. Return valid JSON only, no commentary.
4. Tags should be normalized: use proper casing (e.g., "TypeScript" not "typescript").

---

## Vacancy Text

```
{{VACANCY_TEXT}}
```

**Return exactly one JSON object.**
