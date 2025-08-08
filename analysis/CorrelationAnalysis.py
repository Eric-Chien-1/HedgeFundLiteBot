import pandas as pd

class CorrelationAnalysis:
    def __init__(self, signalLogPath: str):
        self.signalLogPath = signalLogPath

    def loadSignals(self) -> pd.DataFrame:
        df = pd.read_csv(self.signalLogPath)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def calculateCorrelation(self, priceData: pd.DataFrame, outcomeColumn: str = "close"):
        """
        Compares historical signal score to future price direction.
        Assumes priceData includes 'timestamp' and outcomeColumn (e.g., future close).
        """
        df = self.loadSignals()
        merged = pd.merge_asof(df.sort_values("timestamp"),
                               priceData.sort_values("timestamp"),
                               on="timestamp", direction="forward")

        if outcomeColumn not in merged:
            raise ValueError(f"{outcomeColumn} not in price data")

        return merged["score"].corr(merged[outcomeColumn].pct_change().fillna(0))

    def analyzeByComponent(self):
        df = self.loadSignals()
        # Each component encoded as "1.0: MACD aligned"
        componentCounts = {}
        for row in df["breakdown"]:
            parts = [p.strip() for p in row.split(";")]
            for p in parts:
                if ":" in p:
                    component = p.split(":", 1)[1].strip()
                    componentCounts[component] = componentCounts.get(component, 0) + 1

        return dict(sorted(componentCounts.items(), key=lambda item: item[1], reverse=True))
