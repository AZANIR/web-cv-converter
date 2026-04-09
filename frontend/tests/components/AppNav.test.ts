import { describe, it, expect, vi } from 'vitest'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import AppNav from '~/components/AppNav.vue'

mockNuxtImport('useUserSession', () => () => ({
  session: { value: {} },
  loggedIn: { value: true },
  user: { value: null },
  fetch: vi.fn().mockResolvedValue(undefined),
  clear: vi.fn().mockResolvedValue(undefined),
}))

mockNuxtImport('useApiRequest', () => () => vi.fn().mockResolvedValue({ role: null }))

describe('AppNav', () => {
  it('renders the brand name', async () => {
    const wrapper = await mountSuspended(AppNav)
    expect(wrapper.text()).toContain('CV Converter')
  })

  it('shows Dashboard and History links', async () => {
    const wrapper = await mountSuspended(AppNav)
    expect(wrapper.text()).toContain('Dashboard')
    expect(wrapper.text()).toContain('History')
  })

  it('shows Log out button', async () => {
    const wrapper = await mountSuspended(AppNav)
    expect(wrapper.text()).toContain('Log out')
  })
})
