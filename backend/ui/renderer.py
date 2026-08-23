"""
High level UI manager combining menus, state overlays, and OpenCV windows.
"""
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from utils.enums import UIMode
from ui.menu import MenuSystem
from ui.overlay import OverlayRenderer
from pose.keypoints import Keypoint
from exercises.base_exercise import FormWarning
from tracking.alignment_engine import AlignmentResult

class UIRenderer:
    """
    Manages OpenCV windows and routes rendering options dynamically.
    """
    def __init__(self, window_name: str = "AI Gym Trainer"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

    def render(
        self,
        frame: np.ndarray,
        menu: MenuSystem,
        keypoints: Dict[str, Keypoint],
        reps: int,
        sets: int,
        performance_score: float,
        warnings: List[FormWarning],
        timer_display: Optional[str] = None,
        alignment_result: Optional[AlignmentResult] = None,
        is_aligning: bool = False
    ) -> None:
        """
        Draw appropriate screens based on the current system UIMode.
        """
        if menu.mode == UIMode.CATEGORY:
            OverlayRenderer.draw_category_menu(frame, menu.categories)
        
        elif menu.mode == UIMode.EXERCISE:
            OverlayRenderer.draw_exercise_menu(
                frame,
                menu.selected_category_name or "",
                menu.get_exercises_for_current_category()
            )
        
        elif menu.mode == UIMode.TRACK:
            # 1. Render Ghost Skeleton overlay if available
            if alignment_result and alignment_result.ghost_keypoints:
                OverlayRenderer.draw_ghost_skeleton(frame, alignment_result.ghost_keypoints)

            # 2. Render Live User Skeleton with color coding (Green/Yellow/Red)
            if keypoints:
                joint_statuses = alignment_result.joint_statuses if alignment_result else {}
                OverlayRenderer.draw_color_coded_skeleton(frame, keypoints, joint_statuses)

            # 3. Render Alignment HUD or Exercise Tracking HUD
            if is_aligning and alignment_result:
                OverlayRenderer.draw_alignment_hud(frame, alignment_result)
            else:
                OverlayRenderer.draw_tracking_stats(
                    frame=frame,
                    exercise_name=menu.selected_exercise or "",
                    reps=reps,
                    sets=sets,
                    score=performance_score,
                    warnings=warnings,
                    timer_display=timer_display
                )

        # Show frame
        cv2.imshow(self.window_name, frame)

    def is_window_visible(self) -> bool:
        """Check if target OpenCV frame window is open and visible."""
        return cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) >= 1

    def close(self) -> None:
        cv2.destroyAllWindows()
