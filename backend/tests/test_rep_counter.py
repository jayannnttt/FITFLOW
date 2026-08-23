"""
Unit tests for the generic RepCounter tracker.
"""
import pytest
from tracking.rep_counter import RepCounter

def test_rep_counter_flow():
    # Cooldown 0.5s, Down threshold 150, Up threshold 90
    rc = RepCounter(down_threshold=150.0, up_threshold=90.0, cooldown=0.5)

    # Initial state
    assert rc.reps == 0
    assert rc.stage == "up"

    # Start moving down (less than up_threshold 90)
    rep_done = rc.update(85.0, now=1.0)
    assert not rep_done
    assert rc.stage == "down"

    # Move back up (greater than down_threshold 150)
    rep_done = rc.update(155.0, now=2.0)
    assert rep_done
    assert rc.reps == 1
    assert rc.stage == "up"

def test_rep_counter_cooldown_prevention():
    rc = RepCounter(down_threshold=150.0, up_threshold=90.0, cooldown=1.0)

    # First rep completed
    rc.update(80.0, now=1.0)
    rep_done_1 = rc.update(160.0, now=1.5)
    assert rep_done_1
    assert rc.reps == 1

    # Second rep attempted too fast (elapsed time diff = 0.5s < cooldown 1.0s)
    rc.update(80.0, now=1.8)
    rep_done_2 = rc.update(160.0, now=2.0)
    assert not rep_done_2
    assert rc.reps == 1  # rep should not increment

    # Try after cooldown period expires (elapsed time diff = 1.1s > cooldown 1.0s)
    rc.update(80.0, now=2.2)
    rep_done_3 = rc.update(160.0, now=2.7)
    assert rep_done_3
    assert rc.reps == 2
