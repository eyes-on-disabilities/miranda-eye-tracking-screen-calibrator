from transformers.transformer import Transformer

transformers = {}


def has(key: str) -> bool:
    return key in transformers.keys()


def get(key: str) -> Transformer:
    return transformers[key]
