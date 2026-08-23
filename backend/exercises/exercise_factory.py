"""
Factory class to instantiate specific exercise tracking instances from registry.
"""
from typing import Dict, Any, Optional
from exercises.base_exercise import BaseExercise
from exercises.registry import EXERCISE_MAP

class ExerciseFactory:
    """
    Factory to resolve and create exercise objects dynamically.
    """
    @staticmethod
    def create_exercise(name: str, config: Dict[str, Any]) -> BaseExercise:
        """
        Instantiate exercise class mapping matching name from registry.
        """
        if name in EXERCISE_MAP:
            class_type = EXERCISE_MAP[name]
            return class_type(name, config)
        
        raise ValueError(f"Exercise '{name}' is not registered in the system registry.")
