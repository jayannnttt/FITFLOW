#!/bin/bash
# Ensure backend directory and repository root are in Python module search path
export PYTHONPATH=backend:.:$PYTHONPATH

# Step 1: Uninstall ALL OpenCV package variants so pip's metadata and site-packages/cv2 are completely cleared
pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless 2>/dev/null || true

# Step 2: Force reinstall opencv-python-headless to guarantee site-packages/cv2 is fully extracted
pip install --force-reinstall --no-deps opencv-python-headless==4.9.0.80

# Step 3: Explicit startup verification
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
