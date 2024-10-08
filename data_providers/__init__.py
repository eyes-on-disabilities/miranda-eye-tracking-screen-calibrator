from data_providers.data_provider import DataProvider

data_providers = {}


def has(key: str) -> bool:
    return key in data_providers.keys()


def get(key: str) -> DataProvider:
    return data_providers[key]
