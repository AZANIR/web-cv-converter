function apiBaseUrl(config: ReturnType<typeof useRuntimeConfig>): string {
  const serverOnly = config.apiBaseServer as string
  if (import.meta.server && serverOnly) {
    return serverOnly
  }
  return config.public.apiBase as string
}

export function useApiRequest() {
  const config = useRuntimeConfig()
  const { session } = useUserSession()

  return async <T = unknown>(path: string, options: Record<string, unknown> = {}): Promise<T> => {
    const token = session.value?.accessToken as string | undefined
    const idToken = session.value?.idToken as string | undefined
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> | undefined),
    }
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
    if (idToken) {
      headers['X-Auth0-ID-Token'] = idToken
    }
    return $fetch<T>(`${apiBaseUrl(config)}${path}`, {
      ...options,
      headers,
    } as Parameters<typeof $fetch>[1])
  }
}
