"""
CSV Logging implementation.
"""
import os
import csv
from datetime import datetime
from workout_logging.session_logger import SessionLogger

class CSVLogger(SessionLogger):
    """
    Logs repetition-level statistics into CSV format.
    """
    def __init__(self, log_path: str = "performance_log.csv"):
        self.log_path = log_path

    def log_rep(
        self,
        exercise_name: str,
        rep_count: int,
        smoothness: float,
        depth: float,
        score: float
    ) -> None:
        file_exists = os.path.exists(self.log_path)

        with open(self.log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Date", "Exercise", "Reps", "Smoothness", "Depth", "Score"])
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                exercise_name,
                rep_count,
                int(smoothness),
                int(depth),
                int(score)
            ])
