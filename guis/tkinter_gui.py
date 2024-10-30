from tkinter import Canvas, PhotoImage, Tk
from typing import Callable

from guis.gui import GUI
from misc import Vector


class TkinterGUI(GUI):
    """A GUI using Tkinter."""

    def close_window(self, event):
        self.root.destroy()

    def start(self):
        self.root = Tk()

        self.root.attributes("-fullscreen", True)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.screen = (self.screen_width, self.screen_height)

        # highlightthickness removes the border
        self.canvas = Canvas(
            self.root, background="darkblue", width=self.screen_width, height=self.screen_height, highlightthickness=0
        )

        self.root.update()

        self.root.bind("<Escape>", self.close_window)
        self.root.bind("<Control-c>", self.close_window)

        self.canvas.pack()

    def bind(self, sequence: str, func: Callable):
        self.root.bind(sequence, func)

    def set_main_text(self, text: str):
        self.unset_main_text()
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text=text,
            font=("default", 24),
            tags="main_text",
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
        )

    def unset_debug_text(self):
        self.canvas.delete("debug_text")

    def set_calibration_point(self, vector: Vector, text: str = None):
        self.unset_calibration_point()
        radius = 30
        x, y = vector
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="red", tag="calibration_point")
        if text is not None:
            self.canvas.create_text(
                x,
                y,
                text=text,
                font=("default", 18),
                tags="calibration_point",
            )

    def unset_calibration_point(self):
        self.canvas.delete("calibration_point")

    def set_mouse_point(self, vector: Vector):
        self.unset_mouse_point()
        radius = 5
        x, y = vector
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="green", tag="mouse_point")

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
        self.root.after(milliseconds, func, *args)

    def mainloop(self):
        self.root.mainloop()
