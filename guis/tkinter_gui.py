import math
import platform
import tkinter
from datetime import datetime, timedelta
from random import random
from tkinter import Canvas, PhotoImage, Tk, Toplevel
from tkinter.ttk import Button, Frame, Label, Style
from typing import Callable, Optional

import screeninfo
from PIL import Image, ImageTk

from misc import Vector

COLORS = {
    "bg": "#333",
    "text": "#fff",
    "button_bg": "#555",
    "button_bg_hover": "#777",
    "button_text": "#ffffff",
    "canvas_bg": "#555",
    "label_bg": "#333",
    "label_text": "#fff",
    "dropdown_bg": "#555",
    "dropdown_item_bg": "#555",
    "dropdown_item_bg_hover": "#777",
    "dropdown_item_text": "#fff",
}


def apply_theme(root):
    style = Style()
    style.theme_use("clam")

    # background
    root.config(bg=COLORS["bg"])
    # general
    style.configure("TFrame", background=COLORS["bg"])
    style.configure(
        "TButton", background=COLORS["button_bg"], foreground=COLORS["button_text"], borderwidth=0, padding=15
    )
    style.map("TButton", background=[("active", COLORS["button_bg_hover"])])
    style.configure("TLabel", background=COLORS["label_bg"], foreground=COLORS["label_text"])
    # dropdown
    style.configure("Dropdown.TFrame", bordercolor=COLORS["bg"], background=COLORS["dropdown_bg"])
    style.configure("DropdownItem.TFrame", background=COLORS["dropdown_item_bg"])
    style.map("DropdownItem.TFrame", background=[("hover", COLORS["dropdown_item_bg_hover"])])
    style.configure("DropdownItem.TLabel", background=COLORS["dropdown_item_bg"])
    style.map("DropdownItem.TLabel", background=[("hover", COLORS["dropdown_item_bg_hover"])])
    style.configure("Special.TFrame", background=COLORS["dropdown_item_bg"])


