"""
Bicep Curl exercise tracker.
"""
from typing import Dict, Any, List, Tuple
from exercises.base_exercise import BaseExercise, FormWarning
from pose.keypoints import Keypoint
from pose.angles import AngleEngine
from tracking.rep_counter import RepCounter
from utils.enums import ExerciseState, WarningSeverity

class BicepCurl(BaseExercise):
    """
    Tracks bicep curl repetitions and validates form.
    Checks:
    - Swinging elbow (excessive shoulder forward/backward movement).
    - Incomplete extension (not lowering arm fully at the bottom).
    """
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        down_th = config.get("down_threshold", 150.0)
        up_th = config.get("up_threshold", 90.0)
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
        # Calculate angle of target arm (using keypoint mapping)
        # default: left_shoulder, left_elbow, left_wrist
        joints = self.keypoint_mapping
        ang = angle_engine.get_joint_angle(keypoints, joints, frame_shape)

        if ang is not None:
            self.angle_history.append(ang)
            if len(self.angle_history) > self.max_history_len:
                self.angle_history.pop(0)

            # Update RepCounter
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

            # Form warning check
            self.warnings = self.validate_form(keypoints, angle_engine, frame_shape)

    def validate_form(
        self,
        keypoints: Dict[str, Keypoint],
        angle_engine: AngleEngine,
        frame_shape: Tuple[int, int]
    ) -> List[FormWarning]:
        warnings = []
        
        # Check incomplete extension using angle history
        if self.angle_history:
            max_ang = max(self.angle_history)
            # Should reach down threshold (150)
            target_ext = self.config.get("checks", {}).get("incomplete_extension", {}).get("min_down_angle", 140.0)
            if max_ang < target_ext and len(self.angle_history) > 15:
                warnings.append(
                    FormWarning(
                        warning="Incomplete extension",
                        severity=WarningSeverity.WARNING,
                        suggestion="Fully extend your arm at the bottom of the movement."
                    )
                )

        # Check elbow swinging (shoulder alignment to hip)
        # Verify elbow doesn't drift too far from the torso plane (shoulder to hip angle)
        # We can approximate this by measuring the shoulder-hip-knee or vertical shoulder alignment
        if "left_shoulder" in keypoints and "left_hip" in keypoints and "left_elbow" in keypoints:
            sh_ang = angle_engine.get_joint_angle(
                keypoints,
                ["left_elbow", "left_shoulder", "left_hip"],
                frame_shape
            )
            if sh_ang is not None:
                # If elbow drifts forward/backward relative to shoulder-hip axis
                if sh_ang > self.config.get("checks", {}).get("elbow_swing", {}).get("max_shoulder_movement", 30.0):
                    warnings.append(
                        FormWarning(
                            warning="Elbow swinging",
                            severity=WarningSeverity.WARNING,
                            suggestion="Keep your elbows locked close to your sides."
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
