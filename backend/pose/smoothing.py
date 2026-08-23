"""
Landmark coordinate smoothing filters (Kalman, EMA, One Euro Filter).
"""
import math
from typing import Dict, List, Tuple

class LowPassFilter:
    """First-order low-pass filter used in One Euro Filter."""
    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        self.y: float = 0.0
        self.initialized = False

    def filter(self, val: float, alpha: float = -1.0) -> float:
        if alpha >= 0.0:
            self.alpha = alpha
        if not self.initialized:
            self.y = val
            self.initialized = True
        else:
            self.y = self.alpha * val + (1.0 - self.alpha) * self.y
        return self.y


class OneEuroFilter1D:
    """1D One Euro Filter for smoothing coordinates on a single axis."""
    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.0, d_cutoff: float = 1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_filter = LowPassFilter()
        self.dx_filter = LowPassFilter()
        self.last_val = 0.0
        self.initialized = False

    def filter(self, val: float, dt: float) -> float:
        # Avoid zero or negative time intervals
        if dt <= 0.0:
            dt = 0.033  # default ~30 FPS

        # Estimate current rate of variation
        if not self.initialized:
            self.last_val = val
            self.initialized = True
            dx = 0.0
        else:
            dx = (val - self.last_val) / dt
            self.last_val = val

        # Calculate dynamic cutoff frequencies
        alpha_d = self.calculate_alpha(self.d_cutoff, dt)
        edx = self.dx_filter.filter(dx, alpha_d)
        
        cutoff = self.min_cutoff + self.beta * abs(edx)
        alpha = self.calculate_alpha(cutoff, dt)
        
        return self.x_filter.filter(val, alpha)

    def calculate_alpha(self, cutoff: float, dt: float) -> float:
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)


class OneEuroPoseFilter:
    """Manages 2D One Euro filters for multiple landmark keys."""
    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007, d_cutoff: float = 1.0):
        self.filters: Dict[str, Tuple[OneEuroFilter1D, OneEuroFilter1D]] = {}
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.last_time = 0.0

    def filter(self, keypoint_name: str, x: float, y: float, now: float) -> Tuple[float, float]:
        if keypoint_name not in self.filters:
            self.filters[keypoint_name] = (
                OneEuroFilter1D(self.min_cutoff, self.beta, self.d_cutoff),
                OneEuroFilter1D(self.min_cutoff, self.beta, self.d_cutoff)
            )

        if self.last_time == 0.0:
            self.last_time = now
            
        dt = now - self.last_time
        self.last_time = now

        fx, fy = self.filters[keypoint_name]
        return fx.filter(x, dt), fy.filter(y, dt)


class MovingAverageFilter:
    """Smoothing filter based on simple moving average."""
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.history: Dict[str, List[Tuple[float, float]]] = {}

    def filter(self, keypoint_name: str, x: float, y: float) -> Tuple[float, float]:
        if keypoint_name not in self.history:
            self.history[keypoint_name] = []
        
        self.history[keypoint_name].append((x, y))
        if len(self.history[keypoint_name]) > self.window_size:
            self.history[keypoint_name].pop(0)

        coords = self.history[keypoint_name]
        avg_x = sum(pt[0] for pt in coords) / len(coords)
        avg_y = sum(pt[1] for pt in coords) / len(coords)
        return avg_x, avg_y


class EMAFilter:
    """Smoothing filter based on Exponential Moving Average."""
    def __init__(self, alpha: float = 0.4):
        self.alpha = alpha
        self.states: Dict[str, Tuple[float, float]] = {}

    def filter(self, keypoint_name: str, x: float, y: float) -> Tuple[float, float]:
        if keypoint_name not in self.states:
            self.states[keypoint_name] = (x, y)
            return x, y

        prev_x, prev_y = self.states[keypoint_name]
        new_x = self.alpha * x + (1 - self.alpha) * prev_x
        new_y = self.alpha * y + (1 - self.alpha) * prev_y
        self.states[keypoint_name] = (new_x, new_y)
        return new_x, new_y


class KalmanFilter1D:
    """Simple 1D Kalman Filter implementation for a single coordinate axis."""
    def __init__(self, process_noise: float = 1e-4, measurement_noise: float = 1e-2):
        self.q = process_noise  # Process noise covariance
        self.r = measurement_noise  # Measurement noise covariance
        self.x = 0.0  # Estimated state value
        self.p = 1.0  # Estimated error covariance
        self.initialized = False

    def update(self, measurement: float) -> float:
        if not self.initialized:
            self.x = measurement
            self.p = 1.0
            self.initialized = True
            return self.x

        p_pred = self.p + self.q
        k = p_pred / (p_pred + self.r)
        self.x = self.x + k * (measurement - self.x)
        self.p = (1.0 - k) * p_pred
        return self.x


class KalmanPoseFilter:
    """Kalman filtering manager for 2D pose coordinates."""
    def __init__(self, process_noise: float = 1e-4, measurement_noise: float = 1e-2):
        self.filters: Dict[str, Tuple[KalmanFilter1D, KalmanFilter1D]] = {}
        self.q = process_noise
        self.r = measurement_noise

    def filter(self, keypoint_name: str, x: float, y: float) -> Tuple[float, float]:
        if keypoint_name not in self.filters:
            self.filters[keypoint_name] = (
                KalmanFilter1D(self.q, self.r),
                KalmanFilter1D(self.q, self.r)
            )

        kx, ky = self.filters[keypoint_name]
        smoothed_x = kx.update(x)
        smoothed_y = ky.update(y)
        return smoothed_x, smoothed_y
