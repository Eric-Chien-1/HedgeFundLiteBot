import pandas as pd
import logging
from utils.DataCleaner import sort_by_datetime_safe

log = logging.getLogger(__name__)

def correlateSentimentWithPrice(sentimentData, priceData, timeTolerance='30min'):
    """
    Merges sentiment and price data and calculates correlation between
    sentiment_score and next candle return.
    """
    if sentimentData is None or sentimentData.empty:
        log.warning("No sentiment data provided for correlation.")
        return 0.0, pd.DataFrame()

    # --- Always flatten indexes before merge ---
    sentimentData = pd.DataFrame(sentimentData).reset_index(drop=True)
    priceData = pd.DataFrame(priceData).reset_index(drop=True)

    # --- Ensure datetime column exists ---
    if "datetime" not in sentimentData.columns:
        log.error("Sentiment data missing 'datetime' column.")
        return 0.0, pd.DataFrame()

    if "datetime" not in priceData.columns:
        log.error("Price data missing 'datetime' column.")
        return 0.0, pd.DataFrame()

    # --- Ensure datetime format and remove timezone ---
    sentimentData["datetime"] = pd.to_datetime(sentimentData["datetime"]).dt.tz_localize(None)
    priceData["datetime"] = pd.to_datetime(priceData["datetime"]).dt.tz_localize(None)

    # ✅ Sort safely to avoid Pandas FutureWarning
    sentimentData = sort_by_datetime_safe(sentimentData, "datetime")
    priceData = sort_by_datetime_safe(priceData, "datetime")

    # --- Merge sentiment with nearest price timestamp ---
    try:
        merged = pd.merge_asof(
            sentimentData,
            priceData,
            on="datetime",
            direction="nearest",
            tolerance=pd.Timedelta(timeTolerance)
        )
    except Exception as e:
        log.error(f"Merge error: {e}")
        return 0.0, pd.DataFrame()

    if merged.empty:
        log.warning("No sentiment-price matches found within time tolerance.")
        return 0.0, merged

    # --- Calculate next candle return ---
    merged["return"] = (merged["close"] / merged["close"].shift(1) - 1).shift(-1)


    # --- Drop NaN values ---
    merged = merged.dropna(subset=["return", "sentiment_score"])

    # --- Calculate correlation ---
    if len(merged) > 1:
        correlation = merged["sentiment_score"].corr(merged["return"])
    else:
        correlation = 0.0

    log.info(f"Sentiment-Price correlation: {correlation:.4f}")
    return correlation if pd.notnull(correlation) else 0.0, merged
