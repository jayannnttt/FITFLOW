# AI Fitness Coach API Documentation

This document provides a comprehensive and verified API specification for the AI Fitness Coach backend service (`server.py`). All information contained herein is extracted directly from the backend implementation.

---

## 1. System Architecture Summary

The backend is built using **FastAPI** (`server.py`) powered by **Uvicorn**. It decouples AI/CV computer vision logic (MediaPipe 33-landmark pose detection, posture alignment, joint angle calculations, and rep counting state machine) from the frontend web interface.

Key backend components:
- **FastAPI Core (`server.py`)**: Hosts REST endpoints and WebSocket servers.
- **Detector Engine (`pose/detector_factory.py`, `pose/mediapipe_detector.py`)**: Runs MediaPipe Pose landmark estimation.
- **Filter & Smoothing (`pose/pose_filter.py`, `pose/smoothing.py`)**: One-Euro / EMA filtering for joint landmarks.
- **Alignment Engine (`tracking/alignment_engine.py`)**: Real-time target pose posture alignment scoring (0–100%) and ghost keypoint generation.
- **Exercise State Machine (`exercises/*`)**: Tracks workout repetitions, form warnings, and joint metrics.
- **Analytics & Scoring (`analytics/*`)**: Evaluates smoothness, depth, symmetry, and rep score.
- **Storage & Logging (`storage/workout_history.py`, `workout_logging/csv_logger.py`)**: Persists history in `workout_history.json` and rep details in `performance_log.csv`.

---

## 2. API Base URL

- **Development Base URL**: `http://127.0.0.1:8000`
- **WebSocket Base URL**: `ws://127.0.0.1:8000`
- **Host & Port Configuration**: Defined in `AppConfig` (`config.py`) via `server_host` (default `"127.0.0.1"`) and `server_port` (default `8000`).

---

## 3. Authentication & Authorization

- **Authentication Mechanism**: None. Endpoints are currently open/public.
- **Authorization / User Roles**: N/A (single-tenant local runtime).
- **Session Identification**: State is maintained in-memory on the server per active WebSocket connection using `SessionState`.

---

## 4. Complete API Endpoint Table

| Method | Endpoint | Purpose | Auth | Request Data | Response Data | HTTP Status |
| ------ | -------- | ------- | ---- | ------------ | ------------- | ----------- |
| `GET` | `/api/categories` | Get workout category hierarchy & exercises | None | None | Category Map JSON | `200 OK` |
| `GET` | `/api/exercises/{name}` | Get specific exercise configuration & metadata | None | Path: `name` (string) | Exercise Object JSON | `200 OK`, `404 Not Found` |
| `GET` | `/api/history` | Get recorded workout history sessions | None | None | History Array JSON | `200 OK` |
| `GET` | `/api/summary` | Get summary of current active/latest workout session | None | None | Summary Object JSON | `200 OK` |
| `WS` | `/ws/workout` | Real-time WebSocket streaming for frame inference & controls | None | Text JSON / Binary JPEG | Inference Data JSON | `101 Switching Protocols` |
| `GET` | `/{path}` | Static file server mounting `web/` directory | None | Path URL | Static Web Assets | `200 OK`, `404 Not Found` |

---

## 5. Detailed Endpoint Specification

### 5.1 GET `/api/categories`
- **Purpose**: Returns all available workout categories and their associated exercise lists.
- **Authentication**: None.
- **Request Headers**: None.
- **Query Parameters**: None.
- **Request Body**: None.
- **Response Format (`application/json`)**:
  ```json
  {
    "1": {
      "name": "UPPER BODY",
      "exercises": ["Bicep Curl", "Shoulder Press", "Push-ups", "Pull-ups"]
    },
    "2": {
      "name": "LOWER BODY",
      "exercises": ["Squats", "Lunges", "Calf Raises"]
    },
    "3": {
      "name": "CORE",
      "exercises": ["Russian Twists", "Crunches", "Mountain Climbers"]
    },
    "4": {
      "name": "FULL BODY / CARDIO",
      "exercises": ["Jumping Jacks", "High Knees"]
    }
  }
  ```

