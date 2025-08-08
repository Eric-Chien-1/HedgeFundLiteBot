# strategies/tqs_calculator.py

class TqsCalculator:
    def __init__(self):
        self.score = 0
        self.reasons = []

    def add(self, points, reason):
        self.score += points
        self.reasons.append((points, reason))

    def scoreSweep(self, isSwept, isConfirmed):
        if isSwept and isConfirmed:
            self.add(1.5, "Liquidity sweep confirmed")
        elif isSwept:
            self.add(0.5, "Potential sweep (unconfirmed)")

    def scoreDonchianBreakout(self, currentPrice, donchianHigh, donchianLow):
        if currentPrice > donchianHigh:
            self.add(1.0, "Breakout above Donchian high")
        elif currentPrice < donchianLow:
            self.add(1.0, "Breakdown below Donchian low")

    def scoreConfirmationIndicators(self, ev, rvol, macdAligned, rsiAligned):
        if ev > 0:
            self.add(1.0, "Expected value > 0")
        if rvol >= 1.5:
            self.add(1.0, "RVOL >= 1.5")
        if macdAligned:
            self.add(0.5, "MACD aligned")
        if rsiAligned:
            self.add(0.5, "RSI aligned")

    def scoreBiasAndVolatility(self, biasAligned, vixInRange):
        if biasAligned:
            self.add(1.0, "Directional bias aligned")
        if vixInRange:
            self.add(1.0, "Correct VIX regime")

    def getScore(self):
        return self.score

    def getBreakdown(self):
        return self.reasons
