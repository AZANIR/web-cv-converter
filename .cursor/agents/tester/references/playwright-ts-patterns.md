# Playwright TypeScript Patterns

## Test File Structure

```typescript
// tests/e2e/{flow}.spec.ts
import { test, expect } from '@playwright/test'

test.describe('{Feature} flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('happy path: user can {action}', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill('test@example.com')
    await page.getByRole('button', { name: 'Log in' }).click()
    await expect(page).toHaveURL('/dashboard')
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
  })

  test('error case: {condition} shows error message', async ({ page }) => {
    await page.goto('/generate')
    await page.getByRole('button', { name: 'Generate' }).click()
    await expect(page.getByRole('alert')).toContainText('required')
  })
})
```

## Auth Setup (Authenticated Tests)

```typescript
// tests/e2e/auth.setup.ts
import { test as setup } from '@playwright/test'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!)
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!)
  await page.getByRole('button', { name: 'Continue' }).click()
  await page.waitForURL('/dashboard')
  await page.context().storageState({ path: 'tests/e2e/.auth/user.json' })
})
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:3000',
    storageState: 'tests/e2e/.auth/user.json',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    { name: 'e2e', dependencies: ['setup'] },
  ],
})
```

## Common Locators (prefer role/label over CSS)

```typescript
page.getByRole('button', { name: 'Submit' })
page.getByRole('heading', { name: 'Dashboard' })
page.getByRole('link', { name: 'History' })
page.getByRole('alert')
page.getByLabel('Email')
page.getByLabel('Vacancy URL')
page.getByTestId('upload-form')  // last resort
```

## Run Commands

```bash
# Run all E2E tests
npx playwright test

# Run specific spec
npx playwright test tests/e2e/login.spec.ts

# Run with UI
npx playwright test --ui

# Show last report
npx playwright show-report
```
