import { sendRedirect } from 'h3'
// nuxt-auth-utils does not re-export server runtime functions via #auth-utils (types only).
import { clearUserSession } from 'nuxt-auth-utils/dist/runtime/server/utils/session'

export default defineEventHandler(async (event) => {
  await clearUserSession(event)
  return sendRedirect(event, '/login')
})
