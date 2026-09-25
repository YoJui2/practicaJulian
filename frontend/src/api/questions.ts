import { API_BASE_URL } from '../config'

export interface Question {
  id: number
  question: string
  answer: string
  category: string | null
  source: string | null
  options: string[]
  lang?: string
}

export class QuestionsApiError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'QuestionsApiError'
  }
}

function isQuestion(value: unknown, requestedId: number): value is Question {
  if (typeof value !== 'object' || value === null) {
    return false
  }

  const question = value as Record<string, unknown>

  const options = question.options

  return (
    question.id === requestedId &&
    typeof question.question === 'string' &&
    question.question.trim().length > 0 &&
    typeof question.answer === 'string' &&
    question.answer.trim().length > 0 &&
    (question.category === null || typeof question.category === 'string') &&
    (question.source === null || typeof question.source === 'string') &&
    Array.isArray(options) &&
    options.length >= 1 &&
    options.every(
      (option) => typeof option === 'string' && option.trim().length > 0,
    ) &&
    options.includes(question.answer) &&
    (question.lang === undefined || typeof question.lang === 'string')
  )
}

export async function getQuestion(
  questionId: number,
  signal?: AbortSignal,
): Promise<Question> {
  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}/questions/${questionId}`, {
      headers: { Accept: 'application/json' },
      signal,
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }

    throw new QuestionsApiError(
      'No se pudo conectar con la API. Revisá que FastAPI esté corriendo, que VITE_API_BASE_URL apunte al puerto correcto y que el origen de Vite esté permitido por CORS.',
    )
  }

  let body: unknown
  try {
    body = await response.json()
  } catch {
    throw new QuestionsApiError('La API devolvió una respuesta inválida.')
  }

  if (!response.ok) {
    const message =
      typeof body === 'object' &&
      body !== null &&
      typeof (body as Record<string, unknown>).error === 'string'
        ? (body as Record<string, string>).error
        : 'La API no pudo devolver la pregunta.'

    throw new QuestionsApiError(message)
  }

  if (!isQuestion(body, questionId)) {
    throw new QuestionsApiError(
      'La pregunta solicitada no existe o tiene un formato inesperado.',
    )
  }

  return body
}
