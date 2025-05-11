from publishers.publisher import Publisher
from misc import Vector
import pyautogui
from datetime import datetime, timedelta


class MouseScrollPublisher(Publisher):
    """Triggers events based on screen region instead of moving the mouse."""

    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.current_area = None
        self.area_entered_at = None
        self.delay_before_event = timedelta(milliseconds=300)
        self.last_triggered_area = None
        self.active = True

    def start(self):
        pyautogui.FAILSAFE = False

    def stop(self):
        pyautogui.FAILSAFE = True
        self.current_area = None
        self.area_entered_at = None
        self.last_triggered_area = None
        self.active = True

    def get_area(self, vector: Vector):
        x, y = vector
        margin_x = self.screen_width // 5
        margin_y = self.screen_height // 5

        if x < margin_x:
            return 'left'
        elif x > self.screen_width - margin_x:
            return 'right'
        elif y < margin_y:
            return 'up'
        elif y > self.screen_height - margin_y:
            return 'down'
        else:
            return 'center'

    def trigger_event(self, area):
        if area == 'left':
            self.active = not self.active
            print(f"Toggled active to {self.active}")
        elif not self.active:
            return
        elif area == 'up':
            pyautogui.scroll(1)
        elif area == 'down':
            pyautogui.scroll(-1)

    def push(self, vector: Vector):
        area = self.get_area(vector)

        if area != self.current_area:
            self.current_area = area
            self.area_entered_at = datetime.now()
        else:
            if self.area_entered_at and datetime.now() - self.area_entered_at >= self.delay_before_event:
                if area != self.last_triggered_area:
                    self.trigger_event(area)
                    self.last_triggered_area = area
