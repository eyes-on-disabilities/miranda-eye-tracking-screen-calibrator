from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple

from transformers.calibration import CalibrationInstruction, CalibrationResult


class TransformerType(Enum):
    CONTROLLER = "CONTROLLER"
    DIRECT = "DIRECT"


class Transformer(ABC):

    @abstractmethod
    def get_calibration_instructions(self) -> List[CalibrationInstruction]:
        pass

    @abstractmethod
    def calibrate(self, calibration_result: CalibrationResult):
        pass

    @abstractmethod
    def transform(self, x: float, y: float) -> Tuple[float, float]:
        pass

    def get_type() -> TransformerType:
        pass
