# Backtester/MonteCarlo.py

import numpy as np

class MonteCarlo:
    @staticmethod
    def run(trades, numSimulations=1000, startBalance=5000, riskPerTrade=25, rWin=1.8, rLoss=1.0):
        """
        Runs Monte Carlo simulations on the trade log.
        Returns (5th percentile, 50th percentile, 95th percentile) ending balances.
        """
        results = []
        outcomes = [t["outcome"] for t in trades]

        for _ in range(numSimulations):
            balance = startBalance
            shuffled = np.random.permutation(outcomes)
            for outcome in shuffled:
                if outcome == "WIN":
                    balance += rWin * riskPerTrade
                else:
                    balance -= rLoss * riskPerTrade
            results.append(balance)

        p5 = np.percentile(results, 5)
        p50 = np.percentile(results, 50)
        p95 = np.percentile(results, 95)
        return (round(p5, 2), round(p50, 2), round(p95, 2))
