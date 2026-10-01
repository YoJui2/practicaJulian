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
      within(window).getByRole('button', { name: 'Avatar verde con gorra' }),
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
      within(reopened).getByRole('button', { name: 'Avatar turquesa' }),
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
      within(screen.getByRole('dialog')).getByRole('button', { name: 'Avatar rojo' }),
    ).toHaveAttribute('aria-pressed', 'true')
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
})
