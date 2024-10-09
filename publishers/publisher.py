from abc import ABC, abstractmethod
from typing import Tuple


class Publisher(ABC):
    """Publishes a vector to any kind of output method.
    This method could be a simple `print` to the CLI
    or pushing the vector to a message queue."""

    @abstractmethod
    def push(self, vector: Tuple[float, float]):
        """pushes the vector to the output method."""
        pass
