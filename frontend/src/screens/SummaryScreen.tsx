import { useEffect, useState } from 'react'
import type { SessionSummary } from '../types'
import { fetchSummary } from '../services/api'

interface Props {
  summary: SessionSummary | null
  exerciseName: string
  onTryAgain: () => void
  onHome: () => void
}

function formatDuration(sec: number): string {
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

export default function SummaryScreen({
  summary: initialSummary,
  exerciseName,
  onTryAgain,
  onHome,
}: Props) {
  const [summaryData, setSummaryData] = useState<SessionSummary | null>(initialSummary)
  const [loading, setLoading] = useState(!initialSummary)

  useEffect(() => {
    let isMounted = true
    async function loadSummary() {
      if (initialSummary && initialSummary.has_summary) return
      try {
        setLoading(true)
        const data = await fetchSummary()
        if (isMounted && data && data.has_summary) {
          setSummaryData(data)
        }
      } catch (err) {
        console.error('Error loading summary:', err)
      } finally {
        if (isMounted) setLoading(false)
      }
    }
    loadSummary()
    return () => {
      isMounted = false
    }
  }, [initialSummary])

  const reps = summaryData?.reps || 0
  const durationSec = summaryData?.duration_sec || 0
  const formScore = summaryData?.form_score || 0
  const calories = summaryData?.calories_burned || Math.max(1, Math.round(reps * 0.8))

  const scoreColor =
    formScore >= 80 ? 'var(--success)' : formScore >= 60 ? 'var(--warning)' : 'var(--error)'

  return (
    <div className="h-full flex items-center justify-center px-6 py-8 overflow-y-auto">
      <div
        className="p-6 sm:p-8 max-w-[480px] w-full text-center space-y-6 animate-fade-up"
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius)',
        }}
      >
        {/* Header */}
        <div className="space-y-1">
          <div className="text-2xl font-bold leading-none mb-2" style={{ color: 'var(--success)' }}>
            ✓
          </div>
          <h1 className="font-bold text-[28px] text-white tracking-tight leading-tight">
            WORKOUT COMPLETE
          </h1>
          <p className="text-[13px]" style={{ color: 'var(--muted-foreground)' }}>
            {exerciseName}
          </p>
        </div>

        {/* Metrics Grid (4 items) */}
        {loading ? (
          <div className="grid grid-cols-2 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="skeleton-shimmer h-[80px]"
                style={{
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                }}
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {/* Reps */}
            <div
              className="p-4 text-center"
              style={{
                background: 'var(--secondary)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
              }}
            >
              <div className="font-display font-extrabold text-[36px] text-white leading-none">
                {reps}
              </div>
              <div className="text-[11px] uppercase tracking-wider mt-1" style={{ color: 'var(--muted-foreground)' }}>
                Total Reps
              </div>
            </div>

            {/* Duration */}
            <div
              className="p-4 text-center"
              style={{
                background: 'var(--secondary)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
              }}
            >
              <div className="font-display font-extrabold text-[36px] text-white leading-none">
                {formatDuration(durationSec)}
              </div>
              <div className="text-[11px] uppercase tracking-wider mt-1" style={{ color: 'var(--muted-foreground)' }}>
                Duration
              </div>
            </div>

            {/* Form Score */}
            <div
              className="p-4 text-center"
              style={{
                background: 'var(--secondary)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
              }}
            >
              <div
                className="font-display font-extrabold text-[36px] leading-none"
                style={{ color: scoreColor }}
              >
                {Math.round(formScore)}%
              </div>
              <div className="text-[11px] uppercase tracking-wider mt-1" style={{ color: 'var(--muted-foreground)' }}>
                Form Score
              </div>
            </div>

            {/* Calories Burned */}
            <div
              className="p-4 text-center"
              style={{
                background: 'var(--secondary)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
              }}
            >
              <div className="font-display font-extrabold text-[36px] text-white leading-none">
                {calories}
              </div>
              <div className="text-[11px] uppercase tracking-wider mt-1" style={{ color: 'var(--muted-foreground)' }}>
                Calories (kcal)
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
          <button
            onClick={onTryAgain}
            className="w-full sm:w-1/2 py-3 text-[13px] font-semibold uppercase tracking-wider cursor-pointer transition-colors"
            style={{
              background: 'var(--secondary)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
              color: 'var(--foreground)',
            }}
          >
            TRY AGAIN
          </button>
          <button
            onClick={onHome}
            className="select-btn w-full sm:w-1/2 py-3 text-[13px] font-semibold uppercase tracking-wider cursor-pointer"
          >
            BACK TO HOME
          </button>
        </div>
      </div>
    </div>
  )
}
