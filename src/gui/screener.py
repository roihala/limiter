import logging
from functools import partial
from tkinter import ttk
from typing import Dict

from config.schema import Schema
from src.gui.scrollable_frame import ScrollableFrame
from src import tws
from src.structures.screener_result import ScreenerResult


class Screener(object):
    PADX = 10

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

    def draw_grid(self, screener_results: Dict[str, ScreenerResult]):
        if self.frame.scrollable_frame.grid_size() == (0, 0):
            # Draw title
            for index, (_, prop) in enumerate(ScreenerResult.schema()['properties'].items()):
                ttk.Label(self.frame.scrollable_frame,
                          text=prop['title']).grid(column=index, row=0, padx=self.PADX)

        for row_index, (ticker, result) in enumerate(screener_results.items()):
            self.__draw_row(result, ticker, row_index + 1)

    def __draw_row(self, result: ScreenerResult, ticker, row_index):
        col_index = 0

        for idx, (name, value) in enumerate(result):
            col_index = idx
            if name in ['change_percents', 'position_percents']:
                text = str(value) + '%'
            elif name == 'volume':
                text = str(value) + 'M'
            else:
                text = str(value)

            ttk.Label(self.frame.scrollable_frame,
                      text=text).grid(column=col_index, row=row_index, padx=self.PADX)

        if ticker not in self.grid_tickers:
            buy_button = ttk.Button(self.frame.scrollable_frame,
                                    text='BUY',
                                    command=partial(self.__buy_onclick, ticker))

            buy_button.grid(column=col_index + 1, row=row_index)
            self.grid_tickers.add(ticker)
