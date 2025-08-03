# Analysis/Correlation.py

import pandas as pd
import logging

log = logging.getLogger(__name__)

def correlateSentimentWithPrice(sentimentData, priceData, timeTolerance='30min'):
    """
    Merges sentiment and price data and calculates correlation between
    sentiment_score and next candle return.
    
    Parameters:
        sentimentData: DataFrame with datetime, sentiment_score
        priceData: DataFrame with datetime, open, high, low, close
        timeTolerance: tolerance window for merging sentiment to price

    Returns:
        correlation: float, merged_df: DataFrame
    """
    if sentimentData is None or sentimentData.empty:
        log.warning("No sentiment data provided for correlation.")
        return 0.0, pd.DataFrame()

    # Ensure datetime format
    sentimentData["datetime"] = pd.to_datetime(sentimentData["datetime"])
    priceData["datetime"] = pd.to_datetime(priceData["datetime"])

    # Merge sentiment with nearest price timestamp
    merged = pd.merge_asof(
        sentimentData.sort_values("datetime"),
        priceData.sort_values("datetime"),
        on="datetime",
        direction="nearest",
        tolerance=pd.Timedelta(timeTolerance)
    )

    if merged.empty:
        log.warning("No sentiment-price matches found within time tolerance.")
        return 0.0, merged

    # Calculate next candle return
    merged["return"] = merged["close"].pct_change().shift(-1)

    # Drop NaN values
    merged = merged.dropna(subset=["return", "sentiment_score"])

    # Calculate correlation
    if len(merged) > 1:
        correlation = merged["sentiment_score"].corr(merged["return"])
    else:
        correlation = 0.0

    log.info(f"Sentiment-Price correlation: {correlation:.4f}")
    return correlation if pd.notnull(correlation) else 0.0, merged
