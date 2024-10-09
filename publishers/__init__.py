from publishers.print_publisher import PrintPublisher
from publishers.publisher import Publisher

publishers = {
    "print": PrintPublisher,
}


def has(key: str) -> bool:
    return key in publishers.keys()


def get(key: str) -> Publisher:
    return publishers[key]
