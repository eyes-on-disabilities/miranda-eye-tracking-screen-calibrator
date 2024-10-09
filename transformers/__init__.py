from transformers.transformer import Transformer
from transformers.two_d_perspective_transformer import \
    TwoDPerspectiveTransformer

transformers = {
    "2dperspective": TwoDPerspectiveTransformer,
}


def has(key: str) -> bool:
    return key in transformers.keys()


def get(key: str) -> Transformer:
    return transformers[key]
