"""
Scoring Engine for workouts, reps, and overall sessions.
"""
from typing import List
import numpy as np

class ScoringEngine:
    """
    Computes overall score from various performance parameters.
    """
    @staticmethod
    def compute_rep_score(smoothness: float, depth: float, symmetry: float = 100.0) -> int:
        """
        Calculate composite score 0-100.
        """
        # Weighted average
        score = int(smoothness * 0.4 + depth * 0.4 + symmetry * 0.2)
        return max(0, min(100, score))
