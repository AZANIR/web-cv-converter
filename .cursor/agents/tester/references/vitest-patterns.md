# Vitest Patterns

## Component Test Structure

```typescript
// frontend/tests/{Component}.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Component from '~/components/{Component}.vue'

describe('{Component}', () => {
  it('renders with required props', () => {
    const wrapper = mount(Component, {
      props: { title: 'Test Title' },
    })
    expect(wrapper.text()).toContain('Test Title')
  })

  it('emits action event when button clicked', async () => {
    const wrapper = mount(Component, {
      props: { id: 'item-1', title: 'Test' },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('action')).toBeTruthy()
    expect(wrapper.emitted('action')![0]).toEqual(['item-1'])
  })

  it('shows error state when status is error', () => {
    const wrapper = mount(Component, {
      props: { title: 'Test', status: 'error' },
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(true)
  })
})
```

## Composable Test Structure

```typescript
// frontend/tests/use{Name}.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useName } from '~/composables/useName'

vi.mock('~/composables/useApi', () => ({
  useApi: vi.fn().mockResolvedValue({ data: { id: '1' } }),
}))

describe('useName', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with null state', () => {
    const { state, loading, error } = useName()
    expect(state.value).toBeNull()
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('fetches data and updates state', async () => {
    const { state, fetchResource } = useName()
    await fetchResource('test-id')
    expect(state.value).toEqual({ id: '1' })
  })
})
```

## Run Commands

```bash
# Run all frontend unit tests
cd frontend && npx vitest run

# Run with coverage
cd frontend && npx vitest run --coverage

# Run in watch mode
cd frontend && npx vitest

# Run specific test file
cd frontend && npx vitest run tests/UploadForm.test.ts
```
