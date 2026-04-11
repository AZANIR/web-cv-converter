export default defineEventHandler(async () => {
  const apiBase = process.env.NUXT_API_BASE_SERVER || process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000'
  try {
    return await $fetch(`${apiBase}/health/full`)
  }
  catch {
    return { status: 'error', db: 'unreachable' }
  }
})
