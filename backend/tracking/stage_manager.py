"""
Manages transition stages of reps or sets.
"""
from utils.enums import ExerciseState

class StageManager:
    """
    Manages custom phases within exercises.
    """
    def __init__(self):
        self.current_stage: str = "up"

    def set_stage(self, stage: str) -> None:
        self.current_stage = stage

    def get_stage(self) -> str:
        return self.current_stage

    def reset(self) -> None:
        self.current_stage = "up"
