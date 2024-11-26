from typing import Optional

from data_sources.clients.opentrack import Opentrack
from data_sources.data_source import DataSource
from misc import Vector


class OpentrackDataSource(DataSource):

    def __init__(self):
        self.opentrack = Opentrack()

    def start(self):
        self.opentrack.start()

    def stop(self):
        self.opentrack.stop()

    def get_next_vector(self) -> Optional[Vector]:
        head = self.opentrack.get_last_data()
        return (head["yaw"], head["pitch"]) if head is not None else None
