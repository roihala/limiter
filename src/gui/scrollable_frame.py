import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, title=None, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="center")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        if title:
            ttk.Label(self, text=title).grid(column=0, row=0, sticky='N')
            self.canvas.grid(column=0, row=0, sticky='NWSE', pady=20)
            scrollbar.grid(column=1, row=0, sticky='NWSE', pady=20)
        else:
            self.canvas.grid(column=0, row=0, sticky='NWSE')
            scrollbar.grid(column=1, row=0, sticky='NWSE')

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
