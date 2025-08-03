# Analysis/Sentiment.py

import pandas as pd
from textblob import TextBlob
import logging

log = logging.getLogger(__name__)

def analyzeSentiment(newsData):
    """
    Takes a DataFrame of news headlines with 'datetime' and 'title'.
    Returns DataFrame with sentiment_score: 
      1 for bullish, -1 for bearish, 0 for neutral.
    """
    if newsData is None or newsData.empty:
        log.warning("No news data provided for sentiment analysis.")
        return pd.DataFrame(columns=["datetime", "sentiment_score"])

    sentiment_scores = []
    for _, row in newsData.iterrows():
        title = row.get("title", "")
        if not title:
            sentiment_scores.append(0)
            continue

        # Basic polarity scoring
        polarity = TextBlob(title).sentiment.polarity
        if polarity > 0.05:
            sentiment_scores.append(1)
        elif polarity < -0.05:
            sentiment_scores.append(-1)
        else:
            sentiment_scores.append(0)

    result_df = pd.DataFrame({
        "datetime": pd.to_datetime(newsData["datetime"]),
        "sentiment_score": sentiment_scores
    })

    log.info(f"Processed sentiment for {len(result_df)} headlines.")
    return result_df
