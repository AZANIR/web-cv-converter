# CV Markdown → JSON Conversion Prompt

## Task

Convert the CV text below (in free-form Markdown) into a single valid JSON object that matches the schema defined in this prompt. Follow every rule precisely. Do not invent data that is not present in the source — leave the corresponding field empty (empty string `""`, empty array `[]`, or omit optional subfields).

---

## Output JSON Schema

```json
{
  "name": "",
  "title": "",
  "contacts": [],
  "summary": "",
  "skills": [
    { "label": "", "value": "" }
  ],
  "certifications": [],
  "education": [
    {
      "degree": "",
      "institution": "",
      "date": ""
    }
  ],
  "experience": [
    {
      "job_title": "",
      "company": "",
      "date": "",
      "description": "",
      "projects": [
        {
          "name": "",
          "tech_tags": [],
          "team_info": "",
          "bullets": []
        }
      ],
      "bullets": []
    }
  ],
  "languages": [
    { "language": "", "level": "" }
  ]
}
```

---

## Field-by-Field Rules

### `name`
- Full name of the candidate, written in **UPPERCASE**.
- Source: usually the very first line of the CV (bold heading or plain text).
- Example: `"JOHN SMITH"`, `"JANE DOE"`

### `title`
- Current or most recent job title, as written in the CV.
- Usually appears directly below the name.
- Example: `"Senior QA Automation Engineer"`

### `contacts`
- Array of contact strings: email, phone, LinkedIn URL, GitHub URL, Telegram handle, website, etc.
- Each contact is a plain string — no labels, just the raw value.
- If the CV contains no contact information → leave as `[]`.
- Example: `["john.smith@email.com", "github.com/johnsmith", "linkedin.com/in/johnsmith", "t.me/johnsmith"]`

### `summary`
- The candidate's "About" or "Summary" paragraph, copied verbatim (light editing for punctuation only).
- One continuous string.
- If absent → `""`

### `skills`
- Array of `{ "label": "...", "value": "..." }` objects.
- Group individual skills into meaningful **categories** based on their nature.
- `label`: the category name (e.g. `"Automation"`, `"Languages"`, `"Testing"`, `"APIs"`, `"Databases"`, `"CI/CD"`, `"Tools"`, `"Compliance"`, `"LLM/AI"`, `"Security"`, `"BDD/Reporting"`, etc.)
- `value`: comma-separated list of skills/tools belonging to that category.
- Extract skills from the dedicated SKILLS section AND from "Tech stack:" lines inside experience descriptions.
- Do **not** duplicate skills across categories.
- Suggested grouping logic:
  - **Automation**: test automation frameworks (Playwright, Cypress, WebdriverIO, k6, Robot Framework, Pytest, etc.)
  - **Languages**: programming/scripting languages (TypeScript, JavaScript, Python, Java, SQL, etc.)
  - **Testing**: testing types/methodologies (E2E, integration, regression, API, performance, smoke, security, manual, exploratory, LLM evaluation, etc.)
  - **APIs**: API protocols/specs (REST, GraphQL, SOAP, HL7 FHIR, WebSocket, etc.)
  - **Databases**: databases and relevant operations (PostgreSQL, MySQL, MongoDB, etc.)
  - **CI/CD**: CI/CD platforms and containerization (GitHub Actions, GitLab CI, Jenkins, Docker, CircleCI, Azure DevOps, etc.)
  - **LLM/AI**: AI-related skills (prompt injection testing, RAG validation, output consistency, adversarial testing, GPT-4 test generation, etc.) — only if present
  - **Security**: security tools/methodologies (OWASP ZAP, Burp Suite, OWASP Top-10, etc.) — only if present
  - **Compliance**: regulatory frameworks (HIPAA, GDPR, PSD2, AML, SOC 2 Type II, PCI DSS, etc.) — only if present
  - **Tools**: misc tooling (Postman, SoapUI, Allure, TestRail, Jira, Git, Grafana, Chrome DevTools, Confluence, Swagger, etc.)
- If no skills section present → `[]`

### `certifications`
- Array of plain strings, one per certification.
- Include courses, certificates, and notable professional roles (e.g. mentor positions with URLs).
- If no certifications mentioned → `[]`
- Example: `["Jr Penetration Tester Certificate (TryHackMe)"]`

### `education`
- Array of education entries, most recent first.
- Each entry:
  - `degree`: full degree name and field of study as written (e.g. `"Master's degree — Computer Science and Software Engineering"`)
  - `institution`: university or institution name
  - `date`: year range as written (e.g. `"2012 – 2013"`)
- If absent → `[]`

### `experience`
- Array of work experience entries, most recent first (preserve the order from the CV).
- Each entry has the following fields:

#### `job_title`
- Exact title as written for this position.

#### `company`
- Exact company name. If the CV says "Confidential" or "Confidential Project" → use `"Confidential"`.

#### `date`
- Date range in format `"Mon YYYY – Mon YYYY"` or `"Mon YYYY – Present"`.
- Use 3-letter English month abbreviations if months are present (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec).
- Example: `"May 2025 – Present"`, `"Feb 2023 – Apr 2025"`

#### `description`
- Optional free-text field for a **role-level** description — use it only when the position has no project breakdown (e.g., freelance consulting roles or single-company roles without named projects).
- For standard positions where all context is captured inside `projects`, leave as `""` or omit.

