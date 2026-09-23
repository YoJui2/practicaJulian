import { useEffect } from 'react'
import type { CSSProperties, TransitionEvent } from 'react'
import styles from './Wheel.module.css'

interface WheelProps {
  questionIds: readonly number[]
  selectedIndex: number | null
  rotation: number
  spinning: boolean
  onSpin: () => void
  onSpinComplete: () => void
}

const SEGMENT_COLORS = ['#d82424', '#f2bd2d', '#1769aa', '#713b8e', '#198754']

function createGradient(segmentCount: number): string {
  const segmentAngle = 360 / segmentCount

  return SEGMENT_COLORS.map((color, index) => {
    const start = index * segmentAngle
    const end = (index + 1) * segmentAngle
    return `${color} ${start}deg ${end}deg`
  }).join(', ')
}

export function Wheel({
  questionIds,
  selectedIndex,
  rotation,
  spinning,
  onSpin,
  onSpinComplete,
}: WheelProps) {
  const segmentAngle = 360 / questionIds.length

  useEffect(() => {
    if (!spinning) {
      return
    }

    const fallback = window.setTimeout(onSpinComplete, 1800)
    return () => window.clearTimeout(fallback)
  }, [onSpinComplete, spinning])

  function handleTransitionEnd(event: TransitionEvent<HTMLDivElement>) {
    if (event.propertyName === 'transform' && spinning) {
      onSpinComplete()
    }
  }

  return (
    <section className={styles.wheelPanel} aria-labelledby="wheel-title">
      <h2 id="wheel-title">Ruleta</h2>
      <p>El sector marcado determinará la pregunta.</p>

      <div className={styles.wheelStage}>
        <div className={styles.pointer} aria-hidden="true" />
        <div
          className={styles.wheel}
          data-testid="wheel-disc"
          role="img"
          aria-label={`Ruleta clásica con ${questionIds.length} sectores`}
          style={
            {
              transform: `rotate(${rotation}deg)`,
              background: `conic-gradient(${createGradient(questionIds.length)})`,
            } as CSSProperties
          }
          onTransitionEnd={handleTransitionEnd}
        >
          {questionIds.map((questionId, index) => {
            const angle = index * segmentAngle + segmentAngle / 2

            return (
              <span
                className={`${styles.segmentLabel} ${
                  selectedIndex === index ? styles.selectedLabel : ''
                }`}
                key={questionId}
                style={{ '--label-angle': `${angle}deg` } as CSSProperties}
                aria-hidden="true"
              >
                ?
              </span>
            )
          })}
          <span className={styles.hub} aria-hidden="true" />
        </div>
      </div>

      <button
        className={styles.spinButton}
        type="button"
        onClick={onSpin}
        disabled={spinning}
      >
        {spinning ? 'Girando…' : 'Girar la ruleta'}
      </button>
    </section>
  )
}