---

### 5.2 GET `/api/exercises/{name}`
- **Purpose**: Returns full exercise parameters, threshold angles, keypoints, alignment targets, coaching rules, and form check parameters for a specific exercise.
- **Authentication**: None.
- **Path Parameters**:
  - `name` (string, required): Exact name of the exercise (e.g., `"Bicep Curl"`, `"Squats"`).
- **Request Body**: None.
- **Response Format (`application/json`)** - *Status 200 OK*:
  ```json
  {
    "type": "REP_BASED",
    "category": "UPPER BODY",
    "primary_joint": "elbow",
    "keypoints": ["left_shoulder", "left_elbow", "left_wrist"],
    "alt_keypoints": ["right_shoulder", "right_elbow", "right_wrist"],
    "down_threshold": 150.0,
    "up_threshold": 90.0,
    "target_reps": 10,
    "cooldown": 0.8,
    "alignment": {
      "starting_pose_angles": {
        "left_elbow": 175.0,
        "right_elbow": 175.0,
        "torso": 180.0
      },
      "tolerances": {
        "left_elbow": 30.0,
        "right_elbow": 30.0,
        "torso": 25.0
      },
      "coaching_rules": {
        "left_elbow": "Straighten your left arm to start",
        "right_elbow": "Straighten your right arm to start",
        "torso": "Stand upright with back straight"
      }
    },
    "checks": {
      "elbow_swing": {"max_shoulder_movement": 30.0},
      "incomplete_extension": {"min_down_angle": 140.0}
    }
  }
  ```
- **Error Response** - *Status 404 Not Found*:
  ```json
  {
    "detail": "Exercise not found"
  }
  ```

---

### 5.3 GET `/api/history`
- **Purpose**: Returns a list of past logged workout sessions.
- **Authentication**: None.
- **Response Format (`application/json`)** - *Status 200 OK*:
  ```json
  [
    {
      "date": "2026-08-05 00:00:17",
      "exercise": "Bicep Curl",
      "reps": 10,
      "sets": 1,
      "elapsed_time": 36.8,
      "avg_score": 85.0
    }
  ]
  ```

---

### 5.4 GET `/api/summary`
- **Purpose**: Returns the summary metrics for the currently active (or recently ended) workout session.
- **Authentication**: None.
- **Response Format (`application/json`)**:
  - *When Session Active*:
    ```json
    {
      "has_summary": true,
      "exercise": "Bicep Curl",
      "reps": 10,
      "sets": 1,
      "duration_sec": 45,
      "form_score": 88,
      "calories_burned": 7
    }
    ```
  - *When No Active Session*:
    ```json
    {
      "has_summary": false
    }
    ```

---

### 5.5 WS `/ws/workout` (WebSocket Real-Time API)
- **Purpose**: High-speed bidirectional streaming endpoint for camera frames, posture alignment, pose estimation, and workout state tracking.
- **Protocol**: WebSockets.

#### A. Client Text Messages (Control Commands)
Clients send JSON string frames to trigger control actions:

1. **Select Exercise**:
   - Request: `{"action": "select_exercise", "exercise": "Bicep Curl"}`
   - Response: `{"type": "status", "status": "exercise_selected", "exercise": "Bicep Curl"}`

2. **Start Active Tracking**:
   - Request: `{"action": "start_active_tracking"}`
   - Response: `{"type": "status", "status": "tracking_active"}`

3. **Reset Session**:
   - Request: `{"action": "reset"}`
   - Response: `{"type": "status", "status": "reset"}`

#### B. Client Binary Messages (Video Frames)
- Client sends binary JPEG encoded ArrayBuffer frame buffer over WebSocket.

