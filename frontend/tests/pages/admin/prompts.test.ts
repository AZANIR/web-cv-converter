import { describe, it, expect, vi } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import PromptsPage from '~/pages/admin/prompts.vue'

mockNuxtImport('useApiRequest', () => () => vi.fn().mockResolvedValue({ items: [] }))

describe('Admin Prompts Page', () => {
  it('renders the prompts heading', async () => {
    const wrapper = await mountSuspended(PromptsPage)
    expect(wrapper.text()).toContain('Prompts')
  })
})
