from abc import ABC, abstractmethod
from typing import List, Tuple

from transformers.calibration import CalibrationInstruction, CalibrationResult


class Transformer(ABC):
    """Transforms a given vector onto (or more according to) the `target rectangle`,
    which is a 1x1 rectangle. The vector could represent the user's gaze, and the
    target rectangle could represent something that the user can look onto, like a
    screen, a HUD, or a keyboard. With the screen example, if the transformed vector
    ends up inside the target rectangle, we know that the user looks at the screen.
    And if the transformed vector is outside of the rectangle, the user doesn't look
    at the screen.

    Before the Transformer can be used it needs to be calibrated. For guidance, a
    list of CalibrationInstructions can be provided.
    """

    target_rectangle = [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0]]

    @abstractmethod
    def get_calibration_instructions(self) -> List[CalibrationInstruction]:
        """Gives a list of CalibrationInstructions for guidance"""
        pass

    @abstractmethod
    def calibrate(self, calibration_result: CalibrationResult):
        """Calibrates the Transformer. For example, using the calibration points,
        a transformation matrix will be created."""
        pass

    @abstractmethod
    def transform(self, x: float, y: float) -> Tuple[float, float]:
        """transforms a vector into another. Requires the Transformer to be calibrated."""
        pass
