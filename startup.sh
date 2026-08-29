#!/bin/bash
# Ensure backend directory and repository root are in Python module search path
export PYTHONPATH=backend:.:$PYTHONPATH

# Remove desktop OpenCV packages that depend on libGL.so.1 in headless Azure App Service containers
pip uninstall -y opencv-python opencv-contrib-python 2>/dev/null || true

# Ensure opencv-python-headless is installed
pip install opencv-python-headless==4.9.0.80 2>/dev/null || true

# Launch FastAPI app with Gunicorn + Uvicorn worker using explicit backend.server:app module path
gunicorn -w 2 -k uvicorn.workers.UvicornWorker backend.server:app --bind 0.0.0.0:8000
