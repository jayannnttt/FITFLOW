"""
Unit tests for AI-Guided AlignmentEngine, posture evaluation, ghost skeleton generation,
EMA smoothing, coaching message prioritization, and grace period buffer.
"""
import pytest
import time
from pose.keypoints import Keypoint
from pose.angles import AngleEngine
from tracking.alignment_engine import AlignmentEngine, AlignmentResult

@pytest.fixture
def sample_exercise_cfg():
    return {
        "type": "REP_BASED",
        "alignment": {
            "starting_pose_angles": {
                "left_elbow": 165.0,
                "right_elbow": 165.0,
                "torso": 180.0
            },
            "tolerances": {
                "left_elbow": 25.0,
                "right_elbow": 25.0,
                "torso": 20.0
            },
            "coaching_rules": {
                "left_elbow": "Straighten your left arm to start",
                "right_elbow": "Straighten your right arm to start",
                "torso": "Stand upright with back straight"
            }
        }
    }

def test_alignment_engine_ideal_pose_ready_state(sample_exercise_cfg):
    engine = AlignmentEngine(score_threshold=75.0, stabilization_sec=0.5)
    angle_engine = AngleEngine()

    # Perfectly aligned keypoints
    aligned_kps = {
        "left_shoulder": Keypoint("left_shoulder", 0.4, 0.2, 0.9),
        "right_shoulder": Keypoint("right_shoulder", 0.6, 0.2, 0.9),
        "left_elbow": Keypoint("left_elbow", 0.4, 0.5, 0.9),
        "left_wrist": Keypoint("left_wrist", 0.4, 0.8, 0.9),
        "right_elbow": Keypoint("right_elbow", 0.6, 0.5, 0.9),
        "right_wrist": Keypoint("right_wrist", 0.6, 0.8, 0.9),
        "left_hip": Keypoint("left_hip", 0.4, 0.6, 0.9),
        "right_hip": Keypoint("right_hip", 0.6, 0.6, 0.9),
        "left_knee": Keypoint("left_knee", 0.4, 0.8, 0.9),
        "right_knee": Keypoint("right_knee", 0.6, 0.8, 0.9),
    }

    t = 10.0
    angle_engine.clear_cache()
    res1 = engine.evaluate("Bicep Curl", sample_exercise_cfg, aligned_kps, angle_engine, (480, 640), t)

    assert isinstance(res1, AlignmentResult)
    assert res1.alignment_score >= 75.0
    assert len(res1.ghost_keypoints) > 0

    # Advance time beyond stabilization_sec (0.5s)
    t += 0.6
    angle_engine.clear_cache()
    res2 = engine.evaluate("Bicep Curl", sample_exercise_cfg, aligned_kps, angle_engine, (480, 640), t)

    assert res2.ready is True
    assert "✓ Perfect Alignment" in res2.coaching_messages[0]

def test_alignment_engine_coaching_prioritization(sample_exercise_cfg):
    engine = AlignmentEngine()
    angle_engine = AngleEngine()

    # Bent arms (bad posture)
    bad_kps = {
        "left_shoulder": Keypoint("left_shoulder", 0.4, 0.2, 0.9),
        "right_shoulder": Keypoint("right_shoulder", 0.6, 0.2, 0.9),
        "left_elbow": Keypoint("left_elbow", 0.4, 0.5, 0.9),
        "left_wrist": Keypoint("left_wrist", 0.4, 0.3, 0.9), # Curled elbow (~45 deg)
        "right_elbow": Keypoint("right_elbow", 0.6, 0.5, 0.9),
        "right_wrist": Keypoint("right_wrist", 0.6, 0.3, 0.9), # Curled elbow (~45 deg)
        "left_hip": Keypoint("left_hip", 0.4, 0.6, 0.9),
        "right_hip": Keypoint("right_hip", 0.6, 0.6, 0.9)
    }

    angle_engine.clear_cache()
    res = engine.evaluate("Bicep Curl", sample_exercise_cfg, bad_kps, angle_engine, (480, 640), 10.0)

    assert res.ready is False
    assert len(res.coaching_messages) <= 3
    assert any("Straighten" in msg for msg in res.coaching_messages)

def test_alignment_tracking_loss_grace_period(sample_exercise_cfg):
    engine = AlignmentEngine(grace_period_sec=0.5)
    angle_engine = AngleEngine()

    aligned_kps = {
        "left_shoulder": Keypoint("left_shoulder", 0.4, 0.2, 0.9),
        "right_shoulder": Keypoint("right_shoulder", 0.6, 0.2, 0.9),
        "left_elbow": Keypoint("left_elbow", 0.4, 0.5, 0.9),
        "left_wrist": Keypoint("left_wrist", 0.4, 0.8, 0.9),
        "right_elbow": Keypoint("right_elbow", 0.6, 0.5, 0.9),
        "right_wrist": Keypoint("right_wrist", 0.6, 0.8, 0.9),
        "left_hip": Keypoint("left_hip", 0.4, 0.6, 0.9),
        "right_hip": Keypoint("right_hip", 0.6, 0.6, 0.9)
    }

    t = 10.0
    angle_engine.clear_cache()
    res_valid = engine.evaluate("Bicep Curl", sample_exercise_cfg, aligned_kps, angle_engine, (480, 640), t)

    # Empty frame within grace period (0.2s elapsed)
    t += 0.2
    res_grace = engine.evaluate("Bicep Curl", sample_exercise_cfg, {}, angle_engine, (480, 640), t)
    assert res_grace == res_valid  # Preserves previous result during grace period

    # Empty frame past grace period (0.7s elapsed)
    t += 0.5
    res_expired = engine.evaluate("Bicep Curl", sample_exercise_cfg, {}, angle_engine, (480, 640), t)
    assert res_expired != res_valid
    assert "Step into camera view" in res_expired.coaching_messages[0]
