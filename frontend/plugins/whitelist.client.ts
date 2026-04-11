// Plugin runs before app composables are fully available.
// useApiRequest() depends on useNuxtApp().$apiFetch which may not exist yet.
// Using $fetch with useAuthApiHeaders() directly is intentional here.
export default defineNuxtPlugin(async () => {
  const route = useRoute()
  const skip = ['/', '/login', '/access-denied']
  if (skip.includes(route.path)) {
    return
  }

  const { loggedIn, fetch } = useUserSession()
  await fetch()
  if (!loggedIn.value) {
    return
  }

  const config = useRuntimeConfig()
  const headers = useAuthApiHeaders()
  if (!headers.Authorization) {
    return
  }

  try {
    await $fetch(`${config.public.apiBase}/api/me`, {
      headers,
    })
  }
  catch (e: unknown) {
    const err = e as { status?: number; statusCode?: number }
    const code = err.status ?? err.statusCode
    if (code === 403) {
      await navigateTo('/access-denied')
    }
  }
})
