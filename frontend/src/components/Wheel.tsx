import type { CSSProperties } from 'react'
import styles from './Wheel.module.css'

interface WheelProps {
  questionIds: readonly number[]
  rotation: number
  loading: boolean
  onSpin: () => void
}

const CLASSIC_CATEGORY_COLORS = [
  '#f4c542',
  '#e94b4b',
  '#3d8edb',
  '#f08b3e',
  '#4ccf64',
  '#9b4de8',
]
const CATEGORY_EMOJIS = ['🏛️', '⚽', '🌍', '🎨', '🔬', '🎬']

function segmentColor(index: number): string {
  return CLASSIC_CATEGORY_COLORS[index % CLASSIC_CATEGORY_COLORS.length]
}

function createGradient(segmentCount: number): string {
  const segmentAngle = 360 / segmentCount

  return Array.from({ length: segmentCount }, (_, index) => {
    const start = index * segmentAngle
    const end = (index + 1) * segmentAngle
    return `${segmentColor(index)} ${start}deg ${end}deg`
  }).join(', ')
}

export function Wheel({
  questionIds,
  rotation,
  loading,
  onSpin,
}: WheelProps) {
  const segmentAngle = 360 / questionIds.length

  return (
    <section className={styles.wheelPanel} aria-labelledby="wheel-title">
      <h2 id="wheel-title">Ruleta</h2>
      <p>El sector marcado determinará la pregunta.</p>

      <div className={styles.wheelStage}>
        <div className={styles.pointer} aria-hidden="true" />
        <div
          className={`${styles.wheel} ${loading ? styles.loading : ''}`}
          data-testid="wheel-disc"
          role="img"
          aria-label={`Ruleta clásica con ${questionIds.length} sectores`}
          style={
            {
              transform: `rotate(${rotation}deg)`,
              '--wheel-rotation': `${rotation}deg`,
              background: `conic-gradient(${createGradient(questionIds.length)})`,
            } as CSSProperties
          }
        >
          <span className={styles.hub} aria-hidden="true" />
        </div>
        <div
          className={`${styles.labels} ${loading ? styles.loading : ''}`}
          aria-hidden="true"
          style={
            {
              transform: `rotate(${rotation}deg)`,
              '--wheel-rotation': `${rotation}deg`,
            } as CSSProperties
          }
        >
          {questionIds.map((questionId, index) => {
            const angle = index * segmentAngle + segmentAngle / 2

            return (
              <span
                className={styles.segmentLabel}
                key={questionId}
                style={{ '--label-angle': `${angle}deg` } as CSSProperties}
              >
                {CATEGORY_EMOJIS[index % CATEGORY_EMOJIS.length]}
              </span>
            )
          })}
        </div>
      </div>

      <button
        className={styles.spinButton}
        type="button"
        onClick={onSpin}
        disabled={loading}
      >
        {loading ? 'Girando…' : 'Girar la ruleta'}
      </button>
    </section>
  )
}
