# strategies/signal_evaluator.py
from TqsCalculator import TqsCalculator

class SignalEvaluator:
    def __init__(self, *, quoteTick, donchianHigh, donchianLow,
                 isSwept, isSweepConfirmed,
                 ev, rvol, macdAligned, rsiAligned,
                 biasAligned, vixInRange):
        self.quoteTick = quoteTick
        self.currentPrice = self._getCurrentPrice()
        self.donchianHigh = donchianHigh
        self.donchianLow = donchianLow
        self.isSwept = isSwept
        self.isSweepConfirmed = isSweepConfirmed
        self.ev = ev
        self.rvol = rvol
        self.macdAligned = macdAligned
        self.rsiAligned = rsiAligned
        self.biasAligned = biasAligned
        self.vixInRange = vixInRange
        self.calculator = TqsCalculator()

    def _getCurrentPrice(self):
        # Use midpoint of bid/ask as the current price estimate
        bid = self.quoteTick.get("bid")
        ask = self.quoteTick.get("ask")
        last = self.quoteTick.get("last")
        if bid is not None and ask is not None:
            return (bid + ask) / 2
        elif last is not None:
            return last
        return None

    def evaluate(self):
        self.calculator.scoreSweep(self.isSwept, self.isSweepConfirmed)
        self.calculator.scoreDonchianBreakout(self.currentPrice, self.donchianHigh, self.donchianLow)
        self.calculator.scoreConfirmationIndicators(self.ev, self.rvol, self.macdAligned, self.rsiAligned)
        self.calculator.scoreBiasAndVolatility(self.biasAligned, self.vixInRange)

        return {
            "score": self.calculator.getScore(),
            "breakdown": self.calculator.getBreakdown(),
            "priceUsed": self.currentPrice
        }
