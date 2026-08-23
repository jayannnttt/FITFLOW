# Figma Make Frontend UI Specification — AI Fitness Coach

This document is a complete, production-ready specification designed for direct copy-pasting into **Figma Make** (or AI design generation tools) to construct the complete frontend user interface. Every screen, data element, user input, component, and interaction in this specification is mapped strictly to the actual implementation and capability of the AI Fitness Coach backend service (`server.py`).

---

## 1. PRODUCT OVERVIEW

### What the Application Does
AI Fitness Coach is a real-time computer vision workout assistant. It uses a camera feed to track human posture keypoints, evaluates starting posture alignment against target joint angles, counts repetitions, calculates form accuracy scores, provides real-time coaching corrections, and logs session performance history.

### Main Purpose
To provide users with an intelligent, self-contained AI gym trainer experience that guides exercise selection, calibrates posture alignment before reps begin, tracks repetitions in real-time, displays form score telemetry, and records historical workout sessions.

### Target User
Fitness enthusiasts, athletes, home workout users, and physical therapy patients seeking automated form guidance, rep counting, and performance statistics without needing dedicated wearables or hardware sensors.

### Overall Frontend Experience
A futuristic, telemetry-driven single-page web interface (SPA) that seamlessly transitions between exercise selection, camera pose calibration, real-time camera skeleton overlays, instant form feedback notifications, and post-workout analytical summaries.

---

## 2. REQUIRED SCREENS / PAGES

### Screen 1: Dashboard / Home Screen
- **Purpose**: Main landing view welcoming the user, presenting category selection cards, displaying current workout metrics, and quick navigation.
- **What the User Sees**: Top navigation header, hero banner with start workout CTA, stat counter pills, category grid cards, and recent session preview.
- **Sections / Components**:
  - `TopNavBar`: Brand logo ("AI FITNESS COACH"), Home link, History link, connection status pill.
  - `HeroBanner`: Headline ("Ready for today's workout?"), subtitle, "Explore Exercises" CTA.
  - `StatPills`: Total categories count (`4`), total exercises count (`11`), streak counter badge.
  - `CategoryGrid`: Interactive cards for "UPPER BODY", "LOWER BODY", "CORE", "FULL BODY / CARDIO".
- **Information Displayed**: Category name, available exercise count, workout categories list.
- **User Actions**: Click category card to navigate to Exercise Selection Screen; click History link to open History Screen.
- **Loading State**: Skeleton loader pulses for Category Cards while fetching backend categories.
- **Empty State**: Fallback message ("No categories found. Check server connection.") if API returns empty object.
- **Error State**: Banner error toast ("Unable to connect to AI Fitness Coach server.") with retry button.

---

### Screen 2: Exercise Library / Selection Screen
- **Purpose**: Display all available exercises within a selected category.
- **What the User Sees**: Back button, active category header tag, and a grid of exercise cards with primary joint targets.
- **Sections / Components**:
  - `BackBar`: "← Back to Categories" button, Active Category Tag (e.g. `UPPER BODY`).
  - `SectionHeader`: "Choose an Exercise", subtitle ("Select to view posture calibration instructions").
  - `ExerciseGrid`: Cards for each exercise (e.g., Bicep Curl, Shoulder Press, Push-ups, Pull-ups, Squats, Lunges, Calf Raises, Russian Twists, Crunches, Mountain Climbers, Jumping Jacks, High Knees).
- **Information Displayed**: Exercise name, category tag, brief description ("Posture calibration & real-time rep counting").
- **User Actions**: Click an exercise card to trigger the Exercise Details & Onboarding Modal.
- **Loading State**: Grid card pulse placeholders.
- **Empty State**: "No exercises available for this category."
- **Error State**: Toast banner warning if exercise list fails to render.

---

### Screen 3: Exercise Details & Posture Onboarding Modal
- **Purpose**: Present exercise metadata, target reps, primary joint targets, and starting pose calibration instructions before starting the camera.
- **What the User Sees**: Modal dialog containing exercise title, category badge, target metrics, posture instruction checklist, and a primary "START WORKOUT & CALIBRATION" button.
- **Sections / Components**:
  - `ModalHeader`: Category badge, exercise title, primary joint target (`Primary Joint: elbow`).
  - `MetaRow`: Target reps badge (`10 REPS TARGET`), estimated cooldown (`0.8s`).
  - `InstructionsBox`: Numbered list of posture calibration rules (e.g., "Stand tall with legs extended", "Align joints with Ghost Skeleton").
  - `ModalFooter`: Close button ("✕"), Primary Action button ("▶ START WORKOUT").
