import requests
import pandas as pd
import logging

log = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self, apiKey, query="stock market"):
        self.apiKey = apiKey
        self.query = query
        self.baseUrl = "https://newsapi.org/v2/everything"

    def scrapeNews(self, startDate, endDate):
        """
        Fetch news articles between startDate and endDate.
        Returns tz-naive datetime DataFrame.
        """
        log.info(f"Fetching news for '{self.query}' from {startDate} to {endDate}...")

        params = {
            "q": self.query,
            "from": startDate,
            "to": endDate,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": self.apiKey,
            "pageSize": 100
        }

        try:
            response = requests.get(self.baseUrl, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            log.error(f"News API request failed: {e}")
            return pd.DataFrame(columns=["datetime", "title"])

        articles = response.json().get("articles", [])
        if not articles:
            log.warning("No news articles found for this date range.")
            return pd.DataFrame(columns=["datetime", "title"])

        titles, datetimes = [], []
        for article in articles:
            title = article.get("title")
            published_at = article.get("publishedAt")
            if title and published_at:
                titles.append(title)
                datetimes.append(pd.to_datetime(published_at))

        # Create DataFrame
        df = pd.DataFrame({"datetime": datetimes, "title": titles})

        # Normalize datetime to tz-naive
        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)

        # Sort chronologically
        df = df.sort_values("datetime").reset_index(drop=True)

        log.info(f"Retrieved {len(df)} news articles for '{self.query}'.")
        return df
