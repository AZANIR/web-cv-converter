export default defineNuxtPlugin(() => {
  const { clear } = useUserSession()

  const apiFetch = $fetch.create({
    onResponseError({ response }) {
      if (response.status === 401) {
        clear()
        navigateTo('/login')
      }
    },
  })

  return {
    provide: {
      apiFetch,
    },
  }
})
