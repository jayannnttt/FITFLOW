import { useState, useEffect } from 'react'
import TopNavBar from '../components/TopNavBar'
import type { HistoryEntry, Screen } from '../types'
import { fetchHistory } from '../services/api'

interface Props {
  onNavigate: (screen: Screen) => void
}

function formatDuration(sec: number): string {
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return m > 0 ? `${m}m ${s}s` : `${s}s`
}

const getScoreColor = (s: number) =>
  s >= 80 ? 'var(--success)' : s >= 60 ? 'var(--warning)' : 'var(--error)'

export default function HistoryScreen({ onNavigate }: Props) {
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    async function loadData() {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchHistory()
        if (isMounted) {
          setHistory(data)
          setLoading(false)
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load workout history log.')
          setLoading(false)
        }
      }
    }
    loadData()
    return () => {
      isMounted = false
    }
  }, [])

  const allExercises = [...new Set(history.map((h) => h.exercise))]
  const filtered = filter ? history.filter((h) => h.exercise === filter) : history

  const totalSessions = history.length
  const topScore = history.length > 0 ? Math.max(...history.map((h) => h.avg_score)) : 0

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <TopNavBar currentScreen="history" onNavigate={(s) => onNavigate(s)} />

      <div className="flex-1 overflow-y-auto px-6 md:px-8 py-6 md:py-8">
        <div className="max-w-[1120px] mx-auto space-y-6 animate-fade-up">
          {/* Header */}
          <div>
            <h1 className="font-bold text-[28px] text-white tracking-tight leading-tight">
              Workout History
            </h1>
            <p className="text-[13px] mt-1" style={{ color: 'var(--muted-foreground)' }}>
              Recorded workout performance log
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <div
              className="p-4 flex items-center justify-between"
              style={{
                background: 'var(--card)',
                border: '1px solid var(--error)',
                borderRadius: 'var(--radius)',
              }}
            >
              <div className="flex items-center gap-3">
                <span className="font-bold text-sm" style={{ color: 'var(--error)' }}>✕</span>
                <span className="text-[13px]" style={{ color: 'var(--foreground)' }}>
                  {error}
                </span>
              </div>
              <button
                onClick={() => window.location.reload()}
                className="px-3 py-1 text-[12px] font-medium cursor-pointer"
                style={{
                  background: 'var(--secondary)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                  color: 'var(--foreground)',
                }}
              >
                Retry
              </button>
            </div>
          )}

          {/* Stat Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { label: 'Total Sessions', value: totalSessions },
              { label: 'Logged Entries', value: totalSessions },
              { label: 'Top Form Score', value: `${Math.round(topScore)}%` },
            ].map((s) => (
              <div
                key={s.label}
                className="p-4 text-center"
                style={{
                  background: 'var(--card)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                }}
              >
                <div className="font-display font-bold text-[28px] text-white leading-none mb-1">
                  {s.value}
                </div>
                <div
                  className="text-[11px] uppercase tracking-wider"
                  style={{ color: 'var(--muted-foreground)' }}
                >
                  {s.label}
                </div>
              </div>
            ))}
          </div>

          {/* Filter Chips */}
          {allExercises.length > 0 && (
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setFilter('')}
                className="px-3 py-1 text-[12px] font-medium cursor-pointer transition-colors"
                style={{
                  background: 'var(--secondary)',
                  border: `1px solid ${!filter ? 'var(--primary)' : 'var(--border)'}`,
                  color: !filter ? 'var(--primary)' : 'var(--secondary-foreground)',
                  borderRadius: '4px',
                }}
              >
                All
              </button>
              {allExercises.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setFilter(ex)}
                  className="px-3 py-1 text-[12px] font-medium cursor-pointer transition-colors"
                  style={{
                    background: 'var(--secondary)',
                    border: `1px solid ${filter === ex ? 'var(--primary)' : 'var(--border)'}`,
                    color: filter === ex ? 'var(--primary)' : 'var(--secondary-foreground)',
                    borderRadius: '4px',
                  }}
                >
                  {ex}
                </button>
              ))}
            </div>
          )}

          {/* Sessions List */}
          {loading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className="skeleton-shimmer h-[56px]"
                  style={{
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius)',
                  }}
                />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div
              className="p-10 text-center"
              style={{
                background: 'var(--card)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
              }}
            >
              <div
                className="w-10 h-10 mx-auto mb-3 flex items-center justify-center text-lg"
                style={{
                  background: 'var(--secondary)',
                  color: 'var(--muted-foreground)',
                  borderRadius: 'var(--radius)',
                }}
              >
                ■
              </div>
              <h3 className="font-semibold text-[16px] mb-1" style={{ color: 'var(--muted-foreground)' }}>
                No workout history logged yet.
              </h3>
              <p className="text-[13px] mb-5" style={{ color: 'var(--muted-foreground)' }}>
                Complete your first workout to see it logged here!
              </p>
              <button
                onClick={() => onNavigate('home')}
                className="select-btn px-6 py-2.5 text-[13px] font-semibold uppercase tracking-wider cursor-pointer"
              >
                Start Training →
              </button>
            </div>
          ) : (
            <div
              style={{
                background: 'var(--card)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
              }}
            >
              {filtered.map((item, idx) => (
                <div
                  key={idx}
                  className="history-row p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  style={{
                    borderBottom: idx < filtered.length - 1 ? '1px solid var(--border)' : 'none',
                  }}
                >
                  <div className="min-w-0">
                    <div className="font-semibold text-[14px] text-white truncate">
                      {item.exercise}
                    </div>
                    <div className="text-[12px] mt-0.5" style={{ color: 'var(--muted-foreground)' }}>
                      {item.date} · {formatDuration(item.elapsed_time)}
                    </div>
                  </div>

                  <div className="flex items-center gap-6 self-end sm:self-center flex-shrink-0">
                    <div className="text-right">
                      <span className="font-bold text-[14px] text-white">
                        {item.reps} REPS
                      </span>
                      <span className="text-[12px] ml-2" style={{ color: 'var(--muted-foreground)' }}>
                        {item.sets} {item.sets === 1 ? 'set' : 'sets'}
                      </span>
                    </div>

                    <div
                      className="px-2.5 py-0.5 text-[12px] font-semibold uppercase"
                      style={{
                        color: getScoreColor(item.avg_score),
                        letterSpacing: '0.04em',
                      }}
                    >
                      {Math.round(item.avg_score)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
