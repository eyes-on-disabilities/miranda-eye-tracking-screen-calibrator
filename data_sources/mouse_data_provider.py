from typing import Tuple

import pymouse

from data_sources.data_source import DataSource
from typing import Optional


class MouseDataSource(DataSource):
    """Takes the mouse position coordinates as the vector."""

    def __init__(self):
        self.mouse = pymouse.PyMouse()

    def start(self):
        pass

    def stop(self):
        pass

    def get_next_vector(self) -> Optional[Tuple[float, float]]:
        return self.mouse.position()
