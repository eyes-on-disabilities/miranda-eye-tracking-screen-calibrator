import platform
from tkinter import Canvas, Toplevel
from typing import Callable

from PIL import Image
from PIL.ImageTk import PhotoImage

import config
from guis.tkinter.canvas_gaze_button import CanvasGazeButton
from misc import Vector
from guis.tkinter import COLORS


class CalibrationGUIButton:

    def __init__(self, text: str, func: callable, sequence: str = None):
        self.text = text
        self.func = func
        self.sequence = sequence


class CalibrationGUI:

    def __init__(self, root_window):
        self.window = Toplevel(root_window)
        self.window.title(config.APP_FULL_NAME)

        os_name = platform.system()
        if os_name == "Windows":
            self.window.iconbitmap(config.APP_ICON_WINDOWS)
        elif os_name in ("Linux", "Darwin"):  # Darwin is for macOS
            icon_image = Image.open(config.APP_ICON_LINUX)
            self.window.iconphoto(False, PhotoImage(icon_image))

        self.window.attributes("-fullscreen", True)

        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()

        self.canvas = Canvas(
            self.window,
            background=COLORS["bg"],
            width=self.screen_width,
            height=self.screen_height,
            highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas_buttons: list[CanvasGazeButton] = []
        self.seconds_till_button_trigger = 3

        self.window.focus_force()

    def close_window(self):
        self.window.destroy()

    def bind(self, sequence: str, func: Callable):
        self.window.bind(sequence, func)

    def unbind(self, sequence: str):
        self.window.unbind(sequence)

    def set_main_text(self, text: str):
        self.unset_main_text()
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text=text,
            font=("default", 24),
            tags="main_text",
            fill="white",
        )

    def unset_main_text(self):
        self.canvas.delete("main_text")

    def set_debug_text(self, text: str):
        self.unset_debug_text()
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2 + 128,
            text=text,
            font=("default", 18),
            tags="debug_text",
            fill="white",
        )

    def unset_debug_text(self):
        self.canvas.delete("debug_text")

    def set_calibration_point(self, vector: Vector, text: str = None):
        self.unset_calibration_point()
        x, y = vector
        x_text, y_text = vector
        target_radius = 30
        radius = target_radius

        # adjustments of point size and text position on the edges of the screen
        if x < target_radius:
            radius = 2 * target_radius
            x_text = target_radius
        if x > self.screen_width - target_radius:
            radius = 2 * target_radius
            x_text = self.screen_width - target_radius
        if y < target_radius:
            radius = 2 * target_radius
            y_text = target_radius
        if y > self.screen_height - target_radius:
            radius = 2 * target_radius
            y_text = self.screen_height - target_radius

        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius, fill="white", tag="calibration_point", outline=""
        )

        if text is not None:
            self.canvas.create_text(
                x_text,
                y_text,
                text=text,
                font=("default", 18),
                tags="calibration_point",
            )

    def unset_calibration_point(self):
        self.canvas.delete("calibration_point")

    def set_mouse_point(self, vector: Vector):
        self.unset_mouse_point()
        self._update_buttons(vector)
        if self.window.winfo_exists():  # in case the window got closed by a button action
            radius = 5
            x, y = vector
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius, fill="white", tag="mouse_point", outline=""
            )

    def _update_buttons(self, vector: Vector):
        for button in self.canvas_buttons:
            button.update_progress_and_trigger(vector)

    def unset_mouse_point(self):
        self.canvas.delete("mouse_point")

    def set_image(self, path: str):
        self.unset_image()
        # needs to be stored as a variable, since otherwire it will be removed by the garbage collector.
        self.current_image = PhotoImage(file=path)
        self.canvas.create_image(
            (self.screen_width / 2, self.screen_height / 2 + 64), image=self.current_image, tag="image"
        )

    def unset_image(self):
        self.canvas.delete("image")
        self.current_image = None

    def after(self, milliseconds: int, func: Callable = None, *args):
        self.window.after(milliseconds, func, *args)

    def unset_buttons(self):
        if len(self.canvas_buttons) > 0:
            for b in self.canvas_buttons:
                b.delete()
        self.canvas_buttons = []

    def set_buttons(self, buttons: list[CalibrationGUIButton]):
        self.unset_buttons()
        width_per_option = self.screen_width / len(buttons)
        height_per_option = self.screen_height / 4  # an arbitrary number

        for i, button in enumerate(buttons):
            x0 = i * width_per_option
            y0 = self.screen_height - height_per_option
            x1 = (i + 1) * width_per_option
            y1 = self.screen_height
            margin = 30
            canvas_button = CanvasGazeButton(
                self.canvas,
                button.text,
                button.func,
                self.seconds_till_button_trigger,
                x0 + margin,
                y0 + margin,
                x1 - margin,
                y1 - margin,
            )
            self.bind(button.sequence, lambda _, f=button.func: f())
            self.canvas_buttons.append(canvas_button)
            canvas_button.draw()

    def _on_canvas_click(self, mouse_click):
        x = mouse_click.x
        y = mouse_click.y
        for button in self.canvas_buttons:
            if button.is_vector_in_button((x, y)):
                button.func()
                break
