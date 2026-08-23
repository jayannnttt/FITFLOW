"""
Unit tests for the ExerciseTimer state tracking.
"""
import pytest
from tracking.timer import ExerciseTimer

def test_timer_lifecycle():
    timer = ExerciseTimer()

    assert not timer.running
    assert timer.get_elapsed(10.0) == 0.0

    # Start timer at t=10.0
    timer.start(10.0)
    assert timer.running
    assert timer.get_elapsed(15.0) == 5.0

    # Pause timer at t=15.0
    timer.pause(15.0)
    assert not timer.running
    assert timer.get_elapsed(20.0) == 5.0

    # Resume at t=25.0
    timer.resume(25.0)
    assert timer.running
    assert timer.get_elapsed(30.0) == 10.0

    # Reset
    timer.reset()
    assert not timer.running
    assert timer.get_elapsed(40.0) == 0.0