- **Information Displayed**: Exercise name, primary joint, target reps, cooldown, coaching rules per joint.
- **User Actions**: Click "✕" to close modal; click "▶ START WORKOUT" to launch camera permission and transition to Calibration View.
- **Loading State**: Spinner inside modal while fetching `/api/exercises/{name}` metadata.
- **Empty State**: N/A (modal is triggered from valid card).
- **Error State**: Displays fallback exercise defaults if `/api/exercises/{name}` fetch fails.

---

### Screen 4: Posture Calibration & Alignment View (`ALIGNING` State)
- **Purpose**: Guide the user to position themselves in view of the camera and match the semi-transparent target "Ghost Skeleton" starting posture before rep tracking unlocks.
- **What the User Sees**: Full-bleed live camera stream with cyan Ghost Skeleton target overlay, real-time posture alignment ring meter (0–100%), alignment readiness badge, and live posture coaching instructions.
- **Sections / Components**:
  - `CameraContainer`: `<video>` feed + `<canvas>` skeleton overlay.
  - `AlignmentHUDCard`: "AI POSTURE ALIGNMENT" title, percentage meter (`82%`), progress bar fill.
  - `ReadinessBadge`: Pulsing status pill ("CALIBRATING" / "HOLD POSTURE" / "READY").
  - `GhostSkeletonOverlay`: Semi-transparent cyan target posture overlay rendered on canvas.
  - `CoachingBanner`: Step-by-step posture guidance text (e.g., "Straighten your left arm to start").
- **Information Displayed**: Alignment score (`alignment.score`), readiness boolean (`alignment.ready`), coaching messages (`alignment.coaching_messages`), joint alignment statuses (`alignment.joint_statuses`).
- **User Actions**: User adjusts physical body position to match Ghost Skeleton; option to click "Cancel / Exit" back to home.
- **Loading State**: Camera initialization spinner ("Requesting Camera Permission...").
- **Empty State**: Prompt ("Step into camera view") if no pose landmarks are detected.
- **Error State**: "Camera Access Denied or Unequipped" error modal with retry button.

---

### Screen 5: Live AI Workout View (`STARTED` / `DOWN` / `UP` States)
- **Purpose**: Core real-time workout tracking interface displaying live skeleton pose, rep count hero telemetry, set tracking, form score meter, joint angles, and active form warning banners.
- **What the User Sees**: Full-bleed live camera feed with color-coded live skeleton (Green = correct, Yellow = adjusting, Red = error), floating glassmorphism HUD cards, large rep counter hero display, form score dial, live joint angle badges, and control bar.
- **Sections / Components**:
  - `TopHUDBar`: Exercise title badge (`BICEP CURL`), lifecycle state pill (`STARTED`/`DOWN`/`UP`), form score dial (`88%`), joint angle card (`142°`), rep counter hero (`0`), set counter pill (`SET 1`), workout timer (`01:24`).
  - `CanvasOverlay`: Live color-coded user skeleton + floating joint angle text tags (e.g. `left_elbow: 142°`).
  - `WarningCoachingBanner`: Floating notification banner for active warnings (`⚠ Control movement: Slow down repetition tempo`).
  - `HUDControlBar`: "RESET SESSION" button, "END WORKOUT" button.
- **Information Displayed**: Rep count (`reps`), set count (`sets`), form score (`form_score`), state (`state`), joint angles map (`joint_angles`), primary joint angle (`current_angle`), warning suggestions (`warnings`), elapsed workout time (`elapsed_time`).
- **User Actions**: Perform exercise repetitions; click "RESET" to wipe rep count; click "END WORKOUT" to complete session and view Summary.
- **Loading State**: Frame buffering indicator if WebSocket stream pauses.
- **Empty State**: If user leaves camera frame, displays warning ("User Out of View").
- **Error State**: WebSocket Disconnection Modal with "Reconnect" button.

---

### Screen 6: Post-Workout Summary Screen / Modal
- **Purpose**: Celebrate completed workout session and present comprehensive performance metrics breakdown.
- **What the User Sees**: Trophy icon badge, completion banner, 4-card metric grid (Total Reps, Workout Duration, Avg Form Score, Calories Burned), and primary action buttons.
- **Sections / Components**:
  - `SummaryHeader`: Medal icon (`🏅`), "Workout Complete!", subtitle ("Great job! Here is your performance breakdown.").
  - `MetricsGrid`:
    - Card 1: Total Reps (`10`)
    - Card 2: Duration (`01:45`)
    - Card 3: Form Score (`94%`)
    - Card 4: Est. Calories Burned (`18 kcal`)
  - `SummaryFooter`: "↻ TRY AGAIN" button (restarts same exercise), "← BACK TO HOME" button.
