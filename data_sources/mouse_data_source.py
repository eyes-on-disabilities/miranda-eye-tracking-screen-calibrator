from misc import Vector
from typing import Optional
import pyautogui

from data_sources.data_source import DataSource


class MouseDataSource(DataSource):

    def start(self):
        pass

    def stop(self):
        pass

    def get_next_vector(self) -> Optional[Vector]:
        return pyautogui.position()
