import yfinance as yf
import pandas as pd
import logging

log = logging.getLogger(__name__)

class PriceScraper:
    def __init__(self, ticker, tradovateClient=None):
        self.ticker = ticker
        self.tradovateClient = tradovateClient  # optional Tradovate API client

    def getHistoricalData(self, startDate, endDate, interval="30m"):
        log.info(f"Fetching price data for {self.ticker} from {startDate} to {endDate} (yfinance)...")
        df = yf.download(self.ticker, start=startDate, end=endDate, interval=interval)

        # ✅ Handle no data at all
        if df.empty:
            log.warning("No price data found. Returning empty DataFrame.")
            return pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "volume"])

        # ✅ Flatten MultiIndex if needed
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(col).strip().lower() for col in df.columns.values]
        else:
            df.columns = [c.lower() for c in df.columns]

        # ✅ Reset index
        df = df.reset_index()

        # ✅ Normalize datetime column
        if "datetime" in df.columns:
            pass
        elif "date" in df.columns:
            df.rename(columns={"date": "datetime"}, inplace=True)
        else:
            log.warning("No datetime column found, creating placeholder.")
            df["datetime"] = pd.NaT

        # ✅ Ensure OHLCV columns exist
        required_cols = ["open", "high", "low", "close", "volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            log.warning(f"Missing OHLC columns from yfinance data: {missing_cols}. Filling with NaN/dummy values.")
            for col in missing_cols:
                if col == "volume":
                    df[col] = 1
                else:
                    df[col] = float("nan")

        # ✅ Safe volume check
        vol_series = df["volume"]
        no_volume_column = "volume" not in df.columns
        volume_all_na = bool(vol_series.isna().all())
        volume_all_zero = bool((vol_series == 0).all())
        if no_volume_column or volume_all_na or volume_all_zero:
            log.warning("No valid volume data. Filling with dummy values.")
            df["volume"] = 1

        # ✅ Final selection & sorting
        df = df[["datetime", "open", "high", "low", "close", "volume"]]
        df = df.sort_values("datetime").reset_index(drop=True)

        log.info(f"Retrieved {len(df)} rows of price data for {self.ticker}.")
        return df

    def _fetchFromTradovate(self, startDate, endDate, interval):
        """
        Placeholder for Tradovate API historical fetch.
        Replace with actual Tradovate API call in Phase 2.
        """
        log.error("Tradovate API fetch not implemented yet.")
        return pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "volume"])
