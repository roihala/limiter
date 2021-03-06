import logging
import os
import sys
import tkinter as tk
from tkinter import ttk

from src.gui.controller import Controller
from src.gui.screener import Screener


class Gui(tk.Tk):
    def __init__(self, loop, config, tws):
        super().__init__()
        self.tws = tws
        self.loop = loop
        self.config = config
        self.screener = None
        self.controller = None
        self.init_graphics()

    def init_graphics(self):
        self.minsize(500, 200)

        main_panel = tk.PanedWindow(orient=tk.VERTICAL)
        main_panel.pack(fill=tk.BOTH, expand=1)

        self.screener = Screener(main_panel, self.config, self.tws, self.loop)
        self.controller = Controller(main_panel, self.config, self.tws, self.loop)

        self.protocol("WM_DELETE_WINDOW", self.loop.stop)
        # root.iconbitmap(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'images', 'favicon.ico'))
        self.title("Stocker")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        frame = self.screener.frame
        main_panel.add(frame)

        frame = self.controller.frame
        main_panel.add(frame)

    def update(self, **kwargs):
        if 'screener_results' in kwargs:
            self.screener.draw_grid(screener_results=kwargs['screener_results'])
        if 'positions' in kwargs:
            self.controller.draw_positions(tickers=kwargs['positions'])

        super().update()
