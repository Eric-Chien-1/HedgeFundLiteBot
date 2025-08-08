import logging
from strategies.SignalEvaluator import SignalEvaluator
from strategies.DonchianZones import DonchianZones
from strategies.LiquidityZones import LiquidityZones
from utils.PriceBuffer import PriceBuffer
from dotenv import load_dotenv

import csv
import os
from datetime import datetime

logger = logging.getLogger("LiveSignal")
logger.setLevel(logging.INFO)

class LiveSignalRunner:
    def __init__(self, evaluatorInputs):
        self.buffer = PriceBuffer()
        self.evaluatorInputs = evaluatorInputs

    

    def onTick(self, tick):
        load_dotenv()
        import os
        from config.config import config
        TRADE_TRIGGER_SCORE = float(os.getenv("TQS_TRADE_THRESHOLD", config.TQS_TRADE_THRESHOLD))
        WATCHLIST_SCORE = float(os.getenv("TQS_WATCHLIST_THRESHOLD", config.TQS_WATCHLIST_THRESHOLD))
        
        self.buffer.updateFromTick(tick)
        priceData = self.buffer.getBars()

        if not priceData:
            return

        currentPrice = tick.get("last")
        if not currentPrice:
            return

        donchian = DonchianZones(priceData)
        liquidity = LiquidityZones(priceData)
        donchianRange = donchian.getRange()

        isSwept = liquidity.detectSweep(currentPrice, "londonLow")
        isConfirmed = liquidity.isSweepConfirmed(currentPrice, "londonLow")

        evaluator = SignalEvaluator(
            quoteTick=tick,
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
        score = result['score']
        
        if score >= TRADE_TRIGGER_SCORE:
            logger.info(f"🚨 TRADE SIGNAL — TQS: {score:.2f} | Price: {result['priceUsed']} | Reasons: {result['breakdown']}")
        elif score >= WATCHLIST_SCORE:
            logger.info(f"🔍 WATCHLIST — TQS: {score:.2f} | Price: {result['priceUsed']} | Reasons: {result['breakdown']}")
        else:
            logger.info(f"TQS Score: {score:.2f} | Price: {result['priceUsed']} | Reasons: {result['breakdown']}")

        # Log to file
        log_path = os.getenv("TQS_LOG_PATH", "signals_log.csv")
        with open(log_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.utcnow().isoformat(),
                score,
                result["priceUsed"],
                "; ".join(f"{pts}: {msg}" for pts, msg in result["breakdown"])
            ])
