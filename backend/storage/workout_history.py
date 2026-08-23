"""
Workout session storage manager for statistics, best performance, and streaks.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from storage.json_storage import JSONStorage
from analytics.statistics import StatisticsEngine

class WorkoutHistoryManager:
    """
    Saves and indexes workout sessions and calculates statistics.
    """
    def __init__(self, storage_path: str = "workout_history.json"):
        self.storage = JSONStorage(storage_path)
        self.history = self.storage.load()

    def log_session(
        self,
        exercise_name: str,
        reps: int,
        sets: int,
        elapsed_time: float,
        avg_score: float
    ) -> None:
        """
        Record a completed workout session.
        """
        session_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "exercise": exercise_name,
            "reps": reps,
            "sets": sets,
            "elapsed_time": round(elapsed_time, 1),
            "avg_score": round(avg_score, 1)
        }
        self.history.append(session_entry)
        self.storage.save(self.history)

    def get_history(self) -> List[Dict[str, Any]]:
        """Return history sessions list."""
        return self.history

    def get_streak(self) -> int:
        """Calculate current user consecutive workout streak."""
        dates = [entry["date"] for entry in self.history if "date" in entry]
        return StatisticsEngine.calculate_streak(dates)

    def get_personal_bests(self, exercise_name: str) -> Dict[str, Any]:
        """
        Get personal best reps and form score for a specific exercise.
        """
        relevant = [entry for entry in self.history if entry.get("exercise") == exercise_name]
        if not relevant:
            return {"max_reps": 0, "best_score": 0.0}

        max_reps = max(entry.get("reps", 0) for entry in relevant)
        best_score = max(entry.get("avg_score", 0.0) for entry in relevant)
        return {
            "max_reps": max_reps,
            "best_score": float(best_score)
        }
