import { describe, expect, it } from 'vitest'
import {
  canUseWildcard,
  createWildcardUses,
  maxUsesOf,
  optionsToHide,
  spendWildcardUse,
  STARTING_WILDCARD_USES,
  usesLeft,
  WILDCARDS,
} from './wildcards'

const FOUR_OPTIONS = ['Buenos Aires', 'Rosario', 'Cordoba', 'Mendoza']

describe('WILDCARDS', () => {
  it('ofrece cuatro comodines con ids únicos', () => {
    expect(WILDCARDS).toHaveLength(4)
    expect(new Set(WILDCARDS.map((wildcard) => wildcard.id)).size).toBe(4)
  })

  it('incluye podar, chivazo, segundo intento y puntos x2', () => {
    expect(WILDCARDS.map((wildcard) => wildcard.id)).toEqual([
      'podar',
      'chivazo',
      'segundo',
      'doblar',
    ])
  })

  it('limita podar, chivazo y segundo intento a un uso', () => {
    expect(maxUsesOf('podar')).toBe(1)
    expect(maxUsesOf('chivazo')).toBe(1)
    expect(maxUsesOf('segundo')).toBe(1)
  })

  it('limita puntos x2 a tres usos', () => {
    expect(maxUsesOf('doblar')).toBe(3)
  })
})

describe('createWildcardUses', () => {
  it('arranca con la cantidad maxima de cada comodin', () => {
    expect(createWildcardUses()).toEqual({
      podar: 1,
      chivazo: 1,
      segundo: 1,
      doblar: 3,
    })
  })

  it('no comparte el mismo objeto entre jugadores', () => {
    const first = createWildcardUses()
    const second = createWildcardUses()

    first.podar = 0

    expect(second.podar).toBe(1)
    expect(STARTING_WILDCARD_USES.podar).toBe(1)
  })
})

describe('usesLeft', () => {
  it('devuelve los usos disponibles', () => {
    const uses = { podar: 1, chivazo: 1, segundo: 1, doblar: 2 }

    expect(usesLeft(uses, 'doblar')).toBe(2)
  })

  it('nunca devuelve un numero negativo', () => {
    const uses = { podar: 0, chivazo: 0, segundo: 0, doblar: 0 }

    expect(usesLeft(uses, 'doblar')).toBe(0)
  })
})

describe('spendWildcardUse', () => {
  it('descuenta un uso', () => {
    const uses = { podar: 1, chivazo: 1, segundo: 1, doblar: 3 }

    expect(spendWildcardUse(uses, 'doblar')).toEqual({
      podar: 1,
      chivazo: 1,
      segundo: 1,
      doblar: 2,
    })
  })

  it('deja el resto de los comodines intactos', () => {
    const uses = { podar: 1, chivazo: 1, segundo: 1, doblar: 3 }

    expect(spendWildcardUse(uses, 'podar')).toEqual({
      podar: 0,
      chivazo: 1,
      segundo: 1,
      doblar: 3,
    })
    expect(uses.podar).toBe(1)
  })

  it('no descuenta cuando ya no quedan usos', () => {
    const spent = { podar: 0, chivazo: 0, segundo: 0, doblar: 0 }

    expect(spendWildcardUse(spent, 'podar')).toBe(spent)
  })
})

describe('canUseWildcard', () => {
  const full = { podar: 1, chivazo: 1, segundo: 1, doblar: 3 }

  it('permite usar un comodin con usos y sin usar en la ronda', () => {
    expect(canUseWildcard(full, [], 'doblar')).toBe(true)
  })

  it('rechaza un comodin sin usos disponibles', () => {
    expect(canUseWildcard({ ...full, podar: 0 }, [], 'podar')).toBe(false)
  })

  it('rechaza el mismo comodin dos veces en la misma ronda', () => {
    expect(canUseWildcard(full, ['doblar'], 'doblar')).toBe(false)
  })

  it('permite volver a usarlo en la ronda siguiente', () => {
    expect(canUseWildcard({ ...full, doblar: 1 }, [], 'doblar')).toBe(true)
  })

  it('permite combinar comodines distintos en la misma ronda', () => {
    expect(canUseWildcard(full, ['doblar'], 'podar')).toBe(true)
  })
})

describe('optionsToHide', () => {
  it('deja solo dos opciones', () => {
    const hidden = optionsToHide(FOUR_OPTIONS, 'Buenos Aires')
    const remaining = FOUR_OPTIONS.filter((option) => !hidden.includes(option))

    expect(remaining).toHaveLength(2)
  })

  it('nunca oculta la respuesta correcta', () => {
    for (let attempt = 0; attempt < 30; attempt += 1) {
      expect(optionsToHide(FOUR_OPTIONS, 'Cordoba')).not.toContain('Cordoba')
    }
  })

  it('solo oculta respuestas falsas', () => {
    for (let attempt = 0; attempt < 30; attempt += 1) {
      const hidden = optionsToHide(FOUR_OPTIONS, 'Rosario')

      expect(hidden).toHaveLength(2)
      expect(hidden).not.toContain('Rosario')
    }
  })

  it('no oculta nada cuando solo hay dos opciones', () => {
    expect(optionsToHide(['Rosario', 'Cordoba'], 'Cordoba')).toEqual([])
  })

  it('deja siempre la respuesta correcta disponible', () => {
    for (let attempt = 0; attempt < 30; attempt += 1) {
      const hidden = optionsToHide(FOUR_OPTIONS, 'Mendoza')
      const remaining = FOUR_OPTIONS.filter((option) => !hidden.includes(option))

      expect(remaining).toContain('Mendoza')
    }
  })

  it('compara ignorando mayusculas, acentos y espacios', () => {
    const options = ['Córdoba', 'Rosario', 'Mendoza']
    const hidden = optionsToHide(options, '  cordoba ')

    expect(hidden).toHaveLength(1)
    expect(hidden).not.toContain('Córdoba')
  })

  it('no lanza con una sola opcion', () => {
    expect(optionsToHide(['Rosario'], 'Rosario')).toEqual([])
  })
})