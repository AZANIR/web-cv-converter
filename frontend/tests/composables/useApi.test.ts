import { describe, it, expect } from 'vitest'
import { useApiRequest } from '../../composables/useApi'

describe('useApiRequest', () => {
  it('exports a function', () => {
    expect(typeof useApiRequest).toBe('function')
  })
})
