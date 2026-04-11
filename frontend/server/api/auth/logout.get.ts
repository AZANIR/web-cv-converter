import { sendRedirect } from 'h3'
import { clearUserSession } from '#auth-utils'

export default defineEventHandler(async (event) => {
  await clearUserSession(event)
  return sendRedirect(event, '/login')
})
