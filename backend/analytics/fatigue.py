"""
Muscle fatigue analyzer based on workout intensity and performance velocity.
"""
from typing import List

class FatigueAnalyzer:
    """
    Estimates fatigue based on deceleration of reps and form degradation.
    """
    @staticmethod
    def estimate_fatigue(rep_durations: List[float], form_scores: List[float]) -> float:
        """
        Return fatigue percentage (0 to 100).
        """
        if len(rep_durations) < 3:
            return 0.0

        # Check if duration of recent reps is increasing (slowing down)
        recent_avg = sum(rep_durations[-3:]) / 3.0
        baseline_avg = sum(rep_durations[:3]) / 3.0

        ratio = recent_avg / max(0.1, baseline_avg)
        fatigue = 0.0

        if ratio > 1.2:
            fatigue += (ratio - 1.0) * 100.0

        # Form degradation contribution
        if len(form_scores) >= 3:
            recent_form = sum(form_scores[-3:]) / 3.0
            baseline_form = sum(form_scores[:3]) / 3.0
            form_drop = baseline_form - recent_form
            if form_drop > 0:
                fatigue += form_drop * 0.5

        return float(min(100.0, max(0.0, fatigue)))
