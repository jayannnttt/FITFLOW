import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

from config import AppConfig
from exercises.plank import Plank
from exercises.bicep import BicepCurl
from exercises.squat import Squat
from exercises.pushup import Pushup
from exercises.shoulder_press import ShoulderPress
from pose.angles import AngleEngine
from pose.keypoints import Keypoint
from utils.enums import ExerciseState
from utils.helper import load_exercise_configs

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

def mock_invalid_sagging_plank_keypoints():
    return {
        "left_shoulder": Keypoint("left_shoulder", 0.3, 0.3, 0.9),
        "left_hip": Keypoint("left_hip", 0.5, 0.6, 0.9),
        "left_ankle": Keypoint("left_ankle", 0.8, 0.3, 0.9)
    }

results = {}

# TEST 1: Click Start -> timer starts
try:
    plank_cfg = exercises_config["exercises"]["Plank"]
    p = Plank("Plank", plank_cfg)
    now = time.time()
    p.start_tracking(now)
    results["TEST 1 (Click Start -> timer starts)"] = "PASS" if (p.timer.running and p.state == ExerciseState.STARTED) else f"FAIL (running={p.timer.running}, state={p.state})"
except Exception as e:
    results["TEST 1 (Click Start -> timer starts)"] = f"FAIL ({e})"

# TEST 2: Maintain valid plank -> timer continuously increases
try:
    t0 = time.time()
    p = Plank("Plank", plank_cfg)
    p.start_tracking(t0)
    kps = mock_valid_plank_keypoints()
    for step in range(3):
        t_curr = t0 + (step * 0.4)
        angle_engine.clear_cache()
        p.update(kps, angle_engine, frame_shape, t_curr)
    elapsed = p.timer.get_elapsed(t0 + 1.2)
    results["TEST 2 (Maintain valid plank -> timer continuously increases)"] = "PASS" if (elapsed >= 1.0 and p.timer.running and p.state == ExerciseState.STARTED) else f"FAIL (elapsed={elapsed}, running={p.timer.running})"
except Exception as e:
    results["TEST 2 (Maintain valid plank -> timer continuously increases)"] = f"FAIL ({e})"

# TEST 3: Break plank posture -> timer stops automatically after grace period
try:
    t0 = time.time()
    p = Plank("Plank", plank_cfg)
    p.start_tracking(t0)
    kps_valid = mock_valid_plank_keypoints()
    kps_bad = mock_invalid_sagging_plank_keypoints()
    
    angle_engine.clear_cache()
    p.update(kps_valid, angle_engine, frame_shape, t0)
    
    angle_engine.clear_cache()
    p.update(kps_bad, angle_engine, frame_shape, t0 + 0.2)
    running_during_grace = p.timer.running
    
    angle_engine.clear_cache()
    p.update(kps_bad, angle_engine, frame_shape, t0 + 0.8)
    
    metrics = p.get_display_metrics(t0 + 0.8)
    stopped_after_grace = (not p.timer.running) and (p.state == ExerciseState.FINISHED) and (p.completion_reason == "posture_failed")
    results["TEST 3 (Break plank posture -> timer stops automatically after grace period)"] = "PASS" if (running_during_grace and stopped_after_grace) else f"FAIL (running_grace={running_during_grace}, running_end={p.timer.running}, state={p.state}, reason={p.completion_reason})"
except Exception as e:
    results["TEST 3 (Break plank posture -> timer stops automatically after grace period)"] = f"FAIL ({e})"

# TEST 4: Leave camera -> timer stops after grace period
try:
    t0 = time.time()
    p = Plank("Plank", plank_cfg)
    p.start_tracking(t0)
    kps_valid = mock_valid_plank_keypoints()
    kps_empty = {}
    
    angle_engine.clear_cache()
    p.update(kps_valid, angle_engine, frame_shape, t0)
    
    angle_engine.clear_cache()
    p.update(kps_empty, angle_engine, frame_shape, t0 + 0.2)
    
    angle_engine.clear_cache()
    p.update(kps_empty, angle_engine, frame_shape, t0 + 0.8)
    
    stopped_cam_lost = (not p.timer.running) and (p.state == ExerciseState.FINISHED) and (p.completion_reason == "camera_lost")
    results["TEST 4 (Leave camera -> timer stops after grace period)"] = "PASS" if stopped_cam_lost else f"FAIL (running={p.timer.running}, state={p.state}, reason={p.completion_reason})"
except Exception as e:
    results["TEST 4 (Leave camera -> timer stops after grace period)"] = f"FAIL ({e})"

# TEST 5: Temporary single-frame detection failure -> workout does NOT terminate
try:
    t0 = time.time()
    p = Plank("Plank", plank_cfg)
    p.start_tracking(t0)
    kps_valid = mock_valid_plank_keypoints()
    kps_empty = {}
    
    angle_engine.clear_cache()
    p.update(kps_valid, angle_engine, frame_shape, t0)
    
    angle_engine.clear_cache()
    p.update(kps_empty, angle_engine, frame_shape, t0 + 0.2)
    
    angle_engine.clear_cache()
    p.update(kps_valid, angle_engine, frame_shape, t0 + 0.4)
    
    results["TEST 5 (Temporary single-frame detection failure -> workout does NOT terminate)"] = "PASS" if (p.timer.running and p.state == ExerciseState.STARTED) else f"FAIL (running={p.timer.running}, state={p.state})"
