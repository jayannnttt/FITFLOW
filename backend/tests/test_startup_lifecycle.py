"""
Unit and Integration tests for AI Fitness Tracker Startup Lifecycle & State Synchronization.
"""
import json
import pytest
import numpy as np
import cv2
from fastapi.testclient import TestClient
from server import app, session_state
from utils.enums import ExerciseState

client = TestClient(app)

def test_websocket_default_alignment_ready_is_false():
    """Verify that default alignment data returns ready: False before exercise selection."""
    session_state.active_exercise = None
    session_state.exercise_name = None

    with client.websocket_connect("/ws/workout") as websocket:
        # Create dummy JPEG image buffer
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, img_encoded = cv2.imencode('.jpg', img)
        bytes_data = img_encoded.tobytes()

        # Send binary frame
        websocket.send_bytes(bytes_data)
        data = websocket.receive_json()

        assert data["type"] == "inference"
        assert data["alignment"]["ready"] is False
        assert data["tracking"]["state"] == "INITIALIZING"

def test_websocket_exercise_selection_ack():
    """Verify select_exercise returns status ACK and initializes exercise state to ALIGNING."""
    with client.websocket_connect("/ws/workout") as websocket:
        websocket.send_json({"action": "select_exercise", "exercise": "Squats"})
        data = websocket.receive_json()

        assert data["type"] == "status"
        assert data["status"] == "exercise_selected"
        assert data["exercise"] == "Squats"

        assert session_state.active_exercise is not None
        assert session_state.active_exercise.state == ExerciseState.ALIGNING

def test_websocket_start_active_tracking_cmd():
    """Verify start_active_tracking command transitions exercise state from ALIGNING to STARTED."""
    with client.websocket_connect("/ws/workout") as websocket:
        websocket.send_json({"action": "select_exercise", "exercise": "Squats"})
        websocket.receive_json() # ACK

        websocket.send_json({"action": "start_active_tracking"})
        ack = websocket.receive_json()

        assert ack["type"] == "status"
        assert ack["status"] == "tracking_active"
        assert session_state.active_exercise.state == ExerciseState.STARTED
        assert session_state.active_exercise.alignment_ready is True

def test_full_startup_lifecycle_flow():
    """Verify complete startup lifecycle: Connect -> Select -> Calibrate -> Active Tracking."""
    with client.websocket_connect("/ws/workout") as websocket:
        # 1. Connect & Select Exercise
        websocket.send_json({"action": "select_exercise", "exercise": "Bicep Curl"})
        ack = websocket.receive_json()
        assert ack["status"] == "exercise_selected"

        # 2. Transmit frame during calibration
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, img_encoded = cv2.imencode('.jpg', img)
        bytes_data = img_encoded.tobytes()

        websocket.send_bytes(bytes_data)
        inference = websocket.receive_json()
        assert inference["tracking"]["state"] == "ALIGNING"

        # 3. Client finishes countdown and sends start_active_tracking
        websocket.send_json({"action": "start_active_tracking"})
        ack_active = websocket.receive_json()
        assert ack_active["status"] == "tracking_active"

        # 4. Subsequent frame processed in STARTED / active state
        websocket.send_bytes(bytes_data)
        active_inference = websocket.receive_json()
        assert active_inference["tracking"]["state"] == "STARTED"
