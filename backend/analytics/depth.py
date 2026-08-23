"""
Movement depth and Range of Motion (ROM) analyzer.
"""
from typing import List

class DepthAnalyzer:
    """
    Analyzes depth or extension achieved during an exercise rep.
    """
    @staticmethod
    def calculate_depth(angle_history: List[float], min_threshold: float = 90.0) -> float:
        if not angle_history:
            return 0.0

        min_ang = min(angle_history)
        # Original math: depth = max(40, min(100, int((180 - min_ang) * 0.7)))
        depth = max(40.0, min(100.0, float((180.0 - min_ang) * 0.7)))
        return depth
