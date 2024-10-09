from typing import List, Tuple

from transformers.calibration import CalibrationInstruction, CalibrationResult
from transformers.transformer import Transformer, TransformerType


class TwoDPerspectiveTransformer(Transformer):
    """Applies a 2D perspective transformation, also called a 'homographic transformation'."""

    def get_calibration_instructions(self, screen_resolution: Tuple[int, int]) -> List[CalibrationInstruction]:
        pass

    def calibrate(self, screen_resolution: Tuple[int, int], calibration_result: CalibrationResult):
        pass

    def transform(self, x: float, y: float) -> Tuple[float, float]:
        pass

    def get_type() -> TransformerType:
        return TransformerType.DIRECT
