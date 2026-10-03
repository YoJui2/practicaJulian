export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
).replace(/\/+$/, '')

export interface WheelCategory {
  name: string
  label: string
  emoji: string
  color: string
}

export interface WheelCategorySeed extends WheelCategory {
  questionIds: readonly number[]
}

/**
 * Espejo de `CATEGORIES` en `app/categories.py`.
 * `name` es el valor contra el que se consulta
 * `GET /questions/category/{name}`; `emoji` y `color` son presentación.
 *
 * `questionIds` es un reparto PROVISIONAL: hoy la tabla `categorizations` está
 * vacía, así que no hay forma de saber a qué categoría pertenece cada pregunta.
 * El reparto es una suposición para poder probar el juego y se reemplaza por los
 * datos de la API apenas se corra `poetry run python -m app.categorize`.
 */
export const WHEEL_CATEGORIES: readonly WheelCategorySeed[] = [
  {
    name: 'historia',
    label: 'Historia',
    emoji: '🏛️',
    color: '#f4c542',
    questionIds: [1, 2],
  },
  {
    name: 'deportes',
    label: 'Deportes',
    emoji: '⚽',
    color: '#e94b4b',
    questionIds: [3, 4],
  },
  {
    name: 'geografia',
    label: 'Geografía',
    emoji: '🌍',
    color: '#3d8edb',
    questionIds: [5, 6],
  },
  {
    name: 'arte',
    label: 'Arte',
    emoji: '🎨',
    color: '#f08b3e',
    questionIds: [7, 8],
  },
  {
    name: 'ciencia',
    label: 'Ciencia',
    emoji: '🔬',
    color: '#4ccf64',
    questionIds: [9, 10],
  },
  {
    name: 'entretenimiento',
    label: 'Entretenimiento',
    emoji: '🎬',
    color: '#9b4de8',
    questionIds: [11, 12],
  },
]

export const POINTS_PER_CORRECT_ANSWER = 10

export const WHEEL_DRIFT_TURNS = 8
export const WHEEL_DRIFT_MS = 12000
export const WHEEL_SETTLE_MS = 1400
export const WHEEL_REVEAL_MS = 2500
export const WHEEL_MIN_SETTLE_DEGREES = 24