- **Information Displayed**: `reps`, `sets`, `duration_sec`, `form_score`, `calories_burned`, `exercise`.
- **User Actions**: Click "TRY AGAIN" to re-enter calibration for same exercise; click "BACK TO HOME" to return to home screen.
- **Loading State**: Pulse animation on summary metric cards while fetching `/api/summary`.
- **Empty State**: N/A.
- **Error State**: Displays fallback session metrics if `/api/summary` endpoint call fails.

---

### Screen 7: Workout History & Performance Analytics Screen
- **Purpose**: Show recorded past workout sessions, exercise streaks, personal bests, and performance logs.
- **What the User Sees**: Screen header with total workouts stat, streak badge, personal bests summary, and a tabular list of logged workout sessions.
- **Sections / Components**:
  - `HistoryHeader`: Title ("Workout History & Performance"), subtitle ("Recorded AI coaching sessions").
  - `StatSummaryCards`: Total Sessions card, Streak Counter card (`🔥 5 Days`), Top Form Score card (`98%`).
  - `HistoryTable`: Columns for Date/Time, Exercise Name, Reps Completed, Sets, Duration (sec), Avg Form Score (%).
- **Information Displayed**: List of objects containing `date`, `exercise`, `reps`, `sets`, `elapsed_time`, `avg_score`.
- **User Actions**: Filter history by exercise name; click row to expand details; click "Back to Home".
- **Loading State**: Table row skeleton loading placeholders while fetching `/api/history`.
- **Empty State**: Graphic illustration + message ("No workout history recorded yet. Complete your first workout!").
- **Error State**: Error banner ("Failed to load workout history log.").

---

## 3. NAVIGATION

```text
               ┌───────────────────────────┐
               │    TOP NAVBAR BRAND       │
               │  [AI FITNESS COACH Logo]  │
               └─────────────┬─────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
┌───────────────────────┐         ┌───────────────────────┐
│ HOME DASHBOARD        │         │ WORKOUT HISTORY       │
│ Nav Button: "Home"    │         │ Nav Button: "History" │
└───────────┬───────────┘         └───────────────────────┘
            │ Select Category
            ▼
┌───────────────────────┐
│ EXERCISE LIBRARY      │
│ Nav: "← Categories"   │
└───────────┬───────────┘
            │ Select Exercise
            ▼
┌───────────────────────┐
│ EXERCISE DETAIL MODAL │
│ Nav: "✕ Close"        │
└───────────┬───────────┘
            │ Click "▶ START WORKOUT"
            ▼
┌───────────────────────┐
│ POSTURE CALIBRATION   │
│ (Backend: ALIGNING)   │
└───────────┬───────────┘
            │ Alignment Ready / Started
            ▼
┌───────────────────────┐
│ LIVE AI WORKOUT       │
│ Controls: RESET / END │
└───────────┬───────────┘
            │ Finish / Reps Complete
            ▼
┌───────────────────────┐
│ WORKOUT SUMMARY       │
│ Nav: Home / Try Again │
└───────────────────────┘
```

---

## 4. UI COMPONENTS LIST

