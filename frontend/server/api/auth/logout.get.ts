import { sendRedirect } from 'h3'
import { clearUserSession } from '../../../node_modules/nuxt-auth-utils/dist/runtime/server/utils/session.js'

export default defineEventHandler(async (event) => {
  await clearUserSession(event)
  return sendRedirect(event, '/login')
})
