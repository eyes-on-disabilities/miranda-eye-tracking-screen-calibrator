from typing import Tuple

import pymouse

from data_sources.data_provider import DataSource


class MouseDataSource(DataSource):
    """Takes the mouse position coordinates as the vector."""

    def __init__(self):
        self.mouse = pymouse.PyMouse()

    def start(self):
        pass

    def stop(self):
        pass

    def get_vector(self) -> Tuple[float, float]:
        return self.mouse.position()
