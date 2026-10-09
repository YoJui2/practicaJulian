import { describe, expect, it, vi } from 'vitest'
import { WHEEL_CATEGORIES } from '../config'
import type { WheelSector } from './wheel'
import {
  forwardDelta,
  landingRotation,
  normalizeRotation,
  planSpin,
  settleRotation,
} from './wheel'

vi.mock('./random', () => ({
  randomIndex: vi.fn(() => 0),
}))

const SECTORS: readonly WheelSector[] = [
  { name: 'historia', label: 'Historia', emoji: '🏛️', color: '#f4c542' },
  { name: 'deportes', label: 'Deportes', emoji: '⚽', color: '#e94b4b' },
  { name: 'arte', label: 'Arte', emoji: '🎨', color: '#f08b3e' },
]

describe('normalizeRotation', () => {
  it('normalizes negative and oversized rotations', () => {
    expect(normalizeRotation(-90)).toBe(270)
    expect(normalizeRotation(450)).toBe(90)
    expect(normalizeRotation(360)).toBe(0)
  })
})

describe('forwardDelta', () => {
  it('always moves forward without extra turns', () => {
    expect(forwardDelta(350, 10)).toBe(20)
    expect(forwardDelta(10, 350)).toBe(340)
    expect(forwardDelta(100, 100)).toBe(0)
  })
})

describe('landingRotation', () => {
  it('centers the pointer on the requested sector', () => {
    expect(landingRotation(6, 0)).toBe(330)
    expect(landingRotation(6, 1)).toBe(270)
    expect(landingRotation(6, 5)).toBe(30)
  })

  it('never lands on a boundary between sectors', () => {
    for (let index = 0; index < 6; index += 1) {
      const landing = landingRotation(6, index)

      expect(landing % 60).toBe(30)
    }
  })
})

describe('WHEEL_CATEGORIES', () => {
  it('exposes exactly the six canonical categories in backend order', () => {
    expect(WHEEL_CATEGORIES.map((category) => category.name)).toEqual([
      'historia',
      'deportes',
      'geografia',
      'arte',
      'ciencia',
      'entretenimiento',
    ])
  })

  it('gives every category a unique color', () => {
    const colors = WHEEL_CATEGORIES.map((category) => category.color)

    expect(new Set(colors).size).toBe(WHEEL_CATEGORIES.length)
  })
})

describe('planSpin', () => {
  it('picks a sector for the API to use when choosing a question', () => {
    const plan = planSpin(SECTORS, 42, 5)

    expect(plan.sectorIndex).toBe(0)
    expect(SECTORS[plan.sectorIndex].name).toBe('historia')
  })

  it('requests a forward drift of whole turns', () => {
    expect(planSpin(SECTORS, 42, 5).driftTarget).toBe(42 + 5 * 360)
  })
})

describe('settleRotation', () => {
  it('brakes forward onto the sector center', () => {
    const settle = settleRotation(2880, 330)

    expect(settle).toBe(2880 + 330)
    expect(normalizeRotation(settle)).toBe(330)
  })

  it('adds a full turn when the drift already lands on the center', () => {
    const settle = settleRotation(330, 330)

    expect(settle).toBe(690)
    expect(normalizeRotation(settle)).toBe(330)
  })

  it('always moves far enough to fire a transition', () => {
    expect(normalizeRotation(settleRotation(0, 15))).toBe(15)
    expect(settleRotation(0, 15)).toBe(375)
  })
})
