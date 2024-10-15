from abc import ABC, abstractmethod
from typing import Callable
from typing import Tuple
from calibration import CalibrationInstruction


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
        """Sets a prominent text which could contain instructions for the user."""
        pass

    @abstractmethod
    def unset_main_text(self):
        pass

    @abstractmethod
    def set_debug_text(self, text: str):
        """Sets a text for debugging purposes, less prominent or even hidden to the user."""
        pass

    @abstractmethod
    def unset_debug_text(self):
        pass

    @abstractmethod
    def set_calibration_point(self, vector: Tuple[float, float], text: str):
        """Sets a calibration point.
        A calibration point is a point on the screen which the user shall look at.
        Additionally, a text can be displayed inside or next to the point, e.g. a countdown."""
        pass

    @abstractmethod
    def unset_calibration_point():
        pass

    @abstractmethod
    def set_mouse_point(self, vector: Tuple[float, float]):
        """Sets a mouse point.
        A mouse point is a point which represents where
        the mouse position lands according to the tracking approach."""
        pass

    @abstractmethod
    def unset_mouse_point():
        pass

    @abstractmethod
    def set_image(self, path: str):
        "Sets a prominent image which could contain instructions for the user."
        pass

    @abstractmethod
    def unset_image():
        pass

    @abstractmethod
    def set_calibration_instruction(self, calibration_instruction: CalibrationInstruction):
        """Sets a CalibrationInstruction, which is a combination of a calibration point,
        text, and an image. Overwrites whatever is currently set for these things."""
        pass

    @abstractmethod
    def unset_calibration_instruction():
        pass

    @abstractmethod
    def after(milliseconds: int, func: Callable = None, *args):
        """Call function with arguments once after given time."""
        pass

    @abstractmethod
    def mainloop(self):
        """Keeps up the mainloop. Blocks until the window is closed."""
        pass
