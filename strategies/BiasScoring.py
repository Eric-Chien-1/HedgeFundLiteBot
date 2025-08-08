from  analysis.SentimentAnalysis import SentimentAnalysis

class BiasScoring:
    def __init__(self, newsData):
        self.newsData = newsData

    def getBiasScore(self, symbol: str, direction: str, startDate=None, endDate=None) -> float:
        """
        Fetches headlines and scores bias alignment.
        Returns 1.0 if sentiment supports direction, 0.0 otherwise.
        """
        headlines = self.newsData.getNews(symbol, startDate, endDate)
        sentimentAnalyzer = SentimentAnalysis(headlines)
        score = sentimentAnalyzer.scoreBiasDirection()

        if direction == "long" and score > 0:
            return 1.0
        elif direction == "short" and score < 0:
            return 1.0
        else:
            return 0.0
