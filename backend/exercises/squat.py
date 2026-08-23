"""
Squat exercise tracker.
"""
from typing import Dict, Any, List, Tuple
from exercises.base_exercise import BaseExercise, FormWarning
from pose.keypoints import Keypoint
from pose.angles import AngleEngine
from tracking.rep_counter import RepCounter
from utils.enums import ExerciseState, WarningSeverity

class Squat(BaseExercise):
    """
    Tracks squat repetitions and validates form stability.
    Checks:
    - Knee valgus (knees collapsing inward).
    - Insufficient depth (not reaching target depth angle).
    - Excessive forward lean (torso angle leaning too much).
    """
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        down_th = config.get("down_threshold", 155.0)
        up_th = config.get("up_threshold", 110.0)
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

        # Check Insufficient Depth
        if self.angle_history:
            min_ang = min(self.angle_history)
            min_up_angle = self.config.get("checks", {}).get("insufficient_depth", {}).get("min_up_angle", 115.0)
            if min_ang > min_up_angle and len(self.angle_history) > 15:
                warnings.append(
                    FormWarning(
                        warning="Insufficient depth",
                        severity=WarningSeverity.WARNING,
                        suggestion="Lower your hips further until thighs are parallel to ground."
                    )
                )

        # Check Torso Lean (shoulder-hip-vertical vector angle)
        # We check the angle of the left shoulder-hip-knee or vertical leaning.
        if "left_shoulder" in keypoints and "left_hip" in keypoints and "left_knee" in keypoints:
            torso_ang = angle_engine.get_joint_angle(
                keypoints,
                ["left_shoulder", "left_hip", "left_knee"],
                frame_shape
            )
            if torso_ang is not None:
                # Normal torso alignment with vertical: if angle is too small, lean is excessive
                # Here we compare torso angle threshold (e.g. less than 135 degrees relative to knees)
                if torso_ang < 135.0:
                    warnings.append(
                        FormWarning(
                            warning="Leaning too forward",
                            severity=WarningSeverity.WARNING,
                            suggestion="Keep your chest up and back straight."
                        )
                    )

        # Check Knee Valgus (collapsing inward)
        # Check relative horizontal distance of knees to hips if both sides are visible
        if all(kp in keypoints for kp in ["left_hip", "right_hip", "left_knee", "right_knee"]):
            hip_dist = abs(keypoints["left_hip"].x - keypoints["right_hip"].x)
            knee_dist = abs(keypoints["left_knee"].x - keypoints["right_knee"].x)
            if knee_dist < hip_dist * 0.7:
                warnings.append(
                    FormWarning(
                        warning="Knee valgus",
                        severity=WarningSeverity.CRITICAL,
                        suggestion="Push your knees outward in line with your toes."
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
