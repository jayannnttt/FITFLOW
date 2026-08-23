"""
Angle Calculation Engine for tracking joint and body angles.
"""
from typing import Dict, Tuple, List, Optional
from pose.keypoints import Keypoint
from utils.math_utils import calculate_angle_2d
from utils.constants import DEFAULT_VISIBILITY_THRESHOLD

class AngleEngine:
    """
    Centralized joint, segment, and spatial angle engine.
    Stores and reuses computed angles for performance.
    """
    def __init__(self, visibility_threshold: float = DEFAULT_VISIBILITY_THRESHOLD):
        self.visibility_threshold = visibility_threshold
        # Cache to prevent duplicate computations on the same frame
        self._cache: Dict[str, float] = {}

    def clear_cache(self) -> None:
        """Clear cache at the start of a new frame."""
        self._cache.clear()

    def get_joint_angle(
        self,
        keypoints: Dict[str, Keypoint],
        joint_names: List[str],
        frame_shape: Tuple[int, int]
    ) -> Optional[float]:
        """
        Calculate joint angle for 3 keypoint names.
        Reuses cached value if calculated previously.
        """
        if len(joint_names) != 3:
            return None

        cache_key = "-".join(joint_names)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Verify all keypoints exist and meet visibility constraints
        for name in joint_names:
            if name not in keypoints:
                return None
            if keypoints[name].confidence < self.visibility_threshold:
                return None

        pt_a = (keypoints[joint_names[0]].x, keypoints[joint_names[0]].y)
        pt_b = (keypoints[joint_names[1]].x, keypoints[joint_names[1]].y)
        pt_c = (keypoints[joint_names[2]].x, keypoints[joint_names[2]].y)

        h, w = frame_shape
        angle = calculate_angle_2d(pt_a, pt_b, pt_c, w, h)
        self._cache[cache_key] = angle
        return angle

    def get_body_symmetry(
        self,
        keypoints: Dict[str, Keypoint],
        left_joints: List[str],
        right_joints: List[str],
        frame_shape: Tuple[int, int]
    ) -> Optional[float]:
        """
        Calculate the bilateral symmetry score (0 to 100) between left and right side joints.
        100 indicates perfect matching angles.
        """
        left_ang = self.get_joint_angle(keypoints, left_joints, frame_shape)
        right_ang = self.get_joint_angle(keypoints, right_joints, frame_shape)

        if left_ang is None or right_ang is None:
            return None

        diff = abs(left_ang - right_ang)
        # Convert difference to standard score (where 0 difference = 100 score)
        score = max(0.0, 100.0 - (diff * 2.0))
        return score
