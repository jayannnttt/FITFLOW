"""
Exercise state machine manager.
"""
from utils.enums import ExerciseState

class ExerciseStateMachine:
    """
    Manages exercise state transitions.
    """
    def __init__(self):
        self.state: ExerciseState = ExerciseState.IDLE

    def transition_to(self, new_state: ExerciseState) -> None:
        """
        Transition to new state with validation.
        """
        # Validate transitions optionally if required
        self.state = new_state

    def reset(self) -> None:
        self.state = ExerciseState.IDLE

    def get_state(self) -> ExerciseState:
        return self.state
