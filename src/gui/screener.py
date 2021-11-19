from tkinter import ttk

from config.schema import Schema
from src.gui.scrollable_frame import ScrollableFrame
from src.tws.tws import get_todays_alerts


class Screener(object):
    def __init__(self, root, config: Schema):
        self.root = root
        self.config = config
        self.frame = self._init_frame()

    def _init_frame(self):
        self.frame = ScrollableFrame(self.root, title='Screener')
        self.frame['relief'] = 'sunken'
        self.frame['padding'] = 5
        self.frame['borderwidth'] = 5

        self.frame.columnconfigure(0, weight=1)
        return self.frame

    def add_ticker(self, ticker):
        self.__draw_grid(get_todays_alerts() + [ticker])

    def __draw_grid(self, tickers):
        for slave in self.frame.scrollable_frame.grid_slaves():
            slave.grid_forget()

        tickers = iter(tickers)
        new_button = ttk.Button(self.frame.scrollable_frame, text=next(tickers))
        new_button.grid(column=0, row=0)
        self.root.update()

        total_cols = int(self.frame.winfo_width() / new_button.winfo_width()) - 1

        row = 0
        try:
            while True:
                for col in range(total_cols):
                    if row == 0:
                        col += 1
                    new_button = ttk.Button(self.frame.scrollable_frame, text=next(tickers))
                    new_button.grid(sticky='new', column=col, row=row)
                    self.root.update()
                row += 1

        except StopIteration:
            return
