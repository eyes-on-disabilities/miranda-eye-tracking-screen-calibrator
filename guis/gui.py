from abc import ABC, abstractmethod
from typing import Callable


class GUI(ABC):

    @abstractmethod
    def start(self):
        """Starts the GUI."""
        pass

    @abstractmethod
    def stop(self):
        """Stops the GUI."""
        pass

    @abstractmethod
    def bind(self, sequence: str, func: Callable):
        """bind a sequence, like a button press, to a function call.
        See all bindings here: `https://tcl.tk/man/tcl8.7/TkCmd/keysyms.html`
        Examples:
        bind('+', my_add_function())
        bind('<Escape>', my_close_function())
        bind('<Control-c>', my_close_function())"""
        pass

    @abstractmethod
    def set_message(self, text: str):
        """Sets a status message. Could be used for debug information."""
        pass

    @abstractmethod
    def unset_message(self):
        pass

    @abstractmethod
    def mainloop(self):
        """Keeps up the mainloop."""
        pass
