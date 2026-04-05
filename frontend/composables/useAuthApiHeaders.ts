/** Headers for FastAPI: Bearer access token + optional ID token (email when API AT omits email). */
export function useAuthApiHeaders(): Record<string, string> {
  const { session } = useUserSession()
  const token = session.value?.accessToken as string | undefined
  const idToken = session.value?.idToken as string | undefined
  const headers: Record<string, string> = {}
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  if (idToken) {
    headers['X-Auth0-ID-Token'] = idToken
  }
  return headers
}
