from tkinter import Button, Canvas, Frame, Label, PhotoImage, Tk, Toplevel
from typing import Callable

from PIL import Image, ImageTk

from guis.gui import GUI
from misc import Vector


class Dropdown:
    def __init__(self, root, initial_text=""):
        self.root = root
        self.menu_data = []
        self.icons = []
        self.selection_callback = None

        self.dropdown_button = Button(self.root, text=initial_text, compound="left", command=self.toggle_dropdown)
        self.dropdown_button.pack()

        self.dropdown_frame = Frame(self.root, borderwidth=1, relief="solid")
        self.dropdown_frame.place_forget()  # Hide initially

    def set_menu_data(self, menu_data):
        self.menu_data = menu_data
        self.icons.clear()  # Clear icons to avoid memory issues

        # Load icons for each menu item, to keep them in memory
        for entry in menu_data:
            image = Image.open(menu_data[entry]["icon"]).resize((16, 16))
            icon = ImageTk.PhotoImage(image)
            self.icons.append(icon)

    def set_current_selection(self, key):
        for i, entry in enumerate(self.menu_data):
            if key == self.menu_data[entry]["key"]:
                self.show_selection(
                    self.menu_data[entry]["key"],
                    self.menu_data[entry]["title"],
                    self.menu_data[entry]["description"],
                    self.icons[i],
                    trigger_callback=False,
                )
                break

    def on_selection_changed(self, callback):
        self.selection_callback = callback

    def show_selection(self, key, headline, description, icon, trigger_callback=True):
        self.dropdown_button.config(text=headline, image=icon)
        self.dropdown_frame.place_forget()
        if trigger_callback and self.selection_callback:
            self.selection_callback(key)

    def toggle_dropdown(self):
        if self.dropdown_frame.winfo_ismapped():  # If visible, hide it
            self.dropdown_frame.place_forget()
        else:
            # Position dropdown frame directly below the dropdown button
            self.dropdown_frame.place(
                x=self.dropdown_button.winfo_x(), y=self.dropdown_button.winfo_y() + self.dropdown_button.winfo_height()
            )
            self.dropdown_frame.lift()
            self.populate_dropdown()

    def populate_dropdown(self):
        # Clear any existing widgets
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()

        for i, entry in enumerate(self.menu_data):
            key = self.menu_data[entry]["key"]
            headline = self.menu_data[entry]["title"]
            description = self.menu_data[entry]["description"]

            item_frame = Frame(self.dropdown_frame)
            item_frame.pack(fill="x", padx=5, pady=5)

            headline_label = Label(item_frame, text=headline, image=self.icons[i], compound="left", anchor="w")
            headline_label.pack(anchor="w")

            desc_label = Label(item_frame, text=description, anchor="w", fg="grey", justify="left")
            desc_label.pack(anchor="w", padx=20)

            item_frame.bind(
                "<Button-1>",
                lambda e, key=key, hl=headline, desc=description, icon=self.icons[i]: [
                    self.show_selection(key, hl, desc, icon)
                ],
            )
            headline_label.bind(
                "<Button-1>",
                lambda e, key=key, hl=headline, desc=description, icon=self.icons[i]: [
                    self.show_selection(key, hl, desc, icon)
                ],
            )
            desc_label.bind(
                "<Button-1>",
                lambda e, key=key, hl=headline, desc=description, icon=self.icons[i]: [
                    self.show_selection(key, hl, desc, icon)
                ],
            )


class MainMenuGUI:

    def __init__(self):
        self.window = Tk()
        self.window.title("Miranda Eye Track")
        self.window.geometry("500x500")
        self.window.resizable(width=False, height=False)

        image_path = "assets/icon.ico"
        self.image = Image.open(image_path)
        self.tk_image = ImageTk.PhotoImage(self.image)
        image_label = Label(self.window, image=self.tk_image)
        image_label.pack(pady=30)

        self.data_source_dropdown = Dropdown(self.window, "data source")
        self.tracking_approach_dropdown = Dropdown(self.window, "tracking approach")

        self.data_source_has_data_label = Label(self.window)
        self.data_source_has_data_label.pack()

        self.calibration_results_label = Label(self.window)
        self.calibration_results_label.pack()

        self.calibration_button = Button(self.window, text="calibrate", command=self._start_calibration)
        self.calibration_button.pack()

        self.calibration_callback = None

    def _start_calibration(self):
        calibration_gui = CalibrationGUI(self.window)
        if self.calibration_callback is not None:
            self.calibration_callback(calibration_gui)

    def mainloop(self):
        self.window.mainloop()

    def set_data_source_options(self, options):
        self.data_source_dropdown.set_menu_data(options)

    def set_tracking_approach_options(self, options):
        self.tracking_approach_dropdown.set_menu_data(options)

    def set_has_calibration_result(self, has_result):
        self.calibration_results_label.config(text="is configured" if has_result else "is not yet configured")

    def set_current_data_source(self, data_source):
        self.data_source_dropdown.set_current_selection(data_source)

    def set_current_tracking_approach(self, tracking_approach):
        self.tracking_approach_dropdown.set_current_selection(tracking_approach)

    def set_data_source_has_data(self, data_source_has_data):
        self.data_source_has_data_label.config(
            text="data source has data" if data_source_has_data else "data source has no data."
        )

    def on_data_source_change_requested(self, func):
        self.data_source_dropdown.on_selection_changed(func)

    def on_tracking_approach_change_requested(self, func):
        self.tracking_approach_dropdown.on_selection_changed(func)

    def on_calibration_requested(self, func):
        self.calibration_callback = func

    def after(self, milliseconds: int, func: Callable = None, *args):
        self.window.after(milliseconds, func, *args)


class CalibrationGUI:

    def __init__(self, root_window):
        self.window = Toplevel(root_window)
        self.window.title("Haha")
        self.window.attributes("-fullscreen", True)

        self.window.bind("<Escape>", self._close_window)
        self.window.bind("<Control-c>", self._close_window)

        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()

        self.canvas = Canvas(
            self.window, background="darkblue", width=self.screen_width, height=self.screen_height, highlightthickness=0
        )
        self.canvas.pack()

    def _close_window(self, event):
        self.window.destroy()

    def bind(self, sequence: str, func: Callable):
        self.window.bind(sequence, func)

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
        self.window.after(milliseconds, func, *args)


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