1. **`TopNavBar`**: Fixed glassmorphism header containing brand logo (`⚡ AI FITNESS COACH`), navigation links (`Home`, `History`), and live WebSocket server connection status pill.
2. **`HeroBannerCard`**: Gradient highlight card featuring motivational title, category metrics, and quick start action button.
3. **`CategoryCard`**: Surface card showing category tag (`CATEGORY 01`), category title (`UPPER BODY`), and subtext (`4 AI-Guided Exercises`).
4. **`ExerciseCard`**: Grid tile displaying exercise name, category tag, target reps, and click action to open detail modal.
5. **`ModalBackdrop`**: Overlay blur container (`#00000080` + `backdrop-filter: blur(8px)`) housing popup dialogs.
6. **`ExerciseDetailModal`**: Structured popup with exercise metadata, primary joint badges, target metrics, posture instructions, and start button.
7. **`CameraViewport`**: Responsive 16:9 container displaying `<video>` webcam stream and stacked transparent `<canvas>` skeleton overlay.
8. **`AlignmentHUDCard`**: Floating progress ring card displaying AI Posture Alignment score percentage (`0-100%`) and progress bar fill.
9. **`HUDTopBar`**: Glassmorphism overlay bar containing exercise title badge, lifecycle state pill, form score gauge, joint angle indicator, rep count hero metric, set counter, and live timer.
10. **`FormScoreMeter`**: Circular radial progress arc visualizer displaying live form score (`0–100%`).
11. **`JointAngleBadge`**: Telemetry card displaying active joint degree angle (e.g. `142.0°`).
12. **`CoachingBanner`**: High-contrast warning/guidance toast displaying real-time posture suggestions (`⚠ Control movement: Slow down repetition tempo`).
13. **`ControlBar`**: Floating button row with secondary `RESET` button and primary `END WORKOUT` button.
14. **`SummaryMetricsGrid`**: 4-card metric display box showing Reps, Duration, Form Score, and Calories Burned.
15. **`HistoryDataTable`**: Data table with formatted date, exercise name pill, numerical reps badge, duration string, and form score status indicator.
16. **`StatusPill`**: Color-coded state indicator pill (`CALIBRATING` = Yellow, `ACTIVE` = Blue, `READY` = Green, `FINISHED` = Purple).

---

## 5. DATA REQUIREMENTS

Below are the exact data fields required by the frontend screens, matching the backend implementation:

### 1. Categories Data (`GET /api/categories`)
- `key` (string/id): Category key (`"1"`, `"2"`, `"3"`, `"4"`).
- `name` (string): Category name (`"UPPER BODY"`, `"LOWER BODY"`, `"CORE"`, `"FULL BODY / CARDIO"`).
- `exercises` (array of strings): Exercise names array (`["Bicep Curl", "Shoulder Press", "Push-ups", "Pull-ups"]`).

### 2. Exercise Configuration Data (`GET /api/exercises/{name}`)
- `type` (string): `"REP_BASED"` or `"TIME_BASED"`.
- `category` (string): Parent category name.
- `primary_joint` (string): Joint tracked (`"elbow"`, `"knee"`, `"hip"`, `"ankle"`).
- `keypoints` (array of strings): Landmark identifiers (`["left_shoulder", "left_elbow", "left_wrist"]`).
- `alt_keypoints` (array of strings): Secondary joint landmarks (`["right_shoulder", "right_elbow", "right_wrist"]`).
- `down_threshold` (float): Degree angle for down state (e.g. `150.0`).
- `up_threshold` (float): Degree angle for up state (e.g. `90.0`).
- `target_reps` (integer): Target repetition count (default `10`).
- `cooldown` (float): Seconds cooldown (`0.8`).
- `alignment` (object):
  - `starting_pose_angles` (object): Map of joint name -> float target angle.
  - `tolerances` (object): Map of joint name -> float tolerance degrees.
  - `coaching_rules` (object): Map of joint name -> coaching instruction string.
- `checks` (object): Form check threshold rules (`elbow_swing`, `incomplete_extension`).

### 3. Workout History Data (`GET /api/history`)
- `date` (string): Timestamp string (`"2026-08-05 00:00:17"`).
- `exercise` (string): Exercise name (`"Bicep Curl"`).
- `reps` (integer): Repetitions completed (`10`).
- `sets` (integer): Sets completed (`1`).
- `elapsed_time` (float): Workout duration in seconds (`36.8`).
- `avg_score` (float): Average form score percentage (`85.0`).

### 4. Workout Summary Data (`GET /api/summary`)
- `has_summary` (boolean): Active session summary flag (`true` / `false`).
- `exercise` (string): Active exercise name (`"Bicep Curl"`).
- `reps` (integer): Total reps completed (`10`).
- `sets` (integer): Total sets completed (`1`).
- `duration_sec` (integer): Duration in seconds (`45`).
- `form_score` (integer): Overall form score percentage (`88`).
- `calories_burned` (integer): Calculated calories burned (`7`).

### 5. Live WebSocket Frame Payload (`WS /ws/workout`)
- `type` (string): `"inference"` or `"status"`.
- `keypoints` (object): Map of landmark name -> `{"x": float, "y": float, "confidence": float}`.
- `alignment` (object):
  - `score` (float): Alignment score percentage (`82.5`).
  - `ready` (boolean): Posture readiness boolean (`true`/`false`).
  - `joint_statuses` (object): Map of joint name -> status string (`"correct"`, `"adjusting"`, `"incorrect"`).
  - `coaching_messages` (array of strings): Active coaching strings.
  - `ghost_keypoints` (object): Map of target landmark name -> `{"x": float, "y": float}`.
