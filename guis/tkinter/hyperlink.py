import webbrowser
from tkinter.ttk import Label


class Hyperlink(Label):
    def __init__(self, master, url, text=None, *args, **kwargs):
        self.text = text or url
        super().__init__(master, text=self.text, *args, **kwargs)
        self.url = url
        self.bind("<Button-1>", self.on_click)
        self.configure(style="Hyperlink.TLabel", cursor="hand2")

    def on_click(self, event):
        webbrowser.open(self.url)
