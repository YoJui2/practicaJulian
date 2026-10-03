import { describe, expect, it } from 'vitest'
import {
  optionsToHide,
  STARTING_WILDCARDS,
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

  it('arranca con un comodin de cada tipo', () => {
    expect(STARTING_WILDCARDS).toEqual(WILDCARDS.map((wildcard) => wildcard.id))
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