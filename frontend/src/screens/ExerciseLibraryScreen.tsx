import { useState } from 'react'
import TopNavBar from '../components/TopNavBar'
import type { Category, Screen, ExerciseConfig } from '../types'
import { fetchExerciseInfo } from '../services/api'

interface Props {
  category: Category
  onNavigate: (screen: Screen) => void
  onSelectExercise: (name: string, config: ExerciseConfig) => void
}

export default function ExerciseLibraryScreen({ category, onNavigate, onSelectExercise }: Props) {
  const [loadingName, setLoadingName] = useState<string | null>(null)

  const handleExerciseClick = async (name: string) => {
    try {
      setLoadingName(name)
      const config = await fetchExerciseInfo(name)
      onSelectExercise(name, config)
    } catch (e) {
      console.error(`Error loading exercise metadata for ${name}:`, e)
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
        className="flex-shrink-0 px-6 md:px-8 py-3.5 flex items-center gap-3"
        style={{
          background: 'var(--card)',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <button
          onClick={() => onNavigate('home')}
          className="text-[12px] font-medium transition-colors cursor-pointer hover:text-white"
          style={{ color: 'var(--muted-foreground)' }}
        >
          ← Categories
        </button>
        <span style={{ color: 'var(--border)' }}>/</span>
        <span className="text-[12px] font-semibold" style={{ color: 'var(--primary)' }}>
          {category.name}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto px-6 md:px-8 py-6 md:py-8">
        <div className="max-w-[1120px] mx-auto space-y-6 animate-fade-up">
          {/* Header */}
          <div>
            <h1 className="font-bold text-[28px] text-white tracking-tight leading-tight">
              {category.name}
            </h1>
            <p className="text-[13px] mt-1" style={{ color: 'var(--muted-foreground)' }}>
              Select an exercise to configure and start your workout.
            </p>
          </div>

          {category.exercises.length === 0 ? (
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
                No exercises available
              </h3>
              <p className="text-[13px]" style={{ color: 'var(--muted-foreground)' }}>
                There are currently no exercises logged under this category.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {category.exercises.map((name) => {
                const isLoadingThis = loadingName === name
                return (
                  <button
                    key={name}
                    disabled={isLoadingThis}
                    onClick={() => handleExerciseClick(name)}
                    className={`exercise-card p-5 text-left cursor-pointer flex flex-col justify-between h-[110px] transition-opacity ${
                      isLoadingThis ? 'opacity-50 pointer-events-none' : ''
                    }`}
                  >
                    <h3 className="font-semibold text-[15px] text-white leading-snug">
                      {name}
                    </h3>
                    <div className="text-[12px]" style={{ color: 'var(--muted-foreground)' }}>
                      AI-guided · Rep-based
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
