import { useState, useCallback, useEffect } from 'react'
import type { Screen, Category, ExerciseConfig, TrackingData, SessionSummary } from './types'

import HomeScreen from './screens/HomeScreen'
import ExerciseLibraryScreen from './screens/ExerciseLibraryScreen'
import CalibrationScreen from './screens/CalibrationScreen'
import LiveWorkoutScreen from './screens/LiveWorkoutScreen'
import SummaryScreen from './screens/SummaryScreen'
import HistoryScreen from './screens/HistoryScreen'
import ExerciseDetailModal from './components/ExerciseDetailModal'
import { fetchSummary } from './services/api'
import { useCameraAndWebSocket } from './hooks/useCameraAndWebSocket'

export default function App() {
  const [screen, setScreen] = useState<Screen>('home')
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null)
  const [selectedExerciseName, setSelectedExerciseName] = useState<string | null>(null)
  const [selectedExerciseConfig, setSelectedExerciseConfig] = useState<ExerciseConfig | null>(null)
  const [modalExerciseName, setModalExerciseName] = useState<string | null>(null)
  const [modalConfig, setModalConfig] = useState<ExerciseConfig | null>(null)
  const [summary, setSummary] = useState<SessionSummary | null>(null)

  // Session Active state: active during calibration and live workout screens
  const isSessionActive = (screen === 'calibration' || screen === 'workout') && Boolean(selectedExerciseName)

  // Single Parent-Level Persistent Camera & WebSocket Hook
  const {
    videoRef,
    canvasRef,
    wsConnected,
    cameraActive,
    error,
    alignment,
    tracking,
    selectExercise,
    startActiveTracking,
    resetSession,
    stopCamera,
    disconnectWebSocket,
  } = useCameraAndWebSocket(selectedExerciseName, isSessionActive)

  const navigate = useCallback((s: Screen) => setScreen(s), [])

  const handleSelectCategory = (cat: Category) => {
    setSelectedCategory(cat)
    setScreen('library')
  }

  const handleSelectExercise = (name: string, config: ExerciseConfig) => {
    setModalExerciseName(name)
    setModalConfig(config)
  }

  const handleStartWorkout = () => {
    if (!modalExerciseName || !modalConfig) return
    setSelectedExerciseName(modalExerciseName)
    setSelectedExerciseConfig(modalConfig)
    setModalExerciseName(null)
    setModalConfig(null)
    setScreen('calibration')
  }

  // AUTOMATIC VIEW TRANSITION:
  // When backend state changes to active tracking (STARTED, DOWN, UP, REP_COMPLETED), automatically switch view to 'workout'
  useEffect(() => {
    if (screen === 'calibration') {
      const activeStates = ['STARTED', 'DOWN', 'UP', 'REP_COMPLETED']
      if (activeStates.includes(tracking.state) || (alignment.ready && tracking.state !== 'ALIGNING')) {
        console.log('[APP AUTO-TRANSITION] Backend entered active tracking state:', tracking.state, '-> Switching screen to workout')
        setScreen('workout')
      }
    }
  }, [screen, tracking.state, alignment.ready])

  const handleWorkoutEnd = async (currentTracking: TrackingData) => {
    stopCamera()
    disconnectWebSocket()

    try {
      const summaryData = await fetchSummary()
      if (summaryData && summaryData.has_summary) {
        setSummary(summaryData)
      } else {
        const fallbackSummary: SessionSummary = {
          has_summary: true,
          exercise: selectedExerciseName ?? '',
          reps: currentTracking.reps,
          sets: currentTracking.sets,
          duration_sec: Math.round(currentTracking.elapsed_time),
          form_score: currentTracking.form_score,
          calories_burned: Math.max(1, Math.round(currentTracking.reps * 0.8)),
        }
        setSummary(fallbackSummary)
      }
    } catch (e) {
      console.error('Error fetching summary after workout end:', e)
      const fallbackSummary: SessionSummary = {
        has_summary: true,
        exercise: selectedExerciseName ?? '',
        reps: currentTracking.reps,
        sets: currentTracking.sets,
        duration_sec: Math.round(currentTracking.elapsed_time),
        form_score: currentTracking.form_score,
        calories_burned: Math.max(1, Math.round(currentTracking.reps * 0.8)),
      }
      setSummary(fallbackSummary)
    }
    setScreen('summary')
  }

  const handleTryAgain = () => {
    setScreen('calibration')
  }

  return (
    <div className="h-full bg-mesh relative">
      {/* Persistent Hidden/Active Video & Canvas Element Layer */}
      <div className={`absolute inset-0 z-0 ${isSessionActive ? 'block' : 'hidden'}`}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="absolute inset-0 w-full h-full object-cover"
        />
        <canvas
          ref={canvasRef}
          width={1280}
          height={720}
          className="absolute inset-0 w-full h-full object-cover pointer-events-none z-10"
        />
      </div>

      {/* Screen Views */}
      <div className="relative z-10 h-full">
        {screen === 'home' && (
          <HomeScreen
            onNavigate={navigate}
            onSelectCategory={handleSelectCategory}
          />
        )}

        {screen === 'library' && selectedCategory && (
          <ExerciseLibraryScreen
            category={selectedCategory}
            onNavigate={navigate}
            onSelectExercise={handleSelectExercise}
          />
        )}

        {screen === 'calibration' && selectedExerciseName && selectedExerciseConfig && (
          <CalibrationScreen
            exerciseName={selectedExerciseName}
            config={selectedExerciseConfig}
            alignment={alignment}
            wsConnected={wsConnected}
            cameraActive={cameraActive}
            error={error}
            startActiveTracking={startActiveTracking}
            onCancel={() => {
              stopCamera()
              disconnectWebSocket()
              setScreen('library')
            }}
          />
        )}

        {screen === 'workout' && selectedExerciseName && selectedExerciseConfig && (
          <LiveWorkoutScreen
            exerciseName={selectedExerciseName}
            config={selectedExerciseConfig}
            tracking={tracking}
            wsConnected={wsConnected}
            resetSession={resetSession}
            onEnd={() => handleWorkoutEnd(tracking)}
          />
        )}

        {screen === 'summary' && selectedExerciseName && (
          <SummaryScreen
            summary={summary}
            exerciseName={selectedExerciseName}
            onTryAgain={handleTryAgain}
            onHome={() => {
              setSummary(null)
              setScreen('home')
            }}
          />
        )}

        {screen === 'history' && <HistoryScreen onNavigate={navigate} />}
      </div>

      {/* Exercise Detail Modal — overlays any screen */}
      {modalExerciseName && modalConfig && (
        <ExerciseDetailModal
          name={modalExerciseName}
          config={modalConfig}
          onClose={() => {
            setModalExerciseName(null)
            setModalConfig(null)
          }}
          onStart={handleStartWorkout}
        />
      )}
    </div>
  )
}
