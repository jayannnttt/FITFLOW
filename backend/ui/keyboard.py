"""
Keyboard input key handler mapping keys to actions.
"""
from typing import Optional, Tuple
import cv2

class KeyboardHandler:
    """
    Parses pressed keys to UI menu triggers.
    """
    @staticmethod
    def get_key() -> Tuple[int, Optional[str]]:
        """
        Poll key and return code and string character representations.
        """
        key = cv2.waitKey(10) & 0xFF
        if key == 255:
            return key, None
        try:
            return key, chr(key)
        except ValueError:
            return key, None
