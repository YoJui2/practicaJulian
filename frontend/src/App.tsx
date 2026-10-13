import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { getRandomQuestion, QuestionsApiError } from './api/questions'
import type { Question } from './api/questions'
import { AVATARS } from './components/Avatars'
import { AvatarPicker } from './components/AvatarPicker'
import { Wheel } from './components/Wheel'
import {
  POINTS_PER_CORRECT_ANSWER,
  WHEEL_CATEGORIES,
  WHEEL_DRIFT_TURNS,
  WHEEL_REVEAL_MS,
} from './config'
import { normalizeAnswer } from './game/answer'
import { forwardDelta, landingRotation, planSpin } from './game/wheel'
import {
  canUseWildcard,
  createWildcardUses,
  maxUsesOf,
  optionsToHide,
  spendWildcardUse,
  usesLeft,
  WILDCARDS,
} from './game/wildcards'
import type { WildcardId, WildcardUses } from './game/wildcards'
import styles from './App.module.css'

type PlayerId = 'playerOne' | 'playerTwo'
type GamePhase = 'ready' | 'spinning' | 'answering' | 'feedback' | 'error'

interface Player {
  name: string
  score: number
  avatar: number
  wildcardUses: WildcardUses
}

interface Feedback {
  correct: boolean
  submittedAnswer: string
  points: number
}

const BONUS_MULTIPLIER = 2

const INITIAL_PLAYERS: Record<PlayerId, Player> = {
  playerOne: {
    name: 'Jugador 1',
    score: 0,
    avatar: 0,
    wildcardUses: createWildcardUses(),
  },
  playerTwo: {
    name: 'Jugador 2',
    score: 0,
    avatar: 3,
    wildcardUses: createWildcardUses(),
  },
}

