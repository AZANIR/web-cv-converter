export default defineNuxtRouteMiddleware(async (to) => {
  const publicRoutes = ['/', '/login', '/access-denied']
  const { loggedIn, fetch } = useUserSession()
  await fetch()
  if (!loggedIn.value && !publicRoutes.includes(to.path)) {
    return navigateTo('/login')
  }
})
