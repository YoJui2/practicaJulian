import type { WheelCategory } from '../config'
import { WHEEL_MIN_SETTLE_DEGREES } from '../config'
import { randomIndex } from './random'

export type WheelSector = WheelCategory

export interface SpinPlan {
  sectorIndex: number
  driftTarget: number
}

export function normalizeRotation(rotation: number): number {
  return ((rotation % 360) + 360) % 360
}

export function forwardDelta(from: number, to: number): number {
  return normalizeRotation(normalizeRotation(to) - normalizeRotation(from))
}

/**
 * El puntero está en las 12 en punto, así que el sector `sectorIndex`
 * (cuyo centro está en `index * segmentAngle + segmentAngle / 2`) queda
 * arriba cuando el disco rota `360 - centro`.
 */
export function landingRotation(
  sectorCount: number,
  sectorIndex: number,
): number {
  const segmentAngle = 360 / sectorCount

  return normalizeRotation(
    360 - (sectorIndex * segmentAngle + segmentAngle / 2),
  )
}

export function planSpin(
  sectors: readonly WheelSector[],
  currentRotation: number,
  driftTurns: number,
): SpinPlan {
  const sectorIndex = randomIndex(sectors.length)

  return {
    sectorIndex,
    driftTarget: currentRotation + 360 * driftTurns,
  }
}

export function settleRotation(from: number, landing: number): number {
  const delta = forwardDelta(from, landing)

  return from + (delta < WHEEL_MIN_SETTLE_DEGREES ? delta + 360 : delta)
}