except Exception as e:
    results["TEST 5 (Temporary single-frame detection failure -> workout does NOT terminate)"] = f"FAIL ({e})"

# TEST 6: Maintain plank until 60 seconds -> automatically completes
try:
    t0 = time.time()
    p = Plank("Plank", plank_cfg)
    p.start_tracking(t0)
    kps_valid = mock_valid_plank_keypoints()
    
    angle_engine.clear_cache()
    p.update(kps_valid, angle_engine, frame_shape, t0)
    
    angle_engine.clear_cache()
    p.update(kps_valid, angle_engine, frame_shape, t0 + 60.1)
    
    target_completed = (not p.timer.running) and (p.state == ExerciseState.FINISHED) and (p.completion_reason == "target_reached")
    results["TEST 6 (Maintain plank until 60 seconds -> automatically completes)"] = "PASS" if target_completed else f"FAIL (running={p.timer.running}, state={p.state}, reason={p.completion_reason})"
except Exception as e:
    results["TEST 6 (Maintain plank until 60 seconds -> automatically completes)"] = f"FAIL ({e})"

# TEST 7: Click Stop manually -> final time is preserved
try:
    t0 = time.time()
    p = Plank("Plank", plank_cfg)
    p.start_tracking(t0)
    kps_valid = mock_valid_plank_keypoints()
    
    angle_engine.clear_cache()
    p.update(kps_valid, angle_engine, frame_shape, t0 + 5.0)
    
    p.timer.pause(t0 + 5.0)
    p.state = ExerciseState.FINISHED
    p.completion_reason = "user_stopped"
    
    metrics = p.get_display_metrics(t0 + 5.0)
    results["TEST 7 (Click Stop manually -> final time is preserved)"] = "PASS" if (metrics["elapsed_time"] >= 5.0 and metrics["completion_reason"] == "user_stopped") else f"FAIL (elapsed={metrics['elapsed_time']}, reason={metrics['completion_reason']})"
except Exception as e:
    results["TEST 7 (Click Stop manually -> final time is preserved)"] = f"FAIL ({e})"

# TEST 8: Reset -> timer returns to 00:00 and can start again
try:
    t0 = time.time()
    p = Plank("Plank", plank_cfg)
    p.start_tracking(t0)
    
    angle_engine.clear_cache()
    p.update(mock_valid_plank_keypoints(), angle_engine, frame_shape, t0 + 10.0)
    
    p.reset()
    reset_ok = (p.timer.get_elapsed(0) == 0.0 and not p.timer.running and p.state == ExerciseState.ALIGNING)
    
    p.start_tracking(t0 + 20.0)
    restart_ok = (p.timer.running and p.state == ExerciseState.STARTED)
    
    results["TEST 8 (Reset -> timer returns to 00:00 and can start again)"] = "PASS" if (reset_ok and restart_ok) else f"FAIL (reset_ok={reset_ok}, restart_ok={restart_ok})"
except Exception as e:
    results["TEST 8 (Reset -> timer returns to 00:00 and can start again)"] = f"FAIL ({e})"

# TEST 9: Start Plank twice -> no duplicate timers
try:
    t0 = time.time()
    p = Plank("Plank", plank_cfg)
    p.start_tracking(t0)
    
    angle_engine.clear_cache()
    p.update(mock_valid_plank_keypoints(), angle_engine, frame_shape, t0 + 5.0)
    
    p.start_tracking(t0 + 10.0)
    metrics_after = p.get_display_metrics(t0 + 10.0)
    
    results["TEST 9 (Start Plank twice -> no duplicate timers)"] = "PASS" if (metrics_after["elapsed_time"] == 0.0 and p.timer.running) else f"FAIL (elapsed={metrics_after['elapsed_time']}, running={p.timer.running})"
except Exception as e:
    results["TEST 9 (Start Plank twice -> no duplicate timers)"] = f"FAIL ({e})"

# TEST 10: Verify Squat, Bicep Curl, Push-up, Shoulder Press still work
try:
    bicep = BicepCurl("Bicep Curl", exercises_config["exercises"]["Bicep Curl"])
    bicep.start_tracking(time.time())
    
    squat = Squat("Squats", exercises_config["exercises"]["Squats"])
    squat.start_tracking(time.time())
    
    pushup = Pushup("Push-ups", exercises_config["exercises"]["Push-ups"])
    pushup.start_tracking(time.time())
    
    sp = ShoulderPress("Shoulder Press", exercises_config["exercises"]["Shoulder Press"])
    sp.start_tracking(time.time())
    
    rep_exercises_ok = (
        bicep.state == ExerciseState.STARTED and
        squat.state == ExerciseState.STARTED and
        pushup.state == ExerciseState.STARTED and
        sp.state == ExerciseState.STARTED
    )
    results["TEST 10 (Verify Squat, Bicep Curl, Push-up, Shoulder Press still work)"] = "PASS" if rep_exercises_ok else f"FAIL (bicep={bicep.state}, squat={squat.state})"
except Exception as e:
    results["TEST 10 (Verify Squat, Bicep Curl, Push-up, Shoulder Press still work)"] = f"FAIL ({e})"

print("\n==================================================")
print("              TEST RESULTS SUMMARY               ")
print("==================================================")
all_pass = True
for test_name, status in results.items():
    print(f"{test_name}: {status}")
    if status != "PASS":
        all_pass = False
print("==================================================")
print("OVERALL STATUS:", "ALL TESTS PASSED" if all_pass else "TEST SUITE FAILED")
print("==================================================\n")
