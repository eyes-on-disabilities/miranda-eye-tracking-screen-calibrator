import platform
from tkinter import Canvas, PhotoImage, Tk, Toplevel
from tkinter.ttk import Button, Frame, Label, Style
from typing import Callable

import screeninfo
from PIL import Image, ImageTk

from guis.gui import GUI
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


class Dropdown:
    def __init__(self, root, initial_text="", **pack_args):
        self.root = root
        self.menu_data = []
        self.icons = []
        self.selection_callback = None

        self.dropdown_button = Button(self.root, text=initial_text, compound="left", command=self.toggle_dropdown)
        self.dropdown_button.pack(**pack_args)

        self.dropdown_frame = Frame(self.root, borderwidth=4, relief="solid", style="Dropdown.TFrame")
        self.dropdown_frame.place_forget()  # Hide initially

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
        self.window.geometry("500x700")
        self.window.resizable(width=False, height=False)

        apply_theme(self.window)

        os_name = platform.system()
        if os_name == "Windows":
            self.window.iconbitmap("assets/icon.ico")
        elif os_name in ("Linux", "Darwin"):  # Darwin is for macOS
            icon_image = Image.open("assets/icon.png")
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.window.iconphoto(False, icon_photo)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        image = Image.open("assets/icon.png").resize((64, 64))
        self.tk_image = ImageTk.PhotoImage(image)  # 'self' to keep it in memory
        image_label = Label(self.window, image=self.tk_image, style="Image.TLabel")
        image_label.pack(pady=20)

        Label(self.window, text="data source").pack()
        self.data_source_dropdown = Dropdown(self.window, "data source", pady=3)
        Label(self.window, text="tracking approach").pack()
        self.tracking_approach_dropdown = Dropdown(self.window, "tracking approach", pady=3)
        Label(self.window, text="publisher").pack()
        self.publisher_dropdown = Dropdown(self.window, "publisher", pady=3)

        self.data_source_has_data_label = Label(self.window)
        self.data_source_has_data_label.pack()

        self.calibration_results_label = Label(self.window)
        self.calibration_results_label.pack()

        self.calibration_button = Button(self.window, text="calibrate", command=self._start_calibration)
        self.calibration_button.pack(pady=3)

        monitor = screeninfo.get_monitors()[0]
        preview_width = 300
        self.preview_scale = preview_width / monitor.width
        preview_height = self.preview_scale * monitor.height
        self.preview_canvas = Canvas(
            self.window,
            background=COLORS["canvas_bg"],
            width=preview_width,
            height=preview_height,
            highlightthickness=0,
        )
        self.preview_canvas.pack(pady=12)
        self.preview_canvas.create_text(
            preview_width // 2,
            preview_height // 2,
            text="Preview",
            font=("default", 24),
            fill=COLORS["bg"]
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
        self.calibration_results_label.config(text="is configured" if has_result else "is not yet configured")

    def set_data_source_has_data(self, data_source_has_data):
        self.data_source_has_data_label.config(
            text="data source has data" if data_source_has_data else "data source has no data."
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


class CalibrationGUI:

    def __init__(self, root_window):
        self.window = Toplevel(root_window)
        self.window.title("Haha")

        os_name = platform.system()
        if os_name == "Windows":
            self.window.iconbitmap("assets/icon.ico")
        elif os_name in ("Linux", "Darwin"):  # Darwin is for macOS
            icon_image = Image.open("assets/icon.png")
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.window.iconphoto(False, icon_photo)

        self.window.attributes("-fullscreen", True)

        self.window.bind("<Escape>", self._close_window)
        self.window.bind("<Control-c>", self._close_window)

        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()

        self.canvas = Canvas(
            self.window, background=COLORS["bg"], width=self.screen_width, height=self.screen_height, highlightthickness=0
        )
        self.canvas.pack()

        self.on_close_callback = None

    def _close_window(self, event):
        self.window.destroy()
        if self.on_close_callback is not None:
            self.on_close_callback()

    def on_close(self, func):
        self.on_close_callback = func

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
