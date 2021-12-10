import asyncio
import logging
from typing import Dict

import ib_insync
import pydantic
from ib_insync import TagValue, ScannerSubscription

from config.schema import Schema
from structures.screener_result import ScreenerResult


class Screener(object):
    def __init__(self, ib: ib_insync.ib.IB, config: Schema, loop):
        self.screener_results: Dict[str: ScreenerResult] = {}
        self.ib = ib
        self.config = config
        self.loop = loop

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
            self.loop.create_task(self.__update_screener_results(result.contractDetails.contract))

    async def __update_screener_results(self, contract: ib_insync.contract.Contract):
        m_data = self.ib.reqMktData(contract)

        # Wait until data is in.
        while m_data.last != m_data.last:
            await asyncio.sleep(0.01)

        change_percents = (m_data.last / m_data.close) * 100
        change_percents = change_percents - 100 if m_data.last > m_data.close else -1 * (100 - change_percents)

        try:
            screener_result = ScreenerResult(
                ticker=contract.symbol,
                last_value=m_data.last,
                change_percents=change_percents,
                volume=m_data.volume / 10000)
            self.screener_results[contract.symbol] = screener_result
        except pydantic.error_wrappers.ValidationError:
            logging.getLogger('Main').info(f"Couldn't parse market data values - skipping: last: {m_data.last} volume: {m_data.volume} close: {m_data.close}]")
