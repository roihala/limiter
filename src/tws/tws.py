import logging
import os

import ib_insync
import asyncio


class Tws(object):
    def __init__(self, ib: ib_insync.ib.IB):
        self.ib = ib
        self.screener_results = []

    def get_existing_positions(self):
        if bool(os.getenv('DEBUG')):
            return ['AAPL', 'ADBE', 'AMD', 'AMAT', 'FSLR', 'GPRO', 'IBM', 'MSFT', 'MU',
                    'QCOM', 'TXN', 'XLNX', 'CRM', ] + ['BIDU', 'FB', 'GOOG', 'NFLX']
        else:
            return [trade.contract.symbol for trade in self.ib.openTrades()]




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
