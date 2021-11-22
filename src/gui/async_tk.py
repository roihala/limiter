import asyncio
import logging
import tkinter as tk


class AsyncTk(tk.Tk):
    def __init__(self, loop):
        super().__init__()
        self.tasks = []
        self.loop = loop
        self.tasks.append(loop.create_task(self.updater()))

    async def updater(self):
        while True:
            self.update()
            await asyncio.sleep(0.0001)
