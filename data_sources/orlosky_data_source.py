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
        if not last_data:
            return None

        x = last_data["x"]
        y = last_data["y"]
        z = last_data["z"]

        if z == 0:
            return None  # Avoid division by zero

        lol = (x / z, y / z)
        print(lol)
        return lol
