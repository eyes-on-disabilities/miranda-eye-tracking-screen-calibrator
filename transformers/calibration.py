from typing import Any, Tuple


class CalibrationInstruction:
    def __init__(self, text: str = None, image: str = None, vector: Tuple[float, float] = None):
        self.text = text
        self.image = image
        self.vector = vector


class CalibrationResult:
    def __init__(self, result: Any):
        self.result = result


def has_result(data_provider: str, transformer: str) -> bool:
    pass


def load_result(data_provider: str, transformer: str) -> CalibrationResult:
    pass


def save_result(data_provider: str, transformer: str, calibration_result: CalibrationResult):
    pass