#### C. Server Frame Response (Inference Payload)
- Server returns JSON response for each frame received:
  ```json
  {
    "type": "inference",
    "keypoints": {
      "left_shoulder": {"x": 0.452, "y": 0.312, "confidence": 0.98},
      "left_elbow": {"x": 0.461, "y": 0.489, "confidence": 0.96},
      "left_wrist": {"x": 0.458, "y": 0.654, "confidence": 0.95}
    },
    "alignment": {
      "score": 92.5,
      "ready": true,
      "joint_statuses": {
        "left_elbow": true,
        "right_elbow": true,
        "torso": true
      },
      "coaching_messages": [],
      "ghost_keypoints": {
        "left_shoulder": {"x": 0.45, "y": 0.31}
      }
    },
    "tracking": {
      "exercise": "Bicep Curl",
      "state": "STARTED",
      "reps": 3,
      "sets": 0,
      "form_score": 85,
      "warnings": [
        {
          "warning": "Elbow Swing",
          "suggestion": "Keep your upper arm still"
        }
      ],
      "timer_display": null,
      "finished": false,
      "completion_reason": null,
      "elapsed_time": 24.5,
      "joint_angles": {
        "left_elbow": "142°",
        "right_elbow": "145°",
        "left_shoulder": "22°"
      },
      "current_angle": 142.0
    }
  }
  ```

---

## 6. Backend Entities / Data Models

### 1. `Category`
- `name` (string): Name of exercise category (e.g. `"UPPER BODY"`).
- `exercises` (array of strings): List of exercise names.

### 2. `ExerciseConfig`
- `type` (string): `"REP_BASED"` or `"TIME_BASED"`.
- `category` (string): Category title.
- `primary_joint` (string): Primary joint tracked (e.g., `"elbow"`, `"knee"`, `"hip"`).
- `keypoints` (array of strings): MediaPipe keypoint names.
- `down_threshold` (float): Degree angle for lower bound rep state.
- `up_threshold` (float): Degree angle for upper bound rep state.
- `target_reps` (int): Target repetition count (default 10).
- `cooldown` (float): Seconds cooldown between rep triggers.
- `alignment` (object):
  - `starting_pose_angles` (map of joint: float angle).
  - `tolerances` (map of joint: float tolerance).
  - `coaching_rules` (map of joint: instruction string).
- `checks` (object): Form checking thresholds.

### 3. `WorkoutHistoryEntry`
- `date` (string): Timestamp formatted `YYYY-MM-DD HH:MM:SS`.
- `exercise` (string): Exercise name.
- `reps` (integer): Total reps completed.
- `sets` (integer): Total sets completed.
- `elapsed_time` (float): Duration in seconds.
- `avg_score` (float): Form score percentage (0–100).

---

## 7. Frontend Feature Mapping

| Frontend Feature | Backend API | Method | Data Passed |
| ---------------- | ----------- | ------ | ----------- |
| Categories List / Home | `/api/categories` | `GET` | None |
| Exercise Details Modal | `/api/exercises/{name}` | `GET` | `name` in URL |
| Workout History View | `/api/history` | `GET` | None |
| Workout Summary Screen | `/api/summary` | `GET` | None |
| Exercise Selection Action | `/ws/workout` | `WS Text` | `{"action": "select_exercise", "exercise": "..."}` |
| Active Tracking Start | `/ws/workout` | `WS Text` | `{"action": "start_active_tracking"}` |
| Reset Session Action | `/ws/workout` | `WS Text` | `{"action": "reset"}` |
| Real-time Video Stream | `/ws/workout` | `WS Binary` | JPEG image frame buffer (bytes) |

---

## 8. UI States & Error Handling

- **Loading State**: Shown when fetching `/api/categories`, `/api/exercises/{name}`, or initiating WebSocket handshake.
- **Success State**: Loaded exercise list, live posture overlay rendered via keypoints/ghost_keypoints, active rep counter updates.
- **Alignment Feedback State**: Displaying posture alignment score percentage, ghost skeleton alignment guide, and coaching messages.
- **404 Not Found**: Received when requesting details for an invalid exercise name.
- **WebSocket Disconnection / Error**: When `/ws/workout` drops, UI displays `WEBSOCKET_ERROR` and provides a retry mechanism.
