import { normalizeAnswer } from './answer'
import { randomIndex } from './random'

export type WildcardId = 'podar' | 'chivazo' | 'segundo' | 'doblar'

export interface Wildcard {
  id: WildcardId
  name: string
  description: string
  maxUses: number
}

export type WildcardUses = Record<WildcardId, number>

export const WILDCARDS: readonly Wildcard[] = [
  {
    id: 'podar',
    name: 'Podar',
    description: 'Elimina 2 respuestas falsas.',
    maxUses: 1,
  },
  {
    id: 'chivazo',
    name: 'Chivazo',
    description: 'Resuelve la pregunta por vos.',
    maxUses: 1,
  },
  {
    id: 'segundo',
    name: 'Segundo intento',
    description: 'Respondés otra vez si fallás.',
    maxUses: 1,
  },
  {
    id: 'doblar',
    name: 'Puntos x2',
    description: 'La respuesta correcta vale el doble.',
    maxUses: 3,
  },
]

export const STARTING_WILDCARD_USES: WildcardUses = WILDCARDS.reduce(
  (uses, wildcard) => ({ ...uses, [wildcard.id]: wildcard.maxUses }),
  {} as WildcardUses,
)

export function createWildcardUses(): WildcardUses {
  return { ...STARTING_WILDCARD_USES }
}

export function usesLeft(uses: WildcardUses, id: WildcardId): number {
  return Math.max(0, uses[id] ?? 0)
}

export function maxUsesOf(id: WildcardId): number {
  return WILDCARDS.find((wildcard) => wildcard.id === id)?.maxUses ?? 0
}

export function canUseWildcard(
  uses: WildcardUses,
  usedThisRound: readonly WildcardId[],
  id: WildcardId,
): boolean {
  return usesLeft(uses, id) > 0 && !usedThisRound.includes(id)
}

export function spendWildcardUse(
  uses: WildcardUses,
  id: WildcardId,
): WildcardUses {
  const remaining = usesLeft(uses, id)

  if (remaining === 0) {
    return uses
  }

  return { ...uses, [id]: remaining - 1 }
}

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