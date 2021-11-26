import ib_insync
from ib_insync import TagValue, ScannerSubscription

from config.schema import Schema


class Screener(object):
    def __init__(self, ib: ib_insync.ib.IB, config: Schema):
        self.ib = ib
        self.config = config
        self.screener_results = []

    def scan(self):
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

    def get_screener_results(self):
        return [_.contractDetails.contract.symbol for _ in self.screener_results]

    def _update_screener_results(self, screener_results):
        for result in screener_results:
            if result not in self.screener_results:
                self.screener_results.append(result)
