# Tests/TqsDebugTest.py

import yfinance as yf
import pandas as pd
import numpy as np
import logging
from Strategy.Scanner import Scanner
from Config import Config

# ====== LOGGING SETUP ======
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ====== CONFIG ======
SYMBOL = "MES=F"
DAYS = 30  # last 30 days
INTERVAL = "30m"
OUTPUT_CSV = "TqsDebugResults.csv"

# ====== FETCH REAL MES DATA ======
log.info(f"Downloading {DAYS} days of {SYMBOL} data...")
df = yf.download(SYMBOL, period=f"{DAYS}d", interval=INTERVAL)

if df.empty:
    raise ValueError(f"No price data found for {SYMBOL}.")

df = df.reset_index()
df.rename(columns={"Datetime": "datetime"}, inplace=True)
df["datetime"] = pd.to_datetime(df["datetime"])
df = df[["datetime", "open", "high", "low", "close", "volume"]]

# ====== INJECT RANDOM SENTIMENT FOR TEST ======
np.random.seed(42)
sentiment_values = np.random.choice([1, -1, 0], size=len(df))
sentiment_df = pd.DataFrame({
    "datetime": df["datetime"],
    "sentiment_score": sentiment_values
})

# ====== CREATE SCANNER ======
scanner = Scanner(Config)
Config.useSentiment = True  # Force sentiment mode ON for testing

# ====== STORAGE FOR CSV ======
results = []

# ====== DEBUG TQS FUNCTION ======
def debug_tqs(row, sentimentScore, priceData, direction):
    """Calculate and log TQS breakdown for debug purposes."""
    tqs = scanner.calculateTqs(row, sentimentScore, priceData, direction)

    pattern_score = round(tqs - (1 if sentimentScore > 0 else (-1 if sentimentScore < 0 else 0)), 2)
    confirmation_score = round(scanner._confirmationScore(row, direction), 2)
    sentiment_adj = 1 if sentimentScore > 0 else (-1 if sentimentScore < 0 else 0)

    log.info(f"[TRADE] {row['datetime']}")
    log.info(f"  Pattern Score: {pattern_score}")
    log.info(f"  Confirmation Score: {confirmation_score}")
    log.info(f"  Sentiment Adj: {sentiment_adj}")
    log.info(f"  Final TQS: {tqs:.2f}")
    log.info(f"  Direction: {direction}")

    results.append({
        "datetime": row["datetime"],
        "pattern_score": pattern_score,
        "confirmation_score": confirmation_score,
        "sentiment_adj": sentiment_adj,
        "final_tqs": round(tqs, 2),
        "direction": direction
    })

    return tqs

# ====== RUN SCAN WITH BREAKDOWN ======
df = scanner._calculateIndicators(df)
df["sma5"] = df["close"].rolling(window=5).mean()

for _, row in df.iterrows():
    sentimentScore = scanner.getSentimentForTime(row["datetime"], sentiment_df)
    direction = "LONG" if sentimentScore > 0 else "SHORT"
    tqs = debug_tqs(row, sentimentScore, df, direction)

# ====== SAVE TO CSV ======
pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
log.info(f"TQS debug results saved to {OUTPUT_CSV}")
