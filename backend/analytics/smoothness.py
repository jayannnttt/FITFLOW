"""
Smoothness calculation analyzer based on angle transitions.
"""
from typing import List
import numpy as np

class SmoothnessAnalyzer:
    """
    Analyzes landmark velocity profiles to determine movement smoothness.
    """
    @staticmethod
    def calculate_smoothness(angle_history: List[float]) -> float:
        if len(angle_history) < 6:
            return 100.0

        # Calculate angular velocity (difference between successive angles)
        velocity = np.diff(angle_history)
        std_val = float(np.std(velocity))
        
        # Original math: max(0, 100 - int(np.std(velocity) * 12))
        smoothness = max(0.0, 100.0 - (std_val * 12.0))
        return float(smoothness)
