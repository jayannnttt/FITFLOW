"""
Unit tests for FastAPI server REST APIs and WebSocket endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_api_get_categories():
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "1" in data
    assert data["1"]["name"] == "UPPER BODY"

def test_api_get_exercise_info():
    response = client.get("/api/exercises/Bicep%20Curl")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "REP_BASED"
    assert data["primary_joint"] == "elbow"

def test_api_get_exercise_not_found():
    response = client.get("/api/exercises/NonExistentExercise")
    assert response.status_code == 404

def test_api_get_history():
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_websocket_workout_text_command():
    with client.websocket_connect("/ws/workout") as websocket:
        websocket.send_json({"action": "select_exercise", "exercise": "Bicep Curl"})
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["status"] == "exercise_selected"
        assert data["exercise"] == "Bicep Curl"

def test_session_state_performance_analyzer():
    from server import SessionState, session_state
    s = SessionState()
    assert hasattr(s, "performance_analyzer")
    assert s.performance_analyzer is not None
    
    s.select_exercise("Bicep Curl")
    assert hasattr(s, "performance_analyzer")
    assert s.performance_analyzer is not None

    analysis = s.performance_analyzer.analyze_rep([160.0, 120.0, 50.0, 120.0, 160.0])
    assert "score" in analysis
    assert "smoothness" in analysis
    assert "depth" in analysis
