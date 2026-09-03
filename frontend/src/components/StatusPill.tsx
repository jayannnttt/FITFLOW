import type { WorkoutState } from '../types'

interface Props {
  state: WorkoutState
  score?: number
}

const STATE_CONFIG: Record<
  WorkoutState,
  { label: string; color: string }
> = {
  IDLE: {
    label: 'IDLE',
    color: 'var(--muted-foreground)',
  },
  ALIGNING: {
    label: 'CALIBRATING',
    color: 'var(--warning)',
  },
  READY: {
    label: 'READY',
    color: 'var(--success)',
  },
  STARTED: {
    label: 'ACTIVE',
    color: 'var(--primary)',
  },
  DOWN: {
    label: 'ECCENTRIC (DOWN)',
    color: 'var(--primary)',
  },
  UP: {
    label: 'CONCENTRIC (UP)',
    color: 'var(--primary)',
  },
  REP_COMPLETED: {
    label: 'REP COMPLETE',
    color: 'var(--primary)',
  },
  FINISHED: {
    label: 'FINISHED',
    color: 'var(--muted-foreground)',
  },
  RESET: {
    label: 'RESET',
    color: 'var(--muted-foreground)',
  },
}

export default function StatusPill({ state }: Props) {
  const cfg = STATE_CONFIG[state] ?? STATE_CONFIG.IDLE

  return (
    <div
      className="inline-flex items-center px-2.5 py-1 text-[11px] font-semibold uppercase"
      style={{
        background: 'var(--secondary)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        color: cfg.color,
        letterSpacing: '0.1em',
      }}
    >
      {cfg.label}
    </div>
  )
}
