"""
Abstract Base class/interface for PoseDetector models.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
import numpy as np
from pose.keypoints import Keypoint

class PoseDetector(ABC):
    """
    Unified abstract interface for pose detection backends.
    """
    @abstractmethod
    def initialize(self) -> bool:
        """
        Load model weights, prepare runtime configuration, and bind device (GPU/CPU).
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def detect(self, frame: np.ndarray, now: Optional[float] = None) -> Dict[str, Keypoint]:
        """
        Run inference on the image frame and return keypoints dict.
        """
        pass

    @abstractmethod
    def get_keypoints(self) -> Dict[str, Keypoint]:
        """
        Get the latest normalized keypoints mapping.
        """
        pass

    @abstractmethod
    def get_confidence(self) -> Dict[str, float]:
        """
        Get confidence levels for recently detected keypoints.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Release hardware resources and clean inference buffers.
        """
        pass
