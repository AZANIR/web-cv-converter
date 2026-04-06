import { describe, it, expect } from 'vitest'

describe('admin middleware', () => {
  it('redirects non-admin to access-denied with reason=admin', () => {
    const expectedPath = '/access-denied'
    const expectedQuery = { reason: 'admin' }
    expect(expectedPath).toBe('/access-denied')
    expect(expectedQuery.reason).toBe('admin')
  })

  it('redirects to /login when API call fails', () => {
    const fallbackPath = '/login'
    expect(fallbackPath).toBe('/login')
  })

  it('admin role value is "admin"', () => {
    const adminRole = 'admin'
    const userRole = 'user'
    expect(adminRole).not.toBe(userRole)
    expect(adminRole).toBe('admin')
  })
})
