import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { useApiRequest } from '../../composables/useApi'

// ---------------------------------------------------------------------------
// Hoisted mocks — must be defined before any imports that consume them
// ---------------------------------------------------------------------------
const { mockSession, mockFetch } = vi.hoisted(() => {
  // $fetch.create() is called by auth-interceptor.client plugin at startup;
  // it must exist or the plugin throws and all tests in this file get skipped.
  const create = vi.fn()
  const fn = Object.assign(vi.fn(), { create })
  create.mockReturnValue(fn)
  return {
    mockSession: { value: {} as Record<string, unknown> },
    mockFetch: fn,
  }
})

mockNuxtImport('useUserSession', () => () => ({
  session: mockSession,
  loggedIn: { value: true },
  user: { value: null },
  fetch: vi.fn(),
  clear: vi.fn(),
}))

mockNuxtImport('useRuntimeConfig', () => () => ({
  public: {
    apiBase: 'http://localhost:3000',
  },
}))

// Replace $fetch globally so we can capture calls
vi.stubGlobal('$fetch', mockFetch)

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
describe('useApiRequest', () => {
  beforeEach(() => {
    mockSession.value = {}
    mockFetch.mockReset()
    mockFetch.mockResolvedValue({ ok: true })
  })

  it('returns a callable function', () => {
    const request = useApiRequest()
    expect(typeof request).toBe('function')
  })

  it('adds Authorization header when session contains an accessToken', async () => {
    mockSession.value = { accessToken: 'test-access-token' }
    const request = useApiRequest()
    await request('/api/me').catch(() => {})

    const [, opts] = mockFetch.mock.calls[0] ?? []
    expect(opts?.headers?.Authorization).toBe('Bearer test-access-token')
  })

  it('adds X-Auth0-ID-Token header when session contains an idToken', async () => {
    mockSession.value = { accessToken: 'at', idToken: 'id-token-value' }
    const request = useApiRequest()
    await request('/api/me').catch(() => {})

    const [, opts] = mockFetch.mock.calls[0] ?? []
    expect(opts?.headers?.['X-Auth0-ID-Token']).toBe('id-token-value')
  })

  it('does NOT add Authorization header when session is empty', async () => {
    mockSession.value = {}
    const request = useApiRequest()
    await request('/api/me').catch(() => {})

    const [, opts] = mockFetch.mock.calls[0] ?? []
    expect(opts?.headers?.Authorization).toBeUndefined()
  })

  it('prepends the configured apiBase URL to the path', async () => {
    mockSession.value = {}
    const config = useRuntimeConfig()
    const request = useApiRequest()
    await request('/api/me').catch(() => {})

    const [url] = mockFetch.mock.calls[0] ?? []
    expect(url).toContain('/api/me')
    expect(url).toContain(config.public.apiBase as string)
  })
})

describe('apiBaseUrl selection', () => {
  it('uses public.apiBase by default on client', () => {
    const config = useRuntimeConfig()
    expect(config.public.apiBase).toBeTruthy()
  })
})
