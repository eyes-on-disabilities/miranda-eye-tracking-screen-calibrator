from abc import ABC, abstractmethod
from typing import Tuple


class Publisher(ABC):

    @abstractmethod
    def push(self, vector: Tuple[float, float]):
        pass
