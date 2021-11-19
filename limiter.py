import os
import tkinter
import tkinter as tk
import argparse

from src.gui.controller import Controller
from src.gui.screener import Screener


class Limiter(object):
    def __init__(self):
        args = self.create_parser().parse_args()
        os.environ['debug'] = str(args.debug)
        self.root = None
        self.screener = None
        self.controller = None

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', dest='debug', help='debug_mode', default=False, action='store_true')

        return parser

    def init_tkinter(self):
        self.root = tkinter.Tk()
        self.root.minsize(500, 200)

        main_panel = tk.PanedWindow(orient=tk.VERTICAL)
        main_panel.pack(fill=tk.BOTH, expand=1)

        self.screener = Screener(main_panel)
        self.controller = Controller(main_panel)

        root = self.root
        root.iconbitmap(os.path.join(os.path.dirname(__file__), 'lib', 'favicon.ico'))
        root.title("Stocker")
        root.columnconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        frame = self.screener.frame
        main_panel.add(frame)

        frame = self.controller.frame
        main_panel.add(frame)

        root.mainloop()

    def run(self):
        self.init_tkinter()


if __name__ == '__main__':
    Limiter().run()
