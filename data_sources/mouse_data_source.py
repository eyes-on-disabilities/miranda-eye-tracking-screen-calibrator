from misc import Vector
from typing import Optional

import pymouse

from data_sources.data_source import DataSource


class MouseDataSource(DataSource):

    def __init__(self):
        self.mouse = pymouse.PyMouse()

    def start(self):
        pass

    def stop(self):
        pass

    def get_next_vector(self) -> Optional[Vector]:
        return self.mouse.position()
