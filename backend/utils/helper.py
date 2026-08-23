"""
General helper functions for configuration and project setup.
"""
import os
import json
from typing import Dict, Any

def load_exercise_configs(config_path: str) -> Dict[str, Any]:
    """
    Load exercise configurations from a JSON file.
    """
    if not os.path.exists(config_path):
        # Fallback to absolute path construction if workspace path is relative
        fallback_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "exercises.json")
        if os.path.exists(fallback_path):
            config_path = fallback_path
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        return json.load(f)
