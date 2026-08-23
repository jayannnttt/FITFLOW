# AI Fitness Coach — Frontend Design & UI/UX Specification

This document provides a comprehensive, production-ready frontend design specification for the **AI Fitness Coach** application. The proposed design is built strictly around the capabilities, endpoints, and WebSocket payload structures of the existing FastAPI backend (`server.py`).

---

## 1. Existing Frontend Analysis

### Strengths of Current Frontend (`web/`)
- **Deterministic Startup Pipeline**: Clean state machine pattern (`StartupState`) sequentially handling camera permissions, WebSocket connection, and exercise selection ACK.
- **Canvas Overlay**: HTML5 `<canvas>` rendering skeleton connections and color-coded joint nodes on top of the `<video>` element.
- **Binary Frame Transmission**: Offscreen canvas captures frames and streams binary JPEG buffers over WebSocket at ~25 FPS.

### Issues, Gaps & Design Failures
1. **Missing History Screen**: The navbar contains a "History" button (`#nav-history-btn`), but no History screen or modal exists in `index.html`. The backend endpoint `GET /api/history` is implemented but **never displayed** in the UI.
2. **Visual Posture Alignment Phase Skipped**: The UI bypasses the posture alignment calibration state (`ALIGNING`) and transitions straight into active workout mode without presenting a clear visual posture calibration screen for holding the starting pose.
3. **Cluttered Floating HUD**: The HUD overlays cover the camera view. Floating cards block key body areas (head and upper torso), creating visual distraction.
4. **Missing Real-Time Timer UI**: `tracking.elapsed_time` is sent in every WebSocket frame payload, but it is not rendered in the live workout UI.
5. **Hardcoded Text & Fallbacks**: Hardcoded strings (e.g. `~10 kcal/min`, `UPPER BODY` fallback badges) persist even when dynamic backend configuration exists.
6. **Aesthetics & Styling**: Plain dark mode (`#0F172A`) lacking modern glassmorphism, depth gradients, crisp telemetry typography, or cyber-fitness micro-animations.

---

## 2. Backend Capability Analysis

The existing backend exposes the following interfaces:

### REST APIs
- `GET /api/categories`: Returns categories and exercise hierarchy.
- `GET /api/exercises/{name}`: Returns exercise configuration (`primary_joint`, `keypoints`, `down_threshold`, `up_threshold`, `alignment`, `checks`).
- `GET /api/history`: Returns recorded workout session array (`date`, `exercise`, `reps`, `sets`, `elapsed_time`, `avg_score`).
- `GET /api/summary`: Returns summary object of active/latest session (`has_summary`, `exercise`, `reps`, `sets`, `duration_sec`, `form_score`, `calories_burned`).

### WebSocket Endpoint (`/ws/workout`)
- **Client JSON Commands**:
  - `{"action": "select_exercise", "exercise": "<name>"}`
  - `{"action": "start_active_tracking"}`
  - `{"action": "reset"}`
- **Client Binary Messages**: JPEG image byte stream.
- **Server Inference Response Frame (`type: "inference"`)**:
  - `keypoints`: Landmark coordinates `{x, y, confidence}`.
  - `alignment`: `{score, ready, joint_statuses, coaching_messages, ghost_keypoints}`.
  - `tracking`: `{exercise, state, reps, sets, form_score, warnings, timer_display, finished, elapsed_time, joint_angles, current_angle}`.

---

## 3. Backend → Frontend Data Mapping

| Backend Property | Target Screen | UI Component / Element | Display Format |
| ---------------- | ------------- | ---------------------- | -------------- |
| `categories` | Home / Library | Category Cards Grid | Title, exercise count pill |
| `exercises` | Exercise Selection | Exercise Card | Name, primary joint badge, target reps |
| `alignment.score` | Calibration & Workout | Alignment Ring Gauge / Progress Fill | Radial percentage (`0–100%`) |
| `alignment.ready` | Calibration | Calibration Readiness Indicator | Pulse glow: Green = Ready, Amber = Aligning |
| `alignment.ghost_keypoints` | Calibration | Ghost Pose Overlay (Canvas) | Semi-transparent neon cyan skeleton |
| `alignment.coaching_messages` | Calibration & Workout | Live Coaching Banner | Real-time instruction banner |
| `keypoints` | Calibration & Workout | Live User Pose Overlay (Canvas) | Color-coded skeleton (Green/Yellow/Red) |
| `tracking.reps` | Workout Screen | Rep Counter (Hero Metric) | Large bold telemetry number |
| `tracking.sets` | Workout Screen | Set Counter Badge | `SET X` pill |
| `tracking.form_score` | Workout Screen | Form Score Dial | Radial arc / percentage score |
| `tracking.state` | Workout Screen | Lifecycle State Badge | State pill (`IDLE`, `ALIGNING`, `STARTED`, `DOWN`, `UP`, `FINISHED`) |
| `tracking.joint_angles` | Workout Screen | Canvas Joint Badges | Floating angle tags (`142°`) near joint nodes |
| `tracking.current_angle` | Workout Screen | Primary Joint Angle HUD | Telemetry metric (`142.0°`) |
| `tracking.warnings` | Workout Screen | Form Warning Banner | Warning toast (`⚠ Control movement`) |
| `tracking.elapsed_time` | Workout Screen | Live Workout Timer | Stopwatch format `MM:SS` |
| `history` array | History Screen | Session History Table / Cards | List showing Date, Exercise, Reps, Duration, Form Score |
| `/api/summary` data | Summary Modal | Post-Workout Performance Card | Reps, Duration, Form Score, Calories Burned |

