# utils/price_buffer.py
from datetime import datetime
from DataCleaner import DataCleaner

class PriceBuffer:
    def __init__(self, maxBars=500):
        self.maxBars = maxBars
        self.bars = []
        self.currentBar = None

    def updateFromTick(self, tick):
        if not DataCleaner.isValidTick(tick):
            return

        timestamp = datetime.utcnow().replace(second=0, microsecond=0).isoformat()
        price = tick.get("last")

        if not self.currentBar or self.currentBar["timestamp"] != timestamp:
            if self.currentBar:
                self.bars.append(self.currentBar)
                if len(self.bars) > self.maxBars:
                    self.bars.pop(0)
            self.currentBar = {
                "timestamp": timestamp,
                "open": price,
                "high": price,
                "low": price,
                "close": price
            }
        else:
            self.currentBar["high"] = max(self.currentBar["high"], price)
            self.currentBar["low"] = min(self.currentBar["low"], price)
            self.currentBar["close"] = price

    def getBars(self):
        allBars = self.bars + ([self.currentBar] if self.currentBar else [])
        clean = DataCleaner.cleanBars(allBars)
        return DataCleaner.sortBarsByTime(clean)
