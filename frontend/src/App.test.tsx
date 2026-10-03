import { fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

function mockQuestionResponse(fetchMock: ReturnType<typeof vi.fn>) {
  fetchMock.mockImplementation((url: string) => {
    const questionId = Number(url.split('/').at(-1))

    return Promise.resolve({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue({
        id: questionId,
        question: '¿Cuál es la capital de Argentina?',
        answer: 'Buenos Aires',
        category: 'Geografía',
        source: null,
        options: ['Buenos Aires', 'Rosario', 'Córdoba', 'Mendoza'],
        lang: 'es',
      }),
    })
  })
}

async function spinWheel(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole('button', { name: 'Girar la ruleta' }))
  fireEvent.transitionEnd(screen.getByTestId('wheel-disc'), {
    propertyName: 'transform',
  })
}

const WILDCARD_NAMES = {
  podar: 'Podar',
  chivazo: 'Chivazo',
  segundo: 'Segundo intento',
  doblar: 'Puntos x2',
} as const

type WildcardKey = keyof typeof WILDCARD_NAMES

function wildcardButton(key: WildcardKey) {
  return screen.getByRole('button', {
    name: new RegExp(`^${WILDCARD_NAMES[key]}\\.`),
  })
}

function wildcardAvailability(key: WildcardKey) {
  return wildcardButton(key).getAttribute('aria-label') ?? ''
}

async function startRound(user: ReturnType<typeof userEvent.setup>) {
  await spinWheel(user)
  await screen.findByRole('heading', {
    name: '¿Cuál es la capital de Argentina?',
  })
}

async function answerCorrectly(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole('button', { name: 'Buenos Aires' }))
  await screen.findByText('¡Correcto!')
  await user.click(screen.getByRole('button', { name: 'Siguiente jugador' }))
}

