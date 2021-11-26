import logging
import os
from _queue import Empty
from tkinter import messagebox

import ib_insync
import asyncio

from ib_insync import LimitOrder, Stock

from config.schema import Schema
from tws import Screener


class UnexistingTradeException(Exception):
    pass


class Tws(object):
    def __init__(self, ib: ib_insync.ib.IB, config: Schema, screener: Screener):
        self.ib = ib
        self.config = config
        self.screener = screener

    def get_existing_positions(self):
        return [trade.contract.symbol for trade in self.ib.openTrades()]

    async def screener_buy(self, ticker):
        logging.getLogger('Main').info(f'buying {ticker}')

        contract = Stock(ticker, 'SMART', 'USD')

        m_data = self.ib.reqMktData(contract)

        # Wait until data is in.
        while m_data.last != m_data.last:
            await asyncio.sleep(0.01)

        quantity = int(self.config.buttons.screener_buy.position_size_usd / m_data.last)
        limit_price = m_data.last + self.config.buttons.screener_buy.limit_gap
        order = LimitOrder('BUY', quantity, limit_price, outsideRth=True)

        order = self.ib.placeOrder(contract, order)

        # TODO: if didn't work decorator
        while order.orderStatus.status != 'Submitted':
            await asyncio.sleep(0.01)

    def sell_button(self, ticker, percents):
        m_data = self.ib.reqMktData(self.__get_trade(ticker).contract)
        # Wait until data is in.
        while m_data.last != m_data.last:
            self.ib.sleep(0.01)

        limit_price = m_data.last + self.config.buttons.sell_buttons.limit_gap
        self.__partial_sell(ticker, percents, limit_price)

    def presale_combobox(self, ticker, change_percents):
        m_data = self.ib.reqMktData(self.__get_trade(ticker).contract)
        # Wait until data is in.
        while m_data.last != m_data.last:
            self.ib.sleep(0.01)

        limit_price = (change_percents * 0.01 * m_data.last) + m_data.last
        self.__partial_sell(ticker, self.config.buttons.presale_combobox.quantity_percents, limit_price)

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
