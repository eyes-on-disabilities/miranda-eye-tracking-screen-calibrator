from typing import Any, Tuple, Optional


class CalibrationInstruction:
    """An instruction on what to display when calibrating.
    If a vector is given, it represents the display. Since the exact resolution is only
    known to the GUI, the vector shall just have a value range of 0.0<=x<=1.0 and 0.0>=y>=-1.0.
    E.g. (0.0,0.0) is the upper left corner of the screen, and (1.0,-1.0) is the lower right corner."""

    def __init__(self, vector: Tuple[float, float] = None, text: str = None, image: str = None):
        self.vector = vector
        self.text = text
        self.image = image


class CalibrationResult:
    def __init__(self, result: Any):
        self.result = result


def has_result(data_source: str, tracking_approach: str) -> bool:
    return False


def load_result(data_source: str, tracking_approach: str) -> Optional[CalibrationResult]:
    return None


def save_result(data_source: str, tracking_approach: str, calibration_result: CalibrationResult):
    pass