describe('trivia game', () => {
  it('loads a question and awards ten points for a correct answer', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    expect(
      screen.queryByRole('img', { name: 'Personaje del juego' }),
    ).not.toBeInTheDocument()
    await spinWheel(user)

    expect(
      await screen.findByRole('heading', {
        name: '¿Cuál es la capital de Argentina?',
      }),
    ).toBeInTheDocument()

    await user.click(
      screen.getByRole('button', { name: 'Buenos Aires' }),
    )

    expect(await screen.findByText('¡Correcto!')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('Siguiente jugador')).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledOnce()
  })

  it('shows that the question was translated automatically', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await spinWheel(user)

    expect(
      await screen.findByText('Traducida automáticamente (es)'),
    ).toBeInTheDocument()
  })

  it('hides the translation notice when the API does not report a language', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn().mockImplementation((url: string) =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({
          id: Number(url.split('/').at(-1)),
          question: '¿Cuál es la capital de Argentina?',
          answer: 'Buenos Aires',
          category: 'Geografía',
          source: null,
          options: ['Buenos Aires', 'Rosario', 'Córdoba', 'Mendoza'],
        }),
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await spinWheel(user)

    expect(
      await screen.findByRole('heading', {
        name: '¿Cuál es la capital de Argentina?',
      }),
    ).toBeInTheDocument()
    expect(
      screen.queryByText(/Traducida automáticamente/),
    ).not.toBeInTheDocument()
  })

  it('retries the same question after an API connection error', async () => {
    const user = userEvent.setup()
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('connection refused'))
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await spinWheel(user)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'No se pudo conectar con la API',
    )
    await user.click(
      screen.getByRole('button', { name: /Reintentar pregunta/ }),
    )

    expect(
      await screen.findByRole('heading', {
        name: '¿Cuál es la capital de Argentina?',
      }),
    ).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock.mock.calls[0][0]).toBe(fetchMock.mock.calls[1][0])
  })

  it('opens the avatar window and applies the chosen avatar', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

    await user.click(
      screen.getByRole('button', { name: 'Elegí el avatar de Jugador 2' }),
    )

    const window = screen.getByRole('dialog', {
      name: 'Elegí el avatar de Jugador 2',
    })
    expect(within(window).getAllByRole('button', { name: /^Avatar / })).toHaveLength(8)
    expect(
      within(window).getByRole('button', {
        name: 'Avatar verde con gorra. Equipado',
      }),
    ).toHaveAttribute('aria-pressed', 'true')

    await user.click(
      within(window).getByRole('button', { name: 'Avatar turquesa' }),
    )

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

    await user.click(
      screen.getByRole('button', { name: 'Elegí el avatar de Jugador 2' }),
    )

    const reopened = screen.getByRole('dialog')
    expect(
      within(reopened).getByRole('button', {
        name: 'Avatar turquesa. Equipado',
      }),
    ).toHaveAttribute('aria-pressed', 'true')
    expect(
      within(reopened).getByRole('button', { name: 'Avatar verde con gorra' }),
    ).toHaveAttribute('aria-pressed', 'false')
  })

  it('closes the avatar window without choosing', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)

    await user.click(
      screen.getByRole('button', { name: 'Elegí el avatar de Jugador 1' }),
    )
    await user.click(screen.getByRole('button', { name: 'Cerrar' }))

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

    await user.click(
      screen.getByRole('button', { name: 'Elegí el avatar de Jugador 1' }),
    )

    expect(
      within(screen.getByRole('dialog')).getByRole('button', {
        name: 'Avatar cereza. Equipado',
      }),
    ).toHaveAttribute('aria-pressed', 'true')
  })

  it('shows the six canonical categories as the wheel sectors', () => {
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)

    expect(screen.getByTestId('wheel-disc')).toHaveAccessibleName(
      'Ruleta con 6 categorías',
    )

    expect(screen.getByText('🏛️')).toBeInTheDocument()
    expect(screen.getByText('⚽')).toBeInTheDocument()
    expect(screen.getByText('🌍')).toBeInTheDocument()
    expect(screen.getByText('🎨')).toBeInTheDocument()
    expect(screen.getByText('🔬')).toBeInTheDocument()
    expect(screen.getByText('🎬')).toBeInTheDocument()
  })

  it('keeps custom names, accepts a wrong answer and changes turns', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    const playerNames = screen.getAllByLabelText('Nombre')
    await user.clear(playerNames[0])
    await user.type(playerNames[0], 'Ana')
    await user.clear(playerNames[1])
    await user.type(playerNames[1], 'Beto')

    expect(
      screen.getByText('Turno de Ana. Podés girar la ruleta.'),
    ).toBeInTheDocument()

    await spinWheel(user)
    await screen.findByRole('heading', {
      name: '¿Cuál es la capital de Argentina?',
    })
    await user.click(screen.getByRole('button', { name: 'Córdoba' }))

    expect(await screen.findByText('No es correcto')).toBeInTheDocument()
    expect(screen.getByText(/Tu respuesta:/)).toHaveTextContent(
      'Tu respuesta: Córdoba',
    )
    expect(screen.getByText('Buenos Aires')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Siguiente jugador' }))
    expect(
      screen.getByText('Turno de Beto. Podés girar la ruleta.'),
    ).toBeInTheDocument()
  })

  it('podar deja solo dos opciones y siempre mantiene la correcta', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await spinWheel(user)
    await screen.findByRole('heading', {
      name: '¿Cuál es la capital de Argentina?',
    })

    const options = screen.getByRole('group', { name: 'Opciones de respuesta' })
    expect(within(options).getAllByRole('button')).toHaveLength(4)

    await user.click(wildcardButton('podar'))

    const pruned = within(
      screen.getByRole('group', { name: 'Opciones de respuesta' }),
    )

    expect(pruned.getAllByRole('button')).toHaveLength(2)
    expect(
      pruned.getByRole('button', { name: 'Buenos Aires' }),
    ).toBeInTheDocument()
    expect(wildcardButton('podar')).toBeDisabled()
    expect(wildcardButton('podar')).toHaveTextContent('0/1')
    expect(wildcardAvailability('podar')).toContain('Sin usos disponibles.')
  })

  it('chivazo resuelve la pregunta y suma los puntos', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await spinWheel(user)
    await screen.findByRole('heading', {
      name: '¿Cuál es la capital de Argentina?',
    })

    await user.click(wildcardButton('chivazo'))

    expect(await screen.findByText('¡Correcto!')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(
      screen.queryByRole('group', { name: 'Opciones de respuesta' }),
    ).not.toBeInTheDocument()
  })

  it('segundo intento deja responder otra vez si fallás', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await spinWheel(user)
    await screen.findByRole('heading', {
      name: '¿Cuál es la capital de Argentina?',
    })

    await user.click(wildcardButton('segundo'))

    expect(
      screen.getByText(
        'Turno de Jugador 1. Tenés dos chances: elegí una opción.',
      ),
    ).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Córdoba' }))

    expect(
      screen.getByText('Turno de Jugador 1. Te queda un intento más.'),
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Córdoba' }),
    ).not.toBeInTheDocument()
    expect(
      screen.getByRole('group', { name: 'Opciones de respuesta' }),
    ).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Rosario' }))

    expect(await screen.findByText('No es correcto')).toBeInTheDocument()
  })

  it('segundo intento suma los puntos si acertás al retry', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await spinWheel(user)
    await screen.findByRole('heading', {
      name: '¿Cuál es la capital de Argentina?',
    })

    await user.click(wildcardButton('segundo'))
    await user.click(screen.getByRole('button', { name: 'Córdoba' }))
    await user.click(screen.getByRole('button', { name: 'Buenos Aires' }))

    expect(await screen.findByText('¡Correcto!')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
  })

  it('puntos x2 duplica el premio de la respuesta correcta', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await spinWheel(user)
    await screen.findByRole('heading', {
      name: '¿Cuál es la capital de Argentina?',
    })

    await user.click(wildcardButton('doblar'))

    expect(
      screen.getByText(
        'Turno de Jugador 1. Elegí una opción. La respuesta correcta vale 20 puntos.',
      ),
    ).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Buenos Aires' }))

    expect(await screen.findByText('¡Correcto!')).toBeInTheDocument()
    expect(screen.getByText('20')).toBeInTheDocument()
    expect(screen.getByText(/Sumaste 20 puntos/)).toBeInTheDocument()
  })

  it('no deja usar dos veces el mismo comodin en la misma ronda', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await startRound(user)

    expect(wildcardAvailability('doblar')).toContain(
      'Usos disponibles: 3 de 3.',
    )

    await user.click(wildcardButton('doblar'))

    expect(wildcardButton('doblar')).toBeDisabled()
    expect(wildcardButton('doblar')).toHaveTextContent('2/3')
    expect(wildcardAvailability('doblar')).toContain(
      'Ya lo usaste en esta ronda.',
    )

    await user.click(wildcardButton('doblar'))

    expect(
      screen.getByText(
        'Turno de Jugador 1. Elegí una opción. La respuesta correcta vale 20 puntos.',
      ),
    ).toBeInTheDocument()
  })

  it('permite usar podar y puntos x2 en la misma ronda', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await startRound(user)

    await user.click(wildcardButton('doblar'))
    await user.click(wildcardButton('podar'))

    expect(wildcardButton('doblar')).toBeDisabled()
    expect(wildcardButton('podar')).toBeDisabled()
    expect(
      within(
        screen.getByRole('group', { name: 'Opciones de respuesta' }),
      ).getAllByRole('button'),
    ).toHaveLength(2)
  })

  it('puntos x2 vuelve a estar disponible en la ronda siguiente', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await startRound(user)

    await user.click(wildcardButton('doblar'))
    await answerCorrectly(user)

    await startRound(user)
    expect(
      screen.getByText('Turno de Jugador 2. Podés girar la ruleta.'),
    ).toBeInTheDocument()
    expect(wildcardAvailability('doblar')).toContain(
      'Usos disponibles: 3 de 3.',
    )
    await answerCorrectly(user)

    await startRound(user)
    expect(
      screen.getByText('Turno de Jugador 1. Podés girar la ruleta.'),
    ).toBeInTheDocument()
    expect(wildcardButton('doblar')).toBeEnabled()
    expect(wildcardButton('doblar')).toHaveTextContent('2/3')
    expect(wildcardAvailability('doblar')).toContain(
      'Usos disponibles: 2 de 3.',
    )
  })

  it('los comodines de un uso no vuelven para el mismo jugador', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn()
    mockQuestionResponse(fetchMock)
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await startRound(user)

    await user.click(wildcardButton('chivazo'))
    await screen.findByText('¡Correcto!')
    await user.click(screen.getByRole('button', { name: 'Siguiente jugador' }))

    await startRound(user)
    expect(wildcardButton('chivazo')).toBeEnabled()
    expect(wildcardButton('chivazo')).toHaveTextContent('1/1')

    await answerCorrectly(user)

    expect(
      screen.getByText('Turno de Jugador 1. Podés girar la ruleta.'),
    ).toBeInTheDocument()

    await startRound(user)

    expect(wildcardButton('chivazo')).toBeDisabled()
    expect(wildcardButton('chivazo')).toHaveTextContent('0/1')
    expect(wildcardAvailability('chivazo')).toContain('Sin usos disponibles.')
    expect(wildcardButton('podar')).toBeEnabled()
  })
})
