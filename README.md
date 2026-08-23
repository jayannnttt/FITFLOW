# AI Fitness Coach — Full-Stack Application

An intelligent, real-time computer vision workout assistant. Decouples Python FastAPI computer vision (MediaPipe 33-landmark estimation, posture alignment, joint angle telemetry, rep counting) from a high-performance React + Vite + Tailwind CSS v4 web interface.

---

## 📁 Repository Architecture

```text
AI-Fitness-Coach/
├── backend/                         # Python FastAPI AI & Computer Vision Backend
│   ├── analytics/                   # Form scoring, depth, & smoothness engines
│   ├── camera/                      # Camera utilities
│   ├── configs/                     # Exercise JSON parameters & thresholds
│   ├── exercises/                   # Exercise state machine classes
│   ├── pose/                        # MediaPipe detector & angle calculation engine
│   ├── storage/                     # JSON & session storage drivers
│   ├── tracking/                    # Posture alignment evaluation engine
│   ├── utils/                       # Enums & helper utilities
│   ├── workout_logging/             # CSV logging implementations
│   ├── config.py                    # AppConfig system configuration
│   ├── main.py                      # Main backend entry point
│   ├── server.py                    # FastAPI server & WebSocket inference endpoint
│   └── requirements.txt             # Python backend dependencies
├── frontend/                        # React 19 + Vite 8 + Tailwind CSS v4 Frontend
│   ├── public/                      # Static web assets
│   ├── src/                         # Source React application
│   │   ├── components/              # Reusable UI components
│   │   ├── hooks/                   # Custom hooks (Camera & WebSocket stream)
│   │   ├── screens/                 # View screens (Home, Library, Calibration, Workout, Summary, History)
│   │   ├── services/                # REST API client
│   │   ├── types/                   # TypeScript interfaces
│   │   ├── App.tsx                  # Application root & persistent session manager
│   │   └── main.tsx                 # React entrypoint
│   ├── index.html                   # HTML template shell
│   ├── package.json                 # Frontend dependencies & scripts
│   ├── tsconfig.json                # TypeScript configuration
│   └── vite.config.ts               # Vite build configuration (outDir: dist)
├── docs/                            # Documentation & Specifications
│   ├── API_DOCUMENTATION.md          # Backend API & WebSocket Specification
│   ├── FRONTEND_DESIGN_SPEC.md       # Frontend UI/UX Design System Specification
│   ├── FRONTEND_SPEC.md              # Figma Make Specification
│   └── openapi.yaml                 # OpenAPI 3.0 API Schema
├── .env.example                     # Environment template (no secrets)
├── .gitignore                       # Git exclusion rules
└── README.md                        # Root documentation & quickstart guide
```

---

## 🚀 Quickstart Guide

### 1. Run Backend Server (Python FastAPI)

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```
- **Backend Base URL**: `http://127.0.0.1:8000`
- **WebSocket Endpoint**: `ws://127.0.0.1:8000/ws/workout`

---

### 2. Run Frontend Development Server (React Vite)

```bash
cd frontend
pnpm install
pnpm dev
```
- **Frontend Dev URL**: `http://localhost:5173`

---

### 3. Build Frontend for Independent Production Deployment

```bash
cd frontend
pnpm run build
```
- Compiles production static assets directly to `frontend/dist/`.

---

## 🛰️ API & WebSocket Contracts

### REST Endpoints
- `GET /api/categories`: Returns categories and exercise hierarchy.
- `GET /api/exercises/{name}`: Returns detailed exercise parameters, keypoints, and alignment thresholds.
- `GET /api/history`: Returns recorded workout history session entries.
- `GET /api/summary`: Returns current/latest session summary metrics.

### WebSocket Interface (`/ws/workout`)
- **JSON Client Commands**:
  - `{"action": "select_exercise", "exercise": "<name>"}`
  - `{"action": "start_active_tracking"}`
  - `{"action": "reset"}`
- **Binary Stream**: Client streams JPEG Blob buffers over WebSocket (~25 FPS).
- **Server Inference Response**: Returns JSON frame containing `keypoints`, `alignment` (score, ready, ghost_keypoints, coaching_messages), and `tracking` (reps, sets, form_score, warnings, joint_angles, elapsed_time).