---

## 4. Proposed Information Architecture & Screen List

The redesigned application comprises **6 Core View Screens/Modals**:

1. **Dashboard / Home Screen (`/`)**: Hero stats, workout categories, streak/activity summary teaser.
2. **Exercise Library Screen (`/exercises`)**: Exercise grid categorized by muscle group with key joint badges and difficulty tags.
3. **Posture Calibration View (`/calibrate`)**: Dedicated full-bleed camera screen for starting pose alignment (`ALIGNING` state) with ghost skeleton matching and progress ring.
4. **Live AI Workout View (`/workout`)**: Premium HUD camera view with skeleton rendering, hero rep counter, real-time form score dial, live coaching, and joint angle telemetry.
5. **Workout Summary Screen (`/summary`)**: Post-workout metrics showcase with form score breakdown, calories, and performance rating.
6. **Workout History Screen (`/history`)**: Table and card list of past logged workouts fetched directly from `/api/history`.

---

## 5. Complete User Journey Flow

```text
       ┌────────────────────────┐
       │   App Launch / Home    │ (Fetches /api/categories)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   Select Category      │ (Filters exercises)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   Select Exercise      │ (Fetches /api/exercises/{name})
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Exercise Prep Modal    │ (Displays starting pose & target reps)
       └───────────┬────────────┘
                   │ User clicks "Start Calibration"
                   ▼
       ┌────────────────────────┐
       │  Camera & WS Connect   │ (Camera + WebSocket /ws/workout)
       └───────────┬────────────┘
                   │ WS ACK "exercise_selected"
                   ▼
       ┌────────────────────────┐
       │ Posture Calibration    │ (Backend state: ALIGNING)
       │  (Ghost Skeleton)      │ (Alignment score progress ring)
       └───────────┬────────────┘
                   │ alignment.ready === true (or user clicks start)
                   ▼
       ┌────────────────────────┐
       │    Live AI Workout     │ (Backend state: STARTED / DOWN / UP)
       │  (Rep Counter & HUD)   │ (Real-time form score & warnings)
       └───────────┬────────────┘
                   │ tracking.finished === true OR User stops
                   ▼
       ┌────────────────────────┐
       │   Workout Summary      │ (Fetches /api/summary)
       └───────────┬────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌─────────────────┐ ┌─────────────────┐
│ Back to Home    │ │ View History    │ (Fetches /api/history)
└─────────────────┘ └─────────────────┘
```

---

## 6. Workout Screen Specification (Core Feature)

### Layout Blueprint
The Live Workout Screen uses a **Full-Bleed 16:9 Viewport Container** with a dark glassmorphism HUD overlay system:

- **Background Stage**: Live HTML5 Video Stream + HTML5 Canvas overlay.
- **Top Bar HUD**:
  - *Left*: Exercise Title + State Pill (`BICEP CURL` • `ACTIVE`).
  - *Center*: Live Workout Timer (`MM:SS`) derived from `tracking.elapsed_time`.
  - *Right*: Active Connection Status Indicator (Green WS pulse dot).
- **Left Side Telemetry Panel**:
  - *Form Score Meter*: Radial arc gauge displaying real-time `tracking.form_score` (0–100%).
  - *Primary Joint Angle*: Digital readout card displaying `tracking.current_angle`.
- **Right Side Hero Counter**:
  - *Reps Counter*: Oversized digital hero metric (`tracking.reps`).
  - *Sets Pill*: `SET X` badge (`tracking.sets + 1`).
- **Bottom Coaching Banner**:
  - Floating glassmorphism card displaying `tracking.warnings` or posture `coaching_messages`.
- **Bottom Control Bar**:
  - `RESET` session button (sends `{action: "reset"}`).
  - `END WORKOUT` session button (fetches `/api/summary`).

---

## 7. Visual Design System

