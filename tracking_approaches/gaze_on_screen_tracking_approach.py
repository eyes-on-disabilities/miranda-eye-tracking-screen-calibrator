from typing import List, Tuple
from calibration import CalibrationInstruction
from calibration import CalibrationResult
from typing import Optional
from mouse_movement import MouseMovement
from tracking_approaches.tracking_approach import TrackingApproach


class GazeOnScreenTrackingApproach(TrackingApproach):
    """The most classical TrackingApproach:
    Directly translate the user's gaze onto the screen."""

    def get_calibration_instructions(self) -> List[CalibrationInstruction]:
        return [
            CalibrationInstruction((0, 0), "top left", "assets/test_image.png"),
            CalibrationInstruction((1, 0), "top right", "assets/test_image.png"),
            CalibrationInstruction((1, -1), "bottom left", "assets/test_image.png"),
            CalibrationInstruction((0, -1), "bottom right", "assets/test_image.png"),
        ]

    def calibrate(self, calibration_result: CalibrationResult):
        pass

    def get_next_mouse_movement(self, vector: Tuple[float, float]) -> Optional[MouseMovement]:
        pass
