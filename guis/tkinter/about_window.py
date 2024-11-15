import platform
import tkinter
from tkinter import Toplevel
from tkinter.ttk import Frame, Label

from PIL import Image
from PIL.ImageTk import PhotoImage

import config
from guis.tkinter import COLORS
from guis.tkinter.hyperlink import Hyperlink
from misc import resource_path


class AboutWindow:

    def __init__(self, root_window):
        self.window = Toplevel(root_window)
        self.window.title("About")
        self.window.config(bg=COLORS["bg"])

        os_name = platform.system()
        if os_name == "Windows":
            self.window.iconbitmap(config.APP_ICON_WINDOWS)
        elif os_name in ("Linux", "Darwin"):  # Darwin is for macOS
            icon_image = Image.open(config.APP_ICON_LINUX)
            self.window.iconphoto(False, PhotoImage(icon_image))

        image = Image.open(resource_path("assets/icon_with_text.png"))
        resize_percent = 50
        width = int(image.width * resize_percent / 100)
        height = int(image.height * resize_percent / 100)
        image = image.resize((width, height))
        self.tk_image = PhotoImage(image)
        image_label = Label(self.window, image=self.tk_image)
        image_label.pack(pady=30, padx=30)

        Label(self.window, text=config.APP_FULL_NAME).pack()
        Label(self.window, text=config.APP_DESCRIPTION).pack()

        frame = Frame(self.window)
        frame.pack(fill=tkinter.X, padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        Label(frame, text="Website:").grid(row=0, column=0, sticky="w", padx=3, pady=3)
        Hyperlink(frame, url=config.APP_LINK_WEBSITE).grid(row=0, column=1, sticky="w", padx=3, pady=3)
        Label(frame, text="Code:").grid(row=1, column=0, sticky="w", padx=3, pady=3)
        Hyperlink(frame, url=config.APP_LINK_CODE).grid(row=1, column=1, sticky="w", padx=3, pady=3)
