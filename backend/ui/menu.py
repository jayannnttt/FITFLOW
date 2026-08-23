"""
Menu manager handling UI state transitions and selections.
"""
from typing import Dict, Any, List, Optional
from utils.enums import UIMode

class MenuSystem:
    """
    Manages current UI menu options, categories, and key mappings.
    """
    def __init__(self, config_data: Dict[str, Any]):
        self.config_data = config_data
        self.categories: Dict[str, Any] = config_data.get("categories", {})
        self.exercises_config: Dict[str, Any] = config_data.get("exercises", {})
        
        self.mode: UIMode = UIMode.CATEGORY
        self.selected_category_key: Optional[str] = None
        self.selected_category_name: Optional[str] = None
        self.selected_exercise: Optional[str] = None

    def select_category(self, key: str) -> bool:
        """Select a category from key input '1' to '4'."""
        if key in self.categories:
            self.selected_category_key = key
            self.selected_category_name = self.categories[key]["name"]
            self.mode = UIMode.EXERCISE
            return True
        return False

    def select_exercise(self, index: int) -> bool:
        """Select exercise by index inside the active category."""
        if not self.selected_category_key:
            return False

        exercises = self.categories[self.selected_category_key]["exercises"]
        if 0 <= index < len(exercises):
            self.selected_exercise = exercises[index]
            self.mode = UIMode.TRACK
            return True
        return False

    def go_back(self) -> None:
        """Go back to previous menu screen."""
        if self.mode == UIMode.EXERCISE:
            self.mode = UIMode.CATEGORY
            self.selected_category_key = None
            self.selected_category_name = None
        elif self.mode == UIMode.TRACK:
            self.mode = UIMode.EXERCISE
            self.selected_exercise = None

    def get_exercises_for_current_category(self) -> List[str]:
        """Return the list of exercise names in the active category."""
        if not self.selected_category_key:
            return []
        return self.categories[self.selected_category_key]["exercises"]
