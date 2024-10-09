from typing import Tuple

from publishers.publisher import Publisher


class PrintPublisher(Publisher):
    """Prints a given vector, like \"vector: 13.37, 6.9\""""

    def push(self, vector: Tuple[float, float]):
        print(f"vector: {vector[0]}, {vector[1]}")
