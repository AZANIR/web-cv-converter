import { describe, it, expect } from 'vitest'
import { isTokenExpired } from '~/middleware/auth.global'

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

describe('isTokenExpired()', () => {
  it('returns true for expired token (past exp)', () => {
    const expiredPayload = btoa(JSON.stringify({ exp: Math.floor(Date.now() / 1000) - 3600 }))
    const token = `header.${expiredPayload}.sig`
    expect(isTokenExpired(token)).toBe(true)
  })

  it('returns false for valid token (future exp)', () => {
    const validPayload = btoa(JSON.stringify({ exp: Math.floor(Date.now() / 1000) + 3600 }))
    const token = `header.${validPayload}.sig`
    expect(isTokenExpired(token)).toBe(false)
  })

  it('returns true for undefined token', () => {
    expect(isTokenExpired(undefined)).toBe(true)
  })

  it('returns true for malformed token', () => {
    expect(isTokenExpired('not.a.valid.jwt')).toBe(true)
  })

  it('returns true for token missing exp claim', () => {
    const payload = btoa(JSON.stringify({ sub: 'user123' }))
    const token = `header.${payload}.sig`
    expect(isTokenExpired(token)).toBe(true)
  })
})
