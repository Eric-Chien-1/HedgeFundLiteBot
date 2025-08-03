# Strategy/Scanner.py

import numpy as np
import pandas as pd
import logging

class Scanner:
    def __init__(self, config):
        self.config = config
        self.log = logging.getLogger(__name__)

    # =========================
    # Indicator Calculations
    # =========================
    def _calculateIndicators(self, priceData):
        """Pre-calculate RVOL, MACD, and RSI."""
        df = priceData.copy()

        # RVOL
        df["avg_vol"] = df["volume"].rolling(window=20).mean()
        df["rvol"] = df["volume"] / df["avg_vol"]

        # MACD
        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        df["macd_line"] = ema12 - ema26
        df["macd_signal"] = df["macd_line"].ewm(span=9, adjust=False).mean()

        # RSI
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        return df

    # =========================
    # Confirmation Scoring
    # =========================
    def _confirmationScore(self, row, direction):
        score = 0

        # RVOL
        if pd.notnull(row.get("rvol")) and row["rvol"] >= 1.5:
            score += 1

        # MACD alignment
        if pd.notnull(row.get("macd_line")) and pd.notnull(row.get("macd_signal")):
            if direction == "LONG" and row["macd_line"] > row["macd_signal"]:
                score += 0.5
            elif direction == "SHORT" and row["macd_line"] < row["macd_signal"]:
                score += 0.5

        # RSI alignment
        if pd.notnull(row.get("rsi")):
            if direction == "LONG" and row["rsi"] > 50:
                score += 0.5
            elif direction == "SHORT" and row["rsi"] < 50:
                score += 0.5

        return score

    # =========================
    # TQS Calculation
    # =========================
    def calculateTqs(self, row, sentimentScore, priceData, direction):
        patternScore = 0
        idx = priceData.index.get_loc(row.name)

        # Breakout
        if idx > 1:
            prev_high = priceData.loc[idx - 1, "high"]
            prev_low = priceData.loc[idx - 1, "low"]
            if row["close"] > prev_high:
                patternScore += 1
            elif row["close"] < prev_low:
                patternScore += 1

        # Support/Resistance Bounce
        if idx > 5:
            recent_high = priceData.loc[idx - 5:idx, "high"].max()
            recent_low = priceData.loc[idx - 5:idx, "low"].min()
            if abs(row["low"] - recent_low) < (row["close"] * 0.002):
                patternScore += 1
            elif abs(row["high"] - recent_high) < (row["close"] * 0.002):
                patternScore += 1

        # BOS (Break of Structure)
        if idx > 3:
            if (row["high"] > priceData.loc[idx - 1, "high"] and
                priceData.loc[idx - 1, "low"] > priceData.loc[idx - 2, "low"]):
                patternScore += 2
            elif (row["low"] < priceData.loc[idx - 1, "low"] and
                  priceData.loc[idx - 1, "high"] < priceData.loc[idx - 2, "high"]):
                patternScore += 2

        # Sweep (Fakeout)
        if idx > 2:
            if (row["high"] > priceData.loc[idx - 1, "high"] and row["close"] < priceData.loc[idx - 1, "close"]):
                patternScore += 1.5
            elif (row["low"] < priceData.loc[idx - 1, "low"] and row["close"] > priceData.loc[idx - 1, "close"]):
                patternScore += 1.5

        # Confirmation score
        confirmationScore = self._confirmationScore(row, direction)

        # Sentiment adjustment
        sentimentScoreAdj = 0
        if self.config.useSentiment:
            sentimentScoreAdj = 1 if sentimentScore > 0 else (-1 if sentimentScore < 0 else 0)

        # Final TQS
        tqs = patternScore + confirmationScore + sentimentScoreAdj
        return tqs

    # =========================
    # Sentiment Matching
    # =========================
    def getSentimentForTime(self, timestamp, sentimentData):
        if not self.config.useSentiment or sentimentData is None or sentimentData.empty:
            return 0
        closest = sentimentData.iloc[
            (sentimentData["datetime"] - timestamp).abs().argsort()[:1]
        ]
        if not closest.empty:
            return int(closest["sentiment_score"].values[0])
        return 0

    # =========================
    # Scan for Trades
    # =========================
    def scan(self, priceData, sentimentData=None):
        trades = []
        priceData = self._calculateIndicators(priceData)

        # SMA5 for technical-only mode
        if not self.config.useSentiment:
            priceData["sma5"] = priceData["close"].rolling(window=5).mean()

        for _, row in priceData.iterrows():
            sentimentScore = self.getSentimentForTime(row["datetime"], sentimentData)

            if self.config.useSentiment:
                direction = "LONG" if sentimentScore > 0 else "SHORT"
            else:
                if pd.notnull(row.get("sma5")) and row["close"] > row["sma5"]:
                    direction = "LONG"
                else:
                    direction = "SHORT"

            tqs = self.calculateTqs(row, sentimentScore, priceData, direction)

            if tqs >= self.config.tqsThreshold:
                trades.append({
                    "datetime": row["datetime"],
                    "tqs": tqs,
                    "sentimentScore": sentimentScore,
                    "direction": direction
                })
        return trades

    # =========================
    # Trade Simulation
    # =========================
    def runSimulation(self, trades):
        balance = self.config.startBalance
        wins = 0
        losses = 0
        tradeLog = []

        for trade in trades:
            win = np.random.rand() < self.config.winProbability
            if win:
                profit = self.config.rWin * self.config.riskPerTrade
                balance += profit
                wins += 1
                outcome = "WIN"
            else:
                loss = self.config.rLoss * self.config.riskPerTrade
                balance -= loss
                losses += 1
                outcome = "LOSS"

            tradeLog.append({
                **trade,
                "balance": balance,
                "outcome": outcome
            })

        winRate = wins / max(1, (wins + losses))
        ev = (winRate * self.config.rWin) - ((1 - winRate) * self.config.rLoss)

        return tradeLog, balance, winRate, ev
