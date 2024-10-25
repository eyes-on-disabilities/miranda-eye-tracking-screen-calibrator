from abc import ABC, abstractmethod
from misc import Vector
from typing import Optional


class DataSource(ABC):
    """Provides any kind of two-dimensional vector.
    This vector could be the coordinates of the mouse position
    or the rotation angles of an eye."""

    @abstractmethod
    def start(self):
        """Starts the DataSource."""
        pass

    @abstractmethod
    def stop(self):
        """Stops the DataSource."""
        pass

    @abstractmethod
    def get_next_vector(self, timeout_in_ms: int) -> Optional[Vector]:
        """Gets the current vector, if one is available.
        Returns None if the DataSource is not running or we hit the timeout."""
        pass
