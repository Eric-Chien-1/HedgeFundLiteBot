class SentimentAnalysis:
    def __init__(self, headlines: list):
        self.headlines = headlines

    def analyzeHeadlines(self):
        """
        Counts positive, negative, and neutral sentiment headlines.
        Expects each headline dict to contain a 'sentiment' field.
        """
        sentimentCounts = {"positive": 0, "negative": 0, "neutral": 0}

        for headline in self.headlines:
            sentiment = headline.get("sentiment", "").lower()
            if sentiment in sentimentCounts:
                sentimentCounts[sentiment] += 1

        return sentimentCounts

    def scoreBiasDirection(self) -> float:
        """
        Returns a directional bias score based on sentiment counts:
        +1.0 = bullish, -1.0 = bearish, 0.0 = neutral/mixed
        """
        counts = self.analyzeHeadlines()
        pos, neg = counts["positive"], counts["negative"]

        if pos > neg:
            return 1.0
        elif neg > pos:
            return -1.0
        else:
            return 0.0
