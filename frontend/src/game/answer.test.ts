import { describe, expect, it } from 'vitest'
import { normalizeAnswer } from './answer'

describe('normalizeAnswer', () => {
  it('normalizes case, accents and repeated whitespace', () => {
    expect(normalizeAnswer('  BUENOS   Aires  ')).toBe('buenos aires')
    expect(normalizeAnswer('São   PAULO')).toBe('sao paulo')
  })
})
