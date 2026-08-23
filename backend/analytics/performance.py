"""
Composite workout performance analyzer coordinating speed, control, depth, stability and symmetry.
"""
from typing import List, Dict, Any
from analytics.smoothness import SmoothnessAnalyzer
from analytics.depth import DepthAnalyzer
from analytics.scoring import ScoringEngine

class PerformanceAnalyzer:
    """
    Coordinating hub for real-time repetition metrics.
    """
    def __init__(self):
        self.smoothness_analyzer = SmoothnessAnalyzer()
        self.depth_analyzer = DepthAnalyzer()

    def analyze_rep(
        self,
        angle_history: List[float],
        symmetry_score: float = 100.0
    ) -> Dict[str, Any]:
        """
        Analyze the completed rep and output score breakdown.
        """
        smoothness = self.smoothness_analyzer.calculate_smoothness(angle_history)
        depth = self.depth_analyzer.calculate_depth(angle_history)
        
        final_score = ScoringEngine.compute_rep_score(
            smoothness=smoothness,
            depth=depth,
            symmetry=symmetry_score
        )

        warning = ""
        if smoothness < 55.0:
            warning = "Control movement"

        return {
            "smoothness": int(smoothness),
            "depth": int(depth),
            "score": final_score,
            "warning": warning
        }
