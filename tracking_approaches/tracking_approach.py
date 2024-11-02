from abc import ABC, abstractmethod
from misc import Vector
from typing import List, Optional

from calibration import CalibrationInstruction, CalibrationResult
from mouse_movement import MouseMovement


class TrackingApproach(ABC):
    """An approach of how tracking shall be done, e.g. the user looks at the screen
    directly, or the user looks at a control board which 'steers' the mouse cursor.

    Technically speaking, the TrackingApproach takes a vector – likely from a
    DataSource – and translates it to some MouseMovement action.

    Before the TrackingApproach can be used it needs to be calibrated. For guiding
    a calibration, a list of CalibrationInstructions are provided.
    """

    @abstractmethod
    def get_calibration_instructions(self) -> List[CalibrationInstruction]:
        """Gives a list of CalibrationInstructions for guiding a calibration."""
        pass

    @abstractmethod
    def calibrate(self, calibration_result: CalibrationResult):
        """Calibrates the TrackingApproach. For example, using the calibration points,
        a transformation matrix will be created."""
        pass

    @abstractmethod
    def is_calibrated(self) -> bool:
        """Returns True if the TrackingApproach has been calibrated."""
        pass

    @abstractmethod
    def get_next_mouse_movement(self, vector: Vector) -> Optional[MouseMovement]:
        """Based on a vector, a MouseMovement might be translated. For example, when looking at
        a certain position, the mouse shall move to a certain position on the screen."""
        pass
