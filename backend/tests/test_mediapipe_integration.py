"""
Integration tests for MediaPipe Pose detector, AngleEngine, RepCounter, and BaseExercise workflows.
"""
import pytest
import numpy as np
from pose.mediapipe_detector import MediaPipeDetector
from pose.keypoints import Keypoint
from pose.angles import AngleEngine
from exercises.exercise_factory import ExerciseFactory
from utils.constants import MEDIAPIPE_KEYPOINTS
from utils.helper import load_exercise_configs
import os

def test_mediapipe_detector_33_landmarks_schema():
    detector = MediaPipeDetector()
    assert detector.initialize() is True

    # Check keypoint dictionary keys match MEDIAPIPE_KEYPOINTS
    assert len(MEDIAPIPE_KEYPOINTS) == 33
    assert "left_shoulder" in MEDIAPIPE_KEYPOINTS
    assert "right_shoulder" in MEDIAPIPE_KEYPOINTS
    assert "left_knee" in MEDIAPIPE_KEYPOINTS
    assert "left_foot_index" in MEDIAPIPE_KEYPOINTS
    assert "right_foot_index" in MEDIAPIPE_KEYPOINTS

    detector.shutdown()

def test_mediapipe_keypoints_angle_engine():
    angle_engine = AngleEngine()

    mock_kps = {
        "left_shoulder": Keypoint(name="left_shoulder", x=0.5, y=0.2, confidence=0.9),
        "left_elbow": Keypoint(name="left_elbow", x=0.5, y=0.4, confidence=0.9),
        "left_wrist": Keypoint(name="left_wrist", x=0.7, y=0.4, confidence=0.9)
    }

    angle = angle_engine.get_joint_angle(
        mock_kps,
        ["left_shoulder", "left_elbow", "left_wrist"],
        (480, 640)
    )

    assert angle is not None
    # 90-degree right angle check
    assert abs(angle - 90.0) < 1e-2

def test_exercise_rep_counting_state_machine_with_mediapipe_kps():
    config_path = os.path.join("configs", "exercises.json")
    configs = load_exercise_configs(config_path)

    # Instantiate Bicep Curl
    bicep_cfg = configs["exercises"]["Bicep Curl"]
    exercise = ExerciseFactory.create_exercise("Bicep Curl", bicep_cfg)
    angle_engine = AngleEngine()

    # Down position keypoints (arm extended ~180 deg)
    down_kps = {
        "left_shoulder": Keypoint("left_shoulder", 0.5, 0.2, 0.95),
        "left_elbow": Keypoint("left_elbow", 0.5, 0.5, 0.95),
        "left_wrist": Keypoint("left_wrist", 0.5, 0.8, 0.95),
        "left_hip": Keypoint("left_hip", 0.5, 0.6, 0.95)
    }

    # Up position keypoints (arm curled ~45 deg)
    up_kps = {
        "left_shoulder": Keypoint("left_shoulder", 0.5, 0.2, 0.95),
        "left_elbow": Keypoint("left_elbow", 0.5, 0.5, 0.95),
        "left_wrist": Keypoint("left_wrist", 0.5, 0.3, 0.95),
        "left_hip": Keypoint("left_hip", 0.5, 0.6, 0.95)
    }

    t = 100.0
    # Update state: extended arm frame 1
    angle_engine.clear_cache()
    exercise.update(down_kps, angle_engine, (480, 640), t)
    metrics = exercise.get_display_metrics()
    assert metrics["reps"] == 0

    # Curled arm frame 2 (transition to UP stage)
    t += 0.5
    angle_engine.clear_cache()
    exercise.update(up_kps, angle_engine, (480, 640), t)

    # Return to extended arm frame 3 after cooldown
    t += 1.0
    angle_engine.clear_cache()
    exercise.update(down_kps, angle_engine, (480, 640), t)
    metrics = exercise.get_display_metrics()
    assert metrics["reps"] == 1
