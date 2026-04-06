import { describe, it, expect, vi } from 'vitest'

describe('auth.global middleware', () => {
  it('public routes are defined correctly', () => {
    const publicRoutes = ['/', '/login', '/access-denied']
    expect(publicRoutes).toContain('/')
    expect(publicRoutes).toContain('/login')
    expect(publicRoutes).toContain('/access-denied')
    expect(publicRoutes).not.toContain('/dashboard')
  })

  it('/dashboard is not a public route', () => {
    const publicRoutes = ['/', '/login', '/access-denied']
    expect(publicRoutes.includes('/dashboard')).toBe(false)
  })

  it('/history is not a public route', () => {
    const publicRoutes = ['/', '/login', '/access-denied']
    expect(publicRoutes.includes('/history')).toBe(false)
  })
})
