"""
FastAPI Server & Binary WebSocket Inference API for AI Fitness Tracker.
Decouples backend AI logic, MediaPipe, AlignmentEngine, and Rep Counter
from frontend Web UI, canvas rendering, and HTML5 video streaming.
"""
import os
import sys

# Ensure backend directory is in sys.path when executed from repository root
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import json
import time
import cv2
import numpy as np
from typing import Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from config import AppConfig
from pose.detector_factory import DetectorFactory
from pose.pose_filter import PoseFilterManager
from pose.angles import AngleEngine
from exercises.exercise_factory import ExerciseFactory
from exercises.base_exercise import BaseExercise
from tracking.alignment_engine import AlignmentEngine
from workout_logging.csv_logger import CSVLogger
from storage.workout_history import WorkoutHistoryManager
from analytics.performance import PerformanceAnalyzer
from utils.enums import ExerciseState, ExerciseType
from utils.helper import load_exercise_configs

from fastapi.middleware.cors import CORSMiddleware

# Initialize App & Config
config = AppConfig()
app = FastAPI(title="AI Fitness Coach API Server", version="2.0.0")

# Configure CORS via ALLOWED_ORIGINS environment variable or default dev origins
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System Components
exercises_config = load_exercise_configs(config.exercises_config_path)
detector = DetectorFactory.create_detector(
    config.pose_backend,
    min_detection_confidence=config.min_detection_confidence,
    min_tracking_confidence=config.min_tracking_confidence,
    model_complexity=config.model_complexity
)
pose_filter = PoseFilterManager(
    method=config.smoothing_method,
    window_size=config.moving_average_window,
    alpha=config.ema_alpha
)
angle_engine = AngleEngine()
alignment_engine = AlignmentEngine(
    score_threshold=config.alignment_score_threshold,
    stabilization_sec=config.alignment_stabilization_sec,
    grace_period_sec=config.alignment_grace_period_sec,
    smoothing_alpha=config.alignment_smoothing_alpha
)
csv_logger = CSVLogger(config.csv_log_path)
history_manager = WorkoutHistoryManager(config.session_history_path)