class Dropdown:

    def find_root_widget(self):
        current = self.widget
        while current.master is not None:
            current = current.master
        return current

    def get_button_position_based_on_root_widget(self):
        x = self.dropdown_button.winfo_x()
        y = self.dropdown_button.winfo_y()
        current_widget = self.widget
        while current_widget.master is not None:
            x += current_widget.winfo_x()
            y += current_widget.winfo_y()
            current_widget = current_widget.master
        return x, y

    def __init__(self, widget, initial_text=""):
        self.initial_text = initial_text
        self.widget = widget
        self.menu_data = []
        self.icons = []
        self.selection_callback = None

        self.dropdown_button = Button(self.widget, text=initial_text, compound="left", command=self.toggle_dropdown)

        self.dropdown_frame = Frame(self.find_root_widget(), borderwidth=4, relief="solid", style="Dropdown.TFrame")
        self.close_dropdown()

    def grid(self, **grid_args):
        self.dropdown_button.grid(**grid_args)

    def set_menu_data(self, menu_data):
        self.menu_data = menu_data
        self.icons.clear()  # Clear icons to avoid memory issues

        # Load icons for each menu item, to keep them in memory
        for entry in menu_data:
            image = Image.open(menu_data[entry]["icon"]).resize((24, 24))
            icon = ImageTk.PhotoImage(image)
            self.icons.append(icon)

    def set_current_selection(self, key):
        for i, entry in enumerate(self.menu_data):
            if key == self.menu_data[entry]["key"]:
                self.select_entry(
                    self.menu_data[entry]["key"],
                    self.menu_data[entry]["title"],
                    self.menu_data[entry]["description"],
                    self.icons[i],
                    trigger_callback=False,
                )
                break

    def on_selection_changed(self, callback):
        self.selection_callback = callback

    def select_entry(self, key, headline, description, icon, trigger_callback=True):
        self.dropdown_button.config(text=headline, image=icon)
        self.dropdown_frame.place_forget()
        if trigger_callback and self.selection_callback:
            self.selection_callback(key)

    def close_dropdown(self):
        if self.dropdown_frame.winfo_ismapped():
            self.dropdown_frame.place_forget()

    def open_dropdown(self):
        # Position dropdown frame directly below the dropdown button
        dropdown_button_position = self.get_button_position_based_on_root_widget()
        self.dropdown_frame.place(
            x=dropdown_button_position[0], y=dropdown_button_position[1] + self.dropdown_button.winfo_height()
        )
        self.dropdown_frame.lift()
        self.populate_dropdown()

        # to not have a dropdown_frame go outside the window
        self.widget.update()
        right_edge_of_dropdown_frame = dropdown_button_position[0] + self.dropdown_frame.winfo_width()
        window_width = self.find_root_widget().winfo_width()
        if right_edge_of_dropdown_frame > window_width:
            self.dropdown_frame.place(x=dropdown_button_position[0] - (right_edge_of_dropdown_frame - window_width))

    def toggle_dropdown(self):
        if self.dropdown_frame.winfo_ismapped():
            self.close_dropdown()
        else:
            self.open_dropdown()

    def apply_hover_state(self, widgets):
        for w in widgets:
            w.state(["hover"])

    def remove_hover_state(self, widgets):
        for w in widgets:
            w.state(["!hover"])

    def populate_dropdown(self):
        # Clear any existing widgets
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()

        for i, entry in enumerate(self.menu_data):
            key = self.menu_data[entry]["key"]
            headline = self.menu_data[entry]["title"]
            description = self.menu_data[entry]["description"]

            item_frame = Frame(self.dropdown_frame, style="DropdownItem.TFrame")
            item_frame.pack(fill="x", padx=5, pady=5)

            headline_label = Label(
                item_frame, text=headline, image=self.icons[i], compound="left", anchor="w", style="DropdownItem.TLabel"
            )
            headline_label.pack(anchor="w")

            desc_label = Label(item_frame, text=description, anchor="w", justify="left", style="DropdownItem.TLabel")
            desc_label.pack(anchor="w")

            widges = [item_frame, headline_label, desc_label]
            for w in widges:
                w.bind("<Enter>", lambda _, ws=widges: [w.state(["hover"]) for w in ws])
                w.bind("<Leave>", lambda _, ws=widges: [w.state(["!hover"]) for w in ws])

            item_frame.bind(
                "<Button-1>",
                lambda _, key=key, hl=headline, desc=description, icon=self.icons[i]: [
                    self.select_entry(key, hl, desc, icon)
                ],
            )
            headline_label.bind(
                "<Button-1>",
                lambda _, key=key, hl=headline, desc=description, icon=self.icons[i]: [
                    self.select_entry(key, hl, desc, icon)
                ],
            )
            desc_label.bind(
                "<Button-1>",
                lambda _, key=key, hl=headline, desc=description, icon=self.icons[i]: [
                    self.select_entry(key, hl, desc, icon)
                ],
            )


