from datetime import datetime, timedelta
from random import random
from tkinter import Canvas

from misc import Vector


class CanvasGazeButton:
    """A canvas button which triggers a function by focussing on it for a given amount of time.
    While focussing a progress bar visualizes the time till the trigger occurs."""

    def __init__(
        self,
        canvas: Canvas,
        text: str,
        func: callable,
        seconds_till_trigger: int,
        colors: dict,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
    ):
        self.canvas = canvas
        self.text = text
        self.func = func
        self.seconds_till_trigger = seconds_till_trigger
        self.colors = colors
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.tag = f"canvas_gaze_button_{int(random()*1000000)}"  # some unique tag

        self.progress_rect = None
        self.focus_start = None
        self.focus_end = None

    def delete(self):
        self.canvas.delete(self.tag)

    def reset_progress(self):
        self.focus_start = None
        self.focus_end = None
        self._redraw_progress_rect(0.0)

    def update_progress_and_trigger(self, vector: Vector):
        """Increases the progress bar. Once it is full, the button
        triggers the callback function and resets the progress bar."""
        if self.is_vector_in_button(vector):
            if self.focus_start is None:
                self.focus_start = datetime.now()
                self.focus_end = self.focus_start + timedelta(seconds=self.seconds_till_trigger)
            now = datetime.now().timestamp()
            progress = (now - self.focus_start.timestamp()) / (
                self.focus_end.timestamp() - self.focus_start.timestamp()
            )
            self._redraw_progress_rect(progress)
            if progress >= 1.0:
                self.reset_progress()
                self.func()
        elif self.focus_start is not None:
            self.reset_progress()

    def _redraw_progress_rect(self, progress: float):
        x1_progress_bar = self.x0 + int((self.x1 - self.x0) * progress)
        if x1_progress_bar < self.x0:
            x1_progress_bar = self.x0
        if x1_progress_bar > self.x1:
            x1_progress_bar = self.x1
        self.canvas.coords(self.progress_rect, self.x0, self.y0, x1_progress_bar, self.y1)

    def draw(self):
        self.delete()
        self.canvas.create_rectangle(
            self.x0,
            self.y0,
            self.x1,
            self.y1,
            fill=self.colors["button_bg"],
            outline="",
            tag=self.tag,
        )
        self.progress_rect = self.canvas.create_rectangle(
            self.x0,
            self.y0,
            self.x0,
            self.y1,
            fill=self.colors["button_bg_hover"],
            outline="",
            tag=self.tag,
        )
        self.focus_start = None
        self.focus_end = None
        self.canvas.create_text(
            self.x0 + (self.x1 - self.x0) / 2,
            self.y0 + (self.y1 - self.y0) / 2,
            text=self.text,
            font=("default", 24),
            fill=self.colors["button_text"],
            tag=self.tag,
        )

    def is_vector_in_button(self, vector: Vector) -> bool:
        return self.x0 <= vector[0] <= self.x1 and self.y0 <= vector[1] <= self.y1
