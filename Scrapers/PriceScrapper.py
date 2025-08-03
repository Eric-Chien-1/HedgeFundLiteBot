# Scrapers/PriceScraper.py

import yfinance as yf
import pandas as pd
import logging

log = logging.getLogger(__name__)

class PriceScraper:
    def __init__(self, ticker):
        self.ticker = ticker

    def getHistoricalData(self, startDate, endDate, interval="30m"):
        """
        Fetch historical price data for the given ticker and date range.

        Parameters:
            startDate: str YYYY-MM-DD
            endDate: str YYYY-MM-DD
            interval: yfinance interval (e.g., "1m", "5m", "15m", "30m", "1h", "1d")

        Returns:
            DataFrame with datetime, open, high, low, close, volume
        """
        log.info(f"Fetching price data for {self.ticker} from {startDate} to {endDate}...")
        df = yf.download(self.ticker, start=startDate, end=endDate, interval=interval)

        if df.empty:
            log.warning(f"No price data found for {self.ticker} in range {startDate} to {endDate}.")
            return pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "volume"])

        df = df.reset_index()
        if "Datetime" in df.columns:
            df.rename(columns={"Datetime": "datetime"}, inplace=True)
        elif "Date" in df.columns:
            df.rename(columns={"Date": "datetime"}, inplace=True)

        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })

        df = df[["datetime", "open", "high", "low", "close", "volume"]]
        df = df.sort_values("datetime").reset_index(drop=True)

        log.info(f"Retrieved {len(df)} rows of price data for {self.ticker}.")
        return df
