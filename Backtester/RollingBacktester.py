import pandas as pd
import numpy as np
from datetime import timedelta
from Scrapers.PriceScraper import PriceScraper
from Scrapers.NewsScraper import NewsScraper
from Analysis.Sentiment import analyzeSentiment
from config import Config

import logging

log = logging.getLogger(__name__)

class RollingBacktester:
    def __init__(self, symbol, startDate, endDate, config, trainWindowMonths=12, testWindowMonths=3):
        self.symbol = symbol
        self.startDate = pd.to_datetime(startDate)
        self.endDate = pd.to_datetime(endDate)
        self.config = config
        self.trainWindow = pd.DateOffset(months=trainWindowMonths)
        self.testWindow = pd.DateOffset(months=testWindowMonths)

        # Load data on init
        self.priceData = None
        self.sentimentData = None
        self._load_data()

    def _load_data(self):
        log.info(f"Loading price data for {self.symbol} from {self.startDate.date()} to {self.endDate.date()}")
        priceScraper = PriceScraper(self.symbol)
        self.priceData = priceScraper.getHistoricalData(
            self.startDate.strftime("%Y-%m-%d"),
            self.endDate.strftime("%Y-%m-%d")
        )

        if self.config.useSentiment:
            log.info(f"Loading news and sentiment data for {self.symbol}...")
            newsScraper = NewsScraper(self.config.newsApiKey, query=self.symbol)
            newsData = newsScraper.scrapeNews(
                self.startDate.strftime("%Y-%m-%d"),
                self.endDate.strftime("%Y-%m-%d")
            )
            self.sentimentData = analyzeSentiment(newsData)
        else:
            log.warning("Sentiment disabled; skipping sentiment data load.")

    def _generateWindows(self):
        minDate = self.priceData["datetime"].min()
        maxDate = self.priceData["datetime"].max()

        trainStart = minDate
        while True:
            trainEnd = trainStart + self.trainWindow
            testStart = trainEnd
            testEnd = testStart + self.testWindow

            if testEnd > maxDate:
                break

            yield trainStart, trainEnd, testStart, testEnd
            trainStart += self.testWindow

    def _tuneTqsThreshold(self, trainStart, trainEnd):
        log.info(f"Tuning TQS threshold on training window {trainStart.date()} to {trainEnd.date()}")

        bestThreshold = None
        bestWinRate = 0

        thresholds = np.arange(3, 7, 0.5)

        for t in thresholds:
            self.config.tqsThreshold = t

            from Backtester.Engine import Engine
            engine = Engine(self.config)
            result = engine.runBacktest(
                self.symbol,
                trainStart.strftime("%Y-%m-%d"),
                trainEnd.strftime("%Y-%m-%d")
            )

            if result["winRate"] > bestWinRate:
                bestWinRate = result["winRate"]
                bestThreshold = t

        log.info(f"Best TQS threshold found: {bestThreshold} with win rate {bestWinRate:.2%}")
        return bestThreshold

    def runRollingBacktest(self):
        records = []

        for trainStart, trainEnd, testStart, testEnd in self._generateWindows():
            bestThreshold = self._tuneTqsThreshold(trainStart, trainEnd)
            self.config.tqsThreshold = bestThreshold

            log.info(f"Backtesting on test window {testStart.date()} to {testEnd.date()} with TQS threshold {bestThreshold}")

            from Backtester.Engine import Engine
            engine = Engine(self.config)
            result = engine.runBacktest(
                self.symbol,
                testStart.strftime("%Y-%m-%d"),
                testEnd.strftime("%Y-%m-%d")
            )

            records.append({
                "TrainStart": trainStart.date(),
                "TrainEnd": trainEnd.date(),
                "TestStart": testStart.date(),
                "TestEnd": testEnd.date(),
                "TqsThreshold": bestThreshold,
                "FinalBalance": result["finalBalance"],
                "WinRate": result["winRate"],
                "ExpectedValue": result["expectedValue"],
                "MonteCarloP5": result["monteCarlo"][0],
                "MonteCarloP50": result["monteCarlo"][1],
                "MonteCarloP95": result["monteCarlo"][2]
            })

        return pd.DataFrame(records)
