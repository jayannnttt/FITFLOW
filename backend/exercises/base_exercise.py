"""
Base Exercise abstract model defining pose tracking lifecycle.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

from pose.keypoints import Keypoint
from pose.angles import AngleEngine
from utils.enums import ExerciseType, ExerciseState, WarningSeverity

@dataclass
class FormWarning:
    warning: str
    severity: WarningSeverity
    suggestion: str


class BaseExercise(ABC):
    """
    Abstract base class for all rep-based and time-based exercises.
    """
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.type = ExerciseType[config.get("type", "REP_BASED")]
        self.target_reps = config.get("target_reps", 10)
        self.target_sets = config.get("target_sets", 3)
        self.cooldown = config.get("cooldown", 0.8)
        self.primary_joint = config.get("primary_joint", "")
        self.keypoint_mapping = config.get("keypoints", [])
        self.alt_keypoint_mapping = config.get("alt_keypoints", [])

        # Tracking state variables
        self.state = ExerciseState.ALIGNING
        self.alignment_ready = False
        self.completion_reason: Optional[str] = None
        self.warnings: List[FormWarning] = []
        self.angle_history: List[float] = []
        self.max_history_len = 50

    def start_tracking(self, now: float) -> None:
        """Start active tracking session."""
        self.state = ExerciseState.STARTED
        self.alignment_ready = True
        self.completion_reason = None

    @abstractmethod
    def update(
        self,
        keypoints: Dict[str, Keypoint],
        angle_engine: AngleEngine,
        frame_shape: Tuple[int, int],
        now: float
    ) -> None:
        """Process latest landmarks and update internal tracking and exercise state."""
        pass

    @abstractmethod
    def validate_form(
        self,
        keypoints: Dict[str, Keypoint],
        angle_engine: AngleEngine,
        frame_shape: Tuple[int, int]
    ) -> List[FormWarning]:
        """Perform safety and posture checks against keypoint angles."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset tracking state for next session."""
        self.state = ExerciseState.ALIGNING
        self.alignment_ready = False
        self.completion_reason = None
        self.warnings.clear()
        self.angle_history.clear()

    @abstractmethod
    def get_display_metrics(self) -> Dict[str, Any]:
        """Return tracking information for UI display overlay."""
        pass
