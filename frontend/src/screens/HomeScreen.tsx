import { useState, useEffect } from 'react'
import TopNavBar from '../components/TopNavBar'
import type { Category, Screen, HistoryEntry } from '../types'
import { fetchCategories, fetchHistory } from '../services/api'

interface Props {
  onNavigate: (screen: Screen) => void
  onSelectCategory: (cat: Category) => void
}

const CATEGORY_META: Record<string, { accent: string; icon: string; num: string }> = {
  'UPPER BODY': { accent: '#00d4ff', icon: '💪', num: '01' },
  'LOWER BODY': { accent: '#7b2fff', icon: '🦵', num: '02' },
  'CORE': { accent: '#ff2d78', icon: '◎', num: '03' },
  'FULL BODY / CARDIO': { accent: '#ff8c42', icon: '⚡', num: '04' },
}

export default function HomeScreen({ onNavigate, onSelectCategory }: Props) {
  const [categories, setCategories] = useState<Category[]>([])
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    async function loadData() {
      try {
        setLoading(true)
        setError(null)
        const [cats, hist] = await Promise.all([
          fetchCategories().catch(() => []),
          fetchHistory().catch(() => []),
        ])
        if (isMounted) {
          setCategories(cats)
          setHistory(hist)
          setLoading(false)
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Unable to connect to AI Fitness Coach server.')
          setLoading(false)
        }
      }
    }
    loadData()
    return () => { isMounted = false }
  }, [])

  const totalExercises = categories.reduce((sum, c) => sum + (c.exercises?.length || 0), 0)
  const lastSession = history.length > 0 ? history[history.length - 1] : null

  const scoreColor = (s: number) => (s >= 80 ? '#10B981' : s >= 60 ? '#F59E0B' : '#EF4444')

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <TopNavBar currentScreen="home" onNavigate={(s) => onNavigate(s)} />

      <div className="flex-1 overflow-y-auto px-5 md:px-8 py-8 md:py-10">
        <div className="max-w-6xl mx-auto space-y-8">
          {error && (
            <div
              className="rounded-xl px-4 py-3 flex items-center justify-between animate-fade-up"
              style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)' }}
            >
              <div className="flex items-center gap-2">
                <span style={{ color: '#EF4444' }}>⚠</span>
                <span className="text-sm" style={{ color: 'rgba(240,240,248,0.8)' }}>
                  {error}
                </span>
              </div>
              <button
                onClick={() => window.location.reload()}
                className="text-xs font-mono underline"
                style={{ color: '#EF4444' }}
              >
                Retry
              </button>
            </div>
          )}

          {/* Hero Banner */}
          <div
            className="animate-fade-up rounded-2xl p-6 md:p-8 relative overflow-hidden"
            style={{
              background: 'linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(123,47,255,0.08) 100%)',
              border: '1px solid rgba(0,212,255,0.15)',
            }}
          >
            <div
              className="absolute top-0 right-0 w-64 h-64 rounded-full opacity-20 pointer-events-none"
              style={{
                background: 'radial-gradient(circle, #00d4ff 0%, transparent 70%)',
                transform: 'translate(30%, -30%)',
              }}
            />
            <div className="relative z-10 max-w-lg">
              <div
                className="font-mono text-xs tracking-widest mb-3 uppercase"
                style={{ color: 'rgba(0,212,255,0.7)', letterSpacing: '0.2em' }}
              >
                AI-Powered Training
              </div>
              <h1
                className="font-black leading-none mb-3"
                style={{ fontSize: 'clamp(1.6rem, 4vw, 2.6rem)', letterSpacing: '-0.03em', color: 'rgba(240,240,248,0.95)' }}
              >
                Ready for today's <span className="text-gradient-cyan">workout?</span>
              </h1>
              <p className="text-sm mb-6" style={{ color: 'rgba(240,240,248,0.45)', lineHeight: '1.7' }}>
                Real-time posture calibration, rep counting, and form coaching — powered by computer vision.
              </p>

              {/* Stat pills */}
              <div className="flex flex-wrap gap-3">
                {[
                  { label: 'Categories', value: categories.length },
                  { label: 'Exercises', value: totalExercises },
                  { label: '🔥 Total Logged', value: history.length },
                ].map((stat) => (
                  <div
                    key={stat.label}
                    className="px-3 py-1.5 rounded-full flex items-center gap-2"
                    style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
                  >
                    <span className="font-black text-sm" style={{ color: '#00d4ff' }}>
                      {stat.value}
                    </span>
                    <span className="text-xs" style={{ color: 'rgba(240,240,248,0.4)' }}>
                      {stat.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Section Header */}
          <div className="animate-fade-up stagger-1">
            <div
              className="font-mono text-xs tracking-widest uppercase mb-1"
              style={{ color: 'rgba(240,240,248,0.3)', letterSpacing: '0.15em' }}
            >
              Training Categories
            </div>
            <h2 className="font-bold text-lg" style={{ color: 'rgba(240,240,248,0.9)', letterSpacing: '-0.02em' }}>
              Choose a Category
            </h2>
          </div>

          {/* Category Grid */}
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="glass rounded-2xl p-6 animate-pulse" style={{ height: 180 }}>
                  <div className="h-3 rounded-full mb-4" style={{ background: 'rgba(255,255,255,0.06)', width: '40%' }} />
                  <div className="h-5 rounded-full mb-2" style={{ background: 'rgba(255,255,255,0.08)', width: '70%' }} />
                  <div className="h-3 rounded-full" style={{ background: 'rgba(255,255,255,0.04)', width: '90%' }} />
                </div>
              ))}
            </div>
          ) : categories.length === 0 ? (
            <div className="glass rounded-2xl p-10 text-center animate-fade-up">
              <div className="text-3xl mb-3">⚡</div>
              <p className="text-sm" style={{ color: 'rgba(240,240,248,0.4)' }}>
                No categories found. Check server connection.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-up stagger-2">
              {categories.map((cat, i) => {
                const meta = CATEGORY_META[cat.name] ?? { accent: '#00d4ff', icon: '◈', num: '0' + (i + 1) }
                return (
                  <button
                    key={cat.key}
                    onClick={() => onSelectCategory(cat)}
                    className="exercise-card glass rounded-2xl p-5 text-left group"
                    style={{ border: `1px solid rgba(255,255,255,0.07)` }}
                  >
                    <div
                      className="font-mono text-xs mb-4 tracking-widest"
                      style={{ color: 'rgba(240,240,248,0.25)', letterSpacing: '0.15em' }}
                    >
                      CATEGORY {meta.num}
                    </div>
                    <div
                      className="w-9 h-9 rounded-xl flex items-center justify-center text-base mb-4"
                      style={{ background: `${meta.accent}14`, color: meta.accent, border: `1px solid ${meta.accent}28` }}
                    >
                      {meta.icon}
                    </div>
                    <h3
                      className="font-bold text-base mb-1 leading-tight"
                      style={{ color: 'rgba(240,240,248,0.95)', letterSpacing: '-0.01em' }}
                    >
                      {cat.name}
                    </h3>
                    <p className="text-xs" style={{ color: 'rgba(240,240,248,0.38)' }}>
                      {cat.exercises.length} AI-Guided Exercises
                    </p>
                    <div
                      className="mt-4 h-px"
                      style={{ background: `linear-gradient(to right, ${meta.accent}28, transparent)` }}
                    />
                    <div className="mt-3 flex items-center justify-between">
                      <span
                        className="text-xs"
                        style={{ color: meta.accent, fontSize: '0.65rem', letterSpacing: '0.08em', fontFamily: 'var(--font-mono)' }}
                      >
                        EXPLORE →
                      </span>
                    </div>
                  </button>
                )
              })}
            </div>
          )}

          {/* Recent Session Preview */}
          {lastSession && (
            <div className="animate-fade-up stagger-3">
              <div
                className="font-mono text-xs tracking-widest uppercase mb-3"
                style={{ color: 'rgba(240,240,248,0.3)', letterSpacing: '0.15em' }}
              >
                Last Session
              </div>
              <div
                className="glass rounded-2xl p-5 flex items-center justify-between gap-4 cursor-pointer hover:border-white/15 transition-colors"
                style={{ border: '1px solid rgba(255,255,255,0.07)' }}
                onClick={() => onNavigate('history')}
              >
                <div className="flex items-center gap-4 min-w-0">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center text-base flex-shrink-0"
                    style={{ background: 'rgba(0,212,255,0.1)', color: '#00d4ff', border: '1px solid rgba(0,212,255,0.2)' }}
                  >
                    ◈
                  </div>
                  <div className="min-w-0">
                    <div className="font-semibold text-sm truncate" style={{ color: 'rgba(240,240,248,0.9)' }}>
                      {lastSession.exercise}
                    </div>
                    <div
                      className="font-mono text-xs mt-0.5"
                      style={{ color: 'rgba(240,240,248,0.35)', letterSpacing: '0.06em' }}
                    >
                      {lastSession.date} · {lastSession.reps} reps · {lastSession.sets} set
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4 flex-shrink-0">
                  <div className="text-right hidden sm:block">
                    <div className="font-black text-lg" style={{ color: scoreColor(lastSession.avg_score) }}>
                      {lastSession.avg_score}%
                    </div>
                    <div className="font-mono text-xs" style={{ color: 'rgba(240,240,248,0.3)', letterSpacing: '0.06em' }}>
                      Form Score
                    </div>
                  </div>
                  <span style={{ color: 'rgba(240,240,248,0.25)' }}>→</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
