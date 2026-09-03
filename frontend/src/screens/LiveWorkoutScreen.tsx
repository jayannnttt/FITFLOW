import { useEffect, useRef, useState } from 'react'
import type { ExerciseConfig, TrackingData } from '../types'
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
  const [repScale, setRepScale] = useState(false)
  const [localSeconds, setLocalSeconds] = useState(0)
  const prevRepsRef = useRef(tracking.reps)

  useEffect(() => {
    const interval = setInterval(() => {
      setLocalSeconds((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (tracking.reps !== prevRepsRef.current && tracking.reps > 0) {
      setRepScale(true)
      const timer = setTimeout(() => setRepScale(false), 200)
      prevRepsRef.current = tracking.reps
      return () => clearTimeout(timer)
    }
    prevRepsRef.current = tracking.reps
  }, [tracking.reps])

  // Automatically end workout if backend signals FINISHED state
  useEffect(() => {
    if (tracking.finished || tracking.state === 'FINISHED') {
      onEnd()
    }
  }, [tracking.finished, tracking.state, onEnd])

  const activeWarning = tracking.warnings && tracking.warnings.length > 0 ? tracking.warnings[0] : null
  const setNumber = (tracking.sets || 0) + 1

  const displaySeconds =
    tracking.elapsed_time && tracking.elapsed_time > 0
      ? tracking.elapsed_time
      : localSeconds

  const handleResetClick = () => {
    setLocalSeconds(0)
    resetSession()
  }

  return (
    <div className="h-full flex flex-col overflow-hidden bg-transparent relative select-none">
      {/* Top Bar (Exercise info, timer, status dot) */}
      <div
        className="absolute top-0 inset-x-0 z-30 px-6 md:px-8 py-3.5 flex items-center justify-between"
        style={{
          background: 'rgba(0, 0, 0, 0.8)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        }}
      >
        {/* Left: Exercise name + Set indicator */}
        <div className="flex items-center gap-3">
          <h1 className="font-semibold text-[16px] text-white uppercase tracking-tight leading-none">
            {exerciseName}
          </h1>
          <span className="text-[12px] uppercase font-medium" style={{ color: 'var(--muted-foreground)' }}>
            SET {setNumber}
          </span>
        </div>

        {/* Center: Live Timer */}
        <div className="flex items-center gap-2">
          <span className="w-[6px] h-[6px] rounded-full bg-[#e8491d] flex-shrink-0" />
          <span className="font-display font-bold text-[20px] text-white tracking-wider leading-none">
            {formatTime(displaySeconds)}
          </span>
        </div>

        {/* Right: Tiny 6px Connection Dot */}
        <div className="flex items-center">
          <span
            className={`w-[6px] h-[6px] rounded-full flex-shrink-0 transition-opacity ${
              wsConnected ? 'bg-[#34c759] animate-[pulse_2s_ease-in-out_infinite]' : 'bg-[#e8491d]'
            }`}
            title={wsConnected ? 'Connected' : 'Disconnected'}
          />
        </div>
      </div>

      {/* Main Viewport Container */}
      <div className="relative flex-1 min-h-0 w-full h-full overflow-hidden pointer-events-none">
        {/* Left Side — Form Score & Joint Angle */}
        <div className="absolute left-6 md:left-8 top-16 md:top-20 z-20 space-y-3 pointer-events-auto">
          {/* Form Score Panel */}
          <div
            className="p-4 flex flex-col items-center justify-center text-center"
            style={{
              background: 'rgba(0, 0, 0, 0.75)',
              borderRadius: 'var(--radius)',
            }}
          >
            <FormScoreMeter score={tracking.form_score || 0} size={110} />
            <div className="mt-1">
              <span className="font-display font-bold text-[28px] text-white leading-none">
                {Math.round(tracking.form_score || 0)}%
              </span>
              <div
                className="text-[10px] uppercase font-medium tracking-wider"
                style={{ color: 'var(--muted-foreground)' }}
              >
                FORM
              </div>
            </div>
          </div>

          {/* Joint Angle Readout */}
          <div
            className="px-4 py-3 text-center"
            style={{
              background: 'rgba(0, 0, 0, 0.75)',
              borderRadius: 'var(--radius)',
            }}
          >
            <div className="font-display font-bold text-[24px] text-white leading-none">
              {tracking.current_angle !== null && tracking.current_angle !== undefined
                ? `${Math.round(tracking.current_angle)}°`
                : '--°'}
            </div>
            <div
              className="text-[10px] uppercase font-medium tracking-wider mt-0.5"
              style={{ color: 'var(--muted-foreground)' }}
            >
              {config.primary_joint ? config.primary_joint.toUpperCase() : 'JOINT ANGLE'}
            </div>
          </div>
        </div>

        {/* Right Side — Rep Counter (THE HERO) */}
        <div className="absolute right-6 md:right-8 top-16 md:top-20 z-20 text-right pointer-events-auto">
          <div
            className="font-display font-extrabold text-[60px] md:text-[80px] text-white leading-none"
            style={{
              transform: repScale ? 'scale(1.1)' : 'scale(1)',
              transition: 'transform 200ms ease',
              textShadow: '0 2px 20px rgba(0,0,0,0.8)',
            }}
          >
            {tracking.reps || 0}
          </div>
          <div
            className="text-[14px] font-medium mt-1"
            style={{
              color: 'var(--muted-foreground)',
              textShadow: '0 2px 10px rgba(0,0,0,0.8)',
            }}
          >
            / {config.target_reps}
          </div>
        </div>

        {/* Warning Coaching Banner */}
        {activeWarning && (
          <div className="absolute bottom-20 inset-x-6 md:inset-x-auto md:left-8 z-30 pointer-events-auto">
            <div
              className="px-4 py-2.5 text-[13px] text-white"
              style={{
                background: 'rgba(0, 0, 0, 0.85)',
                borderLeft: '3px solid var(--warning)',
                borderRadius: '0 6px 6px 0',
              }}
            >
              <span className="font-bold uppercase mr-2 tracking-wider">
                {activeWarning.warning}:
              </span>
              <span className="font-normal" style={{ color: 'var(--foreground)' }}>
                {activeWarning.suggestion}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Controls Bar */}
      <div
        className="absolute bottom-0 inset-x-0 z-30 px-6 py-3.5 flex items-center justify-center gap-4"
        style={{
          background: 'rgba(0, 0, 0, 0.85)',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        }}
      >
        <button
          onClick={handleResetClick}
          className="px-6 py-2.5 text-[13px] font-semibold uppercase tracking-wider cursor-pointer transition-colors hover:border-[var(--muted-foreground)]"
          style={{
            background: 'transparent',
            border: '1px solid var(--border)',
            color: 'var(--muted-foreground)',
            borderRadius: 'var(--radius)',
          }}
        >
          RESET
        </button>
        <button
          onClick={onEnd}
          className="select-btn px-8 py-2.5 text-[13px] font-semibold uppercase tracking-wider cursor-pointer"
        >
          END
        </button>
      </div>
    </div>
  )
}
