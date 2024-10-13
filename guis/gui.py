from abc import ABC, abstractmethod
from typing import Callable
from typing import Tuple


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
    def set_main_text(self, text: str):
        """Sets a text prominent to the user."""
        pass

    @abstractmethod
    def unset_main_text(self):
        pass

    @abstractmethod
    def set_debug_text(self, text: str):
        """Sets a text for debugging purposes, less prominent to the user."""
        pass

    @abstractmethod
    def unset_debug_text(self):
        pass

    @abstractmethod
    def set_calibration_point(self, vector: Tuple[float, float]):
        pass

    @abstractmethod
    def unset_calibration_point():
        pass

    @abstractmethod
    def set_gaze_point(self, vector: Tuple[float, float]):
        pass

    @abstractmethod
    def unset_gaze_point():
        pass

    @abstractmethod
    def set_image(self, path: str, vector: Tuple[float, float]):
        pass

    @abstractmethod
    def unset_image():
        pass

    @abstractmethod
    def after(milliseconds: int, func: Callable = None, *args):
        """Call function with arguments once after given time."""
        pass

    @abstractmethod
    def mainloop(self):
        """Keeps up the mainloop."""
        pass
