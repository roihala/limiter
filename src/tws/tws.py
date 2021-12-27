import logging
import time
from collections import deque
from tkinter import messagebox

import ib_insync
import asyncio

from ib_insync import LimitOrder, Stock, StopLimitOrder

from config.schema import Schema
from src.tws import Screener


class UnexistingPositionException(Exception):
    def __init__(self, ticker, *args, **kwargs):
        self.ticker = ticker


class Tws(object):
    LIMIT_REJECTION_TEXT = 'We cannot accept an order at the limit price you selected.'
    STOP_LIMIT_REJECTION_TEXT = 'We cannot accept your Stop Limit order because the Limit Price'
    MIN_LIMIT_GAP = 0.01
    MAX_ACTIVE_ORDERS = 200
    IGNORE_ERRORS = [162, 165]

    def __init__(self, ib: ib_insync.ib.IB, config: Schema, screener: Screener, loop):
        ib.errorEvent += self.error_event
        ib.orderStatusEvent += self.order_status_event
        ib.disconnectedEvent += self.disconnect_event

        self.ib = ib
        self.config = config
        self.screener = screener
        self.loop = loop
        self.trades: deque[ib_insync.order.Trade] = deque([_ for _ in self.ib.openTrades()],
                                                          maxlen=self.MAX_ACTIVE_ORDERS)

    async def screener_buy(self, ticker):
        contract = Stock(ticker, 'SMART', 'USD')

        m_data = self.ib.reqMktData(contract)

        # Wait until data is in.
        while m_data.last != m_data.last:
            await asyncio.sleep(0.01)

        quantity = self.config.buttons.screener_buy.position_size_usd / m_data.last
        limit_price = m_data.last + self.config.buttons.screener_buy.limit

        order = LimitOrder('BUY',
                           int(quantity),
                           round(limit_price, ndigits=2),
                           outsideRth=True,
                           orderRef='limiterBuy')

        self.trades.append(self.ib.placeOrder(contract, order))

    async def sell_button(self, ticker, position_percents, price_percents: int = 0):
        contract = self.__get_portfolio_item(ticker).contract
        contract.exchange = 'SMART'
        m_data = self.ib.reqMktData(contract)
        # Wait until data is in.
        while m_data.last != m_data.last:
            await asyncio.sleep(0.01)

        if price_percents > 0:
            limit_price = (price_percents * 0.01 * m_data.last) + m_data.last

        # If price percents is set to 0 execute STP LMT command
        elif price_percents == 0:
            # TODO: stop limit
            limit_price = m_data.last + self.config.buttons.sell_buttons.limit
            stop_price = m_data.last + self.config.buttons.sell_buttons.stop
            self.__partial_sell(ticker, position_percents, limit_price, stop_price)
            return
        else:
            raise ValueError(f"Price percents should be 0 or higher, got {price_percents}!")

        self.__partial_sell(ticker, position_percents, limit_price)

    async def __handle__rejected_orders(self, rejected_trade: ib_insync.order.Trade):
        m_data = self.ib.reqMktData(rejected_trade.contract)
        # Wait until data is in.
        while m_data.last != m_data.last:
            await asyncio.sleep(0.01)

        limit_gap = abs((rejected_trade.order.lmtPrice - m_data.last) / 2)
        limit_price = limit_gap + m_data.last

        # Preventing option for infinite cancels
        if limit_gap < self.MIN_LIMIT_GAP:
            return

        if rejected_trade.order.orderRef == 'limiterBuy':
            new_order = LimitOrder('BUY',
                                   totalQuantity=rejected_trade.order.totalQuantity,
                                   lmtPrice=round(limit_price, ndigits=2),
                                   outsideRth=True,
                                   orderRef='limiterBuy')

        elif rejected_trade.order.orderRef == 'limiterSell':
            new_order = LimitOrder('SELL',
                                   totalQuantity=rejected_trade.order.totalQuantity,
                                   lmtPrice=round(limit_price, ndigits=2),
                                   outsideRth=True,
                                   orderRef='limiterSell')
        elif rejected_trade.order.orderRef == 'limiterStopSell':
            new_order = StopLimitOrder('SELL',
                                       totalQuantity=rejected_trade.order.totalQuantity,
                                       lmtPrice=round(limit_price, ndigits=2),
                                       stopPrice=rejected_trade.order.auxPrice,
                                       outsideRth=True,
                                       orderRef='limiterStopSell')
        else:
            return
        self.trades.append(self.ib.placeOrder(rejected_trade.contract, new_order))

    def remove_existing_presale(self, ticker):
        for trade in self.ib.openTrades():
            if trade.contract.symbol == ticker and \
                    trade.order.orderType == 'LMT' and \
                    trade.order.action == 'SELL':
                self.ib.cancelOrder(trade.order)

    def get_existing_positions(self):
        return [portfolio_item.contract.symbol for portfolio_item in self.ib.portfolio()]

    def disconnect_event(self):
        self.loop.stop()

    def order_status_event(self, trade: ib_insync.order.Trade, *args):
        if trade.orderStatus.status == 'Filled':
            self.loop.create_task(self.__stop_loss(trade))
        elif trade.orderStatus.status == 'Cancelled':
            self.order_cancel_event(trade)

    def order_cancel_event(self, trade: ib_insync.order.Trade, error_string: str = ''):
        if trade.order.orderRef == 'limiterStopLoss':
            return

        # If ordered was cancel due to far limit
        error_reason = error_string.split('reason:')
        if len(error_reason) > 1 and \
                (error_reason[1].startswith(self.LIMIT_REJECTION_TEXT) or
                 error_reason[1].startswith(self.STOP_LIMIT_REJECTION_TEXT)):
            self.loop.create_task(self.__handle__rejected_orders(rejected_trade=trade))

        message = f'{trade.order.action} {trade.order.orderType} order canceled for {trade.contract.symbol}'
        message = message if not error_string else message + '\n' + error_string
        messagebox.showerror(
            message=message,
            title="Order canceled")

    def error_event(self, reqId, errorCode, errorString, *args):
        # 2XXX errors are warnings
        if errorCode in self.IGNORE_ERRORS or int(errorCode / 1000) == 2:
            return
        if errorCode == 202:
            trade = self.__get_trade_by_reqid(reqId)
            if trade:
                self.order_cancel_event(trade, errorString)
                return

        messagebox.showerror(
            message=f"{errorString}\n Error code: {errorCode}, order: {self.__get_trade_by_reqid(reqId)}, args: {args}",
            title="Couldn't perform API action")

    async def __stop_loss(self, trade: ib_insync.order.Trade):
        await asyncio.sleep(1)
        portfolio_item = self.__get_portfolio_item(trade.contract.symbol)

        if portfolio_item.position == 0:
            return
        else:
            await self.__cancel_existing_stop_loss(portfolio_item)

        await asyncio.sleep(1)
        portfolio_item = self.__get_portfolio_item(trade.contract.symbol)
        portfolio_item.contract.exchange = 'SMART'
        m_data = self.ib.reqMktData(portfolio_item.contract)
        # Wait until data is in.
        while m_data.last != m_data.last:
            await asyncio.sleep(0.01)

        limit_price = m_data.last + self.config.auto_stop_loss.limit
        stop_price = portfolio_item.averageCost + (
                0.01 * self.config.auto_stop_loss.stop_percents * portfolio_item.averageCost)
        
        order = StopLimitOrder('SELL',
                               totalQuantity=int(portfolio_item.position),
                               lmtPrice=round(limit_price, ndigits=2),
                               stopPrice=round(stop_price, ndigits=2),
                               outsideRth=True,
                               orderRef='limiterStopLoss')

        self.trades.append(self.ib.placeOrder(portfolio_item.contract, order))

    async def __cancel_existing_stop_loss(self, portfolio_item: ib_insync.objects.PortfolioItem):
        # Handle existing stop limit
        for trade in self.ib.openTrades():
            if trade.contract == trade.contract \
                    and trade.order.orderType == 'STP LMT' \
                    and trade.order.action == 'SELL' \
                    and trade.order.orderRef == 'limiterStopLoss':
                if trade.order.totalQuantity == portfolio_item.position:
                    # Existing Stop limit is good for us
                    return
                else:
                    self.ib.cancelOrder(trade.order)
                    start_time = time.time()
                    # Needed to defend from partial fill
                    while trade.orderStatus != 'Cancelled':
                        if time.time() - start_time > 10:
                            break
                        await asyncio.sleep(0.01)

    def __get_trade_by_reqid(self, req_id) -> ib_insync.order.Trade:
        for trade in self.trades:
            if trade.order.orderId == req_id:
                return trade

    def __partial_sell(self, ticker, quantity_percents, limit_price, stop_price=0.0):
        """
        :param ticker: ticker
        :param quantity_percents: % of shares to sell
        :param limit_price: price
        """
        portfolio_item = self.__get_portfolio_item(ticker)
        quantity = (quantity_percents * 0.01) * portfolio_item.position
        if stop_price != 0:
            order = StopLimitOrder('SELL',
                                   totalQuantity=int(quantity),
                                   lmtPrice=round(limit_price, ndigits=2),
                                   stopPrice=round(stop_price, ndigits=2),
                                   outsideRth=True,
                                   orderRef='limiterStopSell')
        else:
            order = LimitOrder('SELL', int(quantity), round(limit_price, ndigits=2), outsideRth=True,
                               orderRef='limiterSell')
        self.trades.append(self.ib.placeOrder(portfolio_item.contract, order))

    def __get_portfolio_item(self, ticker) -> ib_insync.objects.PortfolioItem:
        for portfolio_item in self.ib.portfolio():
            if portfolio_item.contract.symbol == ticker and portfolio_item.position > 0:
                return portfolio_item

        self.ib.errorEvent.emit(None, None, f"Requirements unmet for {ticker} in portfolio")
        raise UnexistingPositionException(ticker)
