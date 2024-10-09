from typing import Tuple

import pymouse

from data_providers.data_provider import DataProvider


class MouseDataProvider(DataProvider):
    """Takes the mouse position as data."""

    def __init__(self):
        self.mouse = pymouse.PyMouse()

    def start(self):
        pass

    def stop(self):
        pass

    def get_vector(self) -> Tuple[float, float]:
        return self.mouse.position()
