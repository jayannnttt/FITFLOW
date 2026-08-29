import type { Category, ExerciseConfig, HistoryEntry, SessionSummary } from '../types'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')

/**
 * Fetch workout categories dictionary and map to Category array
 * GET /api/categories
 */
export async function fetchCategories(): Promise<Category[]> {
  const res = await fetch(`${API_BASE_URL}/api/categories`)
  if (!res.ok) {
    throw new Error(`Failed to fetch categories: ${res.statusText}`)
  }
  const data: Record<string, { name: string; exercises: string[] }> = await res.json()
  
  return Object.keys(data).map((key) => ({
    key,
    name: data[key].name,
    exercises: data[key].exercises || [],
  }))
}

/**
 * Fetch specific exercise detailed configuration metadata
 * GET /api/exercises/{name}
 */
export async function fetchExerciseInfo(name: string): Promise<ExerciseConfig> {
  const res = await fetch(`${API_BASE_URL}/api/exercises/${encodeURIComponent(name)}`)
  if (!res.ok) {
    throw new Error(`Failed to fetch exercise info for ${name}: ${res.statusText}`)
  }
  return await res.json()
}

/**
 * Fetch recorded workout history sessions list
 * GET /api/history
 */
export async function fetchHistory(): Promise<HistoryEntry[]> {
  const res = await fetch(`${API_BASE_URL}/api/history`)
  if (!res.ok) {
    throw new Error(`Failed to fetch workout history: ${res.statusText}`)
  }
  const data = await res.json()
  return Array.isArray(data) ? data : []
}

/**
 * Fetch latest workout session summary statistics
 * GET /api/summary
 */
export async function fetchSummary(): Promise<SessionSummary> {
  const res = await fetch(`${API_BASE_URL}/api/summary`)
  if (!res.ok) {
    throw new Error(`Failed to fetch session summary: ${res.statusText}`)
  }
  return await res.json()
}