- `tracking` (object):
  - `exercise` (string): Exercise name (`"Bicep Curl"`).
  - `state` (string): Lifecycle state (`"IDLE"`, `"ALIGNING"`, `"READY"`, `"STARTED"`, `"DOWN"`, `"UP"`, `"REP_COMPLETED"`, `"FINISHED"`).
  - `reps` (integer): Rep count (`3`).
  - `sets` (integer): Set count (`0`).
  - `form_score` (integer): Live form score percentage (`85`).
  - `warnings` (array of objects): `[{"warning": string, "suggestion": string}]`.
  - `finished` (boolean): Completion status (`false`).
  - `elapsed_time` (float): Live elapsed seconds (`24.5`).
  - `joint_angles` (object): Map of joint name -> angle string (e.g. `{"left_elbow": "142°"}`).
  - `current_angle` (float): Numerical joint angle value (`142.0`).

---

## 6. USER INPUTS

| Field Name | Input Type | Required/Optional | Validation Rules | UI Placement |
| ---------- | ---------- | ----------------- | ---------------- | ------------ |
| `selectedCategoryKey` | Card Selection | Required | Must be valid category ID (`"1"`, `"2"`, `"3"`, `"4"`) | Home Screen Category Grid |
| `selectedExercise` | Card Selection | Required | Must be valid string in exercises list | Exercise Selection Grid |
| `ws_command` | Button Trigger | Required | Strings: `"select_exercise"`, `"start_active_tracking"`, `"reset"` | Modal & Workout Controls |
| `video_frame` | Camera Media Stream | Required | HTML5 MediaDevices camera access permission | Camera Viewport |

---

## 7. BACKEND CAPABILITY → FRONTEND UI MAPPING

```text
Backend Functionality → Frontend Screen → UI Component → User Action
-------------------------------------------------------------------------------------------------------------
GET /api/categories → Home Screen → CategoryGrid → User clicks category card to explore exercises
GET /api/exercises/{name} → Modal → ExerciseDetailModal → User views metadata & starting posture rules
WS "select_exercise" → Calibration Screen → CameraViewport → User initiates camera & exercise selection ACK
WS Binary JPEG Frames → Calibration Screen → AlignmentHUDCard → User positions body to match Ghost Skeleton
WS "start_active_tracking" → Live Workout → HUDTopBar → User starts workout & tracking state turns ACTIVE
WS Live Inference Stream → Live Workout → FormScoreMeter & Reps → Real-time rep counting & form evaluation
WS "reset" → Live Workout → ControlBar ("RESET") → User resets current rep & set counters to 0
GET /api/summary → Summary Modal → SummaryMetricsGrid → User views completed session metrics & calories
GET /api/history → History Screen → HistoryDataTable → User views past recorded workout history logs
```

---

## 8. ANALYTICS / VISUALIZATION

The backend provides several performance analytics calculations. Below is their frontend visual presentation:

1. **Form Score Percentage (`form_score` / `avg_score`)**:
   - *UI Representation*: Radial Ring Arc Gauge (0–100%) with dynamic color spectrum (Green >= 80%, Yellow 60–79%, Red < 60%).
2. **Repetition Counter (`reps`)**:
   - *UI Representation*: Hero Telemetry Display with oversized numerical font and subtle pulse animation on increment.
3. **Posture Alignment Score (`alignment.score`)**:
   - *UI Representation*: Horizontal Progress Fill Bar + Percentage readout pill (`82%`).
4. **Joint Degree Angles (`joint_angles` / `current_angle`)**:
   - *UI Representation*: Floating Canvas Text Badges pinned adjacent to physical joint landmarks (e.g. `142°`), plus a digital telemetry card.
5. **Workout History & Progress (`GET /api/history`)**:
   - *UI Representation*: Clean Data Table with status pills, session duration badges, and form score progress bars.
6. **Form Warnings (`warnings`)**:
   - *UI Representation*: High-contrast warning toast banner with warning label + corrective suggestion text.

---

## 9. DUMMY DATA REQUIREMENTS

Use the following realistic JSON dummy data structures to visually populate components in Figma Make:

### Dummy Categories (`GET /api/categories`)
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

### Dummy Exercise Metadata (`GET /api/exercises/Bicep%20Curl`)
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

