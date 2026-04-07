export function isTokenExpired(token?: string): boolean {
  if (!token) return true
  try {
    const [, payload] = token.split('.')
    const { exp } = JSON.parse(atob(payload))
    if (typeof exp !== 'number') return true
    return Date.now() / 1000 > exp
  }
  catch {
    return true
  }
}

export default defineNuxtRouteMiddleware(async (to) => {
  const publicRoutes = ['/', '/login', '/access-denied']
  const { loggedIn, fetch, session, clear } = useUserSession()
  await fetch()

  if (loggedIn.value && isTokenExpired(session.value?.idToken as string)) {
    await clear()
    if (!publicRoutes.includes(to.path)) return navigateTo('/login')
  }

  if (!loggedIn.value && !publicRoutes.includes(to.path)) {
    return navigateTo('/login')
  }
})
