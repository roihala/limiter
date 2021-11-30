import asyncio
import os
from functools import partial
from tkinter import ttk

from config.schema import Schema
from src.gui.scrollable_frame import ScrollableFrame
import tws


class Screener(object):
    def __init__(self, root, config: Schema, tws_instance: tws.Tws, loop):
        self.loop = loop
        self.root = root
        self.config = config
        self.tws = tws_instance
        self.frame = self._init_frame()
        self.grid_tickers = set()

    def _init_frame(self):
        self.frame = ScrollableFrame(self.root, title='Screener')
        self.frame['relief'] = 'sunken'
        self.frame['padding'] = 5
        self.frame['borderwidth'] = 5

        self.frame.columnconfigure(0, weight=1)
        return self.frame

    def __buy_onclick(self, ticker):
        self.loop.create_task(self.tws.screener_buy(ticker))

    def draw_grid(self, tickers):
        new_tickers = [ticker for ticker in tickers if ticker not in self.grid_tickers]

        if not new_tickers:
            return

        for slave in self.frame.scrollable_frame.grid_slaves():
            slave.grid_forget()

        tickers = iter(list(self.grid_tickers) + new_tickers)
        ticker = next(tickers)
        self.grid_tickers.add(ticker)
        new_button = ttk.Button(self.frame.scrollable_frame, text=ticker, command=partial(self.__buy_onclick, ticker))
        new_button.grid(column=0, row=0)
        self.root.update()

        total_cols = int(self.frame.winfo_width() / new_button.winfo_width()) - 1

        row = 0
        try:
            while True:
                for col in range(total_cols):
                    if row == 0:
                        col += 1
                    ticker = next(tickers)
                    self.grid_tickers.add(ticker)
                    new_button = ttk.Button(self.frame.scrollable_frame,
                                            text=ticker,
                                            command=partial(self.__buy_onclick, ticker))
                    new_button.grid(sticky='new', column=col, row=row)
                    self.root.update()
                row += 1

        except StopIteration:
            return
