"""
Standard Keypoint dataclass format.
"""
from dataclasses import dataclass

@dataclass
class Keypoint:
    name: str
    x: float          # Normalized or pixel coordinate
    y: float          # Normalized or pixel coordinate
    confidence: float
