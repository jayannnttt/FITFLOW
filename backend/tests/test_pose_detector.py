"""
Unit tests for the MediaPipe PoseDetector interface and factory.
"""
import pytest
import numpy as np
from pose.detector_factory import DetectorFactory
from pose.base_detector import PoseDetector
from pose.mediapipe_detector import MediaPipeDetector

def test_detector_factory_mediapipe():
    detector = DetectorFactory.create_detector("mediapipe")
    
    assert detector is not None
    assert isinstance(detector, PoseDetector)
    assert isinstance(detector, MediaPipeDetector)
    
    # Test interface method presence
    assert hasattr(detector, "initialize")
    assert hasattr(detector, "detect")
    assert hasattr(detector, "get_keypoints")
    assert hasattr(detector, "get_confidence")
    assert hasattr(detector, "shutdown")
    detector.shutdown()

def test_detector_empty_frame_handling():
    detector = DetectorFactory.create_detector("mediapipe")
    
    # Create empty black frame (no person present)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    kps = detector.detect(frame)
    assert isinstance(kps, dict)
    # When no person is detected, returns empty dict without crashing
    assert len(kps) == 0
    
    # Check get_keypoints caching
    cached_kps = detector.get_keypoints()
    assert cached_kps == kps
    
    # Check get_confidence
    confidences = detector.get_confidence()
    assert isinstance(confidences, dict)
    assert len(confidences) == 0

    detector.shutdown()

def test_detector_null_frame_handling():
    detector = DetectorFactory.create_detector("mediapipe")
    
    # None frame test
    kps = detector.detect(None)
    assert isinstance(kps, dict)
    assert len(kps) == 0

    detector.shutdown()
