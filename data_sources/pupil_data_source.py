from typing import Optional

from data_sources.clients.pupil import Pupil
from data_sources.data_source import DataSource
from misc import Vector


class PupilDataSource(DataSource):
    def __init__(self):
        self.pupil = Pupil()

    def start(self):
        self.pupil.start()

    def stop(self):
        self.pupil.stop()

    def get_next_vector(self) -> Optional[Vector]:
        last_data = self.pupil.get_last_data()["3d"]
        return (last_data["theta"], last_data["phi"]) if last_data else None
