from enum import Enum
from misc import Vector


class MouseMovementType(Enum):
    TO_POSITION = "TO_POSITION"
    BY = "BY"


class MouseMovement:
    def __init__(self, mouse_movement_type: MouseMovementType, vector: Vector):
        self.type = mouse_movement_type
        self.vector = vector
