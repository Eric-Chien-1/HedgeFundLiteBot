# utils/price_buffer.py
from datetime import datetime

# Use relative import so PriceBuffer can be imported as part of the utils package
from .DataCleaner import DataCleaner

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

    def updateFromBar(self, bar):
        """Directly append a completed OHLC bar to the buffer.

        Parameters
        ----------
        bar : dict
            A dictionary containing at least the keys
            "timestamp", "open", "high", "low", and "close".
        """
        required = {"timestamp", "open", "high", "low", "close"}
        if not isinstance(bar, dict) or not required.issubset(bar):
            return

        # Normalize timestamps (ensures trailing 'Z') and copy to avoid
        # mutating the caller's dictionary.
        bar = DataCleaner.normalizeTimestamp(dict(bar))

        self.bars.append(bar)
        if len(self.bars) > self.maxBars:
            self.bars.pop(0)

        # When bars are supplied directly we don't keep a "current" bar.
        self.currentBar = None

    def getBars(self):
        allBars = self.bars + ([self.currentBar] if self.currentBar else [])
        clean = DataCleaner.cleanBars(allBars)
        return DataCleaner.sortBarsByTime(clean)
