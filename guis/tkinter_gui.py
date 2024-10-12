from tkinter import Canvas, Tk
from typing import Callable

from guis.gui import GUI
from typing import Tuple


class TkinterGUI(GUI):
    """A GUI using Tkinter."""

    tk: Tk
    canvas: Canvas

    def close_window(self, event):
        self.tk.destroy()

    def start(self):
        self.tk = Tk()

        self.tk.attributes("-fullscreen", True)
        self.screen_width = self.tk.winfo_screenwidth()
        self.screen_height = self.tk.winfo_screenheight()

        # highlightthickness removes the border
        self.canvas = Canvas(
            self.tk, background="darkblue", width=self.screen_width, height=self.screen_height, highlightthickness=0
        )
        self.canvas.pack()

        self.tk.update()

        self.tk.bind("<Escape>", self.close_window)
        self.tk.bind("<Control-c>", self.close_window)

    def stop(self):
        # TODO check if already destroyed.
        # When entering and then exiting the mainloop, tk is already destroyed.
        self.tk.destroy()

    def bind(self, sequence: str, func: Callable):
        self.tk.bind(sequence, func)

    def set_main_text(self, text: str):
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
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2 + 100,
            text=text,
            font=("default", 18),
            tags="debug_text",
        )

    def unset_debug_text(self):
        self.canvas.delete("debug_text")

    def set_calibration_point(self, vector: Tuple[float, float]):
        radius = 5
        x = vector[0]
        y = vector[1]
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius, fill="red", tag="calibration_point"
        )

    def unset_calibration_point(self):
        self.canvas.delete("calibration_point")

    def set_gaze_point(self, vector: Tuple[float, float]):
        radius = 5
        x = vector[0]
        y = vector[1]
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius, fill="green", tag="calibration_point"
        )

    def unset_gaze_point(self):
        self.canvas.delete("gaze_point")

    def mainloop(self):
        self.tk.mainloop()
