from abc import ABC, abstractmethod
from typing import Any, Tuple


class DataProvider(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_position(self) -> Tuple[float, float]:
        pass

    @abstractmethod
    def get_raw(self) -> Any:
        pass

    @abstractmethod
    def is_running(self) -> bool:
        pass

    @abstractmethod
    def has_data(self) -> bool:
        pass
