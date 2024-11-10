import platform
import tkinter
from tkinter import Canvas, Tk, Toplevel
from tkinter.ttk import Button, Frame, Label, Style
from typing import Callable

import screeninfo
from PIL import Image
from PIL.ImageTk import PhotoImage

from guis.tkinter.tkinter_canvas_gaze_button import CanvasGazeButton
from guis.tkinter.tkinter_dropdown import Dropdown, DropdownOption
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

    root.config(bg=COLORS["bg"])
    style.configure("TFrame", background=COLORS["bg"])
    style.configure(
        "TButton", background=COLORS["button_bg"], foreground=COLORS["button_text"], borderwidth=0, padding=15
    )
    style.map("TButton", background=[("active", COLORS["button_bg_hover"])])
    style.configure("TLabel", background=COLORS["label_bg"], foreground=COLORS["label_text"])
    style.configure("Dropdown.TFrame", bordercolor=COLORS["bg"], background=COLORS["dropdown_bg"])
    style.configure("DropdownItem.TFrame", background=COLORS["dropdown_item_bg"])
    style.map("DropdownItem.TFrame", background=[("hover", COLORS["dropdown_item_bg_hover"])])
    style.configure("DropdownItem.TLabel", background=COLORS["dropdown_item_bg"])
    style.map("DropdownItem.TLabel", background=[("hover", COLORS["dropdown_item_bg_hover"])])
    style.configure("Special.TFrame", background=COLORS["dropdown_item_bg"])


MainMenuOption = DropdownOption


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
            icon_photo = PhotoImage(icon_image)
            self.window.iconphoto(False, icon_photo)

        image = Image.open("assets/icon.png").resize((64, 64))
        self.tk_image = PhotoImage(image)  # 'self' to keep it in memory
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

    def set_data_source_options(self, options: dict[MainMenuOption]):
        self.data_source_dropdown.set_menu_options(options)

    def set_current_data_source(self, data_source):
        self.data_source_dropdown.set_current_selection(data_source)

    def on_data_source_change_requested(self, func):
        self.data_source_dropdown.on_selection_changed(func)

    # tracking approaches

    def set_tracking_approach_options(self, options):
        self.tracking_approach_dropdown.set_menu_options(options)

    def set_current_tracking_approach(self, tracking_approach):
        self.tracking_approach_dropdown.set_current_selection(tracking_approach)

    def on_tracking_approach_change_requested(self, func):
        self.tracking_approach_dropdown.on_selection_changed(func)

    # publishers

    def set_publisher_options(self, options):
        self.publisher_dropdown.set_menu_options(options)

    def set_current_publisher(self, publisher):
        self.publisher_dropdown.set_current_selection(publisher)

    def on_publisher_change_requested(self, func):
        self.publisher_dropdown.on_selection_changed(func)

    # the rest

    def set_has_calibration_result(self, has_result):
        self.calibration_results_label.config(text="✅︎ calibrated" if has_result else "❌ not yet calibrated.")

    def set_data_source_has_data(self, data_source_has_data):
        self.data_source_has_data_label.config(
            text="✅︎ receive data from data source." if data_source_has_data else "❌ receive no data from data source."
        )

    def mainloop(self):
        self.window.mainloop()

    def on_calibration_requested(self, func):
        self.calibration_callback = func

    def after(self, milliseconds: int, func: Callable = None, *args):
        self.window.after(milliseconds, func, *args)

    def _start_calibration(self):
        calibration_gui = CalibrationGUI(self.window)
        if self.calibration_callback is not None:
            self.calibration_callback(calibration_gui)


class CalibrationGUIButton:

    def __init__(self, text: str, func: callable, sequence: str = None):
        self.text = text
        self.func = func
        self.sequence = sequence


class CalibrationGUI:

    def __init__(self, root_window):
        self.window = Toplevel(root_window)
        self.window.title("Miranda Eye Track")

        os_name = platform.system()
        if os_name == "Windows":
            self.window.iconbitmap("assets/icon.ico")
        elif os_name in ("Linux", "Darwin"):  # Darwin is for macOS
            icon_image = Image.open("assets/icon.png")
            icon_photo = PhotoImage(icon_image)
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
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas_buttons: list[CanvasGazeButton] = []
        self.seconds_till_button_trigger = 3

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
            button = CanvasGazeButton(
                self.canvas,
                button.text,
                button.func,
                self.seconds_till_button_trigger,
                COLORS,
                x0 + margin,
                y0 + margin,
                x1 - margin,
                y1 - margin,
            )
            self.bind(button.sequence, lambda _, f=button.func: f())
            self.canvas_buttons.append(button)
            button.draw()
