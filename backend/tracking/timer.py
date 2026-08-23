"""
Exercise session and segment timer manager.
"""
from typing import Optional

class ExerciseTimer:
    """
    Manages timer states for time-based exercises (Plank, Wall Sit, etc.).
    """
    def __init__(self):
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.elapsed_offset: float = 0.0
        self.running: bool = False

    def start(self, now: float) -> None:
        """Start or resume the timer."""
        if not self.running:
            self.start_time = now
            self.running = True

    def pause(self, now: float) -> None:
        """Pause the timer."""
        if self.running and self.start_time is not None:
            self.elapsed_offset += now - self.start_time
            self.running = False
            self.start_time = None

    def resume(self, now: float) -> None:
        """Resume the timer after a pause."""
        self.start(now)

    def get_elapsed(self, now: float) -> float:
        """Calculate total elapsed time in seconds."""
        if self.running and self.start_time is not None:
            return self.elapsed_offset + (now - self.start_time)
        return self.elapsed_offset

    def stop(self) -> None:
        """Stop and reset the timer."""
        self.start_time = None
        self.pause_time = None
        self.elapsed_offset = 0.0
        self.running = False

    def reset(self) -> None:
        self.stop()
