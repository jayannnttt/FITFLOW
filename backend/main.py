"""
AI Fitness Coach: Main Application Entry Point.
Launches the FastAPI server and opens the commercial Web UI in the default browser.
"""
import sys
import webbrowser
import uvicorn
from config import AppConfig

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    config = AppConfig()
    host = getattr(config, "server_host", "127.0.0.1")
    port = getattr(config, "server_port", 8000)

    url = f"http://{host}:{port}"
    print("\n=======================================================")
    print("AI Fitness Coach Web Application Launching")
    print(f"URL: {url}")
    print(f"Camera & MediaPipe will initialize on demand when starting a workout.")
    print(f"=======================================================\n")

    # Automatically open browser
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")

    # Run FastAPI uvicorn server
    uvicorn.run("server:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
