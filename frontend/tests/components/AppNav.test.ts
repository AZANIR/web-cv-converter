import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import AppNav from '~/components/AppNav.vue'

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
