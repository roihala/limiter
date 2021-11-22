import logging

from ib_insync import *
import asyncio


def get_existing_positions():
    return ['AAPL', 'ADBE', 'AMD', 'AMAT', 'FSLR', 'GPRO', 'IBM', 'MSFT', 'MU',
                                          'QCOM', 'TXN', 'XLNX', 'CRM', ] + ['BIDU', 'FB', 'GOOG', 'NFLX']


def get_todays_alerts():
    return ['aaaa', 'bbbb', 'cccc', 'dddd', 'eeeee', 'ffff']


async def scan():
    while True:
        logging.getLogger('Limiter').info('scanning')
        await asyncio.sleep(2)
