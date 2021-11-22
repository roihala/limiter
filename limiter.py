import asyncio
import json
import logging
import os
import time
import tkinter
import tkinter as tk
import argparse
from json import JSONDecodeError
from tkinter import messagebox

from pydantic import ValidationError

from config.schema import Schema
from src.gui.positions import Positions
from src.gui.screener import Screener
from src.gui.async_tk import AsyncTk
from src.tws.tws import scan

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config', 'config.json')


class Limiter(object):
    def __init__(self, event_loop):
        args = self.create_parser().parse_args()
        os.environ['debug'] = str(args.debug)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.loop = event_loop
        self.root = None
        self.screener = None
        self.controller = None
        self.config = self._init_config()
        self.init_tkinter()

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', dest='debug', help='debug_mode', default=False, action='store_true')

        return parser

    def init_tkinter(self):
        self.root = AsyncTk(self.loop)
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

    def _init_config(self):
        f = open(CONFIG_FILE_PATH)
        try:
            data = json.load(f)
            return Schema(**data)

        except ValidationError as e:
            messagebox.showerror(
                message=f"Error in config file schema:\n{e}",
                title='Config file error')
            raise ConfigFileError(e)
        except JSONDecodeError as e:
            messagebox.showerror(
                message=f"Error parsing config file:\n{e}",
                title='Config file error')
            raise ConfigFileError(e)
        except Exception as e:
            messagebox.showerror(
                message=f"General config file error:\n{e}",
                title='Config file error')
            raise ConfigFileError(e)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    limiter = Limiter(loop)

    loop.create_task(scan())

    loop.run_forever()
    loop.close()


class ConfigFileError(Exception):
    pass
