"""
Commercial-grade UI Overlay Renderer for AI Fitness Tracker.
Designed with modern, minimal, premium aesthetics inspired by Apple Fitness+ & WHOOP.
Dark Mode Palette: #0F172A (BG), #1E293B (Card Surface), #3B82F6 (Primary Blue),
#22C55E (Success Green), #FACC15 (Warning Yellow), #EF4444 (Error Red).
"""
import cv2
import numpy as np
import math
from typing import Dict, Any, List, Optional, Tuple
from pose.keypoints import Keypoint
from exercises.base_exercise import FormWarning
from tracking.alignment_engine import AlignmentResult
from utils.constants import (
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_BORDER,
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_TEXT_HEADER,
    COLOR_TEXT_OPTION, COLOR_TEXT_INFO, COLOR_SCORE
)

class OverlayRenderer:
    """
    Production-quality frontend UI renderer.
    Renders rounded cards, pill badges, progress bars, ghost skeletons, and floating coaching HUDs.
    """
    SKELETON_CONNECTIONS = [
        ("left_shoulder", "right_shoulder"),
        ("left_shoulder", "left_elbow"),
        ("left_elbow", "left_wrist"),
        ("right_shoulder", "right_elbow"),
        ("right_elbow", "right_wrist"),
        ("left_shoulder", "left_hip"),
        ("right_shoulder", "right_hip"),
        ("left_hip", "right_hip"),
        ("left_hip", "left_knee"),
        ("left_knee", "left_ankle"),
        ("right_hip", "right_knee"),
        ("right_knee", "right_ankle")
    ]

    # --- GRAPHICS & UI DRAWING UTILITIES ---

    @staticmethod
    def draw_rounded_card(
        img: np.ndarray,
        pt1: Tuple[int, int],
        pt2: Tuple[int, int],
        bg_color: Tuple[int, int, int] = COLOR_SURFACE,
        border_color: Tuple[int, int, int] = COLOR_SURFACE_BORDER,
        radius: int = 12,
        alpha: float = 0.85
    ) -> None:
        """Draw alpha-blended rounded card surface with crisp border outline."""
        x1, y1 = pt1
        x2, y2 = pt2
        w = max(10, x2 - x1)
        h = max(10, y2 - y1)

        overlay = img.copy()
        
        # Rounded rectangle fill
        cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), bg_color, -1)
        cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), bg_color, -1)
        cv2.circle(overlay, (x1 + radius, y1 + radius), radius, bg_color, -1)
        cv2.circle(overlay, (x2 - radius, y1 + radius), radius, bg_color, -1)
        cv2.circle(overlay, (x1 + radius, y2 - radius), radius, bg_color, -1)
        cv2.circle(overlay, (x2 - radius, y2 - radius), radius, bg_color, -1)

        # Alpha blend fill onto image
        cv2.addWeighted(overlay, alpha, img, 1.0 - alpha, 0, img)

        # Border outline
        if border_color is not None:
            cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), border_color, 1, cv2.LINE_AA)
            cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), border_color, 1, cv2.LINE_AA)
            cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), border_color, 1, cv2.LINE_AA)
            cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), border_color, 1, cv2.LINE_AA)
            cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, border_color, 1, cv2.LINE_AA)
            cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, border_color, 1, cv2.LINE_AA)
            cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, border_color, 1, cv2.LINE_AA)
            cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, border_color, 1, cv2.LINE_AA)

    @staticmethod
    def draw_pill_badge(
        img: np.ndarray,
        text: str,
        center_pt: Tuple[int, int],
        bg_color: Tuple[int, int, int] = COLOR_PRIMARY,
        text_color: Tuple[int, int, int] = (255, 255, 255),
        scale: float = 0.55,
        thickness: int = 1
    ) -> None:
        """Draw modern rounded pill-shaped status badge."""
        cx, cy = center_pt
        (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
        pw, ph = tw + 20, th + 12
        x1, y1 = cx - pw // 2, cy - ph // 2
        x2, y2 = cx + pw // 2, cy + ph // 2
        radius = ph // 2

        OverlayRenderer.draw_rounded_card(img, (x1, y1), (x2, y2), bg_color, COLOR_SURFACE_BORDER, radius, alpha=0.9)
        cv2.putText(img, text, (cx - tw // 2, cy + th // 2 - 1),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, text_color, thickness, cv2.LINE_AA)

    @staticmethod
    def draw_progress_bar(
        img: np.ndarray,
        pt1: Tuple[int, int],
        pt2: Tuple[int, int],
        progress_ratio: float,
        fill_color: Tuple[int, int, int] = COLOR_PRIMARY,
        bg_color: Tuple[int, int, int] = COLOR_SURFACE
    ) -> None:
        """Draw smooth rounded progress bar."""
        x1, y1 = pt1
        x2, y2 = pt2
        w, h = max(10, x2 - x1), max(6, y2 - y1)
        radius = h // 2

        # Background track
        OverlayRenderer.draw_rounded_card(img, pt1, pt2, bg_color, COLOR_SURFACE_BORDER, radius, alpha=0.9)

        # Progress fill
        ratio = max(0.0, min(1.0, progress_ratio))
        if ratio > 0.02:
            fill_w = int(w * ratio)
            fx2 = x1 + fill_w
            OverlayRenderer.draw_rounded_card(img, (x1, y1), (fx2, y2), fill_color, None, radius, alpha=1.0)

    # --- SCREEN RENDERING METHODS ---

    @staticmethod
    def draw_category_menu(frame: np.ndarray, categories: Dict[str, Any]) -> None:
        """Draw Apple Fitness+ style Home Category Selection Screen."""
        h, w = frame.shape[:2]

        # Background tint card
        OverlayRenderer.draw_rounded_card(frame, (20, 20), (w - 20, h - 20), COLOR_BG, COLOR_SURFACE_BORDER, 16, alpha=0.92)

        # Hero Header
        cv2.putText(frame, "Ready for today's workout?", (50, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)
        cv2.putText(frame, "Select a category to calibrate posture & track performance", (50, 105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

        # Quick stats summary pill badge
        OverlayRenderer.draw_pill_badge(frame, "4 WORKOUT CATEGORIES  |  11 EXERCISES", (w - 230, 85),
                                         COLOR_SURFACE, COLOR_PRIMARY, scale=0.55)

        # Divider line
        cv2.line(frame, (50, 125), (w - 50, 125), COLOR_SURFACE_BORDER, 1, cv2.LINE_AA)

        # Grid layout for 4 Categories
        card_w, card_h = (w - 140) // 2, 135
        coords = [
            (50, 150),                  # Category 1
            (70 + card_w, 150),         # Category 2
            (50, 305),                  # Category 3
            (70 + card_w, 305)          # Category 4
        ]

        for i, (k, cat) in enumerate(categories.items()):
            if i >= len(coords):
                break
            cx, cy = coords[i]
            x2, y2 = cx + card_w, cy + card_h

            # Category Card Surface
            OverlayRenderer.draw_rounded_card(frame, (cx, cy), (x2, y2), COLOR_SURFACE, COLOR_SURFACE_BORDER, 14, alpha=0.95)

            # Key Shortcut Pill Badge [ 1 ], [ 2 ], etc.
            OverlayRenderer.draw_pill_badge(frame, f"[ {k} ]", (cx + 35, cy + 30), COLOR_PRIMARY, (255, 255, 255), 0.5)

            # Category Name
            cat_name = cat.get("name", "")
            cv2.putText(frame, cat_name, (cx + 70, cy + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)

            # Exercise Count Subtitle
            ex_list = cat.get("exercises", [])
            cv2.putText(frame, f"{len(ex_list)} Exercises • AI Guided", (cx + 70, cy + 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

            # Exercises preview pill list
            ex_preview = " • ".join(ex_list[:2]) + ("..." if len(ex_list) > 2 else "")
            cv2.putText(frame, ex_preview, (cx + 20, cy + 105),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_PRIMARY, 1, cv2.LINE_AA)

        # Bottom Navigation Hint Footer Card
        OverlayRenderer.draw_rounded_card(frame, (50, h - 70), (w - 50, h - 35), COLOR_SURFACE, COLOR_SURFACE_BORDER, 10, alpha=0.9)
        cv2.putText(frame, "Press 1 - 4 to Select Category  |  ESC to Exit", (w // 2 - 180, h - 47),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

    @staticmethod
    def draw_exercise_menu(frame: np.ndarray, category_name: str, exercises: List[str]) -> None:
        """Draw Nike Training Club style Exercise Selection Screen."""
        h, w = frame.shape[:2]

        # Background tint card
        OverlayRenderer.draw_rounded_card(frame, (20, 20), (w - 20, h - 20), COLOR_BG, COLOR_SURFACE_BORDER, 16, alpha=0.92)

        # Header
        cv2.putText(frame, f"{category_name.upper()} EXERCISES", (50, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)
        cv2.putText(frame, "Select an exercise to calibrate starting posture", (50, 98),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

        # Divider
        cv2.line(frame, (50, 115), (w - 50, 115), COLOR_SURFACE_BORDER, 1, cv2.LINE_AA)

        # List of Exercise Cards
        card_w, card_h = (w - 120), 55
        start_y = 130

        # Difficulty & calorie metadata mapping
        meta = {
            "Bicep Curl": ("BEGINNER", "10 REPS", "Biceps", "~8 kcal/min"),
            "Shoulder Press": ("INTERMEDIATE", "10 REPS", "Shoulders", "~10 kcal/min"),
            "Push-ups": ("INTERMEDIATE", "10 REPS", "Chest & Triceps", "~12 kcal/min"),
            "Pull-ups": ("ADVANCED", "10 REPS", "Lats & Biceps", "~14 kcal/min"),
            "Squats": ("BEGINNER", "10 REPS", "Quadriceps & Glutes", "~11 kcal/min"),
            "Lunges": ("INTERMEDIATE", "10 REPS", "Legs & Core", "~10 kcal/min"),
            "Calf Raises": ("BEGINNER", "10 REPS", "Calves", "~7 kcal/min"),
            "Russian Twists": ("INTERMEDIATE", "10 REPS", "Abs & Obliques", "~9 kcal/min"),
            "Crunches": ("BEGINNER", "10 REPS", "Abdominals", "~8 kcal/min"),
            "Mountain Climbers": ("ADVANCED", "10 REPS", "Full Body Cardio", "~15 kcal/min"),
            "Jumping Jacks": ("BEGINNER", "10 REPS", "Cardio & Stamina", "~12 kcal/min"),
            "High Knees": ("INTERMEDIATE", "10 REPS", "Cardio & Legs", "~13 kcal/min")
        }

        for i, ex_name in enumerate(exercises[:5]):  # Show up to 5 exercises per page
            cy = start_y + (i * 63)
            x2, y2 = 50 + card_w, cy + card_h

            OverlayRenderer.draw_rounded_card(frame, (50, cy), (x2, y2), COLOR_SURFACE, COLOR_SURFACE_BORDER, 10, alpha=0.95)

            # Key Shortcut Badge
            OverlayRenderer.draw_pill_badge(frame, f"[ {i+1} ]", (85, cy + 27), COLOR_PRIMARY, (255, 255, 255), 0.5)

            # Exercise Name
            cv2.putText(frame, ex_name, (125, cy + 33),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)

            # Difficulty & Muscle Group Metadata
            diff, target_fmt, muscle, cal = meta.get(ex_name, ("BEGINNER", "10 REPS", "Full Body", "~10 kcal/min"))
            OverlayRenderer.draw_pill_badge(frame, diff, (x2 - 280, cy + 27), COLOR_SURFACE_BORDER, COLOR_TEXT_MUTED, 0.45)
            OverlayRenderer.draw_pill_badge(frame, target_fmt, (x2 - 170, cy + 27), COLOR_PRIMARY, (255, 255, 255), 0.45)

            # Muscle Group text
            cv2.putText(frame, f"Target: {muscle} • {cal}", (x2 - 470, cy + 33),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

        # Bottom Footer
        OverlayRenderer.draw_rounded_card(frame, (50, h - 65), (w - 50, h - 30), COLOR_SURFACE, COLOR_SURFACE_BORDER, 10, alpha=0.9)
        cv2.putText(frame, "Press 1 - 9 to Select Exercise  |  Press 'B' to Go Back", (w // 2 - 200, h - 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

    @staticmethod
    def draw_ghost_skeleton(frame: np.ndarray, ghost_keypoints: Dict[str, Keypoint]) -> None:
        """
        Draw semi-transparent Ghost Skeleton representing ideal starting posture.
        Alpha-blended to prevent obstruction of live frame.
        """
        if not ghost_keypoints:
            return

        h, w = frame.shape[:2]
        overlay = frame.copy()

        # Ghost skeleton styling (Soft Cyan / Blue)
        ghost_color = (246, 180, 100)
        ghost_joint_color = (255, 220, 150)

        # Draw connection segments
        for start, end in OverlayRenderer.SKELETON_CONNECTIONS:
            if start in ghost_keypoints and end in ghost_keypoints:
                kp_s, kp_e = ghost_keypoints[start], ghost_keypoints[end]
                pt_s = (int(kp_s.x * w), int(kp_s.y * h))
                pt_e = (int(kp_e.x * w), int(kp_e.y * h))
                cv2.line(overlay, pt_s, pt_e, ghost_color, 3, lineType=cv2.LINE_AA)

        # Draw ghost joints
        for name, kp in ghost_keypoints.items():
            cx, cy = int(kp.x * w), int(kp.y * h)
            cv2.circle(overlay, (cx, cy), 6, ghost_joint_color, -1, lineType=cv2.LINE_AA)

        # Apply alpha blending (0.45 transparency)
        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

    @staticmethod
    def draw_color_coded_skeleton(
        frame: np.ndarray,
        keypoints: Dict[str, Keypoint],
        joint_statuses: Dict[str, str]
    ) -> None:
        """
        Draw live user skeleton with color system:
        Green (94, 197, 34) = Joint correctly aligned
        Yellow (21, 204, 250) = Currently adjusting
        Red (68, 68, 239) = Incorrect joint
        """
        h, w = frame.shape[:2]

        color_map = {
            "correct": COLOR_SUCCESS,     # Emerald Green
            "adjusting": COLOR_WARNING,   # Yellow
            "incorrect": COLOR_ERROR      # Red
        }
        default_color = COLOR_SUCCESS

        # Draw connection segments
        for start, end in OverlayRenderer.SKELETON_CONNECTIONS:
            if start in keypoints and end in keypoints:
                kp_s, kp_e = keypoints[start], keypoints[end]
                if kp_s.confidence > 0.4 and kp_e.confidence > 0.4:
                    pt_s = (int(kp_s.x * w), int(kp_s.y * h))
                    pt_e = (int(kp_e.x * w), int(kp_e.y * h))
                    
                    st_s = joint_statuses.get(start, "correct")
                    st_e = joint_statuses.get(end, "correct")
                    seg_status = "incorrect" if "incorrect" in (st_s, st_e) else ("adjusting" if "adjusting" in (st_s, st_e) else "correct")
                    seg_color = color_map.get(seg_status, default_color)

                    cv2.line(frame, pt_s, pt_e, seg_color, 3, lineType=cv2.LINE_AA)

        # Draw joints
        for name, kp in keypoints.items():
            if kp.confidence > 0.4:
                cx, cy = int(kp.x * w), int(kp.y * h)
                status = joint_statuses.get(name, "correct")
                j_color = color_map.get(status, default_color)
                cv2.circle(frame, (cx, cy), 7, j_color, -1, lineType=cv2.LINE_AA)
                cv2.circle(frame, (cx, cy), 9, (255, 255, 255), 1, lineType=cv2.LINE_AA)

    @staticmethod
    def draw_alignment_hud(frame: np.ndarray, result: AlignmentResult) -> None:
        """
        Draw modern WHOOP style Pre-Workout Alignment Calibration Screen.
        """
        h, w = frame.shape[:2]

        # Top Title Header Card
        OverlayRenderer.draw_rounded_card(frame, (20, 20), (320, 75), COLOR_SURFACE, COLOR_SURFACE_BORDER, 12, alpha=0.9)
        cv2.putText(frame, "POSTURE CALIBRATION", (35, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_PRIMARY, 2, cv2.LINE_AA)
        cv2.putText(frame, "Align body with Ghost Skeleton", (35, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

        # Top-Right Progress Bar Card
        OverlayRenderer.draw_rounded_card(frame, (w - 340, 20), (w - 20, 75), COLOR_SURFACE, COLOR_SURFACE_BORDER, 12, alpha=0.9)
        score = int(result.alignment_score)
        
        cv2.putText(frame, f"Alignment: {score}%", (w - 325, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)

        # Progress bar fill
        bar_x1, bar_y1, bar_x2, bar_y2 = w - 325, 52, w - 35, 64
        fill_color = COLOR_SUCCESS if score >= 85 else (COLOR_WARNING if score >= 60 else COLOR_ERROR)
        OverlayRenderer.draw_progress_bar(frame, (bar_x1, bar_y1), (bar_x2, bar_y2), score / 100.0, fill_color)

        # Bottom Floating Coaching Notification Card (Single prioritized message)
        card_w = 480
        card_x1 = (w - card_w) // 2
        card_y1 = h - 90
        card_x2 = card_x1 + card_w
        card_y2 = h - 35

        if result.ready:
            # Success Ready Banner
            OverlayRenderer.draw_rounded_card(frame, (card_x1, card_y1), (card_x2, card_y2), COLOR_SUCCESS, None, 14, alpha=0.95)
            cv2.putText(frame, "✓ Perfect Alignment | Starting Workout...", (card_x1 + 30, card_y1 + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
        else:
            # Active Coaching Message Card
            OverlayRenderer.draw_rounded_card(frame, (card_x1, card_y1), (card_x2, card_y2), COLOR_SURFACE, COLOR_SURFACE_BORDER, 14, alpha=0.92)
            
            # Message icon & text
            msg = result.coaching_messages[0] if result.coaching_messages else "⚠ Align posture to start"
            cv2.putText(frame, msg, (card_x1 + 25, card_y1 + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WARNING, 2, cv2.LINE_AA)

            # Subtext hint
            cv2.putText(frame, "Rep counting remains locked until posture is aligned", (card_x1 + 25, card_y1 + 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

    @staticmethod
    def draw_tracking_stats(
        frame: np.ndarray,
        exercise_name: str,
        reps: int,
        sets: int,
        score: float,
        warnings: List[FormWarning],
        timer_display: Optional[str] = None
    ) -> None:
        """
        Draw modern WHOOP / Apple Fitness+ style Live Workout HUD.
        Camera is the hero element. Floating clean pill cards only.
        """
        h, w = frame.shape[:2]

        # Top-Left: Exercise Name Card
        OverlayRenderer.draw_rounded_card(frame, (20, 20), (280, 75), COLOR_SURFACE, COLOR_SURFACE_BORDER, 14, alpha=0.9)
        cv2.putText(frame, exercise_name.upper(), (35, 47),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_TEXT_PRIMARY, 2, cv2.LINE_AA)
        cv2.putText(frame, "WORKOUT IN PROGRESS", (35, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_PRIMARY, 1, cv2.LINE_AA)

        # Top-Right: Reps / Time & Sets Hero Badge Card
        OverlayRenderer.draw_rounded_card(frame, (w - 320, 20), (w - 20, 80), COLOR_SURFACE, COLOR_SURFACE_BORDER, 14, alpha=0.9)
        if timer_display:
            cv2.putText(frame, f"TIME: {timer_display}", (w - 300, 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLOR_WARNING, 2, cv2.LINE_AA)
            cv2.putText(frame, "Press 'S' Start/Pause", (w - 300, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, f"REPS: {reps}", (w - 300, 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOR_PRIMARY, 3, cv2.LINE_AA)
            cv2.putText(frame, f"SET: {sets + 1}", (w - 130, 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_TEXT_MUTED, 2, cv2.LINE_AA)

        # Top-Center Form Score Pill
        OverlayRenderer.draw_pill_badge(
            frame,
            f"FORM SCORE: {int(score)}%",
            (w // 2, 45),
            COLOR_SURFACE if score < 70 else COLOR_SUCCESS,
            (255, 255, 255) if score >= 70 else COLOR_TEXT_PRIMARY,
            scale=0.6,
            thickness=2
        )

        # Bottom Floating Coaching Notification Card (Single prioritized card)
        if warnings:
            top_w = warnings[0]
            card_w = 460
            card_x1 = (w - card_w) // 2
            card_y1 = h - 90
            card_x2 = card_x1 + card_w
            card_y2 = h - 35

            OverlayRenderer.draw_rounded_card(frame, (card_x1, card_y1), (card_x2, card_y2), COLOR_SURFACE, COLOR_ERROR, 14, alpha=0.92)
            cv2.putText(frame, f"⚠ Form Correction: {top_w.warning}", (card_x1 + 25, card_y1 + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_ERROR, 2, cv2.LINE_AA)
            cv2.putText(frame, top_w.suggestion, (card_x1 + 25, card_y1 + 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_TEXT_PRIMARY, 1, cv2.LINE_AA)

        # Bottom Navigation Hints Footer
        cv2.putText(frame, "Press 'B' Back  |  'R' Reset Session", (25, h - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

    @staticmethod
    def draw_skeleton(frame: np.ndarray, keypoints: Dict[str, Keypoint]) -> None:
        """Legacy basic skeleton rendering fallback."""
        OverlayRenderer.draw_color_coded_skeleton(frame, keypoints, {})

stream_overlay = OverlayRenderer
