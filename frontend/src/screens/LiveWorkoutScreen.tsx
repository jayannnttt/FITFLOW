import { useEffect, useRef } from 'react'
import type { ExerciseConfig, TrackingData } from '../types'
import StatusPill from '../components/StatusPill'
import FormScoreMeter from '../components/FormScoreMeter'

interface Props {
  exerciseName: string
  config: ExerciseConfig
  tracking: TrackingData
  wsConnected: boolean
  resetSession: () => void
  onEnd: () => void
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
    .toString()
    .padStart(2, '0')
  const s = Math.floor(seconds % 60)
    .toString()
    .padStart(2, '0')
  return `${m}:${s}`
}

export default function LiveWorkoutScreen({
  exerciseName,
  config,
  tracking,
  wsConnected,
  resetSession,
  onEnd,
}: Props) {
  const prevRepsRef = useRef(tracking.reps)
  const repPulse = tracking.reps !== prevRepsRef.current && tracking.reps > 0

  useEffect(() => {
    prevRepsRef.current = tracking.reps
  }, [tracking.reps])

  // Automatically end workout if backend signals FINISHED state
  useEffect(() => {
    if (tracking.finished || tracking.state === 'FINISHED') {
      onEnd()
    }
  }, [tracking.finished, tracking.state, onEnd])

  const handleResetClick = () => {
    resetSession()
  }

  const activeWarning = tracking.warnings && tracking.warnings.length > 0 ? tracking.warnings[0] : null

  return (
    <div className="h-full flex flex-col overflow-hidden bg-transparent relative">
      {/* Top Floating Glassmorphism HUD Bar */}
      <div className="absolute top-0 inset-x-0 z-30 px-5 md:px-8 py-4 flex items-center justify-between bg-gradient-to-b from-black/90 via-black/60 to-transparent">
        {/* Left Badge */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 font-black text-lg">
            ⚡
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-black text-lg text-white/95 tracking-tight uppercase">
                {exerciseName}
              </h1>
              <StatusPill state={tracking.state} />
            </div>
            <div className="font-mono text-xs text-white/40 tracking-wider">
              {config.target_reps} REPS TARGET • SET {(tracking.sets || 0) + 1}
            </div>
          </div>
        </div>

        {/* Center Live Workout Stopwatch Timer */}
        <div className="glass px-4 py-1.5 rounded-xl border border-white/10 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="font-mono font-bold text-sm tracking-widest text-cyan-400">
            {formatTime(tracking.elapsed_time || 0)}
          </span>
        </div>

        {/* Right Connection Status */}
        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono">
            <span
              className={`w-2 h-2 rounded-full ${
                wsConnected ? 'bg-emerald-400 animate-pulse glow-cyan' : 'bg-rose-500'
              }`}
            />
            <span className="text-white/40 text-[10px]">
              {wsConnected ? 'LIVE STREAM' : 'RECONNECTING'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Viewport Container Overlay Layer */}
      <div className="relative flex-1 min-h-0 w-full h-full flex items-center justify-center overflow-hidden">
        {/* Left Side Floating Telemetry Panel */}
        <div className="absolute left-5 md:left-8 top-24 z-20 space-y-4 pointer-events-none">
          {/* Form Score Gauge */}
          <div className="glass-strong p-4 rounded-2xl border border-white/10 pointer-events-auto">
            <FormScoreMeter score={tracking.form_score || 0} size={110} />
          </div>

          {/* Primary Joint Angle Card */}
          <div className="glass-strong p-3.5 rounded-xl border border-white/10 text-center pointer-events-auto">
            <div className="font-mono text-[9px] text-white/40 uppercase tracking-widest mb-0.5">
              PRIMARY JOINT ({config.primary_joint})
            </div>
            <div className="font-mono font-black text-xl text-cyan-400">
              {tracking.current_angle !== null && tracking.current_angle !== undefined
                ? `${Math.round(tracking.current_angle)}°`
                : '--°'}
            </div>
          </div>
        </div>

        {/* Right Side Hero Rep Counter Display */}
        <div className="absolute right-5 md:right-8 top-24 z-20 pointer-events-none">
          <div className="glass-strong p-6 rounded-2xl border border-white/12 text-center min-w-[140px] pointer-events-auto">
            <div className="font-mono text-[10px] text-cyan-400 tracking-widest uppercase mb-1">
              REPETITIONS
            </div>
            <div
              className={`font-mono font-black text-5xl md:text-6xl text-white tracking-tighter transition-transform duration-200 ${
                repPulse ? 'rep-pulse text-cyan-400' : ''
              }`}
            >
              {tracking.reps || 0}
            </div>
            <div className="font-mono text-[10px] text-white/40 tracking-wider mt-1 uppercase">
              / {config.target_reps} GOAL
            </div>
          </div>
        </div>

        {/* Active Warning Coaching Banner */}
        {activeWarning && (
          <div className="absolute bottom-28 inset-x-5 md:inset-x-auto md:left-1/2 md:-translate-x-1/2 z-30">
            <div className="glass-strong px-5 py-3 rounded-xl border border-amber-500/40 bg-amber-500/15 text-amber-300 text-xs font-semibold shadow-lg flex items-center gap-3 animate-fade-up">
              <span className="text-amber-400 text-sm">⚠️</span>
              <div>
                <span className="font-bold uppercase tracking-wider">{activeWarning.warning}: </span>
                <span className="text-white/90">{activeWarning.suggestion}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Floating Controls Bar */}
      <div className="absolute bottom-0 inset-x-0 z-30 p-5 md:p-6 bg-gradient-to-t from-black/95 via-black/70 to-transparent">
        <div className="max-w-md mx-auto flex items-center justify-center gap-4">
          <button
            onClick={handleResetClick}
            className="px-6 py-3 rounded-xl font-mono text-xs font-bold tracking-wider uppercase bg-white/5 hover:bg-white/10 text-white/70 hover:text-white border border-white/10 transition-colors"
          >
            RESET
          </button>
          <button
            onClick={onEnd}
            className="px-8 py-3 rounded-xl font-mono text-xs font-bold tracking-wider uppercase bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 border border-rose-500/40 transition-all shadow-[0_0_20px_rgba(244,63,94,0.2)]"
          >
            END WORKOUT
          </button>
        </div>
      </div>
    </div>
  )
}
