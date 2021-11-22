import asyncio
import json
import logging
import os
import argparse
from json import JSONDecodeError
from tkinter import messagebox

from ib_insync import IB
from pydantic import ValidationError

from config.schema import Schema
from src.gui.async_tk import AsyncTk
from src.tws.tws import scan, Tws

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config', 'config.json')


class ConfigFileError(Exception):
    pass


class Main(object):
    def __init__(self, event_loop):
        args = self.create_parser().parse_args()
        os.environ['DEBUG'] = str(args.debug)
        print(os.getenv('DEBUG'))
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.loop = event_loop
        self.config = self._init_config()

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', dest='debug', help='debug_mode', default=False, action='store_true')

        return parser

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
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)

    tws = Tws(ib)

    loop = asyncio.get_event_loop()
    main = Main(loop)
    gui = AsyncTk(loop, main.config, tws)

    loop.create_task(scan(ib))

    loop.run_forever()
    # loop.close()

