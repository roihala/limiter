import logging
import os

import ib_insync
import asyncio

from ib_insync import LimitOrder, Stock

from config.schema import Schema


class UnexistingTradeException(Exception):
    pass


class Tws(object):
    def __init__(self, ib: ib_insync.ib.IB, config: Schema):
        self.ib = ib
        self.config = config
        self.screener_results = []

    def get_existing_positions(self):
        if bool(os.getenv('DEBUG')):
            return ['AAPL', 'ADBE', 'AMD', 'AMAT', 'FSLR', 'GPRO', 'IBM', 'MSFT', 'MU',
                    'QCOM', 'TXN', 'XLNX', 'CRM', ] + ['BIDU', 'FB', 'GOOG', 'NFLX']
        else:
            return [trade.contract.symbol for trade in self.ib.openTrades()]

    def scanner_buy(self, ticker):
        # TODO: contract
        contract = Stock('GOOGL', 'SMART', 'USD')

        m_data = self.ib.reqMktData(contract)
        # Wait until data is in.
        while m_data.last != m_data.last:
            self.ib.sleep(0.01)

        quantity = self.config.screener.position_size_usd / m_data.last
        limit_price = m_data.last + self.config.screener.limit_gap
        order = LimitOrder('BUY', quantity, limit_price)
        # TODO: Examine return value?
        self.ib.placeOrder(contract, order)

    def sell_button(self, ticker, percents):
        m_data = self.ib.reqMktData(self.__get_trade(ticker).contract)
        # Wait until data is in.
        while m_data.last != m_data.last:
            self.ib.sleep(0.01)

        limit_price = m_data.last - self.config.positions.sell_buttons.limit_gap
        self.__partial_sell(ticker, percents, limit_price)

    def presale_combobox(self, ticker, change_percents):
        m_data = self.ib.reqMktData(self.__get_trade(ticker).contract)
        # Wait until data is in.
        while m_data.last != m_data.last:
            self.ib.sleep(0.01)

        limit_price = (change_percents * 0.01 * m_data.last) + m_data.last
        self.__partial_sell(ticker, self.config.positions.presale_combobox.quantity_precents, limit_price)

    def __partial_sell(self, ticker, quantity_precents, limit_price):
        """
        :param ticker: ticker
        :param quantity_precents: % of shares to sell
        :param limit_price: price
        """
        # TODO: Update corresponding stop limit
        self.__validate_ticker(ticker)
        trade = self.__get_trade(ticker)
        order = LimitOrder('SELL', (quantity_precents * 0.01) * trade.order.totalQuantity, limit_price)
        # TODO: Examine return value?
        self.ib.placeOrder(trade.contract, order)

    def __get_trade(self, ticker) -> ib_insync.order.Trade:
        if self.__validate_ticker(ticker):
            for trade in self.ib.openTrades():
                if trade.contract.symbol == ticker:
                    return trade

    def __validate_ticker(self, ticker):
        # TODO: Check if quantity > 0 and is active
        if ticker not in self.get_existing_positions():
            raise UnexistingTradeException()

        return True


async def scan(ib):
    # TODO: ib shadow
    sub = ib_insync.ScannerSubscription(
        instrument='FUT.US',
        locationCode='FUT.GLOBEX',
        scanCode='TOP_PERC_GAIN')
    # scanData = ib.reqScannerSubscription(sub)
    # scanData.updateEvent += onScanData
    # ib.cancelScannerSubscription(scanData)

    scanData = await ib.reqScannerDataAsync(sub)
    print(scanData)
    print(len(scanData))


# asyncio.run
# asyncio.gather(*tasks)

def onScanData(scanData):
    print(scanData[0])
    print(len(scanData))


# ib = IB()
# ib.connect('127.0.0.1', 7497, clientId=1)
# nflx_contract = Stock('NFLX', 'SMART', 'USD')
# nflx_order = MarketOrder('BUY', 137)
# trade = ib.placeOrder(nflx_contract, nflx_order)


async def realscan():
    # sub = ScannerSubscription(
    #     instrument='FUT.US',
    #     locationCode='FUT.GLOBEX',
    #     scanCode='TOP_PERC_GAIN')
    # scanData = ib.reqScannerSubscription(sub)
    # scanData.updateEvent += onScanData
    # ib.sleep(60)
    # ib.cancelScannerSubscription(scanData)
    while True:
        logging.getLogger('Main').info('scanning')
        print('scanning')
        await asyncio.sleep(2)
    # scanData  = ib.reqScannerDataAsync(sub)
