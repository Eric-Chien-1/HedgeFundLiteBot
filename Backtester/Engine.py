# Backtester/Engine.py

import pandas as pd
import logging
from Scrapers.NewsScraper import NewsScraper
from Scrapers.PriceScraper import PriceScraper
from Analysis.Sentiment import analyzeSentiment
from Analysis.Correlation import correlateSentimentWithPrice
from Strategy.Scanner import Scanner
from Backtester.MonteCarlo import MonteCarlo

class Engine:
    def __init__(self, config):
        self.config = config
        self.log = logging.getLogger(__name__)

    def runBacktest(self, symbol, startDate, endDate):
        # Step 1: Price data
        priceScraper = PriceScraper(symbol)
        priceData = priceScraper.getHistoricalData(startDate, endDate)

        # Step 2: News & Sentiment (only if enabled)
        sentimentData = None
        if self.config.useSentiment:
            newsScraper = NewsScraper(self.config.newsApiKey, query=symbol)
            newsData = newsScraper.scrapeNews(startDate, endDate)

            sentimentData = analyzeSentiment(newsData)
            corr, _ = correlateSentimentWithPrice(sentimentData, priceData)
            self.log.info(f"Sentiment-Price correlation: {corr:.4f}")
        else:
            self.log.warning("Skipping sentiment analysis (Config.useSentiment = False).")

        # Step 3: Scanner
        scanner = Scanner(self.config)
        trades = scanner.scan(priceData, sentimentData)

        # Step 4: Simulation
        tradeLog, finalBalance, winRate, ev = scanner.runSimulation(trades)

        # Step 5: Save trade log
        pd.DataFrame(tradeLog).to_csv("TradeLog.csv", index=False)
        self.log.info("Trade log saved to TradeLog.csv")

        # Step 6: Monte Carlo
        mcResults = MonteCarlo.run(tradeLog)

        # Step 7: Results
        self.log.info(f"Trades Taken: {len(tradeLog)}")
        self.log.info(f"Final Balance: ${finalBalance:,.2f}")
        self.log.info(f"Win Rate: {winRate*100:.2f}%")
        self.log.info(f"Expected Value: {ev:.2f}R")
        self.log.info(f"Monte Carlo (5% / 50% / 95%): {mcResults}")

        return {
            "finalBalance": finalBalance,
            "winRate": winRate,
            "expectedValue": ev,
            "monteCarlo": mcResults
        }
