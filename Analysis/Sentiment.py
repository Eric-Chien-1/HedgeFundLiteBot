import pandas as pd
from textblob import TextBlob
import logging

log = logging.getLogger(__name__)

def analyzeSentiment(newsData, min_words=5, polarity_threshold=0.1, aggregation_minutes=5):
    """
    Processes news headlines to compute aggregated sentiment scores over time windows,
    filtering out low-information or weak sentiment headlines.
    Returns tz-naive datetime DataFrame.
    """
    if newsData is None or newsData.empty:
        log.warning("No news data for sentiment analysis.")
        return pd.DataFrame(columns=["datetime", "sentiment_score"])

    # Filter out very short headlines
    filtered = newsData[newsData["title"].str.split().str.len() >= min_words].copy()

    if filtered.empty:
        log.warning("No headlines left after filtering short titles.")
        return pd.DataFrame(columns=["datetime", "sentiment_score"])

    # Compute polarity
    filtered["polarity"] = filtered["title"].apply(lambda x: TextBlob(x).sentiment.polarity)

    # Filter out weak polarity
    filtered = filtered[filtered["polarity"].abs() >= polarity_threshold]

    if filtered.empty:
        log.warning("No headlines left after filtering weak polarity.")
        return pd.DataFrame(columns=["datetime", "sentiment_score"])

    # Assign discrete sentiment
    filtered["sentiment"] = filtered["polarity"].apply(lambda p: 1 if p > 0 else -1)

    # Convert datetime, remove timezone info, set as index
    filtered["datetime"] = pd.to_datetime(filtered["datetime"]).dt.tz_localize(None)
    filtered.set_index("datetime", inplace=True)

    # Aggregate by time window
    aggregated = filtered["sentiment"].resample(f"{aggregation_minutes}min").mean().dropna()


    # Convert mean sentiment to discrete +1/-1
    aggregated = aggregated.apply(lambda x: 1 if x > 0 else -1)

    # Reset index and ensure tz-naive
    result_df = aggregated.reset_index().rename(columns={"sentiment": "sentiment_score"})
    result_df["datetime"] = pd.to_datetime(result_df["datetime"]).dt.tz_localize(None)

    log.info(f"Processed and aggregated sentiment for {len(result_df)} time windows.")
    return result_df
