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

export default function SummaryScreen({ summary: initialSummary, exerciseName, onTryAgain, onHome }: Props) {
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
    return () => { isMounted = false }
  }, [initialSummary])

  const reps = summaryData?.reps || 0
  const durationSec = summaryData?.duration_sec || 0
  const formScore = summaryData?.form_score || 0
  const calories = summaryData?.calories_burned || Math.max(1, Math.round(reps * 0.8))

  const scoreColor = formScore >= 80 ? '#10B981' : formScore >= 60 ? '#F59E0B' : '#EF4444'

  return (
    <div className="h-full flex items-center justify-center bg-mesh px-5 py-8 overflow-y-auto">
      <div className="glass-strong rounded-3xl p-6 sm:p-10 max-w-lg w-full text-center space-y-8 animate-fade-up border border-white/12 shadow-[0_20px_80px_rgba(0,0,0,0.7)] relative overflow-hidden">
        {/* Background Radial Glow */}
        <div
          className="absolute -top-30 -right-30 w-72 h-72 rounded-full opacity-20 pointer-events-none"
          style={{ background: 'radial-gradient(circle, #10B981 0%, transparent 70%)' }}
        />

        {/* Celebration Trophy Header */}
        <div className="space-y-3">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-3xl mx-auto shadow-[0_0_30px_rgba(16,185,129,0.2)]">
            🏅
          </div>
          <h1 className="font-black text-3xl text-white/95 tracking-tight">Workout Complete!</h1>
          <p className="text-xs font-mono text-white/40 uppercase tracking-widest">
            {exerciseName} • Performance Breakdown
          </p>
        </div>

        {/* Metrics Grid */}
        {loading ? (
          <div className="grid grid-cols-2 gap-4 animate-pulse">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="bg-white/4 rounded-2xl p-5 border border-white/8 h-24" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {/* Reps */}
            <div className="bg-white/4 rounded-2xl p-5 border border-white/8 text-center space-y-1">
              <div className="font-mono font-black text-3xl text-cyan-400">{reps}</div>
              <div className="font-mono text-[10px] text-white/40 uppercase tracking-wider">
                Total Reps
              </div>
            </div>

            {/* Duration */}
            <div className="bg-white/4 rounded-2xl p-5 border border-white/8 text-center space-y-1">
              <div className="font-mono font-black text-3xl text-purple-400">
                {formatDuration(durationSec)}
              </div>
              <div className="font-mono text-[10px] text-white/40 uppercase tracking-wider">
                Duration
              </div>
            </div>

            {/* Form Score */}
            <div className="bg-white/4 rounded-2xl p-5 border border-white/8 text-center space-y-1">
              <div className="font-mono font-black text-3xl" style={{ color: scoreColor }}>
                {formScore}%
              </div>
              <div className="font-mono text-[10px] text-white/40 uppercase tracking-wider">
                Form Score
              </div>
            </div>

            {/* Calories Burned */}
            <div className="bg-white/4 rounded-2xl p-5 border border-white/8 text-center space-y-1">
              <div className="font-mono font-black text-3xl text-amber-400">{calories}</div>
              <div className="font-mono text-[10px] text-white/40 uppercase tracking-wider">
                Calories (kcal)
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
          <button
            onClick={onTryAgain}
            className="w-full sm:w-1/2 py-3.5 rounded-xl font-mono text-xs font-bold tracking-wider uppercase bg-white/5 hover:bg-white/10 text-white/80 border border-white/10 transition-colors"
          >
            ↻ TRY AGAIN
          </button>
          <button
            onClick={onHome}
            className="w-full sm:w-1/2 py-3.5 rounded-xl font-mono text-xs font-bold tracking-wider uppercase text-black bg-cyan-400 hover:bg-cyan-300 transition-all shadow-[0_0_25px_rgba(0,212,255,0.3)]"
          >
            ← BACK TO HOME
          </button>
        </div>
      </div>
    </div>
  )
}
