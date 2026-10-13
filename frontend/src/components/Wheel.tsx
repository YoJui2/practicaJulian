import type { CSSProperties } from 'react'
import frontDecoration from '../../../app/icon/cocodra.png'
import type { WheelSector } from '../game/wheel'
import styles from './Wheel.module.css'

interface WheelProps {
  sectors: readonly WheelSector[]
  rotation: number
  spinning: boolean
  settling: boolean
  onSpin: () => void
}

function createGradient(sectors: readonly WheelSector[]): string {
  const segmentAngle = 360 / sectors.length

  return sectors
    .map((sector, index) => {
      const start = index * segmentAngle
      const end = (index + 1) * segmentAngle
      return `${sector.color} ${start}deg ${end}deg`
    })
    .join(', ')
}

export function Wheel({
  sectors,
  rotation,
  spinning,
  settling,
  onSpin,
}: WheelProps) {
  const segmentAngle = 360 / sectors.length

  return (
    <section className={styles.wheelPanel} aria-labelledby="wheel-title">
      <h2 id="wheel-title">Ruleta</h2>
      <p>El sector marcado determinará la pregunta.</p>

      <div className={styles.wheelAssembly}>
        <div className={styles.wheelStage}>
          <div className={styles.pointer} aria-hidden="true" />
          <div
            className={styles.wheel}
            data-testid="wheel-disc"
            data-spinning={spinning && !settling}
            data-settling={settling}
            role="img"
            aria-label={`Ruleta con ${sectors.length} categorías`}
            style={
              {
                transform: `rotate(${rotation}deg)`,
                '--wheel-rotation': `${rotation}deg`,
                background: `conic-gradient(${createGradient(sectors)})`,
              } as CSSProperties
            }
          >
            <span className={styles.hub} aria-hidden="true" />
          </div>
          <div
            className={styles.labels}
            aria-hidden="true"
            style={
              {
                transform: `rotate(${rotation}deg)`,
                '--wheel-rotation': `${rotation}deg`,
              } as CSSProperties
            }
            data-spinning={spinning && !settling}
          >
            {sectors.map((sector, index) => {
              const angle = index * segmentAngle + segmentAngle / 2

              return (
                <span
                  className={styles.segmentLabel}
                  key={sector.name}
                  style={{ '--label-angle': `${angle}deg` } as CSSProperties}
                >
                  {sector.emoji}
                </span>
              )
            })}
          </div>

          <img
            src={frontDecoration}
            alt=""
            aria-hidden="true"
            className={styles.frontDecoration}
          />
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
