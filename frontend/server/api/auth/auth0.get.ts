import { sendRedirect } from 'h3'
import { defineOAuthAuth0EventHandler } from '../../../node_modules/nuxt-auth-utils/dist/runtime/server/lib/oauth/auth0.js'
import { setUserSession } from '../../../node_modules/nuxt-auth-utils/dist/runtime/server/utils/session.js'

export default defineOAuthAuth0EventHandler({
  config: {
    emailRequired: true,
    scope: ['openid', 'profile', 'email', 'offline_access'],
    authorizationParams: {
      connection: process.env.NUXT_OAUTH_AUTH0_CONNECTION || 'google-oauth2',
    },
  },
  async onSuccess(event, { user, tokens }) {
    const apiBase = process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000'
    const headers: Record<string, string> = {
      Authorization: `Bearer ${tokens.access_token}`,
    }
    const idToken = (tokens as { id_token?: string }).id_token
    if (idToken) {
      headers['X-Auth0-ID-Token'] = idToken
    }

    try {
      await $fetch(`${apiBase}/api/me`, { headers })
    }
    catch (e: unknown) {
      const err = e as { status?: number; statusCode?: number }
      const code = err.status ?? err.statusCode
      if (code === 403) {
        return sendRedirect(event, '/access-denied')
      }
      console.error('Whitelist check failed during login:', e)
      return sendRedirect(event, '/access-denied?reason=auth_error')
    }

    await setUserSession(event, {
      user: {
        sub: user.sub,
        email: user.email,
        name: user.name,
        picture: user.picture,
      },
      accessToken: tokens.access_token,
      idToken,
      loggedInAt: Date.now(),
    })
    return sendRedirect(event, '/dashboard')
  },
  async onError(event, error) {
    console.error('Auth0 OAuth error:', error)
    return sendRedirect(event, '/login?error=auth_failed')
  },
})
