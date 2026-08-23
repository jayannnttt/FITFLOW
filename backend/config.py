"""
System configurations and parameter settings.
"""
import os
from dataclasses import dataclass

@dataclass
class AppConfig:
    # Camera Settings
    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    target_fps: int = 30
    auto_exposure: bool = True

    # Pose Backend Selection (MediaPipe Pose 33 Landmarks)
    pose_backend: str = "mediapipe"
    model_complexity: int = 0  # 0 for lightweight CPU optimization, 1 for balanced
    
    # Thresholds
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5

    # AI Alignment System Configuration
    alignment_enabled: bool = True
    alignment_score_threshold: float = 85.0       # Target alignment score % to unlock reps
    alignment_stabilization_sec: float = 0.8       # Continuous seconds alignment must be held
    alignment_grace_period_sec: float = 0.5       # Tracking loss grace period buffer
    alignment_smoothing_alpha: float = 0.3        # EMA score smoothing factor

    # Smoothing Filter Settings
    smoothing_enabled: bool = True
    smoothing_method: str = "one_euro"  # "one_euro", "ema", "kalman", "moving_average"
    ema_alpha: float = 0.4
    moving_average_window: int = 5

    # Storage Paths
    exercises_config_path: str = os.path.join("configs", "exercises.json")
    csv_log_path: str = "performance_log.csv"
    session_history_path: str = "workout_history.json"
    sqlite_db_path: str = "workout_database.db"

    # Tracking parameters
    default_target_reps: int = 10
    rep_cooldown: float = 0.8
