from misc import Vector
from typing import List, Optional, Tuple

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


class DPadTrackingApproach(TrackingApproach):
    """A TrackingApproach using a d-pad.
    Look at the corners of the d-pad moves the mouse cursor.
    Looking outside the d-pad and at the center of the d-pad stops the mouse movement."""

    def get_calibration_instructions(self) -> List[CalibrationInstruction]:
        return [
            CalibrationInstruction((-1, 1), "top left", "assets/test_image.png"),
            CalibrationInstruction((1, 1), "top right", "assets/test_image.png"),
            CalibrationInstruction((1, -1), "bottom left", "assets/test_image.png"),
            CalibrationInstruction((-1, -1), "bottom right", "assets/test_image.png"),
        ]

    def calibrate(self, calibration_result: CalibrationResult):
        self.transformation_matrix = compute_perspective_transformation_matrix(
            calibration_result.vectors, [(-1, 1), (1, 1), (1, -1), (-1, -1)]
        )

    def get_next_mouse_movement(self, vector: Vector) -> Optional[MouseMovement]:
        new_vector = perspective_transform(self.transformation_matrix, vector)

        if (-1 <= new_vector[0] <= 1) and (1 >= new_vector[1] >= -1):
            if not ((-0.25 <= new_vector[0] <= 0.25) and (0.25 >= new_vector[1] >= -0.25)):
                return MouseMovement(MouseMovementType.BY, new_vector)

        return None
