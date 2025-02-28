from tkinter.ttk import Button, Frame, Label, Scrollbar
from tkinter import Canvas
from typing import Generic, TypeVar

from PIL import Image
from PIL.ImageTk import PhotoImage
from tkinter.constants import VERTICAL
from tkinter.constants import Y
from tkinter.constants import LEFT, RIGHT, BOTH
from guis.tkinter import COLORS
from guis.tkinter.scrollable_frame import ScrollableFrame


T = TypeVar("T")


class DropdownOption:
    def __init__(self, key: str, title: str, description: str, icon: str, clazz: Generic[T]):
        self.key = key
        self.title = title
        self.description = description
        self.icon = icon
        self.clazz = clazz


class Dropdown:

    def __init__(self, widget, initial_text=""):
        self.widget = widget
        self.menu_options = []
        self.icons = {}
        self.selection_callback = None
        self.icon_size = 24

        self.dropdown_button = Button(self.widget, text=initial_text, compound="left", command=self.toggle_dropdown)
        # since a Frame within a Frame can potentially overflow,
        # we want to position the dropdown frame at the root widget.
        self.dropdown_frame = Frame(self._find_root_widget(), borderwidth=4, relief="solid")
        self.close_dropdown()

    def pack(self, **pack_args):
        self.dropdown_button.pack(**pack_args)

    def grid(self, **grid_args):
        self.dropdown_button.grid(**grid_args)

    def set_menu_options(self, menu_options: dict[DropdownOption]):
        self.menu_options = menu_options
        # Load icons for each menu item, to keep them in memory
        self.icons.clear()  # Clear icons to avoid memory issues
        for key, option in menu_options.items():
            image = Image.open(option.icon).resize((self.icon_size, self.icon_size))
            self.icons[option.icon] = PhotoImage(image)

    def set_current_selection(self, selected_key):
        for key, option in self.menu_options.items():
            if selected_key == option.key:
                self._select_option(option=option, trigger_callback=False)
                break

    def on_selection_changed(self, callback: callable):
        self.selection_callback = callback

    def toggle_dropdown(self):
        if self.dropdown_frame.winfo_ismapped():
            self.close_dropdown()
        else:
            self.open_dropdown()

    def close_dropdown(self):
        if self.dropdown_frame.winfo_ismapped():
            self.dropdown_frame.place_forget()

    def open_dropdown(self):
        if self.dropdown_frame.winfo_ismapped():
            return
        # Position dropdown frame directly below the dropdown button
        dropdown_button_position = self._get_button_position_based_on_root_widget()
        self.dropdown_frame.place(
            x=dropdown_button_position[0], y=dropdown_button_position[1] + self.dropdown_button.winfo_height()
        )
        self.dropdown_frame.lift()
        self._populate_dropdown()

        # if dropdown frame overflows to the right side, move it to the left
        self.widget.update()  # to first render everything
        right_edge_of_dropdown_frame = dropdown_button_position[0] + self.dropdown_frame.winfo_width()
        root_width = self._find_root_widget().winfo_width()
        if right_edge_of_dropdown_frame > root_width:
            self.dropdown_frame.place(x=dropdown_button_position[0] - (right_edge_of_dropdown_frame - root_width))

    def _find_root_widget(self):
        current = self.widget
        while current.master is not None:
            current = current.master
        return current

    def _get_button_position_based_on_root_widget(self):
        x = self.dropdown_button.winfo_x()
        y = self.dropdown_button.winfo_y()
        current_widget = self.widget
        while current_widget.master is not None:
            x += current_widget.winfo_x()
            y += current_widget.winfo_y()
            current_widget = current_widget.master
        return x, y

    def _select_option(self, option: DropdownOption, trigger_callback=True):
        self.dropdown_button.config(text=option.title, image=self.icons[option.icon])
        self.dropdown_frame.place_forget()
        if trigger_callback and self.selection_callback:
            self.selection_callback(option.key)

    def _apply_state_to_widgets(self, state, widgets):
        for w in widgets:
            w.state([state])

    def _populate_dropdown(self):
        # Clear any existing widgets
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()

        scrollable_frame = ScrollableFrame(self.dropdown_frame)

        for key, option in self.menu_options.items():
            item_frame = Frame(
                scrollable_frame.second_frame,
                style="DropdownItem.TFrame",
            )
            item_frame.pack(fill="x", padx=5, pady=5)

            headline_label = Label(
                item_frame,
                text=option.title,
                image=self.icons[option.icon],
                compound="left",
                anchor="w",
                style="DropdownItem.TLabel",
            )
            headline_label.pack(anchor="w")

            desc_label = Label(
                item_frame,
                text=option.description,
                anchor="w",
                justify="left",
                style="DropdownItem.TLabel",
            )
            desc_label.pack(anchor="w")

            widges = [item_frame, headline_label, desc_label]
            for w in widges:
                w.bind("<Button-1>", lambda _, o=option: self._select_option(o))
                # frames and labels don't have a hover state by themselves
                w.bind("<Enter>", lambda _, w=widges: self._apply_state_to_widgets("hover", w))
                w.bind("<Leave>", lambda _, w=widges: self._apply_state_to_widgets("!hover", w))

        scrollable_frame.update()
