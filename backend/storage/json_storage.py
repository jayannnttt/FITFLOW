"""
JSON Storage driver to load and persist workout statistics.
"""
import os
import json
from typing import Dict, Any, List

class JSONStorage:
    """
    Local JSON storage driver.
    """
    def __init__(self, filepath: str = "workout_history.json"):
        self.filepath = filepath

    def load(self) -> List[Dict[str, Any]]:
        """Load history list from file."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def save(self, data: List[Dict[str, Any]]) -> None:
        """Persist history list to file."""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving to JSON storage: {e}")
