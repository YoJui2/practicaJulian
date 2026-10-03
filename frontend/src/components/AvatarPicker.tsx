import { useEffect, useState } from 'react'
import type { Avatar } from './Avatars'
import styles from './AvatarPicker.module.css'

interface AvatarPickerProps {
  avatars: readonly Avatar[]
  playerName: string
  value: number
  onSelect: (index: number) => void
}

export function AvatarPicker({
  avatars,
  playerName,
  value,
  onSelect,
}: AvatarPickerProps) {
  const [open, setOpen] = useState(false)
  const selectedAvatar = avatars[value] ?? avatars[0]
  const SelectedIcon = selectedAvatar.Icon

  useEffect(() => {
    if (!open) {
      return
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setOpen(false)
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [open])

  return (
    <>
      <div className={styles.picker}>
        <button
          aria-expanded={open}
          aria-haspopup="dialog"
          aria-label={`Elegí el avatar de ${playerName}`}
          className={styles.trigger}
          onClick={() => setOpen(true)}
          type="button"
        >
          <SelectedIcon className={styles.preview} />
          <span className={styles.hint}>Avatar</span>
        </button>
      </div>

      {open && (
        <div className={styles.backdrop} onClick={() => setOpen(false)}>
          <div
            aria-label={`Elegí el avatar de ${playerName}`}
            aria-modal="true"
            className={styles.window}
            onClick={(event) => event.stopPropagation()}
            role="dialog"
          >
            <div className={styles.windowHeader}>
              <h2 className={styles.windowTitle}>Elegí tu avatar</h2>
              <button
                aria-label="Cerrar"
                className={styles.closeButton}
                onClick={() => setOpen(false)}
                type="button"
              >
                ✕
              </button>
            </div>

            <div className={styles.windowGrid}>
              {avatars.map((avatar, index) => {
                const Icon = avatar.Icon
                const selected = index === value

                return (
                  <button
                    aria-label={
                      selected
                        ? `${avatar.label}. Equipado`
                        : avatar.label
                    }
                    aria-pressed={selected}
                    className={`${styles.windowChoice} ${
                      selected ? styles.windowChoiceSelected : ''
                    }`}
                    key={avatar.id}
                    onClick={() => {
                      onSelect(index)
                      setOpen(false)
                    }}
                    type="button"
                  >
                    <Icon className={styles.windowChoiceIcon} />
                    <span className={styles.windowChoiceName}>
                      {avatar.name}
                    </span>
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </>
  )
}