from typing import Optional

from data_sources.clients.orlosky import Orlosky
from data_sources.data_source import DataSource
from misc import Vector


class OrloskyDataSource(DataSource):
    def __init__(self):
        self.orlosky = Orlosky()

    def start(self):
        self.orlosky.start()

    def stop(self):
        self.orlosky.stop()

    def get_next_vector(self) -> Optional[Vector]:
        last_data = self.orlosky.get_last_data()
        return (last_data["theta"], last_data["phi"]) if last_data else None
