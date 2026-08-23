"""
Generic rep counter component handling debouncing and threshold validation.
"""
from utils.enums import ExerciseState

class RepCounter:
    """
    Tracks repetitions based on value thresholds and cooldown periods.
    """
    def __init__(self, down_threshold: float, up_threshold: float, cooldown: float = 0.8):
        self.down_threshold = down_threshold
        self.up_threshold = up_threshold
        self.cooldown = cooldown
        self.reps = 0
        self.sets = 0
        self.stage = "up"
        self.last_rep_time = 0.0

    def update(self, current_val: float, now: float) -> bool:
        """
        Update state with current value and return True if a rep completes.
        """
        # Determine movement direction and stage transitions
        if current_val < self.up_threshold:
            self.stage = "down"

        elif self.stage == "down" and current_val > self.down_threshold:
            if now - self.last_rep_time > self.cooldown:
                self.reps += 1
                self.last_rep_time = now
                self.stage = "up"
                return True

        return False

    def reset(self) -> None:
        self.reps = 0
        self.sets = 0
        self.stage = "up"
        self.last_rep_time = 0.0
