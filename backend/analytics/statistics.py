"""
Workout sessions statistics and weekly/monthly summary engine.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

class StatisticsEngine:
    """
    Computes averages, counts, streaks, and trends from historical data.
    """
    @staticmethod
    def calculate_streak(workout_dates: List[str]) -> int:
        """
        Calculate consecutive days workout streak.
        """
        if not workout_dates:
            return 0

        parsed_dates = sorted(list(set(
            datetime.strptime(d.split()[0], "%Y-%m-%d").date()
            for d in workout_dates
        )), reverse=True)

        if not parsed_dates:
            return 0

        streak = 0
        today = datetime.now().date()
        expected = today

        # If user didn't workout today, check if they did yesterday to continue streak
        if parsed_dates[0] != today:
            if parsed_dates[0] == today - timedelta(days=1):
                expected = today - timedelta(days=1)
            else:
                return 0

        for date in parsed_dates:
            if date == expected:
                streak += 1
                expected -= timedelta(days=1)
            else:
                break
        return streak

    @staticmethod
    def summarize_sessions(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Produce summaries (weekly, monthly, totals).
        """
        if not sessions:
            return {
                "total_reps": 0,
                "total_sets": 0,
                "avg_score": 0.0,
                "total_time_sec": 0
            }

        total_reps = sum(s.get("reps", 0) for s in sessions)
        total_sets = sum(s.get("sets", 0) for s in sessions)
        avg_score = sum(s.get("avg_score", 0.0) for s in sessions) / len(sessions)
        total_time = sum(s.get("elapsed_time", 0.0) for s in sessions)

        return {
            "total_reps": total_reps,
            "total_sets": total_sets,
            "avg_score": float(avg_score),
            "total_time_sec": int(total_time)
        }
