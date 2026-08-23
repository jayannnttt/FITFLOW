"""
Crunch exercise tracker.
"""
from typing import Dict, Any, List, Tuple
from exercises.base_exercise import BaseExercise, FormWarning
from pose.keypoints import Keypoint
from pose.angles import AngleEngine
from tracking.rep_counter import RepCounter
from utils.enums import ExerciseState, WarningSeverity

class Crunch(BaseExercise):
    """
    Tracks abdominal crunch repetitions.
    Checks:
    - Neck strain (neck flexion/bending forward excessively relative to spine).
    """
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        down_th = config.get("down_threshold", 140.0)
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

        # Check Neck strain (ear-shoulder-hip angle or ear alignment)
        # Using left side ear-shoulder-hip as proxy
        if all(kp in keypoints for kp in ["left_ear", "left_shoulder", "left_hip"]):
            neck_ang = angle_engine.get_joint_angle(
                keypoints,
                ["left_ear", "left_shoulder", "left_hip"],
                frame_shape
            )
            if neck_ang is not None:
                # If chin is tucked too hard/head pulled too far forward, angle deviates
                max_flexion = self.config.get("checks", {}).get("neck_strain", {}).get("max_neck_flexion", 35.0)
                if neck_ang < (90.0 - max_flexion):
                    warnings.append(
                        FormWarning(
                            warning="Neck straining",
                            severity=WarningSeverity.WARNING,
                            suggestion="Keep your gaze up at the ceiling. Don't pull your neck."
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
