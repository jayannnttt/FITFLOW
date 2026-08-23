"""
Mathematical utility functions for pose analysis and geometry.
"""
import numpy as np
from typing import List, Tuple

def calculate_angle_2d(
    pt_a: Tuple[float, float],
    pt_b: Tuple[float, float],
    pt_c: Tuple[float, float],
    frame_width: int = 1,
    frame_height: int = 1
) -> float:
    """
    Calculate the 2D joint angle between three points (pt_a, pt_b, pt_c) with vertex pt_b.
    Points are in normalized coordinates (0.0 to 1.0) and scaled to frame dimensions.
    """
    # Scale points to pixel coordinates if frame width/height are provided
    a = np.array([pt_a[0] * frame_width, pt_a[1] * frame_height])
    b = np.array([pt_b[0] * frame_width, pt_b[1] * frame_height])
    c = np.array([pt_c[0] * frame_width, pt_c[1] * frame_height])

    ba = a - b
    bc = c - b

    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom < 1e-6:
        return 180.0

    cos_ang = np.clip(np.dot(ba, bc) / denom, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_ang)))

def calculate_angle_3d(
    pt_a: Tuple[float, float, float],
    pt_b: Tuple[float, float, float],
    pt_c: Tuple[float, float, float]
) -> float:
    """
    Calculate the 3D angle between three spatial coordinates with vertex pt_b.
    """
    a = np.array(pt_a)
    b = np.array(pt_b)
    c = np.array(pt_c)

    ba = a - b
    bc = c - b

    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom < 1e-6:
        return 180.0

    cos_ang = np.clip(np.dot(ba, bc) / denom, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_ang)))

def calculate_vector_angle_2d(
    v1: Tuple[float, float],
    v2: Tuple[float, float]
) -> float:
    """
    Calculate the angle between two 2D vectors.
    """
    vec1 = np.array(v1)
    vec2 = np.array(v2)

    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    if denom < 1e-6:
        return 0.0

    cos_ang = np.clip(np.dot(vec1, vec2) / denom, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_ang)))
