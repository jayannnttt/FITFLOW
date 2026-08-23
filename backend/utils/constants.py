"""
Global System Constants & Keypoint Mappings
Premium Design System Color Tokens (BGR format for OpenCV)
"""
from typing import Dict, List, Tuple

# Default target parameters
DEFAULT_TARGET_REPS: int = 10
DEFAULT_REP_COOLDOWN_SEC: float = 0.8
DEFAULT_VISIBILITY_THRESHOLD: float = 0.5

# Camera defaults
DEFAULT_CAMERA_INDEX: int = 0
DEFAULT_FRAME_WIDTH: int = 1280
DEFAULT_FRAME_HEIGHT: int = 720
TARGET_FPS: int = 30

# File Paths
DEFAULT_LOG_CSV: str = "performance_log.csv"
DEFAULT_HISTORY_JSON: str = "workout_history.json"
DEFAULT_DB_FILE: str = "workout_database.db"

# Premium Dark Mode Color Palette (BGR format for OpenCV)
# Background: #0F172A (Slate 900)
COLOR_BG: Tuple[int, int, int] = (42, 23, 15)
# Surface Cards: #1E293B (Slate 800)
COLOR_SURFACE: Tuple[int, int, int] = (59, 41, 30)
# Card Borders: #334155 (Slate 700)
COLOR_SURFACE_BORDER: Tuple[int, int, int] = (85, 65, 51)

# Primary Blue: #3B82F6 (Blue 500)
COLOR_PRIMARY: Tuple[int, int, int] = (246, 130, 59)
# Success Green: #22C55E (Emerald 500)
COLOR_SUCCESS: Tuple[int, int, int] = (94, 197, 34)
# Warning Yellow: #FACC15 (Yellow 400)
COLOR_WARNING: Tuple[int, int, int] = (21, 204, 250)
# Error Red: #EF4444 (Red 500)
COLOR_ERROR: Tuple[int, int, int] = (68, 68, 239)

# Text Colors
COLOR_TEXT_PRIMARY: Tuple[int, int, int] = (252, 250, 248)  # #F8FAFC (Slate 50)
COLOR_TEXT_MUTED: Tuple[int, int, int] = (184, 163, 148)    # #94A3B8 (Slate 400)
COLOR_TEXT_HEADER: Tuple[int, int, int] = COLOR_PRIMARY
COLOR_TEXT_OPTION: Tuple[int, int, int] = COLOR_TEXT_PRIMARY
COLOR_TEXT_INFO: Tuple[int, int, int] = COLOR_TEXT_MUTED
COLOR_SCORE: Tuple[int, int, int] = COLOR_SUCCESS

# Landmark Index Dictionary for MediaPipe Pose (33 Keypoints)
MEDIAPIPE_KEYPOINTS: Dict[str, int] = {
    "nose": 0,
    "left_eye_inner": 1,
    "left_eye": 2,
    "left_eye_outer": 3,
    "right_eye_inner": 4,
    "right_eye": 5,
    "right_eye_outer": 6,
    "left_ear": 7,
    "right_ear": 8,
    "mouth_left": 9,
    "mouth_right": 10,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_pinky": 17,
    "right_pinky": 18,
    "left_index": 19,
    "right_index": 20,
    "left_thumb": 21,
    "right_thumb": 22,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
    "left_heel": 29,
    "right_heel": 30,
    "left_foot_index": 31,
    "right_foot_index": 32,
}

# Alias for backwards compatibility
COCO_KEYPOINTS: Dict[str, int] = MEDIAPIPE_KEYPOINTS
