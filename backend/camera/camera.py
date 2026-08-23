"""
Camera management module with thread-safe queueing, resolution controls, and FPS calculation.
"""
import cv2
import time
import threading
from queue import Queue
from typing import Optional, Tuple

class CameraManager:
    """
    Manages OpenCV video capture and processing in a separate thread.
    """
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480, target_fps: int = 30):
        self.camera_index = camera_index
        self.target_width = width
        self.target_height = height
        self.target_fps = target_fps
        self._cap: Optional[cv2.VideoCapture] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame_queue: Queue = Queue(maxsize=3)
        self._fps = 0.0
        self._frame_count = 0
        self._fps_start_time = time.time()
        self._lock = threading.Lock()

    def start(self) -> bool:
        """
        Start the background capture thread.
        """
        self._cap = cv2.VideoCapture(self.camera_index)
        if not self._cap.isOpened():
            print(f"Error: Camera index {self.camera_index} could not be opened.")
            return False

        # Set capture properties
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        return True

    def _capture_loop(self) -> None:
        """
        Internal camera capture loop.
        """
        prev_time = time.time()
        while self._running:
            if self._cap is None:
                break
            ret, frame = self._cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            # FPS calculation
            self._frame_count += 1
            now = time.time()
            elapsed = now - self._fps_start_time
            if elapsed >= 1.0:
                with self._lock:
                    self._fps = self._frame_count / elapsed
                self._frame_count = 0
                self._fps_start_time = now

            # Maintain frame queue (discard old frames)
            if self._frame_queue.full():
                try:
                    self._frame_queue.get_nowait()
                except Exception:
                    pass
            self._frame_queue.put(frame)

            # Cap frame rate if running too fast
            time_spent = time.time() - prev_time
            sleep_time = (1.0 / self.target_fps) - time_spent
            if sleep_time > 0:
                time.sleep(sleep_time)
            prev_time = time.time()

    def read(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """
        Read the latest frame from the frame queue.
        """
        if not self._running or self._frame_queue.empty():
            # Fallback direct read if queue is empty or thread is not running
            if self._cap and self._cap.isOpened():
                ret, frame = self._cap.read()
                return ret, frame
            return False, None
        return True, self._frame_queue.get()

    def get_fps(self) -> float:
        """
        Get the current running capture FPS.
        """
        with self._lock:
            return self._fps

    def stop(self) -> None:
        """
        Stop the camera capture and release resources.
        """
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._cap:
            self._cap.release()
            self._cap = None
        # Empty the queue
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except Exception:
                break

    def set_resolution(self, width: int, height: int) -> None:
        """
        Update camera resolution dynamically.
        """
        self.target_width = width
        self.target_height = height
        if self._cap and self._cap.isOpened():
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
