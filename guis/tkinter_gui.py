from tkinter import Canvas, PhotoImage, Tk
from typing import Callable, Tuple

from guis.gui import GUI


class TkinterGUI(GUI):
    """A GUI using Tkinter."""

    def close_window(self, event):
        self.root.destroy()

    def start(self):
        self.root = Tk()

        self.root.attributes("-fullscreen", True)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # highlightthickness removes the border
        self.canvas = Canvas(
            self.root, background="darkblue", width=self.screen_width, height=self.screen_height, highlightthickness=0
        )

        self.root.update()

        self.root.bind("<Escape>", self.close_window)
        self.root.bind("<Control-c>", self.close_window)

        self.canvas.pack()

    def stop(self):
        # TODO check if already destroyed.
        # When entering and then exiting the mainloop, tk is already destroyed.
        self.root.destroy()

    def bind(self, sequence: str, func: Callable):
        self.root.bind(sequence, func)

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
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="red", tag="calibration_point")

    def unset_calibration_point(self):
        self.canvas.delete("calibration_point")

    def set_gaze_point(self, vector: Tuple[float, float]):
        radius = 5
        x = vector[0]
        y = vector[1]
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="green", tag="calibration_point")

    def unset_gaze_point(self):
        self.canvas.delete("gaze_point")

    def set_image(self, path: str, vector: Tuple[float, float]):
        # needs to be stored as a variable, since otherwire it will be removed by the garbage collector.
        self.current_image = PhotoImage(file=path)
        self.canvas.create_image(vector, image=self.current_image, tag="image")

    def unset_image(self):
        self.canvas.delete("image")
        self.current_image = None

    def mainloop(self):
        self.root.mainloop()
