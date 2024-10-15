from enum import Enum
from typing import Tuple


class MouseMovementType(Enum):
    TO_POSITION = "TO_POSITION",
    BY = "BY"


class MouseMovement():
    def __init__(self, mouse_movement_type: MouseMovementType, vector: Tuple[float, float]):
        self.type = mouse_movement_type
        self.vector = vector
