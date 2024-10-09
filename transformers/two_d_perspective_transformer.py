from typing import List, Tuple

from transformers.calibration import CalibrationInstruction
from transformers.transformer import Transformer


class TwoDPerspectiveTransformer(Transformer):
    """Applies a 2D perspective transformation, also called a 'homographic transformation'."""

    def get_calibration_instructions(self) -> List[CalibrationInstruction]:
        pass

    def calibrate(self, calibration_result: List[Tuple[float, float]]):
        pass

    def transform(self, x: float, y: float) -> Tuple[float, float]:
        pass
