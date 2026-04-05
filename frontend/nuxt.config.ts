export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@nuxt/fonts', 'nuxt-auth-utils'],
  app: {
    head: {
      title: 'CV Converter',
      meta: [
        { name: 'description', content: 'Convert Markdown CVs to PDF with AI' },
      ],
    },
  },
  css: ['~/assets/css/main.css'],
  fonts: {
    families: [{ name: 'Inter', provider: 'google' }],
  },
  runtimeConfig: {
    /** Server-side API base (e.g. http://backend:8000 in Docker). Empty = use public.apiBase everywhere. */
    apiBaseServer: process.env.NUXT_API_BASE_SERVER || '',
    session: {
      password: process.env.NUXT_SESSION_PASSWORD || '',
      maxAge: 60 * 60 * 24 * 7,
    },
    oauth: {
      auth0: {
        domain: process.env.NUXT_OAUTH_AUTH0_DOMAIN || '',
        clientId: process.env.NUXT_OAUTH_AUTH0_CLIENT_ID || '',
        clientSecret: process.env.NUXT_OAUTH_AUTH0_CLIENT_SECRET || '',
        audience: process.env.NUXT_OAUTH_AUTH0_AUDIENCE || '',
      },
    },
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000',
    },
  },
  devtools: { enabled: true },
  compatibilityDate: '2024-11-01',
})
