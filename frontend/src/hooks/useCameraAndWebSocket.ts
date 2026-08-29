import { useState, useEffect, useRef, useCallback } from 'react'
import type { Keypoint, AlignmentData, TrackingData } from '../types'

const SKELETON_CONNECTIONS: [string, string][] = [
  ['left_shoulder', 'right_shoulder'],
  ['left_shoulder', 'left_elbow'],
  ['left_elbow', 'left_wrist'],
  ['right_shoulder', 'right_elbow'],
  ['right_elbow', 'right_wrist'],
  ['left_shoulder', 'left_hip'],
  ['right_shoulder', 'right_hip'],
  ['left_hip', 'right_hip'],
  ['left_hip', 'left_knee'],
  ['left_knee', 'left_ankle'],
  ['right_hip', 'right_knee'],
  ['right_knee', 'right_ankle'],
]

export function useCameraAndWebSocket(exerciseName: string | null, active: boolean) {
  const [wsConnected, setWsConnected] = useState(false)
  const [cameraActive, setCameraActive] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [keypoints, setKeypoints] = useState<Record<string, Keypoint>>({})
  const [alignment, setAlignment] = useState<AlignmentData>({
    score: 0,
    ready: false,
    joint_statuses: {},
    coaching_messages: [],
    ghost_keypoints: {},
  })
  const [tracking, setTracking] = useState<TrackingData>({
    exercise: exerciseName || '',
    state: 'IDLE',
    reps: 0,
    sets: 0,
    form_score: 0,
    warnings: [],
    finished: false,
    elapsed_time: 0,
    joint_angles: {},
    current_angle: null,
  })

  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const offscreenCanvasRef = useRef<HTMLCanvasElement | null>(null)
  const frameTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const hasStartedTrackingRef = useRef<boolean>(false)

  // 1. Camera Initialization
  const startCamera = useCallback(async () => {
    try {
      setError(null)
      if (videoRef.current && videoRef.current.srcObject) {
        setCameraActive(true)
        return
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
        audio: false,
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
        setCameraActive(true)

        if (!offscreenCanvasRef.current) {
          const off = document.createElement('canvas')
          off.width = videoRef.current.videoWidth || 1280
          off.height = videoRef.current.videoHeight || 720
          offscreenCanvasRef.current = off
        }
      }
    } catch (err: any) {
      console.error('Camera access error:', err)
      setError(`Camera access denied or unequipped: ${err.message}`)
      setCameraActive(false)
    }
  }, [])

  const stopCamera = useCallback(() => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      stream.getTracks().forEach((track) => track.stop())
      videoRef.current.srcObject = null
    }
    setCameraActive(false)
  }, [])

  // 2. WebSocket Connection
  const connectWebSocket = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return

    const defaultWsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/workout`
    let wsBaseUrl = (import.meta.env.VITE_WS_BASE_URL || '').trim().replace(/\/+$/, '')
    if (wsBaseUrl) {
      if (wsBaseUrl.startsWith('https://')) {
        wsBaseUrl = wsBaseUrl.replace('https://', 'wss://')
      } else if (wsBaseUrl.startsWith('http://')) {
        wsBaseUrl = wsBaseUrl.replace('http://', 'ws://')
      }
    }
    const wsUrl = wsBaseUrl ? `${wsBaseUrl}/ws/workout` : defaultWsUrl
    const ws = new WebSocket(wsUrl)

    wsRef.current = ws

    ws.onopen = () => {
      setWsConnected(true)
      setError(null)
      hasStartedTrackingRef.current = false
      if (exerciseName) {
        console.log('[WS] Sending select_exercise:', exerciseName)
        ws.send(JSON.stringify({ action: 'select_exercise', exercise: exerciseName }))
      }
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'status') {
          console.log('[WS STATUS ACK]', data)
        } else if (data.type === 'inference') {
          // Dev logging for verification
          console.log('[WS INFERENCE PAYLOAD]', {
            type: data.type,
            alignmentReady: data.alignment?.ready,
            alignmentScore: data.alignment?.score,
            state: data.tracking?.state,
            reps: data.tracking?.reps,
            sets: data.tracking?.sets,
            formScore: data.tracking?.form_score,
            elapsedTime: data.tracking?.elapsed_time,
            currentAngle: data.tracking?.current_angle,
            warnings: data.tracking?.warnings,
          })

          if (data.keypoints) setKeypoints(data.keypoints)
          if (data.alignment) setAlignment(data.alignment)
          if (data.tracking) setTracking(data.tracking)

          // AUTOMATIC START TRACKING TRIGGER
          // When alignment.ready === true and we haven't sent start_active_tracking yet
          if (data.alignment?.ready && !hasStartedTrackingRef.current) {
            hasStartedTrackingRef.current = true
            console.log('[WS AUTO-START] Posture alignment ready! Sending action: start_active_tracking')
            ws.send(JSON.stringify({ action: 'start_active_tracking' }))
          }
        }
      } catch (e) {
        console.error('Error parsing WebSocket frame:', e)
      }
    }

    ws.onerror = () => {
      setWsConnected(false)
      setError('WebSocket connection error')
    }

    ws.onclose = () => {
      setWsConnected(false)
    }
  }, [exerciseName])

  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.onopen = null
      wsRef.current.onmessage = null
      wsRef.current.onerror = null
      wsRef.current.onclose = null
      wsRef.current.close()
      wsRef.current = null
    }
    setWsConnected(false)
    hasStartedTrackingRef.current = false
  }, [])

  // Action methods
  const selectExercise = useCallback((name: string) => {
    hasStartedTrackingRef.current = false
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('[WS] Selecting exercise:', name)
      wsRef.current.send(JSON.stringify({ action: 'select_exercise', exercise: name }))
    }
  }, [])

  const startActiveTracking = useCallback(() => {
    if (!hasStartedTrackingRef.current && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      hasStartedTrackingRef.current = true
      console.log('[WS MANUAL-START] Sending action: start_active_tracking')
      wsRef.current.send(JSON.stringify({ action: 'start_active_tracking' }))
    }
  }, [])

  const resetSession = useCallback(() => {
    hasStartedTrackingRef.current = false
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('[WS RESET] Sending action: reset')
      wsRef.current.send(JSON.stringify({ action: 'reset' }))
    }
  }, [])

  // 3. Binary Frame Streaming Loop (~25 FPS / 40ms)
  useEffect(() => {
    if (!active || !cameraActive || !wsConnected) return

    let cancelled = false

    const sendFrame = () => {
      if (cancelled) return
      const v = videoRef.current
      const off = offscreenCanvasRef.current
      const ws = wsRef.current

      if (v && off && ws && ws.readyState === WebSocket.OPEN) {
        const ctx = off.getContext('2d')
        if (ctx) {
          ctx.drawImage(v, 0, 0, off.width, off.height)
          off.toBlob(
            (blob) => {
              if (blob && ws.readyState === WebSocket.OPEN && !cancelled) {
                ws.send(blob)
              }
              if (!cancelled && active) {
                frameTimerRef.current = setTimeout(sendFrame, 40) // ~25 FPS
              }
            },
            'image/jpeg',
            0.8,
          )
        }
      } else if (!cancelled && active) {
        frameTimerRef.current = setTimeout(sendFrame, 100)
      }
    }

    sendFrame()

    return () => {
      cancelled = true
      if (frameTimerRef.current) clearTimeout(frameTimerRef.current)
    }
  }, [active, cameraActive, wsConnected])

  // 4. Canvas Overlay Rendering Loop
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)
    const w = canvas.width
    const h = canvas.height

    // Draw Ghost Skeleton Overlay (Neon Cyan)
    if (alignment.ghost_keypoints && Object.keys(alignment.ghost_keypoints).length > 0) {
      ctx.save()
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.55)'
      ctx.lineWidth = 4
      ctx.lineCap = 'round'

      SKELETON_CONNECTIONS.forEach(([start, end]) => {
        const p1 = alignment.ghost_keypoints[start]
        const p2 = alignment.ghost_keypoints[end]
        if (p1 && p2) {
          ctx.beginPath()
          ctx.moveTo(p1.x * w, p1.y * h)
          ctx.lineTo(p2.x * w, p2.y * h)
          ctx.stroke()
        }
      })

      ctx.fillStyle = 'rgba(147, 197, 253, 0.7)'
      Object.values(alignment.ghost_keypoints).forEach((kp) => {
        ctx.beginPath()
        ctx.arc(kp.x * w, kp.y * h, 6, 0, 2 * Math.PI)
        ctx.fill()
      })
      ctx.restore()
    }

    // Draw Live User Skeleton (Color-Coded by Joint Status / Confidence)
    if (keypoints && Object.keys(keypoints).length > 0) {
      const colorMap: Record<string, string> = {
        correct: '#10B981',
        adjusting: '#F59E0B',
        incorrect: '#EF4444',
      }

      ctx.save()
      ctx.lineWidth = 4
      ctx.lineCap = 'round'

      SKELETON_CONNECTIONS.forEach(([start, end]) => {
        const p1 = keypoints[start]
        const p2 = keypoints[end]
        if (p1 && p2 && (p1.confidence ?? 1) > 0.4 && (p2.confidence ?? 1) > 0.4) {
          const st1 = alignment.joint_statuses[start] || 'correct'
          const st2 = alignment.joint_statuses[end] || 'correct'
          const status =
            st1 === 'incorrect' || st2 === 'incorrect'
              ? 'incorrect'
              : st1 === 'adjusting' || st2 === 'adjusting'
              ? 'adjusting'
              : 'correct'

          ctx.strokeStyle = colorMap[status] || '#10B981'
          ctx.beginPath()
          ctx.moveTo(p1.x * w, p1.y * h)
          ctx.lineTo(p2.x * w, p2.y * h)
          ctx.stroke()
        }
      })

      Object.keys(keypoints).forEach((name) => {
        const kp = keypoints[name]
        if ((kp.confidence ?? 1) > 0.4) {
          const cx = kp.x * w
          const cy = kp.y * h
          const status = alignment.joint_statuses[name] || 'correct'

          ctx.fillStyle = colorMap[status] || '#10B981'
          ctx.beginPath()
          ctx.arc(cx, cy, 7, 0, 2 * Math.PI)
          ctx.fill()
          ctx.strokeStyle = '#FFFFFF'
          ctx.lineWidth = 1.5
          ctx.stroke()

          // Draw Joint Angle Tag Badge
          if (tracking.joint_angles && tracking.joint_angles[name]) {
            const angTxt = tracking.joint_angles[name]
            ctx.save()
            ctx.font = 'bold 11px Inter, system-ui, sans-serif'
            ctx.fillStyle = 'rgba(9, 13, 22, 0.85)'
            ctx.strokeStyle = '#06B6D4'
            ctx.lineWidth = 1
            const tw = ctx.measureText(angTxt).width
            const pad = 5
            const rx = cx + 10
            const ry = cy - 10

            ctx.beginPath()
            ctx.rect(rx, ry - 14, tw + pad * 2, 18)
            ctx.fill()
            ctx.stroke()
            ctx.fillStyle = '#60A5FA'
            ctx.fillText(angTxt, rx + pad, ry - 1)
            ctx.restore()
          }
        }
      })

      ctx.restore()
    }
  }, [keypoints, alignment, tracking.joint_angles])

  // Lifetime lifecycle
  useEffect(() => {
    if (active) {
      startCamera()
      connectWebSocket()
    } else {
      stopCamera()
      disconnectWebSocket()
    }
  }, [active, startCamera, stopCamera, connectWebSocket, disconnectWebSocket])

  return {
    videoRef,
    canvasRef,
    wsConnected,
    cameraActive,
    error,
    keypoints,
    alignment,
    tracking,
    selectExercise,
    startActiveTracking,
    resetSession,
    stopCamera,
    disconnectWebSocket,
  }
}
