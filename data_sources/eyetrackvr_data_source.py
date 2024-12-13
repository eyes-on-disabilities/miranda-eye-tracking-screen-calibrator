from typing import Optional

from data_sources.data_source import DataSource
from misc import Vector
from data_sources.clients.eyetrackvr import EyeTrackVR


class EyeTrackVRDataSource(DataSource):
    def __init__(self):
        self.eyetrackvr = EyeTrackVR()

    def start(self):
        self.eyetrackvr.start()

    def stop(self):
        self.eyetrackvr.stop()

    def get_next_vector(self) -> Optional[Vector]:
        x, y = self.eyetrackvr.get_last_data()
        return (x, y) if x and y else None
