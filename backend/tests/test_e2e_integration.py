"""
Comprehensive End-to-End Integration Tests for FitFlow FastAPI Server.
Verifies OpenCV headless import, MediaPipe pose detector, REST endpoints,
CORS preflight headers, and WebSocket binary frame streaming & inference.
"""
import pytest
import cv2
import numpy as np
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_opencv_headless_import():
    """Verify OpenCV imports cleanly and cv2 version is accessible."""
    assert cv2.__version__ is not None
    assert hasattr(cv2, "imdecode")
    assert hasattr(cv2, "cvtColor")

def test_rest_categories_endpoint():
    """Verify GET /api/categories returns HTTP 200 and category dictionary."""
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "1" in data
    assert data["1"]["name"] == "UPPER BODY"
    assert "exercises" in data["1"]

def test_rest_history_endpoint():
    """Verify GET /api/history returns HTTP 200 and list."""
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_rest_exercise_info_endpoint():
    """Verify GET /api/exercises/{name} returns HTTP 200 and configuration."""
    response = client.get("/api/exercises/Bicep%20Curl")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "REP_BASED"
    assert data["primary_joint"] == "elbow"

def test_rest_summary_endpoint():
    """Verify GET /api/summary returns HTTP 200."""
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert "has_summary" in data

def test_cors_preflight_for_vercel_origin():
    """Verify CORS preflight OPTIONS request from Vercel domain returns headers."""
    response = client.options(
        "/api/categories",
        headers={
            "Origin": "https://fitflow.vercel.app",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://fitflow.vercel.app"

def test_websocket_binary_frame_inference_e2e():
    """Verify WebSocket handshake, exercise selection, and binary JPEG frame processing."""
    with client.websocket_connect("/ws/workout") as websocket:
        # 1. Select exercise
        websocket.send_json({"action": "select_exercise", "exercise": "Bicep Curl"})
        ack = websocket.receive_json()
        assert ack.get("type") == "status"
        assert ack.get("status") == "exercise_selected"
        assert ack.get("exercise") == "Bicep Curl"

        # 2. Generate synthetic test image & encode as JPEG buffer
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw dummy limbs to give MediaPipe pixel data
        cv2.line(img, (320, 100), (320, 300), (255, 255, 255), 10)
        cv2.circle(img, (320, 100), 30, (255, 255, 255), -1)
        success, buffer = cv2.imencode(".jpg", img)
        assert success

        # 3. Stream binary JPEG frame over WebSocket
        websocket.send_bytes(buffer.tobytes())

        # 4. Receive and validate inference payload
        inference = websocket.receive_json()
        assert inference.get("type") == "inference"
        assert "keypoints" in inference
        assert "alignment" in inference
        assert "tracking" in inference
        assert "state" in inference["tracking"]
