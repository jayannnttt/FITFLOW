#!/bin/bash
# Ensure backend directory and repository root are in Python module search path
export PYTHONPATH=backend:.:$PYTHONPATH

# Verify OpenCV installation; only reinstall if cv2 is missing or corrupted
if ! python -c "import cv2" 2>/dev/null; then
    echo "OpenCV not found or corrupted. Installing opencv-python-headless..."
    pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless 2>/dev/null || true
    pip install --no-deps opencv-python-headless==4.9.0.80
fi

# Explicit startup verification
echo "Verifying OpenCV installation..."
python -c "import cv2; print('OpenCV Version:', cv2.__version__); print('OpenCV Location:', cv2.__file__)"
VERIFY_STATUS=$?

if [ $VERIFY_STATUS -ne 0 ]; then
    echo "ERROR: OpenCV startup verification failed! cv2 could not be imported."
    exit 1
fi

echo "OpenCV verification succeeded. Starting Gunicorn..."

# Launch FastAPI app with Gunicorn + Uvicorn worker using explicit backend.server:app module path
gunicorn -w 2 -k uvicorn.workers.UvicornWorker backend.server:app --bind 0.0.0.0:8000
