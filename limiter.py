import json
import os
import tkinter
import tkinter as tk
import argparse
from json import JSONDecodeError
from tkinter import messagebox

from pydantic import ValidationError

from config.schema import Schema
from src.gui.positions import Positions
from src.gui.screener import Screener


CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config', 'config.json')


class Limiter(object):
    def __init__(self):
        args = self.create_parser().parse_args()
        os.environ['debug'] = str(args.debug)
        self.root = None
        self.screener = None
        self.controller = None
        self.config = self._init_config()
        if self.config:
            self.init_tkinter()

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', dest='debug', help='debug_mode', default=False, action='store_true')

        return parser

    def init_tkinter(self):
        self.root = tkinter.Tk()
        self.root.minsize(500, 200)

        main_panel = tk.PanedWindow(orient=tk.VERTICAL)
        main_panel.pack(fill=tk.BOTH, expand=1)

        self.screener = Screener(main_panel, self.config)
        self.controller = Positions(main_panel, self.config)

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

    def _init_config(self):
        f = open(CONFIG_FILE_PATH)
        try:
            data = json.load(f)
            return Schema(**data)

        except ValidationError as e:
            messagebox.showerror(
                message=f"Error in config file schema:\n{e}",
                title='Config file error')
        except JSONDecodeError as e:
            messagebox.showerror(
                message=f"Error parsing config file:\n{e}",
                title='Config file error')
        except Exception as e:
            messagebox.showerror(
                message=f"General config file error:\n{e}",
                title='Config file error')


if __name__ == '__main__':
    Limiter()
