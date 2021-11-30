import asyncio
import json
import logging
import os
import argparse
from json import JSONDecodeError
from tkinter import messagebox

import ib_insync
from ib_insync import IB
from pydantic import ValidationError

from config.schema import Schema
from gui.gui import Gui
from src.tws.tws import Tws
from tws.screener import Screener

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config', 'config.json')


class ConfigFileError(Exception):
    pass


class Main(object):
    IGNORE_ERRORS = [162, 165]

    def __init__(self, loop):
        args = self.create_parser().parse_args()
        os.environ['DEBUG'] = str(args.debug)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = self._init_config()
        self.loop = loop
        ib = IB()

        ib.RequestTimeout = 10
        ib.connect('127.0.0.1', 7497, clientId=1)
        ib.errorEvent += self.__ib_error
        self.screener = Screener(ib, self.config)
        self.tws = Tws(ib, self.config, self.screener, self.loop)
        self.gui = Gui(self.loop, self.config, self.tws)

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', dest='debug', help='debug_mode', default=False, action='store_true')

        return parser

    def run(self):
        ib_insync.util.patchAsyncio()
        self._updater()
        self.loop.run_forever()

    def _updater(self):
        self.gui.update(screener_results=self.screener.get_screener_results(),
                        positions=self.tws.get_existing_positions())
        self.screener.scan()
        self.loop.call_later(0.005, self._updater)

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

    def __ib_error(self, reqId, errorCode, errorString, *args):
        if errorCode in self.IGNORE_ERRORS:
            return
        messagebox.showerror(
            message=f"{errorString}\n Error code: {errorCode}, Request ID: {reqId}, args: {args}",
            title="Couldn't perform API action")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    Main(loop).run()
