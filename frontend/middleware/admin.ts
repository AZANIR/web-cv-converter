export default defineNuxtRouteMiddleware(async () => {
  const { fetch } = useUserSession()
  await fetch()
  const api = useApiRequest()
  try {
    const me = await api<{ role?: string }>('/api/me')
    if (me?.role !== 'admin') {
      return navigateTo({ path: '/access-denied', query: { reason: 'admin' } })
    }
  }
  catch {
    return navigateTo('/login')
  }
})
