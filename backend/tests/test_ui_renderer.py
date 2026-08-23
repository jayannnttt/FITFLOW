"""
Unit tests for UIRenderer and OverlayRenderer frontend components.
Verifies frame rendering across Home Category Screen, Exercise Selection,
AI Alignment Screen, and Workout Tracking HUD without exceptions.
"""
import pytest
import numpy as np
from ui.menu import MenuSystem
from ui.overlay import OverlayRenderer
from pose.keypoints import Keypoint
from tracking.alignment_engine import AlignmentResult
from exercises.base_exercise import FormWarning
from utils.enums import WarningSeverity, UIMode
from utils.helper import load_exercise_configs
import os

@pytest.fixture
def dummy_frame():
    return np.zeros((720, 1280, 3), dtype=np.uint8)

@pytest.fixture
def menu_system():
    config_path = os.path.join("configs", "exercises.json")
    configs = load_exercise_configs(config_path)
    return MenuSystem(configs)

def test_render_category_home_screen(dummy_frame, menu_system):
    # Category selection mode
    menu_system.mode = UIMode.CATEGORY
    OverlayRenderer.draw_category_menu(dummy_frame, menu_system.categories)
    assert dummy_frame.shape == (720, 1280, 3)

def test_render_exercise_selection_screen(dummy_frame, menu_system):
    menu_system.select_category("1")
    assert menu_system.mode == UIMode.EXERCISE
    exercises = menu_system.get_exercises_for_current_category()
    OverlayRenderer.draw_exercise_menu(dummy_frame, "UPPER BODY", exercises)
    assert dummy_frame.shape == (720, 1280, 3)

def test_render_alignment_hud_and_ghost_skeleton(dummy_frame):
    ghost_kps = {
        "nose": Keypoint("nose", 0.5, 0.2, 0.9),
        "left_shoulder": Keypoint("left_shoulder", 0.4, 0.3, 0.9),
        "right_shoulder": Keypoint("right_shoulder", 0.6, 0.3, 0.9)
    }

    alignment_res = AlignmentResult(
        alignment_score=82.0,
        raw_score=82.0,
        ready=False,
        joint_statuses={"left_shoulder": "correct", "left_elbow": "adjusting"},
        coaching_messages=["⚠ Raise your left elbow"],
        ghost_keypoints=ghost_kps,
        stabilization_progress=0.4
    )

    OverlayRenderer.draw_ghost_skeleton(dummy_frame, ghost_kps)
    OverlayRenderer.draw_color_coded_skeleton(dummy_frame, ghost_kps, alignment_res.joint_statuses)
    OverlayRenderer.draw_alignment_hud(dummy_frame, alignment_res)

    assert dummy_frame.shape == (720, 1280, 3)

def test_render_live_tracking_hud(dummy_frame):
    warnings = [
        FormWarning(
            warning="Elbow swinging",
            severity=WarningSeverity.WARNING,
            suggestion="Keep elbows close to your torso"
        )
    ]

    OverlayRenderer.draw_tracking_stats(
        frame=dummy_frame,
        exercise_name="Bicep Curl",
        reps=8,
        sets=1,
        score=92.0,
        warnings=warnings,
        timer_display=None
    )

    assert dummy_frame.shape == (720, 1280, 3)
