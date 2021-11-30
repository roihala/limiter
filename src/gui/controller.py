import asyncio
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from functools import partial

from config.schema import Schema
from src.gui.scrollable_frame import ScrollableFrame


class Controller(object):
    PRESALE_DEFAULT_VALUE = 0

    def __init__(self, root, config: Schema, tws, loop):
        self.loop = loop
        self.root = root
        self.config = config
        self.tws = tws
        self.presale_vars = {}
        self.existing_positions = set()
        self.frame = self._init_frame()

    def _init_frame(self):
        self.frame = ScrollableFrame(self.root, title='Positions')
        self.frame['relief'] = 'sunken'
        self.frame['padding'] = 5
        self.frame['borderwidth'] = 5

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        return self.frame

    def draw_positions(self, tickers):
        new_tickers = [ticker for ticker in tickers if ticker not in self.existing_positions]

        for ticker in new_tickers:
            # grid_size[1] gives the rows count
            row_index = self.frame.scrollable_frame.grid_size()[1]

            # Ticker name
            ttk.Label(self.frame.scrollable_frame, text=ticker).grid(column=0, row=row_index, pady=3)

            # Sell buttons
            for index, value in enumerate(self.config.buttons.sell_buttons.values):
                button = ttk.Button(self.frame.scrollable_frame,
                                    text=f'sell {value}%',
                                    command=partial(self.__sell_onclick, ticker, value))
                button.grid(column=index + 1, row=row_index, pady=3)

            # Presale combobox
            self.presale_vars[ticker] = IntVar()
            presale_box = ttk.Combobox(self.frame.scrollable_frame, textvariable=self.presale_vars[ticker])
            presale_box['values'] = [0] + self.config.buttons.presale_combobox.values
            presale_box.bind('<<ComboboxSelected>>', partial(self.__presale_popup, ticker))
            presale_box.grid(column=4, row=row_index, pady=3)
            self.existing_positions.add(ticker)

    def __sell_onclick(self, ticker, percents, *args):
        self.loop.create_task(self.tws.sell_button(ticker, percents))

    def __presale_popup(self, ticker, *args):
        var = self.presale_vars[ticker]

        if messagebox.askyesno(
                message=f'Are you sure you want to presale {ticker} at {var.get()}%?',
                icon='question', title='Predefined sell'):
            self.loop.create_task(self.tws.presale_combobox(ticker, var.get()))
        else:
            var.set(self.PRESALE_DEFAULT_VALUE)
            self.tws.remove_existing_presale(ticker)
