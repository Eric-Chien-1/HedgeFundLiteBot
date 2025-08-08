class DonchianZones:
    def __init__(self, priceData):
        self.priceData = priceData

    def getRange(self, period=20):
        """
        Calculate Donchian high/low over the given period.
        :param period: Number of candles to look back
        :return: dict with 'donchianHigh' and 'donchianLow'
        """
        recent = self.priceData[-period:]
        high = max(bar["high"] for bar in recent)
        low = min(bar["low"] for bar in recent)
        return {"donchianHigh": high, "donchianLow": low}
