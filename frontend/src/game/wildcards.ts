import { normalizeAnswer } from './answer'
import { randomIndex } from './random'

export type WildcardId = 'podar' | 'chivazo' | 'segundo' | 'doblar'

export interface Wildcard {
  id: WildcardId
  name: string
  description: string
}

export const WILDCARDS: readonly Wildcard[] = [
  {
    id: 'podar',
    name: 'Podar',
    description: 'Elimina 2 respuestas falsas.',
  },
  {
    id: 'chivazo',
    name: 'Chivazo',
    description: 'Resuelve la pregunta por vos.',
  },
  {
    id: 'segundo',
    name: 'Segundo intento',
    description: 'Respondés otra vez si fallás.',
  },
  {
    id: 'doblar',
    name: 'Puntos x2',
    description: 'La respuesta correcta vale el doble.',
  },
]

export const STARTING_WILDCARDS: readonly WildcardId[] = WILDCARDS.map(
  (wildcard) => wildcard.id,
)

const MAX_HIDDEN_OPTIONS = 2

export function optionsToHide(
  options: readonly string[],
  answer: string,
): string[] {
  const normalizedAnswer = normalizeAnswer(answer)
  const wrongOptions = options.filter(
    (option) => normalizeAnswer(option) !== normalizedAnswer,
  )
  const hiddenCount = Math.min(
    MAX_HIDDEN_OPTIONS,
    Math.max(0, wrongOptions.length - 1),
  )

  for (let index = wrongOptions.length - 1; index > 0; index -= 1) {
    const swapIndex = randomIndex(index + 1)
    const current = wrongOptions[index]
    wrongOptions[index] = wrongOptions[swapIndex]
    wrongOptions[swapIndex] = current
  }

  return wrongOptions.slice(0, hiddenCount)
}