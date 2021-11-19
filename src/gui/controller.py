from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from functools import partial

from src.gui.scrollable_frame import ScrollableFrame
from src.tws.tws import get_existing_positions


class Controller(object):
    PRESALE_DEFAULT_VALUE = 0

    def __init__(self, root):
        self.root = root
        self.presale_vars = {}
        self.frame = self._init_frame()

    def _init_frame(self):
        self.frame = ScrollableFrame(self.root, title='Positions')
        self.frame['relief'] = 'sunken'
        self.frame['padding'] = 5
        self.frame['borderwidth'] = 5

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        for ticker in get_existing_positions():
            self.print_position(ticker)

        return self.frame

    def print_position(self, ticker):
        # grid_size[1] gives the rows count
        row_index = self.frame.scrollable_frame.grid_size()[1]

        # Ticker name
        ttk.Label(self.frame.scrollable_frame, text=ticker).grid(column=0, row=row_index, pady=3)

        # Sell buttons
        ttk.Button(self.frame.scrollable_frame, text='sell 10%').grid(column=1, row=row_index, pady=3)
        ttk.Button(self.frame.scrollable_frame, text='sell 20%').grid(column=2, row=row_index, pady=3)
        ttk.Button(self.frame.scrollable_frame, text='sell 50%').grid(column=3, row=row_index, pady=3)

        # Presale combobox
        self.presale_vars[ticker] = IntVar()
        presale_box = ttk.Combobox(self.frame.scrollable_frame, textvariable=self.presale_vars[ticker])
        presale_box['values'] = (0, 10, 20, 50)
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
