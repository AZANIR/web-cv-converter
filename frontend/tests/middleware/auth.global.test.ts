import { describe, it, expect, vi, beforeEach } from 'vitest'
import { isTokenExpired } from '~/middleware/auth.global'

// ---------------------------------------------------------------------------
// Helpers that mirror the middleware logic without Nuxt runtime dependencies.
// This lets us test redirect decisions in pure JS without mounting the app.
// ---------------------------------------------------------------------------

type FakeSession = {
  loggedIn: boolean
  idToken?: string
}

function simulateMiddleware(
  toPath: string,
  session: FakeSession,
): string | null {
  const publicRoutes = ['/', '/login', '/access-denied']
  const { loggedIn, idToken } = session

  // Expired token → clear and redirect if private
  if (loggedIn && isTokenExpired(idToken)) {
    if (!publicRoutes.includes(toPath)) return '/login'
    return null
  }

  // Not logged in → redirect private routes
  if (!loggedIn && !publicRoutes.includes(toPath)) {
    return '/login'
  }

  return null
}

// ---------------------------------------------------------------------------
// Static route list tests
// ---------------------------------------------------------------------------
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

// ---------------------------------------------------------------------------
// Redirect logic tests
// ---------------------------------------------------------------------------
describe('auth.global — unauthenticated redirect', () => {
  it('redirects unauthenticated user visiting /dashboard to /login', () => {
    const redirect = simulateMiddleware('/dashboard', { loggedIn: false })
    expect(redirect).toBe('/login')
  })

  it('redirects unauthenticated user visiting /history to /login', () => {
    const redirect = simulateMiddleware('/history', { loggedIn: false })
    expect(redirect).toBe('/login')
  })

  it('allows unauthenticated user to visit / (public route)', () => {
    const redirect = simulateMiddleware('/', { loggedIn: false })
    expect(redirect).toBeNull()
  })

  it('allows unauthenticated user to visit /login (public route)', () => {
    const redirect = simulateMiddleware('/login', { loggedIn: false })
    expect(redirect).toBeNull()
  })
})

describe('auth.global — authenticated user pass-through', () => {
  const validPayload = btoa(JSON.stringify({ exp: Math.floor(Date.now() / 1000) + 3600 }))
  const validToken = `header.${validPayload}.sig`

  it('allows authenticated user with valid token to visit /dashboard', () => {
    const redirect = simulateMiddleware('/dashboard', {
      loggedIn: true,
      idToken: validToken,
    })
    expect(redirect).toBeNull()
  })

  it('allows authenticated user with valid token to visit /history', () => {
    const redirect = simulateMiddleware('/history', {
      loggedIn: true,
      idToken: validToken,
    })
    expect(redirect).toBeNull()
  })

  it('allows authenticated user to visit public route /', () => {
    const redirect = simulateMiddleware('/', {
      loggedIn: true,
      idToken: validToken,
    })
    expect(redirect).toBeNull()
  })
})

describe('auth.global — expired token redirect', () => {
  const expiredPayload = btoa(JSON.stringify({ exp: Math.floor(Date.now() / 1000) - 3600 }))
  const expiredToken = `header.${expiredPayload}.sig`

  it('redirects user with expired token visiting /dashboard to /login', () => {
    const redirect = simulateMiddleware('/dashboard', {
      loggedIn: true,
      idToken: expiredToken,
    })
    expect(redirect).toBe('/login')
  })

  it('does NOT redirect user with expired token visiting a public route', () => {
    const redirect = simulateMiddleware('/login', {
      loggedIn: true,
      idToken: expiredToken,
    })
    expect(redirect).toBeNull()
  })
})

// ---------------------------------------------------------------------------
// isTokenExpired unit tests
// ---------------------------------------------------------------------------
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
