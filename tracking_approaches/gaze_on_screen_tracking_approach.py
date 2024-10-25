from misc import Vector
from typing import List, Optional

import numpy as np

from calibration import CalibrationInstruction, CalibrationResult
from mouse_movement import MouseMovement, MouseMovementType
from tracking_approaches.tracking_approach import TrackingApproach


def compute_perspective_transformation_matrix(src_matrix, dst_matrix):
    A = []
    for i in range(4):
        x, y = src_matrix[i][0], src_matrix[i][1]
        u, v = dst_matrix[i][0], dst_matrix[i][1]
        A.append([-x, -y, -1, 0, 0, 0, x * u, y * u, u])
        A.append([0, 0, 0, -x, -y, -1, x * v, y * v, v])
    A = np.array(A)

    U, S, Vt = np.linalg.svd(A)
    H = Vt[-1].reshape(3, 3)

    return H / H[-1, -1]


def perspective_transform(transformation_matrix, vector):
    vector_homogeneous = np.array([vector[0], vector[1], 1])
    transformed_vector_homogeneous = np.dot(transformation_matrix, vector_homogeneous)
    transformed_vector = transformed_vector_homogeneous[:2] / transformed_vector_homogeneous[2]
    return transformed_vector


class GazeOnScreenTrackingApproach(TrackingApproach):
    """The most classical TrackingApproach:
    Directly translate the user's gaze onto the screen."""

    def get_calibration_instructions(self) -> List[CalibrationInstruction]:
        return [
            CalibrationInstruction((-1, 1), "top left", "assets/test_image.png"),
            CalibrationInstruction((1, 1), "top right", "assets/test_image.png"),
            CalibrationInstruction((1, -1), "bottom left", "assets/test_image.png"),
            CalibrationInstruction((-1, -1), "bottom right", "assets/test_image.png"),
        ]

    def calibrate(self, calibration_result: CalibrationResult):
        self.transformation_matrix = compute_perspective_transformation_matrix(
            calibration_result.vectors, [instruction.vector for instruction in self.get_calibration_instructions()]
        )

    def get_next_mouse_movement(self, vector: Vector) -> Optional[MouseMovement]:
        new_vector = perspective_transform(self.transformation_matrix, vector)
        return MouseMovement(MouseMovementType.TO_POSITION, new_vector)
