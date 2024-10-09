from abc import ABC, abstractmethod
from typing import Tuple


class DataProvider(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_vector(self) -> Tuple[float, float]:
        pass
