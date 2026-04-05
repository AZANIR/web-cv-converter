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
    await setUserSession(event, {
      user: {
        sub: user.sub,
        email: user.email,
        name: user.name,
        picture: user.picture,
      },
      accessToken: tokens.access_token,
      idToken: (tokens as { id_token?: string }).id_token,
      loggedInAt: Date.now(),
    })
    return sendRedirect(event, '/dashboard')
  },
  async onError(event, error) {
    console.error('Auth0 OAuth error:', error)
    return sendRedirect(event, '/login?error=auth_failed')
  },
})
