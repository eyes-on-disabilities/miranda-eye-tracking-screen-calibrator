from typing import Any, Tuple


class CalibrationInstruction:
    """An instruction on what to display when calibrating a certain vector"""

    def __init__(self, vector: Tuple[float, float] = None, text: str = None, image: str = None):
        self.vector = vector
        self.text = text
        self.image = image


class CalibrationResult:
    def __init__(self, result: Any):
        self.result = result


def has_result(data_provider: str, transformer: str) -> bool:
    pass


def load_result(data_provider: str, transformer: str) -> CalibrationResult:
    pass


def save_result(data_provider: str, transformer: str, calibration_result: CalibrationResult):
    pass
