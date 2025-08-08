class DataCleaner:
    @staticmethod
    def cleanBars(bars):
        """Remove bars missing required fields."""
        return [
            bar for bar in bars
            if all(key in bar for key in ["timestamp", "open", "high", "low", "close"])
        ]

    @staticmethod
    def sortBarsByTime(bars):
        return sorted(bars, key=lambda b: b["timestamp"])

    @staticmethod
    def isValidTick(tick):
        return isinstance(tick, dict) and tick.get("last") is not None

    @staticmethod
    def normalizeTimestamp(bar):
        ts = bar.get("timestamp")
        if ts and isinstance(ts, str) and not ts.endswith("Z"):
            bar["timestamp"] = ts + "Z"
        return bar
