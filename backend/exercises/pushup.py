"""
Push-up exercise tracker.
"""
from typing import Dict, Any, List, Tuple
from exercises.base_exercise import BaseExercise, FormWarning
from pose.keypoints import Keypoint
from pose.angles import AngleEngine
from tracking.rep_counter import RepCounter
from utils.enums import ExerciseState, WarningSeverity

class Pushup(BaseExercise):
    """
    Tracks push-up repetitions and checks form stability.
    Checks:
    - Hip sagging (hips collapsing towards the floor).
    - Partial ROM (elbow joint not reaching extension or depth).
    """
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        down_th = config.get("down_threshold", 160.0)
        up_th = config.get("up_threshold", 100.0)
        self.rep_counter = RepCounter(
            down_threshold=down_th,
            up_threshold=up_th,
            cooldown=self.cooldown
        )
        self.sets = 0

    def update(
        self,
        keypoints: Dict[str, Keypoint],
        angle_engine: AngleEngine,
        frame_shape: Tuple[int, int],
        now: float
    ) -> None:
        joints = self.keypoint_mapping
        ang = angle_engine.get_joint_angle(keypoints, joints, frame_shape)

        if ang is not None:
            self.angle_history.append(ang)
            if len(self.angle_history) > self.max_history_len:
                self.angle_history.pop(0)

            rep_completed = self.rep_counter.update(ang, now)
            self.state = ExerciseState.STARTED

            if rep_completed:
                self.state = ExerciseState.REP_COMPLETED
                if self.rep_counter.reps >= self.target_reps:
                    self.sets += 1
                    self.rep_counter.reps = 0
                    if self.sets >= self.target_sets:
                        self.state = ExerciseState.FINISHED
                        self.completion_reason = "target_reached"

            self.warnings = self.validate_form(keypoints, angle_engine, frame_shape)

    def validate_form(
        self,
        keypoints: Dict[str, Keypoint],
        angle_engine: AngleEngine,
        frame_shape: Tuple[int, int]
    ) -> List[FormWarning]:
        warnings = []

        # Check Hip Sagging (shoulder-hip-ankle alignment should be straight, i.e., close to 180 degrees)
        # We can map standard left side or right side hip alignment
        hip_joints = ["left_shoulder", "left_hip", "left_ankle"]
        hip_ang = angle_engine.get_joint_angle(keypoints, hip_joints, frame_shape)
        if hip_ang is not None:
            min_hip_angle = self.config.get("checks", {}).get("hip_sagging", {}).get("min_hip_angle", 150.0)
            if hip_ang < min_hip_angle:
                warnings.append(
                    FormWarning(
                        warning="Hip sagging",
                        severity=WarningSeverity.CRITICAL,
                        suggestion="Keep your core tight and body straight. Don't let your hips sag."
                    )
                )

        # Check Partial ROM
        if self.angle_history:
            max_ang = max(self.angle_history)
            max_up_angle = self.config.get("checks", {}).get("partial_rom", {}).get("max_up_angle", 110.0)
            if max_ang < max_up_angle and len(self.angle_history) > 15:
                warnings.append(
                    FormWarning(
                        warning="Partial ROM",
                        severity=WarningSeverity.WARNING,
                        suggestion="Push all the way up to complete the extension."
                    )
                )

        return warnings

    def reset(self) -> None:
        super().reset()
        self.rep_counter.reset()
        self.sets = 0

    def get_display_metrics(self) -> Dict[str, Any]:
        curr_ang = self.angle_history[-1] if self.angle_history else None
        return {
            "reps": self.rep_counter.reps,
            "sets": self.sets,
            "stage": self.rep_counter.stage,
            "state": self.state,
            "finished": (self.state == ExerciseState.FINISHED),
            "completion_reason": self.completion_reason,
            "current_angle": round(curr_ang, 1) if curr_ang is not None else None
        }
