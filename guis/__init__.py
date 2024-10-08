from guis.gui import Gui

guis = {}


def has(key: str) -> bool:
    return key in guis.keys()


def get(key: str) -> Gui:
    return guis[key]