class MainMenuGUI:

    def __init__(self):
        self.window = Tk()
        self.window.title("Miranda Eye Track")
        self.window.geometry("650x450")
        apply_theme(self.window)

        os_name = platform.system()
        if os_name == "Windows":
            self.window.iconbitmap("assets/icon.ico")
        elif os_name in ("Linux", "Darwin"):  # Darwin is for macOS
            icon_image = Image.open("assets/icon.png")
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.window.iconphoto(False, icon_photo)

        image = Image.open("assets/icon.png").resize((64, 64))
        self.tk_image = ImageTk.PhotoImage(image)  # 'self' to keep it in memory
        image_label = Label(self.window, image=self.tk_image, style="Image.TLabel")
        image_label.pack(pady=20)

        dropdowns_frame = Frame(self.window)
        dropdowns_frame.pack(fill=tkinter.X, padx=10, pady=10, side="top")
        dropdowns_frame.grid_columnconfigure(0, weight=1)
        dropdowns_frame.grid_columnconfigure(1, weight=1)
        dropdowns_frame.grid_columnconfigure(2, weight=1)

        Label(dropdowns_frame, text="data source").grid(row=0, column=0, sticky="w", pady=3)
        self.data_source_dropdown = Dropdown(dropdowns_frame, "data source")
        self.data_source_dropdown.grid(row=1, column=0, sticky="we", padx=3)

        Label(dropdowns_frame, text="tracking approach").grid(row=0, column=1, sticky="w", pady=3)
        self.tracking_approach_dropdown = Dropdown(dropdowns_frame, "tracking approach")
        self.tracking_approach_dropdown.grid(row=1, column=1, sticky="we", padx=3)

        Label(dropdowns_frame, text="publisher").grid(row=0, column=2, sticky="w", pady=3)
        self.publisher_dropdown = Dropdown(dropdowns_frame, "publisher")
        self.publisher_dropdown.grid(row=1, column=2, sticky="we", padx=3)

        # on window resize close dropdowns
        self.window.bind(
            "<Configure>",
            lambda e: (
                [
                    self.data_source_dropdown.close_dropdown(),
                    self.tracking_approach_dropdown.close_dropdown(),
                    self.publisher_dropdown.close_dropdown(),
                ]
                if e.widget == self.window
                else None
            ),
        )

        left_frame = Frame(self.window)
        left_frame.pack(side="left", fill=tkinter.BOTH, expand=True, padx=20, pady=20)

        right_frame = Frame(self.window)
        right_frame.pack(side="right", fill=tkinter.BOTH, expand=True, padx=20, pady=20)

        self.data_source_has_data_label = Label(left_frame)
        self.data_source_has_data_label.pack(anchor="w")

        self.calibration_results_label = Label(left_frame)
        self.calibration_results_label.pack(anchor="w")

        self.calibration_button = Button(left_frame, text="re-calibrate", command=self._start_calibration)
        self.calibration_button.pack(padx=12, pady=12)

        monitor = screeninfo.get_monitors()[0]
        preview_width = 300
        self.preview_scale = preview_width / monitor.width
        preview_height = self.preview_scale * monitor.height
        self.preview_canvas = Canvas(
            right_frame,
            background=COLORS["canvas_bg"],
            width=preview_width,
            height=preview_height,
            highlightthickness=0,
        )
        self.preview_canvas.pack(side="top", anchor="w")
        self.preview_canvas.create_text(
            preview_width // 2, preview_height // 2, text="Preview", font=("default", 24), fill=COLORS["bg"]
        )

        self.calibration_callback = None

    def set_mouse_point(self, vector: Vector):
        self.unset_mouse_point()
        if vector is not None:
            radius = 3
            x = vector[0] * self.preview_scale
            y = vector[1] * self.preview_scale
            self.preview_canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius, fill="white", tag="preview_mouse_point", outline=""
            )

    def unset_mouse_point(self):
        self.preview_canvas.delete("preview_mouse_point")

    # data sources

    def set_data_source_options(self, options):
        self.data_source_dropdown.set_menu_data(options)

    def set_current_data_source(self, data_source):
        self.data_source_dropdown.set_current_selection(data_source)

    def on_data_source_change_requested(self, func):
        self.data_source_dropdown.on_selection_changed(func)

    # tracking approaches

    def set_tracking_approach_options(self, options):
        self.tracking_approach_dropdown.set_menu_data(options)

    def set_current_tracking_approach(self, tracking_approach):
        self.tracking_approach_dropdown.set_current_selection(tracking_approach)

    def on_tracking_approach_change_requested(self, func):
        self.tracking_approach_dropdown.on_selection_changed(func)

    # publishers

    def set_publisher_options(self, options):
        self.publisher_dropdown.set_menu_data(options)

    def set_current_publisher(self, publisher):
        self.publisher_dropdown.set_current_selection(publisher)

    def on_publisher_change_requested(self, func):
        self.publisher_dropdown.on_selection_changed(func)

    # the rest

    def set_has_calibration_result(self, has_result):
        self.calibration_results_label.config(text=("✅︎ calibrated" if has_result else "❌ not yet calibrated."))

    def set_data_source_has_data(self, data_source_has_data):
        self.data_source_has_data_label.config(
            text=(
                "✅︎ receive data from data source." if data_source_has_data else "❌ receive no data from data source."
            )
        )

    def _start_calibration(self):
        calibration_gui = CalibrationGUI(self.window)
        if self.calibration_callback is not None:
            self.calibration_callback(calibration_gui)

    def mainloop(self):
        self.window.mainloop()

    def on_calibration_requested(self, func):
        self.calibration_callback = func

    def after(self, milliseconds: int, func: Callable = None, *args):
        self.window.after(milliseconds, func, *args)


