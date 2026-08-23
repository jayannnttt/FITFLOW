import type { WorkoutState } from '../types'

interface Props {
  state: WorkoutState
  score?: number
}

const STATE_CONFIG: Record<
  WorkoutState,
  { label: string; bg: string; text: string; border: string; dot: string; glow?: string }
> = {
  IDLE: {
    label: 'IDLE',
    bg: 'rgba(255, 255, 255, 0.05)',
    text: 'rgba(240, 240, 248, 0.5)',
    border: 'rgba(255, 255, 255, 0.1)',
    dot: 'rgba(240, 240, 248, 0.3)',
  },
  ALIGNING: {
    label: 'CALIBRATING POSTURE',
    bg: 'rgba(245, 158, 11, 0.12)',
    text: '#F59E0B',
    border: 'rgba(245, 158, 11, 0.3)',
    dot: '#F59E0B',
  },
  READY: {
    label: 'POSTURE CONFIRMED — READY',
    bg: 'rgba(16, 185, 129, 0.15)',
    text: '#10B981',
    border: 'rgba(16, 185, 129, 0.4)',
    dot: '#10B981',
    glow: '0 0 20px rgba(16, 185, 129, 0.3)',
  },
  STARTED: {
    label: 'ACTIVE TRACKING',
    bg: 'rgba(0, 212, 255, 0.12)',
    text: '#00d4ff',
    border: 'rgba(0, 212, 255, 0.3)',
    dot: '#00d4ff',
  },
  DOWN: {
    label: 'ECCENTRIC (DOWN)',
    bg: 'rgba(0, 212, 255, 0.15)',
    text: '#00d4ff',
    border: 'rgba(0, 212, 255, 0.4)',
    dot: '#00d4ff',
  },
  UP: {
    label: 'CONCENTRIC (UP)',
    bg: 'rgba(123, 47, 255, 0.15)',
    text: '#7b2fff',
    border: 'rgba(123, 47, 255, 0.4)',
    dot: '#7b2fff',
  },
  REP_COMPLETED: {
    label: 'REP COMPLETED ✓',
    bg: 'rgba(16, 185, 129, 0.2)',
    text: '#10B981',
    border: 'rgba(16, 185, 129, 0.5)',
    dot: '#10B981',
    glow: '0 0 25px rgba(16, 185, 129, 0.4)',
  },
  FINISHED: {
    label: 'SESSION COMPLETE',
    bg: 'rgba(123, 47, 255, 0.2)',
    text: '#a855f7',
    border: 'rgba(123, 47, 255, 0.4)',
    dot: '#a855f7',
  },
  RESET: {
    label: 'RESET',
    bg: 'rgba(255, 255, 255, 0.1)',
    text: '#ffffff',
    border: 'rgba(255, 255, 255, 0.2)',
    dot: '#ffffff',
  },
}

export default function StatusPill({ state }: Props) {
  const cfg = STATE_CONFIG[state] ?? STATE_CONFIG.IDLE

  return (
    <div
      className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono tracking-wider font-semibold transition-all duration-300"
      style={{
        background: cfg.bg,
        color: cfg.text,
        border: `1px solid ${cfg.border}`,
        boxShadow: cfg.glow,
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full animate-pulse flex-shrink-0"
        style={{ background: cfg.dot }}
      />
      <span>{cfg.label}</span>
    </div>
  )
}
