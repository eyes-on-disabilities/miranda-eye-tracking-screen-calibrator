from tkinter.ttk import Style

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
    "hyperlink": "#cc37a9",
    "hyperlink_hover": "#ff44d3",
}


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

    # dropdown
    style.configure("Dropdown.TFrame", bordercolor=COLORS["bg"], background=COLORS["dropdown_bg"])
    style.configure("DropdownItem.TFrame", background=COLORS["dropdown_item_bg"])
    style.map("DropdownItem.TFrame", background=[("hover", COLORS["dropdown_item_bg_hover"])])

    style.configure("DropdownItem.TLabel", background=COLORS["dropdown_item_bg"])
    style.map("DropdownItem.TLabel", background=[("hover", COLORS["dropdown_item_bg_hover"])])

    # hyperlink
    style.configure("Hyperlink.TLabel", foreground=COLORS["hyperlink"], cursor="hand2")
    style.map("Hyperlink.TLabel", foreground=[("hover", COLORS["hyperlink_hover"])])
