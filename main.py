import asyncio
import json
import logging
import os
import argparse
import sys
from json import JSONDecodeError
from tkinter import messagebox

import ib_insync
from ib_insync import IB
from pydantic import ValidationError
from config.schema import Schema
from src.gui.gui import Gui
from src.tws.tws import Tws
from src.tws.screener import Screener

CONFIG_FILE_PATH = os.path.join(os.path.dirname(sys.argv[0]), 'config', 'config.json')
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'log')


class ConfigFileError(Exception):
    pass


class Main(object):
    SCREENER_INTERVAL = 1
    GUI_INTERVAL = 0.005

    def __init__(self, loop):
        args = self.create_parser().parse_args()
        os.environ['ENV'] = 'DEBUG' if args.debug else 'PROD'
        if os.environ['ENV'] == 'DEBUG':
            logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        else:
            os.makedirs(LOGS_DIR, exist_ok=True)
            logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                                filename=os.path.join(LOGS_DIR, 'log.log'))
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = self._init_config()
        self.loop = loop
        ib = IB()
        ib.RequestTimeout = 10
        ib.connect('127.0.0.1', 7497, clientId=1)
        self.screener = Screener(ib, self.config, self.loop)
        self.tws = Tws(ib, self.config, self.screener, self.loop)
        self.gui = Gui(self.loop, self.config, self.tws)

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', dest='debug', help='debug_mode', default=False, action='store_true')

        return parser

    def run(self):
        ib_insync.util.patchAsyncio()
        self._gui_updater()
        self._screener_updater()
        self.loop.run_forever()

    def _gui_updater(self):
        self.gui.update(screener_results=self.screener.screener_results,
                        positions=self.tws.get_existing_positions())

        self.loop.call_later(self.GUI_INTERVAL, self._gui_updater)

    def _screener_updater(self):
        self.screener.scan()

        self.loop.call_later(self.SCREENER_INTERVAL, self._screener_updater)

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

    @staticmethod
    def loop_exception_handler(loop_instance, context):
        # context["message"] will always be there; but context["exception"] may not
        msg = context.get("exception", context["message"])
        messagebox.showerror(
            message=f"Internal failure in event loop:\n{msg}",
            title='Event loop failure')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(Main.loop_exception_handler)
    Main(loop).run()
