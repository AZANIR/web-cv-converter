import { describe, it, expect, vi } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

const { mockSession } = vi.hoisted(() => ({
  mockSession: { value: {} as Record<string, unknown> },
}))

mockNuxtImport('useUserSession', () => () => ({
  session: mockSession,
  loggedIn: { value: true },
  user: { value: null },
  fetch: vi.fn(),
  clear: vi.fn(),
}))

describe('useAuthApiHeaders', () => {
  it('returns empty headers when no tokens', () => {
    mockSession.value = {}
    const headers = useAuthApiHeaders()
    expect(headers).toEqual({})
  })

  it('returns Authorization header when accessToken present', () => {
    mockSession.value = { accessToken: 'my-access-token' }
    const headers = useAuthApiHeaders()
    expect(headers.Authorization).toBe('Bearer my-access-token')
    expect(headers['X-Auth0-ID-Token']).toBeUndefined()
  })

  it('returns both headers when both tokens present', () => {
    mockSession.value = { accessToken: 'at', idToken: 'idt' }
    const headers = useAuthApiHeaders()
    expect(headers.Authorization).toBe('Bearer at')
    expect(headers['X-Auth0-ID-Token']).toBe('idt')
  })

  it('returns only ID token header when no access token', () => {
    mockSession.value = { idToken: 'idt-only' }
    const headers = useAuthApiHeaders()
    expect(headers.Authorization).toBeUndefined()
    expect(headers['X-Auth0-ID-Token']).toBe('idt-only')
  })
})
