export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
).replace(/\/+$/, '')

export interface WheelCategory {
  name: string
  label: string
  emoji: string
  color: string
}

/**
 * Espejo de `CATEGORIES` en `app/categories.py`.
 * `name` se usa para pedir a la API una pregunta aleatoria de esa categoría;
 * `emoji` y `color` son presentación.
 */
export const WHEEL_CATEGORIES: readonly WheelCategory[] = [
  {
    name: 'historia',
    label: 'Historia',
    emoji: '🏛️',
    color: '#f4c542',
  },
  {
    name: 'deportes',
    label: 'Deportes',
    emoji: '⚽',
    color: '#e94b4b',
  },
  {
    name: 'geografia',
    label: 'Geografía',
    emoji: '🌍',
    color: '#3d8edb',
  },
  {
    name: 'arte',
    label: 'Arte',
    emoji: '🎨',
    color: '#f08b3e',
  },
  {
    name: 'ciencia',
    label: 'Ciencia',
    emoji: '🔬',
    color: '#4ccf64',
  },
  {
    name: 'entretenimiento',
    label: 'Entretenimiento',
    emoji: '🎬',
    color: '#9b4de8',
  },
]

export const POINTS_PER_CORRECT_ANSWER = 10

export const WHEEL_DRIFT_TURNS = 8
export const WHEEL_DRIFT_MS = 12000
export const WHEEL_SETTLE_MS = 1400
export const WHEEL_REVEAL_MS = 2500
export const WHEEL_MIN_SETTLE_DEGREES = 24
