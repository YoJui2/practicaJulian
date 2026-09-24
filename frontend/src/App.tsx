import { useMemo, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { getQuestion, QuestionsApiError } from './api/questions'
import type { Question } from './api/questions'
import { Wheel } from './components/Wheel'
import { POINTS_PER_CORRECT_ANSWER, WHEEL_QUESTION_IDS } from './config'
import { normalizeAnswer } from './game/answer'
import { randomIndex } from './game/random'
import styles from './App.module.css'

type PlayerId = 'playerOne' | 'playerTwo'
type GamePhase =
  'ready' | 'spinning' | 'loading' | 'answering' | 'feedback' | 'error'

interface Player {
  name: string
  score: number
}

interface Feedback {
  correct: boolean
  submittedAnswer: string
}

const INITIAL_PLAYERS: Record<PlayerId, Player> = {
  playerOne: { name: 'Jugador 1', score: 0 },
  playerTwo: { name: 'Jugador 2', score: 0 },
}

function App() {
  const [players, setPlayers] = useState(INITIAL_PLAYERS)
  const [activePlayerId, setActivePlayerId] = useState<PlayerId>('playerOne')
  const [phase, setPhase] = useState<GamePhase>('ready')
  const [round, setRound] = useState(1)
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const [selectedQuestionId, setSelectedQuestionId] = useState<number | null>(
    null,
  )
  const [rotation, setRotation] = useState(0)
  const [question, setQuestion] = useState<Question | null>(null)
  const [feedback, setFeedback] = useState<Feedback | null>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const spinCompletionHandled = useRef(false)

  const activePlayer = players[activePlayerId]
  const segmentAngle = 360 / WHEEL_QUESTION_IDS.length
  const gameLocked = phase !== 'ready'

  const statusMessage = useMemo(() => {
    switch (phase) {
      case 'spinning':
        return `La ruleta está eligiendo la pregunta de ${activePlayer.name}.`
      case 'loading':
        return `Buscando la pregunta ${selectedQuestionId} para ${activePlayer.name}.`
      case 'answering':
        return `Turno de ${activePlayer.name}. Elegí una opción.`
      case 'feedback':
        return feedback?.correct
          ? `Respuesta correcta. ${activePlayer.name} ganó ${POINTS_PER_CORRECT_ANSWER} puntos.`
          : `Respuesta incorrecta. La respuesta correcta era ${question?.answer}.`
      case 'error':
        return errorMessage
      default:
        return `Turno de ${activePlayer.name}. Podés girar la ruleta.`
    }
  }, [
    activePlayer.name,
    errorMessage,
    feedback?.correct,
    phase,
    question?.answer,
    selectedQuestionId,
  ])

  async function loadQuestion(questionId: number) {
    setPhase('loading')
    setErrorMessage('')

    try {
      const nextQuestion = await getQuestion(questionId)
      setQuestion(nextQuestion)
      setPhase('answering')
    } catch (error) {
      setErrorMessage(
        error instanceof QuestionsApiError
          ? error.message
          : 'Ocurrió un error inesperado al pedir la pregunta.',
      )
      setPhase('error')
    }
  }

  async function finishSpin() {
    if (
      phase !== 'spinning' ||
      selectedQuestionId === null ||
      spinCompletionHandled.current
    ) {
      return
    }

    spinCompletionHandled.current = true
    await loadQuestion(selectedQuestionId)
  }

  function handleSpin() {
    if (phase !== 'ready') {
      return
    }

    const nextIndex = randomIndex(WHEEL_QUESTION_IDS.length)
    const currentRotation = ((rotation % 360) + 360) % 360
    const selectedCenter = nextIndex * segmentAngle + segmentAngle / 2
    const targetRotation = (360 - selectedCenter) % 360
    const rotationDelta = (targetRotation - currentRotation + 360) % 360

    spinCompletionHandled.current = false
    setSelectedIndex(nextIndex)
    setSelectedQuestionId(WHEEL_QUESTION_IDS[nextIndex])
    setRotation(currentRotation + rotationDelta + 6 * 360)
    setQuestion(null)
    setFeedback(null)
    setErrorMessage('')
    setPhase('spinning')
  }

  function handlePlayerNameChange(playerId: PlayerId, name: string) {
    if (gameLocked) {
      return
    }

    setPlayers((current) => ({
      ...current,
      [playerId]: { ...current[playerId], name },
    }))
  }

  function handleAnswerSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (phase !== 'answering' || !question) {
      return
    }

    const submitter = event.nativeEvent as SubmitEvent
    const chosen =
      submitter.submitter instanceof HTMLButtonElement
        ? submitter.submitter.value
        : ''
    if (!chosen.trim()) {
      return
    }

    const correct = normalizeAnswer(chosen) === normalizeAnswer(question.answer)

    if (correct) {
      setPlayers((current) => ({
        ...current,
        [activePlayerId]: {
          ...current[activePlayerId],
          score: current[activePlayerId].score + POINTS_PER_CORRECT_ANSWER,
        },
      }))
    }

    setFeedback({ correct, submittedAnswer: chosen.trim() })
    setPhase('feedback')
  }

  function handleNextRound() {
    setActivePlayerId((current) =>
      current === 'playerOne' ? 'playerTwo' : 'playerOne',
    )
    setRound((current) => current + 1)
    setSelectedIndex(null)
    setSelectedQuestionId(null)
    setQuestion(null)
    setFeedback(null)
    setErrorMessage('')
    setPhase('ready')
  }

  return (
    <main className={styles.page}>
      <header className={styles.hero}>
        <p className={styles.eyebrow}>Preguntados</p>
        <h1>La rueda de las preguntas</h1>
        <p>Dos jugadores, una partida y todas las ganas de jugar.</p>
      </header>

      <section className={styles.players} aria-label="Jugadores y puntajes">
        {(Object.keys(players) as PlayerId[]).map((playerId) => {
          const player = players[playerId]
          const active = playerId === activePlayerId

          return (
            <article
              className={`${styles.playerCard} ${active ? styles.activePlayer : ''}`}
              key={playerId}
            >
              <div>
                <span className={styles.turnLabel}>
                  {active ? 'Turno actual' : 'En espera'}
                </span>
                <label htmlFor={`player-${playerId}`}>Nombre</label>
                <input
                  id={`player-${playerId}`}
                  value={player.name}
                  maxLength={30}
                  disabled={gameLocked}
                  onChange={(event) =>
                    handlePlayerNameChange(playerId, event.target.value)
                  }
                />
              </div>
              <strong className={styles.score}>
                {player.score}
                <span> puntos</span>
              </strong>
            </article>
          )
        })}
      </section>

      <p className={styles.round}>Ronda {round}</p>
      <p className={styles.liveStatus} role="status" aria-live="polite">
        {statusMessage}
      </p>

      <div className={styles.gameLayout}>
        <Wheel
          questionIds={WHEEL_QUESTION_IDS}
          selectedIndex={selectedIndex}
          rotation={rotation}
          spinning={phase === 'spinning' || phase === 'loading'}
          loading={phase === 'loading'}
          onSpin={handleSpin}
          onSpinComplete={() => void finishSpin()}
        />

        <section
          className={styles.questionPanel}
          aria-labelledby="question-title"
        >
          <h2 id="question-title">Pregunta</h2>

          {phase === 'ready' && (
            <div className={styles.emptyState}>
              <span aria-hidden="true">?</span>
              <p>Girala para elegir la próxima pregunta.</p>
            </div>
          )}

          {(phase === 'spinning' || phase === 'loading') && (
            <div className={styles.loadingState} role="status">
              <span className={styles.loader} aria-hidden="true" />
              <p>
                {phase === 'spinning'
                  ? 'La ruleta ya tiene un ganador…'
                  : 'Buscando la pregunta en la API…'}
              </p>
            </div>
          )}

          {phase === 'error' && (
            <div className={styles.errorState} role="alert">
              <h3>No pudimos cargar la pregunta</h3>
              <p>{errorMessage}</p>
              <button
                type="button"
                onClick={() => void loadQuestion(selectedQuestionId!)}
              >
                Reintentar pregunta #{selectedQuestionId}
              </button>
            </div>
          )}

          {(phase === 'answering' || phase === 'feedback') && question && (
            <div className={styles.questionContent}>
              <div className={styles.questionMeta}>
                <span>Pregunta #{question.id}</span>
                {question.category && <span>{question.category}</span>}
              </div>
              <h3>{question.question}</h3>

              {phase === 'answering' ? (
                <form onSubmit={handleAnswerSubmit}>
                  <div className={styles.options} role="group" aria-label="Opciones de respuesta">
                    {question.options.map((option) => (
                      <button
                        className={styles.option}
                        key={option}
                        type="submit"
                        name="option"
                        value={option}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                </form>
              ) : (
                <div
                  className={`${styles.feedback} ${
                    feedback?.correct ? styles.correct : styles.incorrect
                  }`}
                >
                  <h3>{feedback?.correct ? '¡Correcto!' : 'No es correcto'}</h3>
                  {feedback && !feedback.correct && (
                    <p>Tu respuesta: {feedback.submittedAnswer}</p>
                  )}
                  <p>
                    Respuesta correcta: <strong>{question.answer}</strong>
                  </p>
                  {feedback?.correct && (
                    <p>
                      Sumaste{' '}
                      <strong>{POINTS_PER_CORRECT_ANSWER} puntos</strong>.
                    </p>
                  )}
                  <button type="button" onClick={handleNextRound}>
                    Siguiente jugador
                  </button>
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </main>
  )
}

export default App
