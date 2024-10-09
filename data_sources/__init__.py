from data_sources.data_source import DataSource
from data_sources.mouse_data_source import MouseDataSource

data_sources = {
    "mouse": MouseDataSource,
}


def has(key: str) -> bool:
    return key in data_sources.keys()


def get(key: str) -> DataSource:
    return data_sources[key]
