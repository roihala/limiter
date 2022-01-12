import asyncio
import logging
import time
from tkinter import messagebox
from typing import Dict

import ib_insync
import pydantic
from ib_insync import TagValue, ScannerSubscription

from config.schema import Schema
from src.structures.screener_result import ScreenerResult


class Screener(object):
    def __init__(self, ib: ib_insync.ib.IB, config: Schema, loop):
        self.screener_results: Dict[str: ScreenerResult] = {}
        self.ib = ib
        self.config = config
        self.loop = loop
        self.first_scan = True

    def scan(self):
        try:
            sub = ScannerSubscription(
                instrument='STK',
                locationCode='STK.US.MAJOR',
                scanCode='TOP_PERC_GAIN')

            tagValues = [
                TagValue("changePercAbove", str(self.config.screener.change_percents)),
                TagValue('priceAbove', str(self.config.screener.above_price)),
                TagValue('priceBelow', str(self.config.screener.below_price)),
                TagValue('volumeAbove', str(self.config.screener.above_volume))]

            screener_results = self.ib.reqScannerData(sub, scannerSubscriptionFilterOptions=tagValues)
            self._update_screener_results(screener_results)
        except Exception as e:
            logging.getLogger('Main').warning("Scan failed")
            logging.getLogger('Main').exception(e)

    def _update_screener_results(self, screener_results):
        for result in screener_results:
            if result.contractDetails.contract.symbol not in self.screener_results \
                    and not self.first_scan:

                messagebox.showinfo(title='Scanner Detected ticker',
                                    message=f'Detected {result.contractDetails.contract.symbol}')
            self.loop.create_task(self.__update_screener_results(result.contractDetails.contract))

        self.first_scan = False

    async def __update_screener_results(self, contract: ib_insync.contract.Contract):
        m_data = self.ib.reqMktData(contract)
        start_time = time.time()

        # Wait until data is in.
        while m_data.last != m_data.last:
            if time.time() - start_time > 3:
                break
            await asyncio.sleep(0.01)

        change_percents, position_percents = self.get_table_values(m_data, contract)

        try:
            screener_result = ScreenerResult(
                ticker=contract.symbol,
                last_value=m_data.last,
                change_percents=change_percents,
                position_percents=position_percents,
                volume=m_data.volume / 10000)
            self.screener_results[contract.symbol] = screener_result
        except pydantic.error_wrappers.ValidationError:
            logging.getLogger('Main').info(f"Couldn't parse market data values - skipping: last: {m_data.last} volume: {m_data.volume} close: {m_data.close}]")
            screener_result = ScreenerResult(
                ticker=contract.symbol,
                last_value=0,
                change_percents=0,
                position_percents=0,
                volume=0)
            self.screener_results[contract.symbol] = screener_result

    def get_table_values(self, m_data: ib_insync.ticker.Ticker, contract: ib_insync.contract.Contract):
        change_percents = (m_data.last / m_data.close) * 100
        change_percents = change_percents - 100 if m_data.last > m_data.close else -1 * (100 - change_percents)

        position = [position for position in self.ib.positions() if position.contract.symbol == contract.symbol]
        if len(position) != 1:
            position_percents = 0

        else:
            position = position[0]
            position_percents = (m_data.last / position.avgCost) * 100
            position_percents = position_percents - 100 if m_data.last > position.avgCost else -1 * (100 - change_percents)

        return change_percents, position_percents
