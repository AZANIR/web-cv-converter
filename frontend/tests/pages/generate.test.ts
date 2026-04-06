import { describe, it, expect, vi } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import GeneratePage from '~/pages/generate/index.vue'

const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  go: vi.fn(),
  beforeEach: vi.fn(),
  beforeResolve: vi.fn(),
  afterEach: vi.fn(),
  currentRoute: { value: { path: '/generate' } },
  resolve: vi.fn().mockReturnValue({ href: '/' }),
  addRoute: vi.fn(),
  removeRoute: vi.fn(),
  hasRoute: vi.fn(),
  getRoutes: vi.fn().mockReturnValue([]),
}

mockNuxtImport('useApiRequest', () => () => vi.fn())
mockNuxtImport('useRouter', () => () => mockRouter)

describe('Generate Page', () => {
  it('renders the page heading', async () => {
    const wrapper = await mountSuspended(GeneratePage)
    expect(wrapper.text()).toContain('Generate CV')
  })

  it('shows the vacancy input form', async () => {
    const wrapper = await mountSuspended(GeneratePage)
    expect(wrapper.text()).toContain('Paste a vacancy')
  })
})
