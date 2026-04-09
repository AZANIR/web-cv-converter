# Style Guide

## Python

Follows PEP 8 with project-specific additions.

| Rule | Standard | Example |
|---|---|---|
| Functions / methods | `snake_case` | `get_user_data()` |
| Classes | `PascalCase` | `ConversionService` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_FILE_SIZE_MB = 10` |
| Private functions | `_snake_case` prefix | `_validate_token()` |
| Type hints | Required on all public functions | `def create(self, user_id: str) -> dict:` |
| Max line length | 100 characters | — |
| Imports | stdlib then third-party then local, separated by blank lines | — |

## TypeScript / Vue

Follows Vue 3 Composition API conventions.

| Rule | Standard | Example |
|---|---|---|
| Components | PascalCase file + component name | `UploadForm.vue` |
| Composables | `use` prefix, camelCase | `useApi.ts` |
| Pages | kebab-case or Nuxt route convention | `generate-history.vue` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES = 3` |
| Interfaces | PascalCase | `interface Props { ... }` |
| Reactive variables | Descriptive, no `val` / `data` suffix | `isLoading`, `conversions` |

## Commit Messages

Follow Conventional Commits as defined in `.cursor/rules/git-workflow.mdc`.

| Violation | Advisory Note |
|---|---|
| Message in past tense | Use present tense: "add" not "added" |
| Message > 72 chars | Shorten or move detail to body |
| Missing type prefix | Add `feat:`, `fix:`, `docs:` etc. |
| Generic message | "fix bug" is not useful — describe what bug |
