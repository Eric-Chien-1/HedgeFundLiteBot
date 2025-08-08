from strategies.SignalEvaluator import SignalEvaluator
from strategies.DonchianZones import DonchianZones
from strategies.LiquidityZones import LiquidityZones
from utils.PriceBuffer import PriceBuffer

class BacktestEngine:
    def __init__(self, priceData, evaluatorInputs):
        self.priceData = priceData.to_dict("records")  # Convert DataFrame to list of dicts
        self.evaluatorInputs = evaluatorInputs
        self.buffer = PriceBuffer()

    def run(self):
        results = []

        for bar in self.priceData:
            self.buffer.updateFromBar(bar)
            bars = self.buffer.getBars()
            if not bars or len(bars) < 100:  # Skip warm-up
                continue

            currentPrice = bar["close"]
            donchian = DonchianZones(bars)
            liquidity = LiquidityZones(bars)
            donchianRange = donchian.getRange()

            isSwept = liquidity.detectSweep(currentPrice, "londonLow")
            isConfirmed = liquidity.isSweepConfirmed(currentPrice, "londonLow")

            evaluator = SignalEvaluator(
                quoteTick={"last": currentPrice},
                donchianHigh=donchianRange["donchianHigh"],
                donchianLow=donchianRange["donchianLow"],
                isSwept=isSwept,
                isSweepConfirmed=isConfirmed,
                ev=self.evaluatorInputs["ev"],
                rvol=self.evaluatorInputs["rvol"],
                macdAligned=self.evaluatorInputs["macdAligned"],
                rsiAligned=self.evaluatorInputs["rsiAligned"],
                biasAligned=self.evaluatorInputs["biasAligned"],
                vixInRange=self.evaluatorInputs["vixInRange"]
            )

            result = evaluator.evaluate()
            result["timestamp"] = bar["timestamp"]
            results.append(result)

        return results
