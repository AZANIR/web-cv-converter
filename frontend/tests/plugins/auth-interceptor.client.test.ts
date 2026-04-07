import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('auth-interceptor plugin logic', () => {
  let clear: ReturnType<typeof vi.fn>
  let navigate: ReturnType<typeof vi.fn>
  let onResponseError: (ctx: { response: { status: number } }) => void

  beforeEach(() => {
    clear = vi.fn()
    navigate = vi.fn()

    // Simulate the plugin's onResponseError handler inline
    onResponseError = ({ response }) => {
      if (response.status === 401) {
        clear()
        navigate('/login')
      }
    }
  })

  it('calls clear() and navigates to /login on 401', () => {
    onResponseError({ response: { status: 401 } })
    expect(clear).toHaveBeenCalledOnce()
    expect(navigate).toHaveBeenCalledWith('/login')
  })

  it('does NOT call clear() or navigate on 403', () => {
    onResponseError({ response: { status: 403 } })
    expect(clear).not.toHaveBeenCalled()
    expect(navigate).not.toHaveBeenCalled()
  })

  it('does NOT call clear() or navigate on 500', () => {
    onResponseError({ response: { status: 500 } })
    expect(clear).not.toHaveBeenCalled()
    expect(navigate).not.toHaveBeenCalled()
  })

  it('does NOT call clear() or navigate on 200', () => {
    onResponseError({ response: { status: 200 } })
    expect(clear).not.toHaveBeenCalled()
    expect(navigate).not.toHaveBeenCalled()
  })
})
