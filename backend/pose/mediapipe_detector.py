"""
MediaPipe Pose concrete PoseDetector implementation using Google MediaPipe (33 Landmarks).
Supports Python 3.11+ and both MediaPipe Solutions & Tasks APIs.
"""
import os
import time
import urllib.request
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Any, Optional
from pose.base_detector import PoseDetector
from pose.keypoints import Keypoint
from utils.constants import MEDIAPIPE_KEYPOINTS

class MediaPipeDetector(PoseDetector):
    """
    Production-ready MediaPipe Pose detector for 33 landmark detection.
    Optimized for real-time CPU execution using model_complexity=0.
    """
    def __init__(
        self,
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.6,
        model_complexity: int = 0
    ):
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.model_complexity = model_complexity
        
        self.backend_type: Optional[str] = None
        self.pose: Any = None
        self.latest_kps: Dict[str, Keypoint] = {}
        self.latest_conf: Dict[str, float] = {}

    def initialize(self) -> bool:
        """
        Initialize MediaPipe Pose detector backend (Solutions API or Tasks API).
        Returns True if successful, False otherwise.
        """
        # Try Solutions API (MediaPipe <= 0.10.14)
        try:
            import mediapipe.solutions.pose as mp_pose
            self.pose = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=self.model_complexity,
                smooth_landmarks=True,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            self.backend_type = "solutions"
            return True
        except (ImportError, AttributeError):
            pass

        # Try Tasks API fallback (MediaPipe >= 0.10.15)
        try:
            from mediapipe.tasks import python as mp_tasks
            from mediapipe.tasks.python import vision

            model_path = "pose_landmarker_lite.task"
            if not os.path.exists(model_path):
                url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
                urllib.request.urlretrieve(url, model_path)

            options = vision.PoseLandmarkerOptions(
                base_options=mp_tasks.BaseOptions(model_asset_path=model_path),
                running_mode=vision.RunningMode.VIDEO,
                num_poses=1,
                min_pose_detection_confidence=self.min_detection_confidence,
                min_pose_presence_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            self.pose = vision.PoseLandmarker.create_from_options(options)
            self.backend_type = "tasks"
            self._last_timestamp_ms = 0
            return True
        except Exception as e:
            print(f"Error initializing MediaPipe Pose detector: {e}")
            self.pose = None
            return False

    def detect(self, frame: np.ndarray, now: Optional[float] = None) -> Dict[str, Keypoint]:
        """
        Run MediaPipe Pose inference on an image frame and return normalized 33 keypoints.
        Gracefully handles empty frames and missing person detections.
        """
        self.latest_kps = {}
        self.latest_conf = {}

        if self.pose is None or frame is None or frame.size == 0:
            return self.latest_kps

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.backend_type == "solutions":
                results = self.pose.process(rgb_frame)
                if results and results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    self._extract_landmarks(landmarks)

            elif self.backend_type == "tasks":
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                if now is None or now <= 0.0:
                    now = time.time()
                timestamp_ms = int(now * 1000)

                # Ensure strictly increasing timestamp for MediaPipe Tasks VIDEO mode
                if hasattr(self, "_last_timestamp_ms") and timestamp_ms <= self._last_timestamp_ms:
                    timestamp_ms = self._last_timestamp_ms + 1
                self._last_timestamp_ms = timestamp_ms

                results = self.pose.detect_for_video(mp_image, timestamp_ms)
                if results and results.pose_landmarks and len(results.pose_landmarks) > 0:
                    landmarks = results.pose_landmarks[0]
                    self._extract_landmarks(landmarks)

        except Exception as e:
            print(f"Error during MediaPipe Pose detection: {e}")

        return self.latest_kps

    def _extract_landmarks(self, landmarks: Any) -> None:
        """Helper to extract 33 landmarks into Keypoint dict."""
        for name, idx in MEDIAPIPE_KEYPOINTS.items():
            if idx < len(landmarks):
                lm = landmarks[idx]
                vis = getattr(lm, "visibility", None)
                pres = getattr(lm, "presence", None)
                confidence = float(vis if vis is not None else (pres if pres is not None else 1.0))
                kp = Keypoint(
                    name=name,
                    x=float(lm.x),
                    y=float(lm.y),
                    confidence=confidence
                )
                self.latest_kps[name] = kp
                self.latest_conf[name] = confidence

    def get_keypoints(self) -> Dict[str, Keypoint]:
        """Get the latest detected keypoints dictionary."""
        return self.latest_kps

    def get_confidence(self) -> Dict[str, float]:
        """Get keypoint confidence scores mapping."""
        return self.latest_conf

    def shutdown(self) -> None:
        """Close MediaPipe Pose instance and free resources."""
        if self.pose is not None:
            if hasattr(self.pose, "close"):
                self.pose.close()
            self.pose = None
        self.latest_kps.clear()
        self.latest_conf.clear()
