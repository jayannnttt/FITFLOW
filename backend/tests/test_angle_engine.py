"""
Unit tests for AngleEngine and mathematical angle functions.
"""
import pytest
from pose.angles import AngleEngine
from pose.keypoints import Keypoint

def test_angle_calculation_right_angle():
    engine = AngleEngine()
    
    # 90 degrees angle points (forming an L shape)
    kps = {
        "left_shoulder": Keypoint("left_shoulder", 0.0, 0.0, 1.0),
        "left_elbow": Keypoint("left_elbow", 0.0, 1.0, 1.0),
        "left_wrist": Keypoint("left_wrist", 1.0, 1.0, 1.0)
    }

    angle = engine.get_joint_angle(
        kps,
        ["left_shoulder", "left_elbow", "left_wrist"],
        (480, 640)
    )
    
    assert angle is not None
    assert abs(angle - 90.0) < 1e-3

def test_angle_calculation_straight_line():
    engine = AngleEngine()
    
    # 180 degrees (straight line)
    kps = {
        "pt_a": Keypoint("pt_a", 0.0, 0.0, 1.0),
        "pt_b": Keypoint("pt_b", 0.0, 1.0, 1.0),
        "pt_c": Keypoint("pt_c", 0.0, 2.0, 1.0)
    }

    angle = engine.get_joint_angle(
        kps,
        ["pt_a", "pt_b", "pt_c"],
        (480, 640)
    )
    
    assert angle is not None
    assert abs(angle - 180.0) < 1e-3

def test_angle_calculation_low_visibility():
    engine = AngleEngine(visibility_threshold=0.5)
    
    # Test point with visibility under threshold
    kps = {
        "pt_a": Keypoint("pt_a", 0.0, 0.0, 0.8),
        "pt_b": Keypoint("pt_b", 0.0, 1.0, 0.3),  # below 0.5
        "pt_c": Keypoint("pt_c", 0.0, 2.0, 0.9)
    }

    angle = engine.get_joint_angle(
        kps,
        ["pt_a", "pt_b", "pt_c"],
        (480, 640)
    )
    
    assert angle is None
