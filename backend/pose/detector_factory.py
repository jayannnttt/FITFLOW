"""
Factory module for instantiating the MediaPipe Pose detector.
"""
from typing import Any
from pose.base_detector import PoseDetector
from pose.mediapipe_detector import MediaPipeDetector

class DetectorFactory:
    """
    Factory to instantiate and initialize the MediaPipe pose detector backend.
    """
    @staticmethod
    def create_detector(backend_name: str = "mediapipe", **kwargs: Any) -> PoseDetector:
        """
        Instantiate and return the MediaPipe PoseDetector.
        """
        min_det = kwargs.get("min_detection_confidence", 0.6)
        min_track = kwargs.get("min_tracking_confidence", 0.6)
        model_complexity = kwargs.get("model_complexity", 0)

        detector = MediaPipeDetector(
            min_detection_confidence=min_det,
            min_tracking_confidence=min_track,
            model_complexity=model_complexity
        )
        detector.initialize()
        return detector