### Dummy Live Inference Payload (`WS /ws/workout`)
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
      "left_elbow": "correct",
      "right_elbow": "correct",
      "torso": "correct"
    },
    "coaching_messages": ["Hold posture for 1 sec"],
    "ghost_keypoints": {
      "left_shoulder": {"x": 0.45, "y": 0.31},
      "left_elbow": {"x": 0.46, "y": 0.49}
    }
  },
  "tracking": {
    "exercise": "Bicep Curl",
    "state": "STARTED",
    "reps": 4,
    "sets": 0,
    "form_score": 88,
    "warnings": [
      {
        "warning": "Elbow Swing",
        "suggestion": "Keep your upper arm still against your torso"
      }
    ],
    "finished": false,
    "elapsed_time": 32.4,
    "joint_angles": {
      "left_elbow": "142°",
      "right_elbow": "145°"
    },
    "current_angle": 142.0
  }
}
```

### Dummy Workout History (`GET /api/history`)
```json
[
  {
    "date": "2026-08-22 18:30:00",
    "exercise": "Bicep Curl",
    "reps": 10,
    "sets": 1,
    "elapsed_time": 45.2,
    "avg_score": 92.0
  },
  {
    "date": "2026-08-22 18:15:00",
    "exercise": "Squats",
    "reps": 12,
    "sets": 1,
    "elapsed_time": 62.0,
    "avg_score": 86.5
  },
  {
    "date": "2026-08-21 17:40:00",
    "exercise": "Push-ups",
    "reps": 15,
    "sets": 1,
    "elapsed_time": 50.8,
    "avg_score": 89.0
  }
]
```

### Dummy Session Summary (`GET /api/summary`)
```json
{
  "has_summary": true,
  "exercise": "Bicep Curl",
  "reps": 10,
  "sets": 1,
  "duration_sec": 45,
  "form_score": 92,
  "calories_burned": 8
}
```

---

## 10. RESPONSIVE DESIGN

### 1. Desktop Screen Layout (`>= 1280px`)
- Wide 16:9 full-bleed camera container (`1280x720` canvas overlay).
- Dual telemetry panels pinned to left and right viewport edges.
- 4-column category grid on home dashboard.
- Full side-by-side data table for workout history.

### 2. Tablet Screen Layout (`768px – 1279px`)
- Scaled 16:9 camera viewport container.
- Compact HUD cards arranged along top edge.
- 2-column grid for categories and exercises.
- Scrollable horizontal data table for history.

### 3. Mobile Screen Layout (`< 768px`)
- Vertical camera aspect ratio (`4:3` or `1:1` fallback).
- Single-column card stack for categories and exercises.
- Bottom sheet drawer for exercise details and post-workout summary.
- Minimalist hero rep badge overlay + collapsible coaching banner.

---

## 11. UI/UX REQUIREMENTS

- **Visual Hierarchy**: Primary emphasis on camera skeleton canvas and rep hero counter; secondary emphasis on joint angle badges; subtle tertiary positioning for elapsed timer and set badges.
- **Color Feedback Logic**:
  - `Green (#10B981)`: Correct joint posture, completed repetitions, high form score (>80%).
  - `Yellow (#F59E0B)`: Posture alignment calibration phase, minor form adjustment needed.
  - `Red (#EF4444)`: Incorrect joint execution, form warning violation, camera/connection errors.
  - `Cyan (#06B6D4)`: Target Ghost Skeleton alignment overlay guide.
- **Accessibility**: High-contrast text labels (`#F9FAFB` on `#111827`), aria-labels on buttons, minimum 44px tap targets for touch devices.

---

## 12. FUTURE API INTEGRATION NOTES

When connecting this frontend UI to the backend server:

1. **Dashboard Categories**: Fetch `GET http://127.0.0.1:8000/api/categories` on app mount.
2. **Exercise Instructions**: Fetch `GET http://127.0.0.1:8000/api/exercises/{name}` when an exercise card is selected.
3. **Real-time Inference Engine**: Connect WebSocket `ws://127.0.0.1:8000/ws/workout`. Send JSON `select_exercise` action command, then stream binary JPEG Blob buffers from offscreen canvas at ~25 FPS. Parse incoming `"type": "inference"` payloads to re-render overlay canvas and update HUD elements.
4. **Post-Workout Summary**: Fetch `GET http://127.0.0.1:8000/api/summary` when session completes.
5. **Workout History Log**: Fetch `GET http://127.0.0.1:8000/api/history` when opening the History screen.