#### `projects`
- Array of project objects within this job.
- **When to use**: when the CV describes one or more distinct client projects, domains, or product areas under a single employer.
- **When to use `[]`**: when the role has only one undivided context and bullets sit at the top level.
- Each project object:

  **`name`** — descriptive project title you compose from the CV text. Format:
  - For multi-project roles: `"Project N — [Product Description] ([Domain])"` e.g. `"Project 1 — Digital Banking Platform (Fintech)"`
  - For single-project roles: `"[Product Description] ([Domain])"` e.g. `"AI Infrastructure & LLM Developer Tools Platform"`
  - Domain tags to use: Fintech, Healthcare, E-Commerce, Telecom, Media, Banking, Enterprise, etc.

  **`tech_tags`** — array of individual technology/tool strings extracted from the **"Tech stack:"** line of that role (or from the bullets if no tech stack line exists).
  - Each tag is a separate string: `["TypeScript", "Playwright", "k6", "Docker"]`
  - Do not include compliance frameworks (HIPAA, GDPR, etc.) in tech_tags — those belong in skills.

  **`team_info`** — optional string with team size, duration, geography, compliance context, or other brief role metadata.
  - Format examples: `"Team: 4 QA engineers | PSD2, AML, GDPR compliance"`, `"EMEA region | GDPR compliance"`, `"Team: 6 people | Duration: 9 months"`
  - If no such info is present → `""` or omit the field.

  **`bullets`** — array of achievement/responsibility strings, one per bullet point.
  - Copy from the CV bullet list for that role/project.
  - Light editing is acceptable: remove markdown asterisks, straighten punctuation, keep meaning intact.
  - Do not merge bullets. Do not split one bullet into many.

#### Top-level `bullets` (on the experience entry, not inside a project)
- Use when the experience entry has `"projects": []` — i.e., all bullets belong directly to the role with no project subdivision.
- Same format as project-level bullets.
- If projects are used → set top-level `bullets` to `[]`.

### `languages`
- Array of `{ "language": "...", "level": "..." }` objects.
- Include the candidate's spoken/written languages and their proficiency levels.
- If no language information is present in the CV → `[]`
- Example: `[{ "language": "Ukrainian", "level": "Native" }, { "language": "English", "level": "B2 (Upper-Intermediate)" }]`

---

## General Rules

1. **No invented data.** If a piece of information is not in the source CV, leave the field as `""`, `[]`, or omit the optional subfield. Never guess, infer, or hallucinate.
2. **Preserve order.** Experience entries must appear in the same order as in the source (typically reverse-chronological).
3. **Valid JSON only.** Output must be parseable by `JSON.parse()`. No trailing commas, no comments, no markdown fences around the final output.
4. **String escaping.** Properly escape any characters that require it in JSON strings (quotes, backslashes, etc.).
5. **No extra fields.** Do not add fields that are not defined in the schema above.
6. **Compliance tags** (HIPAA, GDPR, PSD2, SOC 2, AML, PCI DSS) go into `skills[].value` under the `"Compliance"` label — not into `tech_tags`.
7. **Tech stack line removal.** Do not include the raw "Tech stack: ..." line as a bullet point — extract it into `tech_tags` and discard the original line.

---

## Worked Example

**Input (excerpt):**
```
John Smith

Senior QA Automation Engineer

ABOUT

QA engineer with 11 years of experience...

EXPERIENCE

Senior QA Automation Engineer
Confidential Project   May 2025 – Present

An AI infrastructure company...

* Own the test strategy for an LLM-powered platform...
* Design and run prompt injection...

Tech stack: Playwright (TypeScript), k6, Postman, LLM evaluation frameworks, GitHub Actions, Docker, Jira, Allure
```

**Output (excerpt):**
```json
{
  "name": "John Smith",
  "title": "Senior QA Automation Engineer",
  "contacts": [],
  "summary": "QA engineer with 11 years of experience...",
  "experience": [
    {
      "job_title": "Senior QA Automation Engineer",
      "company": "Confidential",
      "date": "May 2025 – Present",
      "description": "",
      "projects": [
        {
          "name": "AI Infrastructure & LLM Developer Tools Platform",
          "tech_tags": ["TypeScript", "Playwright", "k6", "Postman", "GitHub Actions", "Docker", "Allure"],
          "team_info": "",
          "bullets": [
            "Own the test strategy for an LLM-powered platform: cover the deterministic application layer (UI, REST APIs, auth) in Playwright and the non-deterministic LLM output layer using structured evaluation frameworks",
            "Design and run prompt injection and adversarial input test suites against the prompt management API; maintain a library of known injection patterns and test each release for new bypass vectors"
          ]
        }
      ],
      "bullets": []
    }
  ]
}
```

Note: `"LLM evaluation frameworks"` from the tech stack becomes an entry in `skills` under `"LLM/AI"` label, not a tech_tag. `"Jira"` goes to `skills` under `"Tools"`. Only direct tools/languages/frameworks go into `tech_tags`.

---

## Source CV

Paste the full CV Markdown text below this line:

```
[INSERT CV MARKDOWN HERE]
```

---

**Return exactly one JSON object** matching the schema above. No commentary before or after. You may wrap that object in a markdown code block whose language tag is `json`.

Keep `description`, `bullets`, and `summary` text **concise** (no unnecessary repetition) so the full JSON stays compact.
