import type { ExerciseConfig } from '../types'

interface Props {
  name: string
  config: ExerciseConfig
  onClose: () => void
  onStart: () => void
}

export default function ExerciseDetailModal({ name, config, onClose, onStart }: Props) {
  const rules = config.alignment?.coaching_rules
    ? Object.values(config.alignment.coaching_rules)
    : [
        'Position yourself in clear view of the webcam.',
        'Align your posture with the semi-transparent Ghost Skeleton.',
        'Hold starting posture until calibration reaches 100%.',
      ]

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 animate-fade-in"
      style={{ background: 'rgba(0, 0, 0, 0.7)' }}
    >
      <div
        className="w-full max-w-[480px] p-6 sm:p-7 space-y-6 relative animate-fade-up"
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius)',
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-lg leading-none cursor-pointer transition-colors hover:text-white"
          style={{ color: 'var(--muted-foreground)' }}
          aria-label="Close"
        >
          ✕
        </button>

        {/* Header */}
        <div>
          <div
            className="text-[12px] uppercase tracking-wider mb-1.5"
            style={{ color: 'var(--muted-foreground)' }}
          >
            {config.category || 'WORKOUT'} · {config.type || 'REP_BASED'}
          </div>
          <h2 className="font-bold text-[24px] text-white tracking-tight leading-snug">
            {name}
          </h2>
          {config.primary_joint && (
            <div
              className="text-[12px] mt-1"
              style={{ color: 'var(--secondary-foreground)' }}
            >
              Primary Joint: <span className="text-white capitalize">{config.primary_joint}</span>
            </div>
          )}
        </div>

        {/* Meta section: Three columns with flat dividers */}
        <div
          className="grid grid-cols-3 py-3 px-1"
          style={{
            background: 'var(--secondary)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
          }}
        >
          <div className="text-center px-2">
            <div className="font-display font-semibold text-[20px] text-white leading-tight">
              {config.target_reps}
            </div>
            <div className="text-[11px] mt-0.5" style={{ color: 'var(--muted-foreground)' }}>
              Target Reps
            </div>
          </div>
          <div
            className="text-center px-2"
            style={{
              borderLeft: '1px solid var(--border)',
              borderRight: '1px solid var(--border)',
            }}
          >
            <div className="font-display font-semibold text-[20px] text-white leading-tight">
              {config.cooldown}s
            </div>
            <div className="text-[11px] mt-0.5" style={{ color: 'var(--muted-foreground)' }}>
              Cooldown
            </div>
          </div>
          <div className="text-center px-2">
            <div className="font-display font-semibold text-[20px] text-white leading-tight">
              ~10 kcal
            </div>
            <div className="text-[11px] mt-0.5" style={{ color: 'var(--muted-foreground)' }}>
              Est. Burn/min
            </div>
          </div>
        </div>

        {/* Posture Rules */}
        <div className="space-y-2">
          <div
            className="text-[12px] uppercase tracking-wider font-semibold"
            style={{ color: 'var(--foreground)' }}
          >
            Posture Calibration Rules
          </div>
          <ol className="space-y-1.5 text-[13px] list-decimal list-inside" style={{ color: 'var(--secondary-foreground)' }}>
            {rules.map((rule, idx) => (
              <li key={idx} className="leading-relaxed">
                <span>{rule}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Start Button */}
        <button
          onClick={onStart}
          className="select-btn w-full py-3.5 font-semibold text-[14px] uppercase tracking-wider cursor-pointer flex items-center justify-center gap-2"
        >
          START CALIBRATION
        </button>
      </div>
    </div>
  )
}