### Color Palette (Futuristic Cyber-Fitness)
- **Background Main**: `#090D16` (Deep Space Dark)
- **Surface Elevation**: `#111827` / Glassmorphism `#111827CC` with `backdrop-filter: blur(16px)`
- **Border Overlay**: `rgba(255, 255, 255, 0.08)`
- **Accent Primary (Cyan Neon)**: `#06B6D4` (Ghost skeleton & active indicators)
- **Success Green (Form Correct)**: `#10B981` (Rep completions & good posture)
- **Warning Amber (Form Adjusting)**: `#F59E0B` (Posture warnings & adjustments)
- **Critical Red (Form Incorrect)**: `#EF4444` (Severe form errors)
- **Typography Colors**: Primary `#F9FAFB`, Muted `#9CA3AF`

### Typography & Fonts
- **Primary Font**: `Inter`, sans-serif (UI headings & labels).
- **Telemetry Font**: `JetBrains Mono` or `Space Grotesk`, monospace (Rep numbers, angles, stopwatches).

---

## 8. Figma-Ready Specifications

```text
================================================================================
SCREEN 1: DASHBOARD / HOME (`/`)
================================================================================
Purpose: Main landing page displaying workout options and summary metrics.
Layout: Top Navbar + Hero Banner + Category Grid + Streak Summary Panel.
Navigation: Links to Exercise Library and Workout History.
Components:
  ├── Top Navigation Bar (Logo, Home link, History button, Status dot)
  ├── Hero Section ("AI-Powered Motion Tracking", Quick Start CTA)
  ├── Stat Badges (Total Categories, Available Exercises, Streak Count)
  └── Category Cards Grid (Upper Body, Lower Body, Core, Full Body)
Data: Fetches GET /api/categories and GET /api/history.

================================================================================
SCREEN 2: EXERCISE LIBRARY (`/exercises`)
================================================================================
Purpose: Display exercises within selected category.
Layout: Back button header + Exercise Cards Grid.
Components:
  ├── Header Bar (Category Tag, Search/Filter)
  └── Exercise Cards (Title, Primary Joint Badge, Target Reps, Select CTA)
Data: Filtered list from GET /api/categories.

================================================================================
SCREEN 3: EXERCISE PREPARATION & POSTURE CALIBRATION MODAL
================================================================================
Purpose: Onboard user to exercise posture before starting camera stream.
Components:
  ├── Exercise Header (Name, Category Badge, Primary Joint)
  ├── Target Reps & Estimated Calories Card
  ├── Starting Posture Instructions (Rules & tolerances)
  └── CTA Button ("▶ START CAMERA & CALIBRATION")
Data: Fetches GET /api/exercises/{name}.

================================================================================
SCREEN 4: LIVE AI WORKOUT SCREEN (`/workout`)
================================================================================
Purpose: Real-time pose estimation, rep counting, and posture feedback.
Layout: Full-bleed camera container + Canvas overlay + Floating Glassmorphism HUD.
Components:
  ├── Top HUD Bar (Exercise Name, Live Timer, Network Status)
  ├── Canvas Overlay (Ghost Skeleton Cyan + User Skeleton Color-Coded)
  ├── Left Telemetry Panel (Form Score Radial Arc, Joint Angle Card)
  ├── Right Hero Metrics (Large Rep Counter, Set Pill)
  ├── Bottom Coaching Banner (Warnings & Form Advice)
  └── Floating Controls (Reset Button, Finish Workout Button)
Data: Bi-directional WebSocket /ws/workout.

================================================================================
SCREEN 5: WORKOUT SUMMARY MODAL (`/summary`)
================================================================================
Purpose: Display breakdown after completing workout session.
Components:
  ├── Celebration Header (Trophy Icon, Completion Title)
  ├── Metrics Grid (Total Reps, Workout Duration, Avg Form Score, Calories)
  └── Actions (Try Again Button, Return Home Button)
Data: Fetches GET /api/summary.

================================================================================
SCREEN 6: WORKOUT HISTORY SCREEN (`/history`)
================================================================================
Purpose: Display recorded workout sessions.
Components:
  ├── History Header (Total Sessions, Cumulative Reps)
  └── History Sessions List/Table (Date, Exercise Name, Reps, Time, Score)
Data: Fetches GET /api/history.
```

---

## 9. Backend Invariants (Must NOT Be Modified)

When building the new frontend, the following backend interfaces **must remain unchanged**:

1. **REST Paths**: `/api/categories`, `/api/exercises/{name}`, `/api/history`, `/api/summary`.
2. **WebSocket Path**: `/ws/workout`.
3. **WebSocket Action Payload Format**:
   - `{"action": "select_exercise", "exercise": "<name>"}`
   - `{"action": "start_active_tracking"}`
   - `{"action": "reset"}`
4. **WebSocket Inference Payload Keys**: `type`, `keypoints`, `alignment`, `tracking`.
5. **Frame Format**: Binary JPEG image buffer over WebSocket.
