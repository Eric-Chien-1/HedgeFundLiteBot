# Config.py

class Config:
    # API Keys
    newsApiKey = "815b8274e8f94a5db950c060865bb3db"

    # Backtest parameters
    startBalance = 5000
    riskPerTrade = 25
    rWin = 1.8
    rLoss = 1.0
    winProbability = 0.53

    # TQS settings
    tqsThreshold = 5

    # Monte Carlo settings
    numMonteCarloSimulations = 1000

    # Sentiment usage (controlled in Main.py based on testMode)
    useSentiment = True
