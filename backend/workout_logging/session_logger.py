"""
Abstract Logger interface for session analytics logging.
"""
from abc import ABC, abstractmethod

class SessionLogger(ABC):
    """
    Abstract interface for logging completed reps and session outcomes.
    """
    @abstractmethod
    def log_rep(
        self,
        exercise_name: str,
        rep_count: int,
        smoothness: float,
        depth: float,
        score: float
    ) -> None:
        """Log performance metadata of a completed repetition."""
        pass