function App() {
  const [players, setPlayers] = useState(INITIAL_PLAYERS)
  const [activePlayerId, setActivePlayerId] = useState<PlayerId>('playerOne')
  const [phase, setPhase] = useState<GamePhase>('ready')
  const [round, setRound] = useState(1)
  const [selectedCategoryName, setSelectedCategoryName] = useState<
    string | null
  >(null)
  const [rotation, setRotation] = useState(0)
  const [question, setQuestion] = useState<Question | null>(null)
  const [feedback, setFeedback] = useState<Feedback | null>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [spinDone, setSpinDone] = useState(false)
  const [fetchDone, setFetchDone] = useState(false)
  const [hiddenOptions, setHiddenOptions] = useState<string[]>([])
  const [eliminatedOptions, setEliminatedOptions] = useState<string[]>([])
  const [attemptsLeft, setAttemptsLeft] = useState(1)
  const [retryActive, setRetryActive] = useState(false)
  const [bonusPoints, setBonusPoints] = useState(false)
  const [usedWildcards, setUsedWildcards] = useState<WildcardId[]>([])
  const activePlayer = players[activePlayerId]
  const gameLocked = phase !== 'ready'
  const showWheel = phase === 'ready' || phase === 'spinning'
  const stake = POINTS_PER_CORRECT_ANSWER * (bonusPoints ? BONUS_MULTIPLIER : 1)

  const visibleOptions = question
    ? question.options.filter(
        (option) =>
          !hiddenOptions.includes(option) &&
          !eliminatedOptions.includes(option),
      )
    : []

  const statusMessage = useMemo(() => {
    switch (phase) {
      case 'spinning': {
        const categoryLabel =
          WHEEL_CATEGORIES.find(
            (category) => category.name === selectedCategoryName,
          )?.label ?? selectedCategoryName

        return `La ruleta se detiene en ${categoryLabel} para ${activePlayer.name}.`
      }
      case 'answering': {
        const base = retryActive
          ? attemptsLeft > 1
            ? `Turno de ${activePlayer.name}. Tenés dos chances: elegí una opción.`
            : `Turno de ${activePlayer.name}. Te queda un intento más.`
          : `Turno de ${activePlayer.name}. Elegí una opción.`

        return bonusPoints
          ? `${base} La respuesta correcta vale ${stake} puntos.`
          : base
      }
      case 'feedback':
        return feedback?.correct
          ? `Respuesta correcta. ${activePlayer.name} ganó ${feedback.points} puntos.`
          : `Respuesta incorrecta. La respuesta correcta era ${question?.answer}.`
      case 'error':
        return errorMessage
      default:
        return `Turno de ${activePlayer.name}. Podés girar la ruleta.`
    }
  }, [
    activePlayer.name,
    attemptsLeft,
    bonusPoints,
    errorMessage,
    feedback,
    phase,
    question?.answer,
    retryActive,
    selectedCategoryName,
    stake,
  ])

  useEffect(() => {
    if (phase !== 'spinning' || !spinDone || !fetchDone) {
      return
    }

    const timer = window.setTimeout(() => {
      setPhase(question ? 'answering' : 'error')
    }, WHEEL_REVEAL_MS)

    return () => window.clearTimeout(timer)
  }, [fetchDone, phase, question, spinDone])

  function clearRoundState() {
    setQuestion(null)
    setFeedback(null)
    setErrorMessage('')
    setHiddenOptions([])
    setEliminatedOptions([])
    setAttemptsLeft(1)
    setRetryActive(false)
    setBonusPoints(false)
    setUsedWildcards([])
  }

  async function loadQuestion(categoryName: string): Promise<Question | null> {
    setFetchDone(false)
    setErrorMessage('')

    try {
      const nextQuestion = await getRandomQuestion(categoryName)
      setQuestion(nextQuestion)
      return nextQuestion
    } catch (error) {
      setErrorMessage(
        error instanceof QuestionsApiError
          ? error.message
          : 'Ocurrió un error inesperado al pedir la pregunta.',
      )
      return null
    } finally {
      setFetchDone(true)
    }
  }

  function handleSpin() {
    if (phase !== 'ready') {
      return
    }

    const plan = planSpin(WHEEL_CATEGORIES, rotation, WHEEL_DRIFT_TURNS)
    const landing = landingRotation(WHEEL_CATEGORIES.length, plan.sectorIndex)
    const category = WHEEL_CATEGORIES[plan.sectorIndex]

    setSelectedCategoryName(category.name)
    setRotation(plan.driftTarget + forwardDelta(plan.driftTarget, landing))
    clearRoundState()
    setSpinDone(false)
    setPhase('spinning')
    void loadQuestion(category.name)
  }

  function handleSpinEnd() {
    setSpinDone(true)
  }

  async function handleRetryQuestion() {
    if (!selectedCategoryName) {
      return
    }

    const nextQuestion = await loadQuestion(selectedCategoryName)
    setPhase(nextQuestion ? 'answering' : 'error')
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

  function handleAvatarChange(playerId: PlayerId, avatar: number) {
    setPlayers((current) => ({
      ...current,
      [playerId]: { ...current[playerId], avatar },
    }))
  }

  function awardPoints(playerId: PlayerId, points: number) {
    setPlayers((current) => ({
      ...current,
      [playerId]: {
        ...current[playerId],
        score: current[playerId].score + points,
      },
    }))
  }

  function spendWildcard(playerId: PlayerId, wildcardId: WildcardId) {
    setPlayers((current) => ({
      ...current,
      [playerId]: {
        ...current[playerId],
        wildcardUses: spendWildcardUse(
          current[playerId].wildcardUses,
          wildcardId,
        ),
      },
    }))
  }

  function finishAnswer(submittedAnswer: string, correct: boolean) {
    const points = correct ? stake : 0

    if (correct) {
      awardPoints(activePlayerId, points)
      setBonusPoints(false)
    }

    setFeedback({ correct, submittedAnswer, points })
    setPhase('feedback')
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

    const answer = chosen.trim()
    const correct = normalizeAnswer(answer) === normalizeAnswer(question.answer)

    if (!correct && attemptsLeft > 1) {
      setEliminatedOptions((current) => [...current, answer])
      setAttemptsLeft((current) => current - 1)
      return
    }

    finishAnswer(answer, correct)
  }

  function handleUseWildcard(wildcardId: WildcardId) {
    if (phase !== 'answering' || !question) {
      return
    }

    if (!canUseWildcard(activePlayer.wildcardUses, usedWildcards, wildcardId)) {
      return
    }

    spendWildcard(activePlayerId, wildcardId)
    setUsedWildcards((current) => [...current, wildcardId])

    switch (wildcardId) {
      case 'podar':
        setHiddenOptions(optionsToHide(question.options, question.answer))
        break
      case 'segundo':
        setRetryActive(true)
        setAttemptsLeft(2)
        break
      case 'doblar':
        setBonusPoints(true)
        break
      case 'chivazo':
        finishAnswer(question.answer, true)
        break
    }
  }

  function handleNextRound() {
    setActivePlayerId((current) =>
      current === 'playerOne' ? 'playerTwo' : 'playerOne',
    )
    setRound((current) => current + 1)
    setSelectedCategoryName(null)
    clearRoundState()
    setPhase('ready')
  }

  return (
    <main className={styles.page}>
      <header className={styles.hero}>
        <p className={styles.eyebrow}>🎉 Preguntados</p>
        <h1>¡Girá y ganá!</h1>
        <p>Dos jugadores. Una ruleta. ¿Quién se lleva la gloria?</p>
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
              <AvatarPicker
                avatars={AVATARS}
                onSelect={(avatar) => handleAvatarChange(playerId, avatar)}
                playerName={player.name}
                value={player.avatar}
              />
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
        {showWheel ? (
          <Wheel
            sectors={WHEEL_CATEGORIES}
            rotation={rotation}
            spinning={phase === 'spinning'}
            onSpin={handleSpin}
            onSpinEnd={handleSpinEnd}
          />
        ) : (
          <section
            className={styles.questionPanel}
            aria-labelledby="question-title"
          >
            <h2 id="question-title">Pregunta</h2>

            {phase === 'error' && (
              <div className={styles.errorState} role="alert">
                <h3>No pudimos cargar la pregunta</h3>
                <p>{errorMessage}</p>
                <button
                  type="button"
                  onClick={() => void handleRetryQuestion()}
                >
                  Reintentar pregunta
                  {selectedCategoryName
                    ? ` de ${WHEEL_CATEGORIES.find((category) => category.name === selectedCategoryName)?.label ?? selectedCategoryName}`
                    : ''}
                </button>
              </div>
            )}

            {(phase === 'answering' || phase === 'feedback') && question && (
              <div className={styles.questionContent}>
                <div className={styles.questionMeta}>
                  <span>Pregunta #{question.id}</span>
                  {question.category && <span>{question.category}</span>}
                  {question.lang && (
                    <span>Traducida automáticamente ({question.lang})</span>
                  )}
                </div>
                <h3>{question.question}</h3>

                {phase === 'answering' ? (
                  <>
                    <div className={styles.wildcards}>
                      <p className={styles.wildcardsTitle}>
                        Comodines de {activePlayer.name}
                      </p>
                      <div className={styles.wildcardsRow}>
                        {WILDCARDS.map((wildcard) => {
                          const remaining = usesLeft(
                            activePlayer.wildcardUses,
                            wildcard.id,
                          )
                          const total = maxUsesOf(wildcard.id)
                          const spentThisRound = usedWildcards.includes(
                            wildcard.id,
                          )
                          const usable = !spentThisRound && remaining > 0
                          const availability =
                            remaining === 0
                              ? 'Sin usos disponibles.'
                              : spentThisRound
                                ? 'Ya lo usaste en esta ronda.'
                                : `Usos disponibles: ${remaining} de ${total}.`

                          return (
                            <button
                              aria-label={`${wildcard.name}. ${wildcard.description} ${availability}`}
                              className={`${styles.wildcard} ${
                                usable
                                  ? ''
                                  : spentThisRound
                                    ? styles.wildcardSpent
                                    : styles.wildcardUnavailable
                              }`}
                              disabled={!usable}
                              key={wildcard.id}
                              onClick={() => handleUseWildcard(wildcard.id)}
                              type="button"
                            >
                              <strong>{wildcard.name}</strong>
                              <span>{wildcard.description}</span>
                              <span className={styles.wildcardUses}>
                                {remaining}/{total}
                              </span>
                            </button>
                          )
                        })}
                      </div>
                    </div>

                    <form onSubmit={handleAnswerSubmit}>
                      <div
                        aria-label="Opciones de respuesta"
                        className={styles.options}
                        role="group"
                      >
                        {visibleOptions.map((option) => (
                          <button
                            className={styles.option}
                            data-tone={question.options.indexOf(option) + 1}
                            key={option}
                            name="option"
                            type="submit"
                            value={option}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    </form>
                  </>
                ) : (
                  <div
                    className={`${styles.feedback} ${
                      feedback?.correct ? styles.correct : styles.incorrect
                    }`}
                  >
                    <h3>
                      {feedback?.correct ? '¡Correcto!' : 'No es correcto'}
                    </h3>
                    {feedback && !feedback.correct && (
                      <p>Tu respuesta: {feedback.submittedAnswer}</p>
                    )}
                    <p>
                      Respuesta correcta: <strong>{question.answer}</strong>
                    </p>
                    {feedback?.correct && (
                      <p>
                        Sumaste <strong>{feedback.points} puntos</strong>.
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
        )}
      </div>
    </main>
  )
}

export default App
