import { afterEach, describe, expect, it, vi } from 'vitest'
import { randomIndex } from './random'

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('randomIndex', () => {
  it('always returns a valid index', () => {
    for (let attempt = 0; attempt < 100; attempt += 1) {
      const result = randomIndex(12)
      expect(result).toBeGreaterThanOrEqual(0)
      expect(result).toBeLessThan(12)
    }
  })

  it('rejects invalid lengths', () => {
    expect(() => randomIndex(0)).toThrow(RangeError)
    expect(() => randomIndex(1.5)).toThrow(RangeError)
  })

  it('uses Math.random when Web Crypto is unavailable', () => {
    vi.stubGlobal('crypto', undefined)
    vi.spyOn(Math, 'random').mockReturnValue(0.5)

    expect(randomIndex(4)).toBe(2)
  })
})
