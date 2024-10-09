from guis.gui import GUI
from guis.tkinter_gui import TkinterGUI

guis = {
    "tkinter": TkinterGUI,
}


def has(key: str) -> bool:
    return key in guis.keys()


def get(key: str) -> GUI:
    return guis[key]