class CalibrationGUIOption:

    def __init__(self, text: str, func: callable, sequence: str = None):
        self.text = text
        self.func = func
        self.sequence = sequence


class _CalibrationGUIButton:

    def __init__(
        self, canvas: Canvas, text: str, func: callable, focus_time_in_seconds: int, x0: int, y0: int, x1: int, y1: int
    ):
        self.canvas = canvas
        self.text = text
        self.func = func
        self.focus_time_in_seconds = focus_time_in_seconds
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.tag = f"calibration_gui_button_{int(random()*1000000)}"
        self.x1_progress_bar = self.x0

        self.progress_rect = None

        self.focus_start = None
        self.focus_end = None

    def delete(self):
        self.canvas.delete(self.tag)

    def update(self, vector):
        if self.is_vector_in_button(vector):
            if self.focus_start is None:
                self.focus_start = datetime.now()
                self.focus_end = self.focus_start + timedelta(seconds=self.focus_time_in_seconds)
            now = datetime.now().timestamp()
            progress = (now - self.focus_start.timestamp()) / (
                self.focus_end.timestamp() - self.focus_start.timestamp()
            )
            self.set_progress(progress)
            if progress >= 1.0:
                self.focus_start = None
                self.focus_end = None
                self.set_progress(0.0)
                self.func()
        else:
            if self.focus_start is not None:
                self.focus_start = None
                self.focus_end = None
                self.set_progress(0.0)

    def set_progress(self, progress: float):
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
            fill=COLORS["button_bg"],
            outline="",
            tag=self.tag,
        )
        self.progress_rect = self.canvas.create_rectangle(
            self.x0,
            self.y0,
            self.x0,
            self.y1,
            fill=COLORS["button_bg_hover"],
            outline="",
            tag=self.tag,
        )
        self.canvas.create_text(
            self.x0 + (self.x1 - self.x0) / 2,
            self.y0 + (self.y1 - self.y0) / 2,
            text=self.text,
            font=("default", 24),
            fill=COLORS["button_text"],
            tag=self.tag,
        )

    def is_vector_in_button(self, vector: Vector) -> bool:
        return self.x0 <= vector[0] <= self.x1 and self.y0 <= vector[1] <= self.y1


class CalibrationGUI:

    def __init__(self, root_window):
        self.window = Toplevel(root_window)
        self.window.title("Miranda Eye Track")

        os_name = platform.system()
        if os_name == "Windows":
            self.window.iconbitmap("assets/icon.ico")
        elif os_name in ("Linux", "Darwin"):  # Darwin is for macOS
            icon_image = Image.open("assets/icon.png")
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.window.iconphoto(False, icon_photo)

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
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.focus_time_in_seconds = 3
        self.buttons = []

    def on_canvas_click(self, mouse_click):
        x = mouse_click.x
        y = mouse_click.y
        for button in self.buttons:
            if button.is_vector_in_button((x, y)):
                button.func()
                break

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
        for button in self.buttons:
            button.update(vector)

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

    def unset_options(self):
        if len(self.buttons) > 0:
            for b in self.buttons:
                b.delete()
        self.buttons = []

    def set_options(self, options: list[CalibrationGUIOption]):
        self.unset_options()
        width_per_option = self.screen_width / len(options)
        height_per_option = self.screen_height / 4  # an arbitrary number

        for i, option in enumerate(options):
            x0 = i * width_per_option
            y0 = self.screen_height - height_per_option
            x1 = (i + 1) * width_per_option
            y1 = self.screen_height
            margin = 30
            button = _CalibrationGUIButton(
                self.canvas,
                option.text,
                option.func,
                self.focus_time_in_seconds,
                x0 + margin,
                y0 + margin,
                x1 - margin,
                y1 - margin,
            )
            self.bind(option.sequence, lambda _, f=option.func: f())
            self.buttons.append(button)
            button.draw()
