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
  config,
  alignment,
  wsConnected,
  cameraActive,
  error,
  startActiveTracking,
  onCancel,
}: Props) {
  const scoreColor = alignment.score >= 80 ? '#10B981' : alignment.score >= 50 ? '#F59E0B' : '#EF4444'
  const fillPercent = Math.min(100, alignment.score)

  const coachingText =
    alignment.coaching_messages && alignment.coaching_messages.length > 0
      ? alignment.coaching_messages[0]
      : 'Step into camera view and align your body with the Ghost Skeleton target pose.'

  return (
    <div className="h-full flex flex-col overflow-hidden relative">
      {/* Top HUD Header */}
      <div className="absolute top-0 inset-x-0 z-30 px-5 md:px-8 py-4 flex items-center justify-between bg-gradient-to-b from-black/90 via-black/50 to-transparent">
        <div className="flex items-center gap-3">
          <button
            onClick={onCancel}
            className="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-white/60 hover:text-white text-xs font-mono tracking-wider transition-colors border border-white/10"
          >
            ← CANCEL
          </button>
          <div>
            <div className="font-mono text-[10px] text-cyan-400 tracking-widest uppercase">
              POSTURE CALIBRATION
            </div>
            <h1 className="font-black text-lg text-white/95 tracking-tight">{exerciseName}</h1>
          </div>
        </div>

        {/* Readiness Status Pill */}
        <StatusPill state={alignment.ready ? 'READY' : 'ALIGNING'} />
      </div>

      {/* Viewport Overlay Effects */}
      <div className="relative flex-1 min-h-0 w-full h-full flex items-center justify-center overflow-hidden">
        {/* Calibration Scanline effect */}
        <div className="calib-scanline pointer-events-none z-20" />

        {/* Error overlay if camera or WebSocket fails */}
        {error && (
          <div className="absolute inset-0 z-40 bg-black/90 flex items-center justify-center p-6">
            <div className="glass-strong rounded-2xl p-8 max-w-md text-center border border-rose-500/30">
              <div className="text-4xl mb-4 text-rose-500">📷</div>
              <h2 className="font-bold text-lg text-white/90 mb-2">Camera Access Required</h2>
              <p className="text-xs text-white/50 mb-6">{error}</p>
              <button
                onClick={onCancel}
                className="w-full py-3 rounded-xl font-bold text-xs bg-rose-500/15 text-rose-400 border border-rose-500/30 hover:bg-rose-500/25 transition-colors"
              >
                Return to Home
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Alignment HUD & Coaching Card */}
      <div className="absolute bottom-0 inset-x-0 z-30 p-5 md:p-8 bg-gradient-to-t from-black/95 via-black/80 to-transparent">
        <div className="max-w-2xl mx-auto space-y-4">
          {/* Coaching Message Banner */}
          <div
            className="glass rounded-xl p-3.5 border text-center transition-all duration-300"
            style={{
              borderColor: alignment.ready ? 'rgba(16,185,129,0.3)' : 'rgba(0,212,255,0.2)',
              background: alignment.ready ? 'rgba(16,185,129,0.08)' : 'rgba(0,212,255,0.05)',
            }}
          >
            <div className="text-xs font-semibold text-white/90 flex items-center justify-center gap-2">
              <span style={{ color: scoreColor }}>◈</span>
              <span>{coachingText}</span>
            </div>
          </div>

          {/* Alignment Score Meter & Action */}
          <div className="glass-strong rounded-2xl p-5 border border-white/10 flex items-center justify-between gap-4">
            <div className="flex-1 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-white/40 tracking-wider">AI POSTURE ALIGNMENT</span>
                <span className="font-bold text-base" style={{ color: scoreColor }}>
                  {alignment.score.toFixed(1)}%
                </span>
              </div>
              <div className="h-2 rounded-full bg-white/6 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-300"
                  style={{
                    width: `${fillPercent}%`,
                    background: `linear-gradient(90deg, ${scoreColor}80, ${scoreColor})`,
                    boxShadow: `0 0 15px ${scoreColor}60`,
                  }}
                />
              </div>
            </div>

            {/* Optional Manual Start Action */}
            <button
              onClick={startActiveTracking}
              disabled={!alignment.ready && alignment.score < 50}
              className={`px-6 py-3 rounded-xl font-mono font-bold text-xs tracking-wider uppercase transition-all duration-300 flex items-center gap-2 flex-shrink-0 ${
                alignment.ready || alignment.score >= 50
                  ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-black shadow-[0_0_25px_rgba(16,185,129,0.4)] hover:scale-105 active:scale-95 cursor-pointer'
                  : 'bg-white/5 text-white/30 border border-white/8 cursor-not-allowed'
              }`}
            >
              <span>▶</span>
              <span>{alignment.ready ? 'STARTING...' : 'CALIBRATING...'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
