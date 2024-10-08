from publishers.publisher import Publisher

publishers = {}


def has(key: str) -> bool:
    return key in publishers.keys()


def get(key: str) -> Publisher:
    return publishers[key]
