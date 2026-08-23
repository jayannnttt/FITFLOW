"""
Enum Definitions for AI Fitness Tracker Backend
"""
from enum import Enum


class ExerciseType(str, Enum):
    """Category of exercise tracking mode."""
    REP_BASED = "REP_BASED"
    TIME_BASED = "TIME_BASED"


class ExerciseState(str, Enum):
    """Exercise lifecycle state machine states."""
    IDLE = "IDLE"
    ALIGNING = "ALIGNING"
    READY = "READY"
    STARTED = "STARTED"
    DOWN = "DOWN"
    UP = "UP"
    REP_COMPLETED = "REP_COMPLETED"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    RESET = "RESET"


class UIMode(str, Enum):
    """UI Screen mode."""
    CATEGORY = "CATEGORY"
    EXERCISE = "EXERCISE"
    TRACK = "TRACK"


class WarningSeverity(str, Enum):
    """Form warning severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
