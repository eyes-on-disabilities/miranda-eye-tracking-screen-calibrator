from data_providers.data_provider import DataProvider
from data_providers.mouse_data_provider import MouseDataProvider

data_providers = {
    "mouse": MouseDataProvider,
}


def has(key: str) -> bool:
    return key in data_providers.keys()


def get(key: str) -> DataProvider:
    return data_providers[key]
