export interface Category {
  key: string
  name: string
  exercises: string[]
}

export interface ExerciseAlignment {
  starting_pose_angles: Record<string, number>
  tolerances: Record<string, number>
  coaching_rules: Record<string, string>
}

export interface ExerciseConfig {
  type: 'REP_BASED' | 'TIME_BASED'
  category: string
  primary_joint: string
  keypoints: string[]
  alt_keypoints: string[]
  down_threshold: number
  up_threshold: number
  target_reps: number
  cooldown: number
  alignment: ExerciseAlignment
  checks: Record<string, Record<string, number>>
}

export interface Keypoint {
  x: number
  y: number
  confidence?: number
}

export interface AlignmentData {
  score: number
  ready: boolean
  joint_statuses: Record<string, 'correct' | 'adjusting' | 'incorrect'>
  coaching_messages: string[]
  ghost_keypoints: Record<string, { x: number; y: number }>
}

export interface Warning {
  warning: string
  suggestion: string
}

export type WorkoutState =
  | 'IDLE'
  | 'ALIGNING'
  | 'READY'
  | 'STARTED'
  | 'DOWN'
  | 'UP'
  | 'REP_COMPLETED'
  | 'FINISHED'
  | 'RESET'

export interface TrackingData {
  exercise: string
  state: WorkoutState
  reps: number
  sets: number
  form_score: number
  warnings: Warning[]
  finished: boolean
  elapsed_time: number
  joint_angles: Record<string, string>
  current_angle: number | null
}

export interface InferenceFrame {
  type: 'inference' | 'status'
  status?: string
  exercise?: string
  keypoints: Record<string, Keypoint>
  alignment: AlignmentData
  tracking: TrackingData
}

export interface HistoryEntry {
  date: string
  exercise: string
  reps: number
  sets: number
  elapsed_time: number
  avg_score: number
}

export interface SessionSummary {
  has_summary: boolean
  exercise?: string
  reps?: number
  sets?: number
  duration_sec?: number
  form_score?: number
  calories_burned?: number
}

export type Screen =
  | 'home'
  | 'library'
  | 'calibration'
  | 'workout'
  | 'summary'
  | 'history'
