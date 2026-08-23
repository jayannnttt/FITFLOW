import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

from config import AppConfig
from exercises.plank import Plank
from pose.angles import AngleEngine
from pose.keypoints import Keypoint
from utils.enums import ExerciseState
from utils.helper import load_exercise_configs
import server

# Initialize server components
config = AppConfig()
exercises_config = load_exercise_configs(config.exercises_config_path)
angle_engine = AngleEngine()
frame_shape = (480, 640)

def mock_valid_plank_keypoints():
    return {
        "left_shoulder": Keypoint("left_shoulder", 0.3, 0.4, 0.9),
        "left_hip": Keypoint("left_hip", 0.5, 0.4, 0.9),
        "left_ankle": Keypoint("left_ankle", 0.8, 0.4, 0.9)
    }

print("\n==================================================")
print("     VERIFYING WEBSOCKET BUTTON -> PLANK TIMER    ")
print("==================================================")

# 1. Select Plank Exercise
server.session_state.select_exercise("Plank")
ex = server.session_state.active_exercise
print(f"1. Exercise selected: {server.session_state.exercise_name} (Timer running: {ex.timer.running})")
assert not ex.timer.running, "Timer should NOT run before Start Plank is clicked"

# 2. Simulate User clicking [ ▶ START PLANK ] -> 3s countdown finishes -> sends 'start_active_tracking'
t0 = time.time()
ex.start_tracking(t0)
print(f"2. [ START PLANK ] clicked -> start_tracking called. Timer running: {ex.timer.running}, State: {ex.state}")
assert ex.timer.running, "Timer MUST run after Start Plank"
assert ex.state == ExerciseState.STARTED, "State must be STARTED"

# 3. Simulate frame updates over 2 seconds
kps = mock_valid_plank_keypoints()
ex.update(kps, angle_engine, frame_shape, t0 + 1.0)
metrics1 = ex.get_display_metrics(t0 + 1.0)
print(f"3. Frame @ +1.0s -> Display Timer: {int(metrics1['elapsed_time'])}s (running: {metrics1['running']})")

ex.update(kps, angle_engine, frame_shape, t0 + 2.5)
metrics2 = ex.get_display_metrics(t0 + 2.5)
print(f"4. Frame @ +2.5s -> Display Timer: {int(metrics2['elapsed_time'])}s (running: {metrics2['running']})")
assert metrics2['elapsed_time'] >= 2.0, "Timer must visibly count upward from 00:00"

# 4. Simulate User clicking [ ↻ RESTART TIMER ] -> sends 'reset' -> 3s countdown finishes -> sends 'start_active_tracking'
ex.reset()
metrics_reset = ex.get_display_metrics(t0 + 2.6)
print(f"5. [ RESTART TIMER ] clicked -> reset called. Display Timer: {int(metrics_reset['elapsed_time'])}s (running: {metrics_reset['running']})")
assert metrics_reset['elapsed_time'] == 0.0, "Timer must reset to 00:00"

t_restart = t0 + 5.0
ex.start_tracking(t_restart)
print(f"6. Countdown finished -> start_tracking called. Timer running: {ex.timer.running}")
assert ex.timer.running, "Timer MUST start again after restart countdown"

ex.update(kps, angle_engine, frame_shape, t_restart + 1.5)
metrics_restart = ex.get_display_metrics(t_restart + 1.5)
print(f"7. Frame @ restart +1.5s -> Display Timer: {int(metrics_restart['elapsed_time'])}s")
assert 1.0 <= metrics_restart['elapsed_time'] <= 2.0, "Timer must count from 00:00 after restart"

# 5. Simulate User clicking [ ⏹ STOP ] -> stops timer, preserves final time
ex.timer.pause(t_restart + 3.0)
ex.state = ExerciseState.FINISHED
ex.completion_reason = "user_stopped"
metrics_stopped = ex.get_display_metrics(t_restart + 3.0)
print(f"8. [ STOP ] clicked -> Timer stopped. Preserved Elapsed Time: {int(metrics_stopped['elapsed_time'])}s (finished: {metrics_stopped['finished']})")
assert not metrics_stopped['running'], "Timer must stop"
assert metrics_stopped['elapsed_time'] >= 3.0, "Final time must be preserved"

print("==================================================")
print("   WEBSOCKET BUTTON -> TIMER VERIFICATION PASSED! ")
print("==================================================\n")
