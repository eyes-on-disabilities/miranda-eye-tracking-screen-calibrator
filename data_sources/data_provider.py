from abc import ABC, abstractmethod
from typing import Tuple


class DataSource(ABC):
    """Provides any kind of two-dimensional vector.
    This vector could be the coordinates of the mouse position
    or the rotation angles of an eye."""

    @abstractmethod
    def start(self):
        """Start the DataSource."""
        pass

    @abstractmethod
    def stop(self):
        """Stop the DataSource."""
        pass

    @abstractmethod
    def get_vector(self) -> Tuple[float, float]:
        """Gets the current vector, if one is available.
        This method shall be called only when the DataSource is running."""
        pass
