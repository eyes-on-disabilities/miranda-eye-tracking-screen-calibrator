from publishers.publisher import Publisher
from misc import Vector
import pyautogui


class MousePublisher(Publisher):
    """Moves the Mouse to the given Vector."""

    def start(self):
        # pyautogui has a failsafe mechanism. If e.g. a bug in the program cause the mouse
        # moving uncontrollably and the mouse touches a corner of the screen, then, by default,
        # pyautogui stops taking mouse movement calls so users can take back control.
        # Since in our case touching the corners is expected, we deactivate this failsafe.
        # More info: https://pyautogui.readthedocs.io/en/latest/#fail-safes
        pyautogui.FAILSAFE = False

    def stop(self):
        pyautogui.FAILSAFE = True

    def push(self, vector: Vector):
        pyautogui.moveTo(*vector, _pause=False)
