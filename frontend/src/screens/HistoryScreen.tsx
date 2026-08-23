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

const scoreColor = (s: number) => (s >= 80 ? '#10B981' : s >= 60 ? '#F59E0B' : '#EF4444')
const scoreBg = (s: number) => (s >= 80 ? 'rgba(16,185,129,0.1)' : s >= 60 ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)')
const scoreBorder = (s: number) => (s >= 80 ? 'rgba(16,185,129,0.25)' : s >= 60 ? 'rgba(245,158,11,0.25)' : 'rgba(239,68,68,0.25)')

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
    return () => { isMounted = false }
  }, [])

  const allExercises = [...new Set(history.map((h) => h.exercise))]
  const filtered = filter ? history.filter((h) => h.exercise === filter) : history

  const totalSessions = history.length
  const topScore = history.length > 0 ? Math.max(...history.map((h) => h.avg_score)) : 0

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <TopNavBar currentScreen="history" onNavigate={(s) => onNavigate(s)} />

      <div className="flex-1 overflow-y-auto px-5 md:px-8 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="animate-fade-up">
            <div
              className="font-mono text-xs tracking-widest uppercase mb-1"
              style={{ color: 'rgba(240,240,248,0.3)', letterSpacing: '0.15em' }}
            >
              Performance Log
            </div>
            <h1
              className="font-black text-2xl md:text-3xl mb-1"
              style={{ color: 'rgba(240,240,248,0.95)', letterSpacing: '-0.02em' }}
            >
              Workout History
            </h1>
            <p className="text-sm" style={{ color: 'rgba(240,240,248,0.4)' }}>
              Recorded AI coaching sessions
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <div
              className="rounded-xl px-4 py-3 animate-fade-up"
              style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#EF4444' }}
            >
              ⚠ {error}
            </div>
          )}

          {/* Stat Summary Cards */}
          <div className="animate-fade-up stagger-1 grid grid-cols-3 gap-3">
            {[
              { label: 'Total Sessions', value: totalSessions, color: '#00d4ff' },
              { label: '🔥 Active Log', value: `${totalSessions} Entries`, color: '#ff8c42' },
              { label: 'Top Form Score', value: `${topScore}%`, color: '#10B981' },
            ].map((s) => (
              <div
                key={s.label}
                className="glass rounded-2xl p-4 text-center"
                style={{ border: `1px solid ${s.color}18` }}
              >
                <div className="font-black text-xl md:text-2xl mb-1" style={{ color: s.color }}>
                  {s.value}
                </div>
                <div
                  className="font-mono text-xs"
                  style={{ color: 'rgba(240,240,248,0.35)', letterSpacing: '0.08em', fontSize: '0.62rem' }}
                >
                  {s.label.toUpperCase()}
                </div>
              </div>
            ))}
          </div>

          {/* Filter Chips */}
          {allExercises.length > 0 && (
            <div className="animate-fade-up stagger-2 flex gap-2 flex-wrap">
              <button
                onClick={() => setFilter('')}
                className="category-chip glass px-3 py-1.5 rounded-full text-xs font-semibold"
                style={{
                  border: `1px solid ${!filter ? 'rgba(0,212,255,0.4)' : 'rgba(255,255,255,0.08)'}`,
                  color: !filter ? '#00d4ff' : 'rgba(240,240,248,0.4)',
                  background: !filter ? 'rgba(0,212,255,0.08)' : undefined,
                  letterSpacing: '0.06em',
                }}
              >
                All
              </button>
              {allExercises.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setFilter(ex)}
                  className="category-chip glass px-3 py-1.5 rounded-full text-xs font-semibold"
                  style={{
                    border: `1px solid ${filter === ex ? 'rgba(0,212,255,0.4)' : 'rgba(255,255,255,0.08)'}`,
                    color: filter === ex ? '#00d4ff' : 'rgba(240,240,248,0.4)',
                    background: filter === ex ? 'rgba(0,212,255,0.08)' : undefined,
                    letterSpacing: '0.06em',
                  }}
                >
                  {ex}
                </button>
              ))}
            </div>
          )}

          {/* Sessions List */}
          {loading ? (
            <div className="space-y-2 animate-fade-up">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="glass rounded-xl p-4 animate-pulse h-16" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="glass rounded-2xl p-12 text-center animate-fade-up">
              <div className="text-4xl mb-4">◎</div>
              <h3 className="font-bold text-lg mb-2" style={{ color: 'rgba(240,240,248,0.7)' }}>
                No workout history recorded yet.
              </h3>
              <p className="text-sm mb-6" style={{ color: 'rgba(240,240,248,0.35)' }}>
                Complete your first workout to see it logged here!
              </p>
              <button
                onClick={() => onNavigate('home')}
                className="select-btn px-6 py-3 rounded-xl text-sm font-bold"
                style={{ background: 'rgba(0,212,255,0.1)', color: '#00d4ff', border: '1px solid rgba(0,212,255,0.25)' }}
              >
                Start Training →
              </button>
            </div>
          ) : (
            <div className="animate-fade-up stagger-3 space-y-3">
              {filtered.map((item, idx) => (
                <div
                  key={idx}
                  className="glass rounded-2xl p-4 flex items-center justify-between gap-4 border border-white/8 hover:border-white/15 transition-all"
                >
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 font-black text-sm flex-shrink-0">
                      ⚡
                    </div>
                    <div className="min-w-0">
                      <div className="font-bold text-sm text-white/90 truncate">{item.exercise}</div>
                      <div className="font-mono text-xs text-white/40 mt-0.5">
                        {item.date} • {formatDuration(item.elapsed_time)}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 flex-shrink-0">
                    <div className="text-right">
                      <div className="font-mono font-bold text-sm text-white/90">{item.reps} REPS</div>
                      <div className="font-mono text-[10px] text-white/40">{item.sets} Set</div>
                    </div>

                    <div
                      className="px-3 py-1.5 rounded-xl font-mono font-bold text-sm text-center"
                      style={{
                        background: scoreBg(item.avg_score),
                        color: scoreColor(item.avg_score),
                        border: `1px solid ${scoreBorder(item.avg_score)}`,
                      }}
                    >
                      {item.avg_score}%
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
