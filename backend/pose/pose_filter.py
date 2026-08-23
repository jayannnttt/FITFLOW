"""
Pose filter manager to apply configured smoothing filters on keypoint sets.
"""
from typing import Dict
from pose.keypoints import Keypoint
from pose.smoothing import MovingAverageFilter, EMAFilter, KalmanPoseFilter, OneEuroPoseFilter

class PoseFilterManager:
    """
    Applies coordinate smoothing filters (EMA, MA, Kalman, or One Euro Filter).
    """
    def __init__(self, method: str = "one_euro", window_size: int = 5, alpha: float = 0.4):
        self.method = method.lower().strip()
        self.ma_filter = MovingAverageFilter(window_size=window_size)
        self.ema_filter = EMAFilter(alpha=alpha)
        self.kalman_filter = KalmanPoseFilter()
        self.one_euro_filter = OneEuroPoseFilter()

    def filter_pose(self, keypoints: Dict[str, Keypoint], now: float = 0.0) -> Dict[str, Keypoint]:
        """
        Apply current smoothing strategy to each keypoint in the dataset.
        """
        if self.method == "none":
            return keypoints

        smoothed_keypoints: Dict[str, Keypoint] = {}
        for name, kp in keypoints.items():
            if self.method == "moving_average":
                sx, sy = self.ma_filter.filter(name, kp.x, kp.y)
            elif self.method == "ema":
                sx, sy = self.ema_filter.filter(name, kp.x, kp.y)
            elif self.method == "kalman":
                sx, sy = self.kalman_filter.filter(name, kp.x, kp.y)
            elif self.method == "one_euro":
                sx, sy = self.one_euro_filter.filter(name, kp.x, kp.y, now)
            else:
                sx, sy = kp.x, kp.y

            smoothed_keypoints[name] = Keypoint(
                name=kp.name,
                x=sx,
                y=sy,
                confidence=kp.confidence
            )

        return smoothed_keypoints

    def reset(self) -> None:
        """Reset internal filter states for new session."""
        self.ma_filter = MovingAverageFilter(window_size=self.ma_filter.window_size)
        self.ema_filter = EMAFilter(alpha=self.ema_filter.alpha)
        self.kalman_filter = KalmanPoseFilter()
        self.one_euro_filter = OneEuroPoseFilter()

