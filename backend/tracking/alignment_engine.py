"""
AI-Guided Alignment Engine for pre-exercise posture verification and form coaching.
Clean separation of backend posture analysis from frontend rendering logic.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import math
import numpy as np

from pose.keypoints import Keypoint
from pose.angles import AngleEngine
from utils.constants import MEDIAPIPE_KEYPOINTS

@dataclass
class AlignmentResult:
    """Structured alignment result passed from backend to frontend UI renderer."""
    alignment_score: float             # Smoothed 0 to 100 percentage score
    raw_score: float                   # Instantaneous score
    ready: bool                        # True when posture calibration completes
    joint_statuses: Dict[str, str]      # "correct", "incorrect", "adjusting"
    coaching_messages: List[str]       # Top 2-3 prioritized coaching messages
    ghost_keypoints: Dict[str, Keypoint] # Dynamically scaled target reference skeleton
    stabilization_progress: float      # 0.0 to 1.0 stabilization timer ratio


class AlignmentEngine:
    """
    Evaluates starting postures and live exercise form against configurable target joint angles.
    Generates scale-aware ghost skeletons, EMA-smoothed alignment scores, prioritized coaching,
    and tracking-loss grace periods.
    """
    def __init__(
        self,
        score_threshold: float = 85.0,
        stabilization_sec: float = 0.8,
        grace_period_sec: float = 0.5,
        smoothing_alpha: float = 0.3
    ):
        self.score_threshold = score_threshold
        self.stabilization_sec = stabilization_sec
        self.grace_period_sec = grace_period_sec
        self.smoothing_alpha = smoothing_alpha

        # Internal state tracking
        self.smoothed_score: float = 0.0
        self.stabilization_start_time: Optional[float] = None
        self.last_valid_time: float = 0.0
        self.last_result: Optional[AlignmentResult] = None
        self.is_ready: bool = False

    def reset(self) -> None:
        """Reset alignment engine state for new session."""
        self.smoothed_score = 0.0
        self.stabilization_start_time = None
        self.last_valid_time = 0.0
        self.last_result = None
        self.is_ready = False

    def evaluate(
        self,
        exercise_name: str,
        config: Dict[str, Any],
        keypoints: Dict[str, Keypoint],
        angle_engine: AngleEngine,
        frame_shape: Tuple[int, int],
        now: float
    ) -> AlignmentResult:
        """
        Evaluate current pose against exercise alignment configuration.
        """
        # Handle tracking loss grace period
        has_user = len(keypoints) > 0 and any(kp.confidence > 0.4 for kp in keypoints.values())

        if has_user:
            self.last_valid_time = now
        else:
            # Check grace period buffer
            if self.last_result is not None and (now - self.last_valid_time) <= self.grace_period_sec:
                return self.last_result
            else:
                self.reset()
                empty_result = AlignmentResult(
                    alignment_score=0.0,
                    raw_score=0.0,
                    ready=False,
                    joint_statuses={},
                    coaching_messages=["⚠ Step into camera view"],
                    ghost_keypoints=self._generate_default_ghost(frame_shape),
                    stabilization_progress=0.0
                )
                self.last_result = empty_result
                return empty_result

        alignment_cfg = config.get("alignment", {})
        target_angles = alignment_cfg.get("starting_pose_angles", {})
        tolerances = alignment_cfg.get("tolerances", {})
        coaching_rules = alignment_cfg.get("coaching_rules", {})

        joint_statuses: Dict[str, str] = {}
        raw_coaching: List[Tuple[float, str]] = []  # (deviation, message)
        joint_scores: List[float] = []

        # Evaluate target joint angles
        for joint_key, target_deg in target_angles.items():
            tol = tolerances.get(joint_key, 20.0)
            measured_ang, joint_names = self._measure_joint_angle(joint_key, keypoints, angle_engine, frame_shape)

            if measured_ang is None:
                joint_scores.append(0.0)
                msg = coaching_rules.get(joint_key, f"Adjust {joint_key.replace('_', ' ')}")
                raw_coaching.append((999.0, f"⚠ {msg}"))
                for jn in joint_names:
                    joint_statuses[jn] = "incorrect"
                continue

            diff = abs(measured_ang - target_deg)
            # Normalize score for this joint
            j_score = max(0.0, 100.0 - (diff / tol) * 50.0)
            joint_scores.append(j_score)

            # Determine status: Green (correct), Yellow (adjusting), Red (incorrect)
            if diff <= tol * 0.5:
                status = "correct"
            elif diff <= tol:
                status = "adjusting"
            else:
                status = "incorrect"

            for jn in joint_names:
                # Retain worst status for shared keypoints
                if joint_statuses.get(jn) != "incorrect":
                    joint_statuses[jn] = status

            if status != "correct":
                msg = coaching_rules.get(joint_key, f"Adjust {joint_key.replace('_', ' ')}")
                raw_coaching.append((diff, f"⚠ {msg}"))

        # Camera centering / facing guidance checks
        if "left_shoulder" in keypoints and "right_shoulder" in keypoints:
            ls, rs = keypoints["left_shoulder"], keypoints["right_shoulder"]
            center_x = (ls.x + rs.x) / 2.0
            if center_x < 0.25:
                raw_coaching.append((50.0, "⚠ Move slightly to the right"))
            elif center_x > 0.75:
                raw_coaching.append((50.0, "⚠ Move slightly to the left"))

            shoulder_width = abs(ls.x - rs.x)
            if shoulder_width < 0.1:
                raw_coaching.append((60.0, "⚠ Face the camera directly"))

        # Calculate raw alignment score
        raw_score = sum(joint_scores) / len(joint_scores) if joint_scores else 0.0

        # Apply EMA Temporal Smoothing to alignment score
        if self.smoothed_score == 0.0:
            self.smoothed_score = raw_score
        else:
            self.smoothed_score = (self.smoothing_alpha * raw_score) + ((1.0 - self.smoothing_alpha) * self.smoothed_score)

        # Prioritize top 2-3 coaching messages (sort by deviation severity)
        raw_coaching.sort(key=lambda x: x[0], reverse=True)
        coaching_messages = [item[1] for item in raw_coaching[:3]]

        # Stabilization timer for ready state
        stabilization_ratio = 0.0
        if self.smoothed_score >= self.score_threshold:
            if self.stabilization_start_time is None:
                self.stabilization_start_time = now
            
            elapsed = now - self.stabilization_start_time
            stabilization_ratio = min(1.0, elapsed / self.stabilization_sec)

            if elapsed >= self.stabilization_sec:
                self.is_ready = True
                coaching_messages = ["✓ Perfect Alignment | Starting Rep Counter..."]
        else:
            self.stabilization_start_time = None
            self.is_ready = False

        # Generate scale-aware Ghost Skeleton overlay matching user body size
        ghost_kps = self._generate_scale_aware_ghost(keypoints, target_angles)

        result = AlignmentResult(
            alignment_score=round(self.smoothed_score, 1),
            raw_score=round(raw_score, 1),
            ready=self.is_ready,
            joint_statuses=joint_statuses,
            coaching_messages=coaching_messages,
            ghost_keypoints=ghost_kps,
            stabilization_progress=round(stabilization_ratio, 2)
        )
        self.last_result = result
        return result

    def _measure_joint_angle(
        self,
        joint_key: str,
        keypoints: Dict[str, Keypoint],
        angle_engine: AngleEngine,
        frame_shape: Tuple[int, int]
    ) -> Tuple[Optional[float], List[str]]:
        """Map abstract joint keys to keypoint triplets and compute angle."""
        mapping = {
            "left_elbow": ["left_shoulder", "left_elbow", "left_wrist"],
            "right_elbow": ["right_shoulder", "right_elbow", "right_wrist"],
            "left_knee": ["left_hip", "left_knee", "left_ankle"],
            "right_knee": ["right_hip", "right_knee", "right_ankle"],
            "torso": ["left_shoulder", "left_hip", "left_knee"],
            "hip": ["left_shoulder", "left_hip", "left_knee"],
            "left_ankle": ["left_knee", "left_ankle", "left_foot_index"],
            "right_ankle": ["right_knee", "right_ankle", "right_foot_index"]
        }
        joint_names = mapping.get(joint_key, ["left_shoulder", "left_elbow", "left_wrist"])
        ang = angle_engine.get_joint_angle(keypoints, joint_names, frame_shape)
        return ang, joint_names

    def _generate_scale_aware_ghost(
        self,
        user_kps: Dict[str, Keypoint],
        target_angles: Dict[str, float]
    ) -> Dict[str, Keypoint]:
        """
        Dynamically generate reference Ghost Skeleton scale-aligned and centered
        relative to the user's detected torso height and shoulder position.
        """
        if "left_shoulder" not in user_kps or "right_shoulder" not in user_kps:
            return self._generate_default_ghost((720, 1280))

        ls = user_kps["left_shoulder"]
        rs = user_kps["right_shoulder"]
        cx = (ls.x + rs.x) / 2.0
        cy = (ls.y + rs.y) / 2.0

        # Torso height estimation
        hip_y = user_kps["left_hip"].y if "left_hip" in user_kps else cy + 0.3
        torso_scale = max(0.15, abs(hip_y - cy))

        ghost: Dict[str, Keypoint] = {}
        
        # Base head & shoulder anchors
        ghost["nose"] = Keypoint("nose", cx, cy - torso_scale * 0.4, 0.9)
        ghost["left_shoulder"] = Keypoint("left_shoulder", cx - torso_scale * 0.4, cy, 0.9)
        ghost["right_shoulder"] = Keypoint("right_shoulder", cx + torso_scale * 0.4, cy, 0.9)

        # Arms based on target elbow angle
        left_elbow_ang = target_angles.get("left_elbow", 170.0)
        right_elbow_ang = target_angles.get("right_elbow", 170.0)

        # Calculate elbow/wrist relative vectors
        l_arm_rad = math.radians(180.0 - left_elbow_ang / 2.0)
        r_arm_rad = math.radians(180.0 - right_elbow_ang / 2.0)

        ghost["left_elbow"] = Keypoint(
            "left_elbow",
            cx - torso_scale * 0.5,
            cy + torso_scale * 0.6 * math.sin(l_arm_rad),
            0.9
        )
        ghost["left_wrist"] = Keypoint(
            "left_wrist",
            cx - torso_scale * 0.5,
            cy + torso_scale * 1.2 * math.sin(l_arm_rad),
            0.9
        )

        ghost["right_elbow"] = Keypoint(
            "right_elbow",
            cx + torso_scale * 0.5,
            cy + torso_scale * 0.6 * math.sin(r_arm_rad),
            0.9
        )
        ghost["right_wrist"] = Keypoint(
            "right_wrist",
            cx + torso_scale * 0.5,
            cy + torso_scale * 1.2 * math.sin(r_arm_rad),
            0.9
        )

        # Hips and legs
        ghost["left_hip"] = Keypoint("left_hip", cx - torso_scale * 0.25, cy + torso_scale, 0.9)
        ghost["right_hip"] = Keypoint("right_hip", cx + torso_scale * 0.25, cy + torso_scale, 0.9)

        left_knee_ang = target_angles.get("left_knee", 170.0)
        leg_rad = math.radians(180.0 - left_knee_ang / 2.0)

        ghost["left_knee"] = Keypoint(
            "left_knee",
            cx - torso_scale * 0.25,
            cy + torso_scale * 1.7 * math.sin(leg_rad),
            0.9
        )
        ghost["left_ankle"] = Keypoint(
            "left_ankle",
            cx - torso_scale * 0.25,
            cy + torso_scale * 2.4 * math.sin(leg_rad),
            0.9
        )

        ghost["right_knee"] = Keypoint(
            "right_knee",
            cx + torso_scale * 0.25,
            cy + torso_scale * 1.7 * math.sin(leg_rad),
            0.9
        )
        ghost["right_ankle"] = Keypoint(
            "right_ankle",
            cx + torso_scale * 0.25,
            cy + torso_scale * 2.4 * math.sin(leg_rad),
            0.9
        )

        return ghost

    def _generate_default_ghost(self, frame_shape: Tuple[int, int]) -> Dict[str, Keypoint]:
        """Default centered ghost template if no user is detected."""
        cx, cy = 0.5, 0.35
        return {
            "nose": Keypoint("nose", cx, cy - 0.1, 0.8),
            "left_shoulder": Keypoint("left_shoulder", cx - 0.12, cy, 0.8),
            "right_shoulder": Keypoint("right_shoulder", cx + 0.12, cy, 0.8),
            "left_elbow": Keypoint("left_elbow", cx - 0.15, cy + 0.15, 0.8),
            "left_wrist": Keypoint("left_wrist", cx - 0.15, cy + 0.3, 0.8),
            "right_elbow": Keypoint("right_elbow", cx + 0.15, cy + 0.15, 0.8),
            "right_wrist": Keypoint("right_wrist", cx + 0.15, cy + 0.3, 0.8),
            "left_hip": Keypoint("left_hip", cx - 0.08, cy + 0.25, 0.8),
            "right_hip": Keypoint("right_hip", cx + 0.08, cy + 0.25, 0.8),
            "left_knee": Keypoint("left_knee", cx - 0.08, cy + 0.45, 0.8),
            "left_ankle": Keypoint("left_ankle", cx - 0.08, cy + 0.65, 0.8),
            "right_knee": Keypoint("right_knee", cx + 0.08, cy + 0.45, 0.8),
            "right_ankle": Keypoint("right_ankle", cx + 0.08, cy + 0.65, 0.8),
        }
