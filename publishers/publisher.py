from abc import ABC, abstractmethod
from misc import Vector


class Publisher(ABC):
    """Publishes a vector to any kind of output method.
    This method could be a simple `print` to the CLI
    or pushing the vector to a message queue."""

    @abstractmethod
    def start(self):
        """Starts the Publisher."""
        pass

    @abstractmethod
    def stop(self):
        """Stops the Publisher."""
        pass

    @abstractmethod
    def push(self, vector: Vector):
        """pushes the vector to the output method."""
        pass
