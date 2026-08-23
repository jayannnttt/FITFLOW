import { useState } from 'react'
import TopNavBar from '../components/TopNavBar'
import type { Category, Screen, ExerciseConfig } from '../types'
import { fetchExerciseInfo } from '../services/api'

interface Props {
  category: Category
  onNavigate: (screen: Screen) => void
  onSelectExercise: (name: string, config: ExerciseConfig) => void
}

const CATEGORY_META: Record<string, { accent: string; icon: string; num: string }> = {
  'UPPER BODY': { accent: '#00d4ff', icon: '💪', num: '01' },
  'LOWER BODY': { accent: '#7b2fff', icon: '🦵', num: '02' },
  'CORE': { accent: '#ff2d78', icon: '◎', num: '03' },
  'FULL BODY / CARDIO': { accent: '#ff8c42', icon: '⚡', num: '04' },
}

export default function ExerciseLibraryScreen({ category, onNavigate, onSelectExercise }: Props) {
  const meta = CATEGORY_META[category.name] ?? { accent: '#00d4ff', icon: '◈', num: '01' }
  const [loadingName, setLoadingName] = useState<string | null>(null)

  const handleExerciseClick = async (name: string) => {
    try {
      setLoadingName(name)
      const config = await fetchExerciseInfo(name)
      onSelectExercise(name, config)
    } catch (e) {
      console.error(`Error loading exercise metadata for ${name}:`, e)
      // Fallback configuration if API fails
      const fallbackConfig: ExerciseConfig = {
        type: 'REP_BASED',
        category: category.name,
        primary_joint: 'elbow',
        keypoints: ['left_shoulder', 'left_elbow', 'left_wrist'],
        alt_keypoints: ['right_shoulder', 'right_elbow', 'right_wrist'],
        down_threshold: 150.0,
        up_threshold: 90.0,
        target_reps: 10,
        cooldown: 0.8,
        alignment: {
          starting_pose_angles: {},
          tolerances: {},
          coaching_rules: {},
        },
        checks: {},
      }
      onSelectExercise(name, fallbackConfig)
    } finally {
      setLoadingName(null)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <TopNavBar currentScreen="library" onNavigate={(s) => onNavigate(s)} />

      {/* Back Bar */}
      <div
        className="flex-shrink-0 px-5 md:px-8 py-3 flex items-center gap-3 border-b border-white/8"
        style={{ background: 'rgba(255,255,255,0.02)' }}
      >
        <button
          onClick={() => onNavigate('home')}
          className="flex items-center gap-1.5 text-xs font-mono tracking-widest transition-colors hover:text-white/70"
          style={{ color: 'rgba(240,240,248,0.35)', letterSpacing: '0.15em' }}
        >
          ← BACK TO CATEGORIES
        </button>
        <span style={{ color: 'rgba(240,240,248,0.15)' }}>/</span>
        <div
          className="font-mono text-xs px-2.5 py-1 rounded-full"
          style={{
            background: `${meta.accent}12`,
            color: meta.accent,
            border: `1px solid ${meta.accent}28`,
            letterSpacing: '0.1em',
          }}
        >
          {category.name}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-5 md:px-8 py-8">
        <div className="max-w-5xl mx-auto">
          {/* Section Header */}
          <div className="animate-fade-up mb-8">
            <h1
              className="font-black text-2xl md:text-3xl mb-1"
              style={{ color: 'rgba(240,240,248,0.95)', letterSpacing: '-0.02em' }}
            >
              Choose an Exercise
            </h1>
            <p className="text-sm" style={{ color: 'rgba(240,240,248,0.38)' }}>
              Select to view posture calibration instructions
            </p>
          </div>

          {category.exercises.length === 0 ? (
            <div className="glass rounded-2xl p-12 text-center animate-fade-up">
              <div className="text-4xl mb-3">◎</div>
              <p className="text-sm" style={{ color: 'rgba(240,240,248,0.4)' }}>
                No exercises available for this category.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {category.exercises.map((name, i) => {
                const isLoadingThis = loadingName === name
                return (
                  <button
                    key={name}
                    disabled={isLoadingThis}
                    onClick={() => handleExerciseClick(name)}
                    className={`animate-fade-up stagger-${Math.min(
                      i + 1,
                      6,
                    )} exercise-card glass rounded-2xl p-5 text-left transition-all ${
                      isLoadingThis ? 'opacity-50 pointer-events-none' : ''
                    }`}
                    style={{ border: '1px solid rgba(255,255,255,0.07)' }}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div
                        className="font-mono text-xs px-2 py-1 rounded-md"
                        style={{
                          background: `${meta.accent}12`,
                          color: meta.accent,
                          border: `1px solid ${meta.accent}25`,
                          letterSpacing: '0.1em',
                          fontSize: '0.6rem',
                        }}
                      >
                        {category.name}
                      </div>
                      <span className="text-lg">{meta.icon}</span>
                    </div>

                    <h3
                      className="font-bold text-base mb-1"
                      style={{ color: 'rgba(240,240,248,0.95)', letterSpacing: '-0.01em' }}
                    >
                      {name}
                    </h3>
                    <p className="text-xs mb-4" style={{ color: 'rgba(240,240,248,0.38)', lineHeight: '1.5' }}>
                      Posture calibration & real-time rep counting
                    </p>

                    <div className="flex gap-2 flex-wrap">
                      <div
                        className="font-mono text-xs px-2 py-0.5 rounded-md"
                        style={{
                          background: 'rgba(255,255,255,0.04)',
                          color: 'rgba(240,240,248,0.5)',
                          border: '1px solid rgba(255,255,255,0.07)',
                          fontSize: '0.6rem',
                        }}
                      >
                        {isLoadingThis ? 'LOADING...' : 'AI GUIDED'}
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