# Active Session State
class SessionState:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset session state for clean isolation between workouts."""
        self.active_exercise: Optional[BaseExercise] = None
        self.exercise_name: Optional[str] = None
        self.session_start_time: float = 0.0
        self.performance_score: float = 0.0
        self.smoothness_score: float = 0.0
        self.depth_score: float = 0.0
        self.performance_analyzer: PerformanceAnalyzer = PerformanceAnalyzer()
        alignment_engine.reset()
        pose_filter.reset()

    def select_exercise(self, name: str) -> bool:
        if name in exercises_config["exercises"]:
            ex_cfg = exercises_config["exercises"][name]
            self.exercise_name = name
            self.active_exercise = ExerciseFactory.create_exercise(name, ex_cfg)
            self.session_start_time = time.time()
            self.performance_score = 0.0
            self.smoothness_score = 0.0
            self.depth_score = 0.0
            self.performance_analyzer = PerformanceAnalyzer()
            alignment_engine.reset()
            pose_filter.reset()
            return True
        return False

session_state = SessionState()


# --- REST ENDPOINTS ---

@app.get("/api/categories")
def get_categories():
    """Get workout categories and exercise hierarchy."""
    return JSONResponse(content=exercises_config.get("categories", {}))


@app.get("/api/exercises/{name}")
def get_exercise_info(name: str):
    """Get exercise detailed configuration and metadata."""
    ex = exercises_config.get("exercises", {}).get(name)
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return JSONResponse(content=ex)


@app.get("/api/history")
def get_workout_history():
    """Get recorded workout history sessions."""
    history = history_manager.get_history()
    return JSONResponse(content=history if isinstance(history, list) else [])


@app.get("/api/summary")
def get_latest_summary():
    """Get latest workout summary statistics."""
    if not session_state.active_exercise:
        return JSONResponse(content={"has_summary": False})

    metrics = session_state.active_exercise.get_display_metrics()
    elapsed = time.time() - session_state.session_start_time
    
    cal_burned = max(1, int((elapsed / 60.0) * 10.5))
    
    return JSONResponse(content={
        "has_summary": True,
        "exercise": session_state.exercise_name,
        "reps": metrics.get("reps", 0),
        "sets": metrics.get("sets", 0),
        "duration_sec": int(elapsed),
        "form_score": int(session_state.performance_score),
        "calories_burned": cal_burned
    })


# --- BINARY WEBSOCKET INFERENCE API ---

@app.websocket("/ws/workout")
async def websocket_workout_endpoint(websocket: WebSocket):
    """
    High-performance binary WebSocket endpoint.
    Receives binary JPEG frame buffers -> performs MediaPipe & AI inference -> returns JSON.
    """
    await websocket.accept()
    session_state.reset()
    frame_counter = 0

    try:
        while True:
            message = await websocket.receive()
            
            if "text" in message and message["text"]:
                try:
                    data = json.loads(message["text"])
                    cmd = data.get("action")
                    if cmd == "select_exercise":
                        ex_name = data.get("exercise")
                        session_state.select_exercise(ex_name)
                        await websocket.send_json({
                            "type": "status",
                            "status": "exercise_selected",
                            "exercise": ex_name
                        })
                    elif cmd == "start_active_tracking":
                        if session_state.active_exercise:
                            session_state.active_exercise.start_tracking(time.time())
                        await websocket.send_json({
                            "type": "status",
                            "status": "tracking_active"
                        })
                    elif cmd == "reset":
                        alignment_engine.reset()
                        if session_state.active_exercise:
                            session_state.active_exercise.reset()
                        await websocket.send_json({"type": "status", "status": "reset"})
                except Exception as e:
                    print(f"Error handling WebSocket text message: {e}")

            elif "bytes" in message and message["bytes"]:
                frame_counter += 1
                bytes_data = message["bytes"]
                now = time.time()
                angle_engine.clear_cache()

                np_arr = np.frombuffer(bytes_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is None:
                    print(f"[FRAME #{frame_counter}] Timestamp: {now:.3f} | Frame decode FAILED: cv2.imdecode returned None")
                    continue

                if session_state.active_exercise is None:
                    # Session not initialized yet -> return empty initializing state
                    await websocket.send_json({
                        "type": "inference",
                        "keypoints": {},
                        "alignment": {"score": 0.0, "ready": False, "joint_statuses": {}, "coaching_messages": [], "ghost_keypoints": {}},
                        "tracking": {"exercise": "", "state": "INITIALIZING", "reps": 0, "sets": 0, "form_score": 0, "warnings": [], "finished": False}
                    })
                    continue

                # Run pose detection
                h, w = frame.shape[:2]

                keypoints = detector.detect(frame, now)
                keypoints_dict = {}
                if keypoints:
                    keypoints = pose_filter.filter_pose(keypoints, now)
                    keypoints_dict = {
                        name: {"x": kp.x, "y": kp.y, "confidence": kp.confidence}
                        for name, kp in keypoints.items()
                    }

                num_kps = len(keypoints)
                joint_angles = {}

                if num_kps > 0:
                    l_elbow = angle_engine.get_joint_angle(keypoints, ["left_shoulder", "left_elbow", "left_wrist"], (h, w))
                    r_elbow = angle_engine.get_joint_angle(keypoints, ["right_shoulder", "right_elbow", "right_wrist"], (h, w))
                    l_shoulder = angle_engine.get_joint_angle(keypoints, ["left_hip", "left_shoulder", "left_elbow"], (h, w))
                    r_shoulder = angle_engine.get_joint_angle(keypoints, ["right_hip", "right_shoulder", "right_elbow"], (h, w))
                    l_knee = angle_engine.get_joint_angle(keypoints, ["left_hip", "left_knee", "left_ankle"], (h, w))
                    r_knee = angle_engine.get_joint_angle(keypoints, ["right_hip", "right_knee", "right_ankle"], (h, w))
                    l_hip = angle_engine.get_joint_angle(keypoints, ["left_shoulder", "left_hip", "left_knee"], (h, w))

                    if l_elbow is not None: joint_angles["left_elbow"] = f"{int(l_elbow)}°"
                    if r_elbow is not None: joint_angles["right_elbow"] = f"{int(r_elbow)}°"
                    if l_shoulder is not None: joint_angles["left_shoulder"] = f"{int(l_shoulder)}°"
                    if r_shoulder is not None: joint_angles["right_shoulder"] = f"{int(r_shoulder)}°"
                    if l_knee is not None: joint_angles["left_knee"] = f"{int(l_knee)}°"
                    if r_knee is not None: joint_angles["right_knee"] = f"{int(r_knee)}°"
                    if l_hip is not None: joint_angles["left_hip"] = f"{int(l_hip)}°"

                alignment_data = {
                    "score": 0.0,
                    "ready": False,
                    "joint_statuses": {},
                    "coaching_messages": [],
                    "ghost_keypoints": {}
                }

                metrics = session_state.active_exercise.get_display_metrics() if session_state.active_exercise else {}

                tracking_data = {
                    "exercise": session_state.exercise_name or "",
                    "state": "IDLE",
                    "reps": 0,
                    "sets": 0,
                    "form_score": int(session_state.performance_score),
                    "warnings": [],
                    "timer_display": None,
                    "finished": metrics.get("finished", False),
                    "completion_reason": metrics.get("completion_reason", None),
                    "elapsed_time": metrics.get("elapsed_time", 0.0),
                    "joint_angles": joint_angles,
                    "current_angle": metrics.get("current_angle", None)
                }

                if session_state.active_exercise:
                    ex_name = session_state.exercise_name
                    ex_cfg = exercises_config["exercises"].get(ex_name, {})

                    alignment_res = alignment_engine.evaluate(
                        exercise_name=ex_name,
                        config=ex_cfg,
                        keypoints=keypoints,
                        angle_engine=angle_engine,
                        frame_shape=frame.shape[:2],
                        now=now
                    )

                    ghost_dict = {
                        name: {"x": kp.x, "y": kp.y}
                        for name, kp in alignment_res.ghost_keypoints.items()
                    }

                    alignment_data = {
                        "score": alignment_res.alignment_score,
                        "ready": alignment_res.ready,
                        "joint_statuses": alignment_res.joint_statuses,
                        "coaching_messages": alignment_res.coaching_messages,
                        "ghost_keypoints": ghost_dict
                    }

                    is_aligning = (session_state.active_exercise.state == ExerciseState.ALIGNING)
                    if is_aligning and alignment_res.ready:
                        session_state.active_exercise.alignment_ready = True

                    tracking_data["state"] = session_state.active_exercise.state.value

                    # Pipeline Audit Logging
                    reason_not_ready = ""
                    if not alignment_res.ready:
                        if num_kps == 0:
                            reason_not_ready = "No landmarks detected by MediaPipe"
                        elif alignment_res.alignment_score < alignment_engine.score_threshold:
                            reason_not_ready = f"Score ({alignment_res.alignment_score:.1f}%) < Threshold ({alignment_engine.score_threshold:.1f}%)"
                        elif alignment_res.stabilization_progress < 1.0:
                            reason_not_ready = f"Stabilizing posture ({int(alignment_res.stabilization_progress * 100)}% complete)"

                    if not is_aligning:
                        prev_reps = session_state.active_exercise.get_display_metrics().get("reps", 0)
                        session_state.active_exercise.update(keypoints, angle_engine, frame.shape[:2], now)
                        
                        metrics = session_state.active_exercise.get_display_metrics()
                        tracking_data["reps"] = metrics.get("reps", 0)
                        tracking_data["sets"] = metrics.get("sets", 0)
                        tracking_data["finished"] = metrics.get("finished", False)
                        tracking_data["current_angle"] = metrics.get("current_angle", None)

                        if session_state.active_exercise.state == ExerciseState.REP_COMPLETED and tracking_data["reps"] != prev_reps:
                            analysis = session_state.performance_analyzer.analyze_rep(
                                session_state.active_exercise.angle_history
                            )
                            session_state.performance_score = analysis.get("score", 0)
                            csv_logger.log_rep(
                                exercise_name=session_state.exercise_name,
                                rep_count=tracking_data["reps"],
                                smoothness=analysis.get("smoothness", 0),
                                depth=analysis.get("depth", 0),
                                score=session_state.performance_score
                            )

                        tracking_data["warnings"] = [
                            {"warning": w.warning, "suggestion": w.suggestion}
                            for w in session_state.active_exercise.warnings[:2]
                        ]
                        tracking_data["form_score"] = int(session_state.performance_score)

                payload = {
                    "type": "inference",
                    "keypoints": keypoints_dict,
                    "alignment": alignment_data,
                    "tracking": tracking_data
                }
                await websocket.send_json(payload)

    except WebSocketDisconnect:
        print("WebSocket client disconnected.")
        session_state.reset()
    except Exception as e:
        print(f"WebSocket session error: {e}")
        session_state.reset()


# Mount Static Files (Frontend HTML/CSS/JS)
web_dirs = [
    os.path.join(os.path.dirname(__file__), "..", "web"),
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"),
    os.path.join(os.path.dirname(__file__), "web"),
]
for target_dir in web_dirs:
    if os.path.exists(target_dir):
        app.mount("/", StaticFiles(directory=target_dir, html=True), name="static")
        break
