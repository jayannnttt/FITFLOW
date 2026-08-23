"""
Exercise Registry to register and look up exercise class types.
"""
from typing import Dict, Type
from exercises.base_exercise import BaseExercise
from exercises.bicep import BicepCurl
from exercises.shoulder_press import ShoulderPress
from exercises.pushup import Pushup
from exercises.pullup import Pullup
from exercises.squat import Squat
from exercises.lunge import Lunge
from exercises.calf_raise import CalfRaise
from exercises.russian_twist import RussianTwist
from exercises.crunch import Crunch
from exercises.mountain_climber import MountainClimber
from exercises.jumping_jack import JumpingJack
from exercises.high_knees import HighKnees

# Registry mapping name to class type
EXERCISE_MAP: Dict[str, Type[BaseExercise]] = {
    "Bicep Curl": BicepCurl,
    "Shoulder Press": ShoulderPress,
    "Push-ups": Pushup,
    "Pull-ups": Pullup,
    "Squats": Squat,
    "Lunges": Lunge,
    "Calf Raises": CalfRaise,
    "Russian Twists": RussianTwist,
    "Crunches": Crunch,
    "Mountain Climbers": MountainClimber,
    "Jumping Jacks": JumpingJack,
    "High Knees": HighKnees
}
