"""
Unit tests for the ExerciseStateMachine state checks.
"""
import pytest
from tracking.state_machine import ExerciseStateMachine
from utils.enums import ExerciseState

def test_state_transitions():
    sm = ExerciseStateMachine()

    assert sm.get_state() == ExerciseState.IDLE

    # Transition to ready
    sm.transition_to(ExerciseState.READY)
    assert sm.get_state() == ExerciseState.READY

    # Transition to down
    sm.transition_to(ExerciseState.DOWN)
    assert sm.get_state() == ExerciseState.DOWN

    # Reset
    sm.reset()
    assert sm.get_state() == ExerciseState.IDLE
