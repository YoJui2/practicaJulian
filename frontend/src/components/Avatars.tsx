import type { ComponentType } from 'react'

interface AvatarProps {
  className?: string
}

function AvatarRojo({ className }: AvatarProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 48 48"
    >
      <circle cx="24" cy="26" r="20" fill="#d93662" />
      <circle cx="17" cy="23" r="3" fill="#fff8ef" />
      <circle cx="31" cy="23" r="3" fill="#fff8ef" />
      <path
        d="M16 32c2.5 3.5 5.2 5 8 5s5.5-1.5 8-5"
        fill="none"
        stroke="#fff8ef"
        strokeLinecap="round"
        strokeWidth="3"
      />
    </svg>
  )
}

function AvatarAzul({ className }: AvatarProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 48 48"
    >
      <rect x="5" y="7" width="38" height="38" rx="12" fill="#1769aa" />
      <path
        d="M13 20h6M29 20h6"
        stroke="#fff8ef"
        strokeLinecap="round"
        strokeWidth="3"
      />
      <circle cx="17" cy="29" r="3" fill="#fff8ef" />
      <circle cx="31" cy="29" r="3" fill="#fff8ef" />
      <path
        d="M17 36c2 2.5 4.3 3.5 7 3.5s5-1 7-3.5"
        fill="none"
        stroke="#fff8ef"
        strokeLinecap="round"
        strokeWidth="3"
      />
    </svg>
  )
}

function AvatarMostaza({ className }: AvatarProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 48 48"
    >
      <circle cx="24" cy="26" r="20" fill="#ffdc4a" />
      <rect x="11" y="19" width="11" height="9" rx="4" fill="#073b4c" />
      <rect x="26" y="19" width="11" height="9" rx="4" fill="#073b4c" />
      <path d="M22 23.5h4" stroke="#073b4c" strokeWidth="3" />
      <path
        d="M17 35c2 3 4.3 4 7 4s5-1 7-4"
        fill="none"
        stroke="#073b4c"
        strokeLinecap="round"
        strokeWidth="3"
      />
    </svg>
  )
}

function AvatarVerde({ className }: AvatarProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 48 48"
    >
      <circle cx="24" cy="29" r="17" fill="#168653" />
      <path d="M7 23a17 17 0 0 1 34 0z" fill="#073b4c" />
      <rect x="24" y="19" width="18" height="5" rx="2.5" fill="#073b4c" />
      <circle cx="18" cy="30" r="3" fill="#fff8ef" />
      <circle cx="31" cy="30" r="3" fill="#fff8ef" />
      <path
        d="M19 37c1.8 2.2 3.4 3 5 3s3.2-1 5-3"
        fill="none"
        stroke="#fff8ef"
        strokeLinecap="round"
        strokeWidth="3"
      />
    </svg>
  )
}

function AvatarVioleta({ className }: AvatarProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 48 48"
    >
      <circle cx="24" cy="29" r="17" fill="#7c4dff" />
      <g fill="#5b32b8">
        <circle cx="13" cy="19" r="6" />
        <circle cx="24" cy="14" r="6" />
        <circle cx="35" cy="19" r="6" />
      </g>
      <circle cx="18" cy="29" r="3" fill="#fff8ef" />
      <circle cx="30" cy="29" r="3" fill="#fff8ef" />
      <path
        d="M19 36c1.8 2.2 3.3 3 5 3s3.2-1 5-3"
        fill="none"
        stroke="#fff8ef"
        strokeLinecap="round"
        strokeWidth="3"
      />
    </svg>
  )
}

function AvatarNaranja({ className }: AvatarProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 48 48"
    >
      <circle cx="24" cy="26" r="20" fill="#f0783c" />
      <g fill="none" stroke="#073b4c" strokeWidth="2.5">
        <circle cx="17" cy="25" r="6" />
        <circle cx="31" cy="25" r="6" />
        <path d="M23 25h2" />
      </g>
      <circle cx="17" cy="25" r="2" fill="#073b4c" />
      <circle cx="31" cy="25" r="2" fill="#073b4c" />
      <path
        d="M17 36c2 3 4.3 4 7 4s5-1 7-4"
        fill="none"
        stroke="#073b4c"
        strokeLinecap="round"
        strokeWidth="3"
      />
    </svg>
  )
}

function AvatarRosa({ className }: AvatarProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 48 48"
    >
      <circle cx="24" cy="9" r="6" fill="#073b4c" />
      <rect x="6" y="11" width="36" height="34" rx="12" fill="#ef476f" />
      <circle cx="18" cy="26" r="3" fill="#fff8ef" />
      <circle cx="30" cy="26" r="3" fill="#fff8ef" />
      <path
        d="M19 34c1.8 2.2 3.3 3 5 3s3.2-1 5-3"
        fill="none"
        stroke="#fff8ef"
        strokeLinecap="round"
        strokeWidth="3"
      />
    </svg>
  )
}

function AvatarTurquesa({ className }: AvatarProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 48 48"
    >
      <circle cx="24" cy="26" r="20" fill="#06d6a0" />
      <circle cx="17" cy="22" r="3" fill="#073b4c" />
      <circle cx="31" cy="22" r="3" fill="#073b4c" />
      <path
        d="M16 33c3-2.5 5.5-2 8 1 2.5-3 5-3.5 8-1-1.5 4-4.5 5.5-8 5.5s-6.5-1.5-8-5.5z"
        fill="#073b4c"
      />
    </svg>
  )
}

export interface Avatar {
  id: string
  name: string
  label: string
  Icon: ComponentType<AvatarProps>
}

export const AVATARS: readonly Avatar[] = [
  { id: 'rojo', name: 'Rojo', label: 'Avatar rojo', Icon: AvatarRojo },
  { id: 'azul', name: 'Azul', label: 'Avatar azul', Icon: AvatarAzul },
  {
    id: 'mostaza',
    name: 'Mostaza',
    label: 'Avatar mostaza',
    Icon: AvatarMostaza,
  },
  {
    id: 'verde',
    name: 'Gorra',
    label: 'Avatar verde con gorra',
    Icon: AvatarVerde,
  },
  {
    id: 'violeta',
    name: 'Violeta',
    label: 'Avatar violeta',
    Icon: AvatarVioleta,
  },
  {
    id: 'naranja',
    name: 'Anteojos',
    label: 'Avatar naranja con anteojos',
    Icon: AvatarNaranja,
  },
  { id: 'rosa', name: 'Rosa', label: 'Avatar rosa', Icon: AvatarRosa },
  {
    id: 'turquesa',
    name: 'Turquesa',
    label: 'Avatar turquesa',
    Icon: AvatarTurquesa,
  },
]