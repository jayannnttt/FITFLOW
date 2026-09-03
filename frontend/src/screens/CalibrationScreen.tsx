import type { ExerciseConfig, AlignmentData } from '../types'
import StatusPill from '../components/StatusPill'

interface Props {
  exerciseName: string
  config: ExerciseConfig
  alignment: AlignmentData
  wsConnected: boolean
  cameraActive: boolean
  error: string | null
  startActiveTracking: () => void
  onCancel: () => void
}

export default function CalibrationScreen({
  exerciseName,
  alignment,
  error,
  startActiveTracking,
  onCancel,
}: Props) {
  const fillPercent = Math.min(100, Math.max(0, alignment.score))

  const coachingText =
    alignment.coaching_messages && alignment.coaching_messages.length > 0
      ? alignment.coaching_messages[0]
      : 'Step into camera view and align your posture.'

  return (
    <div className="h-full flex flex-col overflow-hidden relative">
      {/* Top HUD Header */}
      <div
        className="absolute top-0 inset-x-0 z-30 px-6 md:px-8 py-3.5 flex items-center justify-between"
        style={{
          background: 'var(--card)',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <div className="flex items-center gap-4">
          <button
            onClick={onCancel}
            className="text-[12px] font-medium transition-colors cursor-pointer hover:text-white"
            style={{ color: 'var(--muted-foreground)' }}
          >
            ← Cancel
          </button>
          <div>
            <div
              className="text-[11px] uppercase tracking-wider font-medium"
              style={{ color: 'var(--muted-foreground)' }}
            >
              POSTURE CALIBRATION
            </div>
            <h1 className="font-bold text-[18px] text-white tracking-tight leading-none mt-0.5">
              {exerciseName}
            </h1>
          </div>
        </div>

        {/* Readiness Status Pill */}
        <StatusPill state={alignment.ready ? 'READY' : 'ALIGNING'} />
      </div>

      {/* Main Viewport Container */}
      <div className="relative flex-1 min-h-0 w-full h-full flex items-center justify-center overflow-hidden">
        {/* Error overlay if camera or WebSocket fails */}
        {error && (
          <div
            className="absolute inset-0 z-40 flex items-center justify-center p-6"
            style={{ background: 'rgba(0, 0, 0, 0.85)' }}
          >
            <div
              className="p-6 max-w-md w-full text-center space-y-4"
              style={{
                background: 'var(--card)',
                border: '1px solid var(--error)',
                borderRadius: 'var(--radius)',
              }}
            >
              <div className="font-bold text-lg" style={{ color: 'var(--error)' }}>
                Camera Access Required
              </div>
              <p className="text-[13px]" style={{ color: 'var(--secondary-foreground)' }}>
                {error}
              </p>
              <button
                onClick={onCancel}
                className="w-full py-2.5 text-[13px] font-semibold cursor-pointer"
                style={{
                  background: 'var(--secondary)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                  color: 'var(--foreground)',
                }}
              >
                Return to Library
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Alignment HUD & Coaching Panel */}
      <div className="absolute bottom-0 inset-x-0 z-30 p-6 md:p-8 pointer-events-none">
        <div className="max-w-2xl mx-auto space-y-3 pointer-events-auto">
          {/* Coaching Message Banner */}
          <div
            className="p-3.5 text-center text-[13px] transition-colors"
            style={{
              background: 'var(--card)',
              border: alignment.ready ? '1px solid var(--success)' : '1px solid var(--border)',
              borderRadius: 'var(--radius)',
              color: 'var(--foreground)',
            }}
          >
            {coachingText}
          </div>

          {/* Alignment Progress Bar & Start Action */}
          <div
            className="p-4 flex items-center justify-between gap-6"
            style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
            }}
          >
            <div className="flex-1 flex items-center gap-4">
              <div className="flex-1">
                <div className="flex items-center justify-between text-[11px] uppercase tracking-wider mb-1.5" style={{ color: 'var(--muted-foreground)' }}>
                  <span>ALIGNMENT</span>
                  <span className="font-display font-bold text-[20px] leading-none text-white">
                    {Math.round(alignment.score)}%
                  </span>
                </div>
                <div
                  className="w-full h-[6px] overflow-hidden"
                  style={{
                    background: 'var(--secondary)',
                    borderRadius: '3px',
                  }}
                >
                  <div
                    className="h-full transition-all duration-300"
                    style={{
                      width: `${fillPercent}%`,
                      background: alignment.ready ? 'var(--success)' : 'var(--primary)',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>
            </div>

            <button
              onClick={startActiveTracking}
              disabled={!alignment.ready && alignment.score < 50}
              className="select-btn px-6 py-3 font-semibold text-[13px] uppercase tracking-wider cursor-pointer flex-shrink-0 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {alignment.ready ? 'START WORKOUT' : 'CALIBRATING'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
