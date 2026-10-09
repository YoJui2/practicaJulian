import { afterEach, describe, expect, it, vi } from 'vitest'
import { getQuestion, getRandomQuestion, QuestionsApiError } from './questions'

function response(body: unknown, ok = true, status = 200) {
  return {
    ok,
    status,
    json: vi.fn().mockResolvedValue(body),
  } as unknown as Response
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('getQuestion', () => {
  it('returns a valid question', async () => {
    const question = {
      id: 7,
      question: '¿Cuál es la capital de Argentina?',
      answer: 'Buenos Aires',
      category: 'Geografía',
      source: null,
      options: ['Buenos Aires', 'Rosario', 'Córdoba', 'Mendoza'],
    }
    const fetchMock = vi.fn().mockResolvedValue(response(question))
    vi.stubGlobal('fetch', fetchMock)

    await expect(getQuestion(7)).resolves.toEqual(question)
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/questions/7',
      expect.objectContaining({ headers: { Accept: 'application/json' } }),
    )
  })

  it('accepts a translated question that reports its language', async () => {
    const question = {
      id: 7,
      question: '¿Cuál es la capital de Argentina?',
      answer: 'Buenos Aires',
      category: 'Geografía',
      source: null,
      options: ['Buenos Aires', 'Rosario', 'Córdoba', 'Mendoza'],
      lang: 'es',
    }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response(question)))

    await expect(getQuestion(7)).resolves.toEqual(question)
  })

  it('rejects a question with an invalid language', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        response({
          id: 7,
          question: '¿Cuál es la capital de Argentina?',
          answer: 'Buenos Aires',
          category: 'Geografía',
          source: null,
          options: ['Buenos Aires', 'Rosario', 'Córdoba', 'Mendoza'],
          lang: 42,
        }),
      ),
    )

    await expect(getQuestion(7)).rejects.toThrow('formato inesperado')
  })

  it('turns API errors into useful messages', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValue(
          response({ error: 'Pregunta no encontrada' }, false, 404),
        ),
    )

    await expect(getQuestion(99)).rejects.toEqual(
      new QuestionsApiError('Pregunta no encontrada'),
    )
  })

  it('rejects a successful response with an error body', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(response({ error: 'Pregunta no encontrada' })),
    )

    await expect(getQuestion(99)).rejects.toThrow(
      'La pregunta solicitada no existe',
    )
  })

  it('rejects malformed questions', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(response({ id: 7, question: 'Incompleta' })),
    )

    await expect(getQuestion(7)).rejects.toThrow('formato inesperado')
  })

  it('rejects a question without answer options', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        response({
          id: 7,
          question: '¿Cuál es la capital de Argentina?',
          answer: 'Buenos Aires',
          category: 'Geografía',
          source: null,
          options: ['Rosario', 'Córdoba', 'Mendoza'],
        }),
      ),
    )

    await expect(getQuestion(7)).rejects.toThrow('formato inesperado')
  })

  it('reports connection failures', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('offline')))

    await expect(getQuestion(1)).rejects.toThrow(
      'No se pudo conectar con la API',
    )
  })

  it('reports invalid JSON', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockRejectedValue(new SyntaxError('invalid json')),
      } as unknown as Response),
    )

    await expect(getQuestion(1)).rejects.toThrow('respuesta inválida')
  })
})

describe('getRandomQuestion', () => {
  it('requests a question by category and validates the returned shape', async () => {
    const question = {
      id: 49_594,
      question: '¿Quién ganó?',
      answer: 'Equipo A',
      category: 'deportes',
      source: 'OpenTriviaQA: sports',
      options: ['Equipo A', 'Equipo B'],
      lang: 'es',
    }
    const fetchMock = vi.fn().mockResolvedValue(response(question))
    vi.stubGlobal('fetch', fetchMock)

    await expect(getRandomQuestion('deportes')).resolves.toEqual(question)
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/questions/random/deportes',
      expect.objectContaining({ headers: { Accept: 'application/json' } }),
    )
  })

  it('encodes the category and reports a missing category', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        response({ detail: 'No hay preguntas disponibles.' }, false, 404),
      )
    vi.stubGlobal('fetch', fetchMock)

    await expect(getRandomQuestion('arte y cultura')).rejects.toEqual(
      new QuestionsApiError('No hay preguntas disponibles.'),
    )
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/questions/random/arte%20y%20cultura',
      expect.objectContaining({ headers: { Accept: 'application/json' } }),
    )
  })
})
