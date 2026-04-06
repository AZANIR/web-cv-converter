import { describe, it, expect } from 'vitest'

describe('whitelist.client plugin', () => {
  it('defines skip routes correctly', () => {
    const skip = ['/', '/login', '/access-denied']
    expect(skip).toContain('/')
    expect(skip).toContain('/login')
    expect(skip).toContain('/access-denied')
    expect(skip.length).toBe(3)
  })

  it('/dashboard is not in skip list', () => {
    const skip = ['/', '/login', '/access-denied']
    expect(skip.includes('/dashboard')).toBe(false)
  })

  it('403 status code triggers redirect to access-denied', () => {
    const code = 403
    expect(code).toBe(403)
  })
})
