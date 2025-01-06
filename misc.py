import os
import sys

import numpy as np

Vector = tuple[float, float]


def resource_path(relative_path):
    """Get the absolute path to a resource (works for PyInstaller dir and dev modes)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")  # Development mode
    return os.path.join(base_path, relative_path)


def rotate_yaw_pitch_roll(yaw, pitch, roll):
    yaw = yaw * np.pi / 180.0
    pitch = pitch * np.pi / 180.0
    roll = roll * np.pi / 180.0

    Rr = np.matrix(
        [
            [1.0, 0.0, 0.0],
            [0.0, np.cos(roll), -np.sin(roll)],
            [0.0, np.sin(roll), np.cos(roll)],
        ]
    )
    Rp = np.matrix(
        [
            [np.cos(pitch), 0.0, np.sin(pitch)],
            [0.0, 1.0, 0.0],
            [-np.sin(pitch), 0.0, np.cos(pitch)],
        ]
    )
    Ry = np.matrix(
        [
            [np.cos(yaw), -np.sin(yaw), 0.0],
            [np.sin(yaw), np.cos(yaw), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )

    return Rr * Rp * Ry
