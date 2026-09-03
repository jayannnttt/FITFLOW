import { useState, useEffect } from 'react'
import TopNavBar from '../components/TopNavBar'
import type { Category, Screen, HistoryEntry } from '../types'
import { fetchCategories, fetchHistory, requestExercise } from '../services/api'

interface Props {
  onNavigate: (screen: Screen) => void
  onSelectCategory: (cat: Category) => void
}

export default function HomeScreen({ onNavigate, onSelectCategory }: Props) {
  const [categories, setCategories] = useState<Category[]>([])
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Request Exercise Modal state
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [requestedExercise, setRequestedExercise] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [isSuccess, setIsSuccess] = useState(false)
  const [submittedExercise, setSubmittedExercise] = useState('')

  useEffect(() => {
    let isMounted = true
    async function loadData() {
      try {
        setLoading(true)
        setError(null)
        const [cats, hist] = await Promise.all([
          fetchCategories().catch((err) => {
            console.error('[API Error] fetchCategories failed:', err)
            return []
          }),
          fetchHistory().catch((err) => {
            console.error('[API Error] fetchHistory failed:', err)
            return []
          }),
        ])

        if (isMounted) {
          setCategories(cats)
          setHistory(hist)
          setLoading(false)
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Unable to connect to FITFLOW server.')
          setLoading(false)
        }
      }
    }
    loadData()
    return () => {
      isMounted = false
    }
  }, [])

  const totalExercises = categories.reduce((sum, c) => sum + (c.exercises?.length || 0), 0)
  const lastSession = history.length > 0 ? history[history.length - 1] : null

  const handleOpenModal = () => {
    setRequestedExercise('')
    setSubmitError(null)
    setIsSuccess(false)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    if (isSubmitting) return
    setIsModalOpen(false)
    setSubmitError(null)
    setIsSuccess(false)
  }

  const handleSubmitRequest = async (e: React.FormEvent) => {
    e.preventDefault()
    const sanitized = requestedExercise.trim()
    if (!sanitized) {
      setSubmitError('Please enter an exercise name.')
      return
    }

    try {
      setIsSubmitting(true)
      setSubmitError(null)
      await requestExercise(sanitized)
      setSubmittedExercise(sanitized)
      setIsSuccess(true)
      setRequestedExercise('')
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to submit request. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <TopNavBar currentScreen="home" onNavigate={(s) => onNavigate(s)} />

      <div className="flex-1 overflow-y-auto px-6 md:px-8 py-6 md:py-8">
        <div className="max-w-[1120px] mx-auto space-y-8 animate-fade-up">
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

          {/* Hero Section — The Athletic Cover */}
          <div
            className="p-6 md:p-8 flex flex-col md:flex-row md:items-center md:justify-between gap-6"
            style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
            }}
          >
            {/* Left side */}
            <div className="max-w-md">
              <h1 className="font-bold text-[36px] text-white tracking-tight leading-tight mb-2">
                Ready to train?
              </h1>
              <p className="text-[14px]" style={{ color: 'var(--muted-foreground)' }}>
                Pick a category to get started.
              </p>
            </div>

            {/* Right side: Three stat numbers displayed as stacked or inline rows */}
            <div className="flex flex-wrap sm:flex-nowrap items-center gap-8 sm:gap-12">
              <div>
                <div className="font-display font-extrabold text-[48px] text-white leading-none">
                  {totalExercises}
                </div>
                <div className="text-[12px] mt-1" style={{ color: 'var(--muted-foreground)' }}>
                  exercises
                </div>
              </div>
              <div>
                <div className="font-display font-extrabold text-[48px] text-white leading-none">
                  {categories.length}
                </div>
                <div className="text-[12px] mt-1" style={{ color: 'var(--muted-foreground)' }}>
                  categories
                </div>
              </div>
              <div>
                <div className="font-display font-extrabold text-[48px] text-white leading-none">
                  {history.length}
                </div>
                <div className="text-[12px] mt-1" style={{ color: 'var(--muted-foreground)' }}>
                  sessions
                </div>
              </div>
            </div>
          </div>

          {/* Section Heading */}
          <div>
            <h2 className="font-bold text-[24px] text-white tracking-tight">
              Categories
            </h2>
          </div>

          {/* Category Grid */}
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className="skeleton-shimmer p-5 h-[120px]"
                  style={{
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius)',
                  }}
                />
              ))}
            </div>
          ) : categories.length === 0 ? (
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
                No categories found.
              </h3>
              <p className="text-[13px]" style={{ color: 'var(--muted-foreground)' }}>
                Please check your server connection.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {categories.map((cat) => (
                <button
                  key={cat.key}
                  onClick={() => onSelectCategory(cat)}
                  className="exercise-card p-5 text-left cursor-pointer flex flex-col justify-between h-[120px]"
                >
                  <h3 className="font-bold text-[16px] text-white leading-snug">
                    {cat.name}
                  </h3>
                  <div className="text-[13px]" style={{ color: 'var(--muted-foreground)' }}>
                    {cat.exercises.length} exercises
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Stay Tuned for More Exercises Section */}
          <div
            onClick={handleOpenModal}
            className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer transition-colors hover:border-[var(--primary)]"
            style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
            }}
          >
            <div className="space-y-1">
              <div
                className="text-[11px] font-medium uppercase tracking-wider"
                style={{ color: 'var(--muted-foreground)' }}
              >
                Upcoming Additions
              </div>
              <h3 className="font-bold text-[18px] text-white tracking-tight leading-snug">
                STAY TUNED FOR MORE EXERCISES
              </h3>
              <p className="text-[13px]" style={{ color: 'var(--secondary-foreground)' }}>
                Don't see the movement you want to track? Tell us what exercise to build next.
              </p>
            </div>

            <div className="flex-shrink-0 self-start sm:self-center">
              <span
                className="inline-flex items-center px-4 py-2 text-[12px] font-semibold uppercase tracking-wider transition-colors"
                style={{
                  background: 'var(--secondary)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                  color: 'var(--foreground)',
                }}
              >
                Request an Exercise →
              </span>
            </div>
          </div>

          {/* Recent Session Preview */}
          {lastSession && (
            <div className="space-y-3">
              <div
                className="text-[11px] font-medium uppercase tracking-wider"
                style={{ color: 'var(--muted-foreground)' }}
              >
                Recent Session
              </div>
              <div
                onClick={() => onNavigate('history')}
                className="p-5 flex items-center justify-between gap-4 cursor-pointer transition-colors hover:border-[var(--primary)]"
                style={{
                  background: 'var(--card)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                }}
              >
                <div className="min-w-0">
                  <div className="font-semibold text-[15px] text-white truncate">
                    {lastSession.exercise}
                  </div>
                  <div className="text-[13px] mt-0.5" style={{ color: 'var(--muted-foreground)' }}>
                    {lastSession.date} · {lastSession.reps} reps · {lastSession.sets} {lastSession.sets === 1 ? 'set' : 'sets'}
                  </div>
                </div>

                <div className="flex items-center gap-4 flex-shrink-0">
                  <div className="text-right">
                    <div
                      className="font-display font-bold text-[28px] leading-none"
                      style={{
                        color: lastSession.avg_score >= 80 ? 'var(--success)' : 'var(--muted-foreground)',
                      }}
                    >
                      {Math.round(lastSession.avg_score)}%
                    </div>
                    <div className="text-[10px] uppercase tracking-wider mt-0.5" style={{ color: 'var(--muted-foreground)' }}>
                      Form Score
                    </div>
                  </div>
                  <span style={{ color: 'var(--muted-foreground)' }}>→</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Request Exercise Modal */}
      {isModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 animate-fade-in"
          style={{ background: 'rgba(0, 0, 0, 0.75)' }}
        >
          <div
            className="w-full max-w-[480px] p-6 sm:p-7 space-y-5 relative animate-fade-up"
            style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
            }}
          >
            {/* Close button */}
            <button
              onClick={handleCloseModal}
              disabled={isSubmitting}
              className="absolute top-5 right-5 text-lg leading-none cursor-pointer transition-colors hover:text-white"
              style={{ color: 'var(--muted-foreground)' }}
              aria-label="Close"
            >
              ✕
            </button>

            {/* Header */}
            <div>
              <h2 className="font-bold text-[22px] text-white tracking-tight leading-snug">
                REQUEST AN EXERCISE
              </h2>
              <p className="text-[13px] mt-1.5" style={{ color: 'var(--secondary-foreground)' }}>
                Suggest an exercise or movement you'd like to see added to FITFLOW with real-time AI form analysis.
              </p>
            </div>

            {isSuccess ? (
              <div className="space-y-4 pt-1">
                <div
                  className="p-4 flex items-center gap-3"
                  style={{
                    background: 'var(--secondary)',
                    border: '1px solid var(--success)',
                    borderRadius: 'var(--radius)',
                  }}
                >
                  <span className="font-bold text-base" style={{ color: 'var(--success)' }}>✓</span>
                  <div className="text-[13px] text-white">
                    Thank you! Your request for <span className="font-semibold text-white">"{submittedExercise}"</span> has been sent.
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="select-btn w-full py-3 font-semibold text-[13px] uppercase tracking-wider cursor-pointer"
                >
                  CLOSE
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmitRequest} className="space-y-4">
                {submitError && (
                  <div
                    className="p-3 text-[13px] flex items-center gap-2"
                    style={{
                      background: 'var(--secondary)',
                      border: '1px solid var(--error)',
                      borderRadius: 'var(--radius)',
                      color: 'var(--error)',
                    }}
                  >
                    <span>✕</span>
                    <span>{submitError}</span>
                  </div>
                )}

                <div className="space-y-2">
                  <label
                    htmlFor="exercise-input"
                    className="block text-[12px] font-semibold uppercase tracking-wider"
                    style={{ color: 'var(--foreground)' }}
                  >
                    What exercise would you like to see?
                  </label>
                  <input
                    id="exercise-input"
                    type="text"
                    value={requestedExercise}
                    onChange={(e) => {
                      setRequestedExercise(e.target.value)
                      if (submitError) setSubmitError(null)
                    }}
                    placeholder="e.g. Deadlift, Barbell Bench Press, Overhead Squat"
                    maxLength={100}
                    disabled={isSubmitting}
                    className="w-full px-3.5 py-3 text-[14px] text-white outline-none transition-colors"
                    style={{
                      background: 'var(--secondary)',
                      border: '1px solid var(--border)',
                      borderRadius: 'var(--radius)',
                    }}
                    onFocus={(e) => (e.currentTarget.style.borderColor = 'var(--primary)')}
                    onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--border)')}
                    autoFocus
                  />
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    disabled={isSubmitting}
                    className="w-1/2 py-3 text-[13px] font-semibold uppercase tracking-wider cursor-pointer transition-colors disabled:opacity-50"
                    style={{
                      background: 'var(--secondary)',
                      border: '1px solid var(--border)',
                      borderRadius: 'var(--radius)',
                      color: 'var(--foreground)',
                    }}
                  >
                    CANCEL
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting || !requestedExercise.trim()}
                    className="select-btn w-1/2 py-3 text-[13px] font-semibold uppercase tracking-wider cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? 'SENDING...' : 'SEND REQUEST'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
