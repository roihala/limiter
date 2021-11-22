import asyncio
import os
import tkinter as tk

from src.gui.positions import Positions
from src.gui.screener import Screener
from src.tws.tws import Tws


class AsyncTk(tk.Tk):
    def __init__(self, loop, config, tws: Tws):
        super().__init__()
        self.loop = loop
        self.config = config
        self.tws = tws
        self.screener = None
        self.controller = None
        self.init_tkinter()

        self.tasks = []
        self.tasks.append(loop.create_task(self.updater()))

    async def updater(self):
        while True:
            self.update()
            await asyncio.sleep(0.0001)

    def init_tkinter(self):
        self.minsize(500, 200)

        main_panel = tk.PanedWindow(orient=tk.VERTICAL)
        main_panel.pack(fill=tk.BOTH, expand=1)

        self.screener = Screener(main_panel, self.config, self.tws)
        self.controller = Positions(main_panel, self.config, self.tws)

        root = self
        root.iconbitmap(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'lib', 'favicon.ico'))
        root.title("Stocker")
        root.columnconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        frame = self.screener.frame
        main_panel.add(frame)

        frame = self.controller.frame
        main_panel.add(frame)
