from tkinter.ttk import Button, Frame, Label, Scrollbar
from tkinter import Canvas
from typing import Generic, TypeVar

from PIL import Image
from PIL.ImageTk import PhotoImage
from tkinter.constants import VERTICAL
from tkinter.constants import Y
from tkinter.constants import LEFT, RIGHT, BOTH
from guis.tkinter import COLORS


class ScrollableFrame:
    def __init__(self, widget, max_height=200):
        self.widget = widget
        self.max_height = max_height

        # Create a canvas
        self.my_canvas = Canvas(self.widget, background=COLORS["dropdown_bg"], highlightthickness=0)
        self.my_canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # Add a scrollbar to the canvas
        self.my_scrollbar = Scrollbar(self.widget, orient=VERTICAL, command=self.my_canvas.yview)

        # Configure the canvas
        self.my_canvas.configure(yscrollcommand=self.my_scrollbar.set)

        # Create another frame inside the canvas
        self.second_frame = Frame(self.my_canvas, style="Dropdown.TFrame")

        # Add that new frame to a window in the canvas
        self.window_id = self.my_canvas.create_window((0, 0), window=self.second_frame, anchor="nw")

        # Ensure `second_frame` expands to match `Canvas` width dynamically
        self.my_canvas.bind("<Configure>", lambda e: self.my_canvas.itemconfig(self.window_id, width=e.width))

    def update(self):
        # Update UI before fetching sizes
        self.my_canvas.update_idletasks()

        # Get actual height of second_frame
        second_frame_height = self.second_frame.winfo_height()

        # Determine if scrolling is needed
        if second_frame_height > self.max_height:
            self.my_canvas.configure(height=self.max_height)
            self.my_scrollbar.pack(side=RIGHT, fill=Y)  # Show scrollbar
        else:
            self.my_canvas.configure(height=second_frame_height)
            self.my_scrollbar.pack_forget()  # Hide scrollbar

        # Ensure scrolling works properly
        self.my_canvas.configure(scrollregion=self.my_canvas.bbox("all"))

        # Enable Mouse Scroll
        def on_mouse_wheel(event):
            self.my_canvas.yview_scroll(-1 * (event.delta // 120), "units")  # Windows/macOS

        def on_linux_scroll(event):
            if event.num == 4:  # Scroll up
                self.my_canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Scroll down
                self.my_canvas.yview_scroll(1, "units")

        self.my_canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows/macOS
        self.my_canvas.bind_all("<Button-4>", on_linux_scroll)   # Linux scroll up
        self.my_canvas.bind_all("<Button-5>", on_linux_scroll)   # Linux scroll down
