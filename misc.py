import os
import sys

Vector = tuple[float, float]


def resource_path(relative_path):
    """Get the absolute path to a resource (works for PyInstaller dir and dev modes)."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")  # Development mode
    return os.path.join(base_path, relative_path)
