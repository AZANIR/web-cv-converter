import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('useApiRequest', () => {
  it('returns a function', () => {
    const request = useApiRequest()
    expect(typeof request).toBe('function')
  })
})

describe('apiBaseUrl selection', () => {
  it('uses public.apiBase by default on client', () => {
    const config = useRuntimeConfig()
    expect(config.public.apiBase).toBeTruthy()
  })
})
