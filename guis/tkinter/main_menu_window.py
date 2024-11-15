import platform
import tkinter
from tkinter import Canvas, Menu, Tk
from tkinter.ttk import Button, Frame, Label, Style
from typing import Callable

import screeninfo
from PIL import Image
from PIL.ImageTk import PhotoImage

import config
from guis.tkinter import COLORS
from guis.tkinter.calibration_window import CalibrationWindow
from guis.tkinter.dropdown import Dropdown, DropdownOption
from misc import Vector, resource_path


def apply_theme(root):
    style = Style()
    style.theme_use("clam")
    # standard widgets
    root.config(bg=COLORS["bg"])
    style.configure("TFrame", background=COLORS["bg"])
    style.configure(
        "TButton",
        background=COLORS["button_bg"],
        foreground=COLORS["button_text"],
        borderwidth=0,
        padding=15,
    )
    style.map("TButton", background=[("active", COLORS["button_bg_hover"])])
    style.configure("TLabel", background=COLORS["label_bg"], foreground=COLORS["label_text"])
    # custom widgets
    style.configure("Dropdown.TFrame", bordercolor=COLORS["bg"], background=COLORS["dropdown_bg"])
    style.configure("DropdownItem.TFrame", background=COLORS["dropdown_item_bg"])
    style.map("DropdownItem.TFrame", background=[("hover", COLORS["dropdown_item_bg_hover"])])
    style.configure("DropdownItem.TLabel", background=COLORS["dropdown_item_bg"])
    style.map("DropdownItem.TLabel", background=[("hover", COLORS["dropdown_item_bg_hover"])])


MainMenuOption = DropdownOption


class MainMenuWindow:

    def __init__(self):
        self.window = Tk()
        self.window.title(config.APP_FULL_NAME)
        self.window.geometry(f"{config.MAIN_MENU_WIDTH}x{config.MAIN_MENU_HEIGHT}")
        apply_theme(self.window)

        os_name = platform.system()
        if os_name == "Windows":
            self.window.iconbitmap(config.APP_ICON_WINDOWS)
        elif os_name in ("Linux", "Darwin"):  # Darwin is for macOS
            icon_image = Image.open(config.APP_ICON_LINUX)
            self.window.iconphoto(False, PhotoImage(icon_image))

        menubar = Menu(
            self.window,
            bg=COLORS["bg"],
            fg=COLORS["text"],
            borderwidth=0,
            activebackground=COLORS["button_bg_hover"],
            activeforeground=COLORS["text"],
        )
        self.window.config(menu=menubar)
        menubar.add_command(
            label="About",
            command=self.window.destroy,
        )

        image = Image.open(resource_path("assets/icon.png")).resize((64, 64))
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
        if self.calibration_callback is not None:
            self.calibration_callback(CalibrationWindow(self.window))
