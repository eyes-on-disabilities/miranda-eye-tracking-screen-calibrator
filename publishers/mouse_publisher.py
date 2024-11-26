from publishers.publisher import Publisher
from misc import Vector
import pyautogui
from datetime import datetime, timedelta


class MousePublisher(Publisher):
    """Moves the Mouse to the given Vector.
    When the mouse is moved manually this publisher pauses for some time."""

    def __init__(self):
        self.manually_moved_to = None
        self.pause_publishing_until = None
        self.pause_time_in_seconds = 1

        self.last_moved_to = None

    def start(self):
        # Since in our case touching the corners is expected, we deactivate pyautogui's failsafe.
        # see https://pyautogui.readthedocs.io/en/latest/#fail-safes
        pyautogui.FAILSAFE = False

    def stop(self):
        pyautogui.FAILSAFE = True
        self.manually_moved_to = None
        self.pause_publishing_until = None
        self.last_moved_to = None

    def push(self, vector: Vector):
        mouse_position = pyautogui.position()
        if self.last_moved_to is not None and self.last_moved_to != mouse_position:
            self.manually_moved_to = mouse_position
            self.last_moved_to = mouse_position
            self.pause_publishing_until = datetime.now() + timedelta(seconds=self.pause_time_in_seconds)
        elif self.pause_publishing_until:
            if self.pause_publishing_until < datetime.now():
                self.manually_moved_to = None
                self.pause_publishing_until = None
                pyautogui.moveTo(*vector, _pause=False)
                self.last_moved_to = pyautogui.position()
        else:
            pyautogui.moveTo(*vector, _pause=False)
            self.last_moved_to = pyautogui.position()
