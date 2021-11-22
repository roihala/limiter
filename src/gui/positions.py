from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from functools import partial

from config.schema import Schema
from src.gui.scrollable_frame import ScrollableFrame
from src.tws.tws import Tws


class Positions(object):
    PRESALE_DEFAULT_VALUE = 0

    def __init__(self, root, config: Schema, tws: Tws):
        self.root = root
        self.config = config
        self.tws = tws
        self.presale_vars = {}
        self.frame = self._init_frame()

    def _init_frame(self):
        self.frame = ScrollableFrame(self.root, title='Positions')
        self.frame['relief'] = 'sunken'
        self.frame['padding'] = 5
        self.frame['borderwidth'] = 5

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        for ticker in self.tws.get_existing_positions():
            self.print_position(ticker)

        return self.frame

    def print_position(self, ticker):
        # grid_size[1] gives the rows count
        row_index = self.frame.scrollable_frame.grid_size()[1]

        # Ticker name
        ttk.Label(self.frame.scrollable_frame, text=ticker).grid(column=0, row=row_index, pady=3)

        for index, value in enumerate(self.config.positions.sell_buttons):
            # Sell buttons
            ttk.Button(self.frame.scrollable_frame, text=f'sell {value}%').grid(column=index + 1, row=row_index, pady=3)

        # Presale combobox
        self.presale_vars[ticker] = IntVar()
        presale_box = ttk.Combobox(self.frame.scrollable_frame, textvariable=self.presale_vars[ticker])
        presale_box['values'] = [0] + self.config.positions.presale_values
        presale_box.bind('<<ComboboxSelected>>', partial(self.__presale_popup, ticker))
        presale_box.grid(column=4, row=row_index, pady=3)

    def __presale_popup(self, ticker, *args):
        var = self.presale_vars[ticker]

        if messagebox.askyesno(
                message=f'Are you sure you want to presale {ticker} at {var.get()}%?',
                icon='question', title='Predefined sell'):
            pass
        else:
            var.set(self.PRESALE_DEFAULT_VALUE)
