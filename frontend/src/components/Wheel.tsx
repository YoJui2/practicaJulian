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

function segmentColor(index: number, segmentCount: number): string {
  const hue = Math.round((index * 360) / segmentCount)
  return `hsl(${hue} 80% 58%)`
}

function createGradient(segmentCount: number): string {
  const segmentAngle = 360 / segmentCount

  return Array.from({ length: segmentCount }, (_, index) => {
    const start = index * segmentAngle
    const end = (index + 1) * segmentAngle
    return `${segmentColor(index, segmentCount)} ${start}deg ${end}deg`
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
          <span className={styles.hub} aria-hidden="true" />
        </div>
        <div className={styles.labels} aria-hidden="true">
          {questionIds.map((questionId, index) => {
            const angle = index * segmentAngle + segmentAngle / 2

            return (
              <span
                className={`${styles.segmentLabel} ${
                  selectedIndex === index ? styles.selectedLabel : ''
                }`}
                key={questionId}
                style={{ '--label-angle': `${angle}deg` } as CSSProperties}
              >
                ?
              </span>
            )
          })}
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
