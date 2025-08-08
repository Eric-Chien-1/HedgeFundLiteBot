from datetime import datetime, timedelta

class LiquidityZones:
    def __init__(self, priceData):
        self.priceData = priceData
        self.zones = self.getZones()

    def _filterByTimeRange(self, startTime, endTime):
        return [bar for bar in self.priceData if startTime <= datetime.fromisoformat(bar["timestamp"]) <= endTime]

    def getZones(self):
        now = datetime.utcnow()
        today = now.date()

        # Define session times in UTC
        asianStart = datetime.combine(today, datetime.min.time()) + timedelta(hours=0)   # 00:00 UTC
        asianEnd = asianStart + timedelta(hours=8)  # 00:00–08:00 UTC

        londonStart = asianEnd
        londonEnd = londonStart + timedelta(hours=4)  # 08:00–12:00 UTC

        nyStart = londonEnd
        nyEnd = nyStart + timedelta(hours=6.5)  # 12:00–18:30 UTC

        weekStart = now - timedelta(days=5)

        # Filter bars
        asianSession = self._filterByTimeRange(asianStart, asianEnd)
        londonSession = self._filterByTimeRange(londonStart, londonEnd)
        nySession = self._filterByTimeRange(nyStart, nyEnd)
        weeklyData = self._filterByTimeRange(weekStart, now)

        return {
            "asianLow": min(bar["low"] for bar in asianSession) if asianSession else None,
            "asianHigh": max(bar["high"] for bar in asianSession) if asianSession else None,
            "londonLow": min(bar["low"] for bar in londonSession) if londonSession else None,
            "londonHigh": max(bar["high"] for bar in londonSession) if londonSession else None,
            "nyLow": min(bar["low"] for bar in nySession) if nySession else None,
            "nyHigh": max(bar["high"] for bar in nySession) if nySession else None,
            "weeklyHigh": max(bar["high"] for bar in weeklyData) if weeklyData else None,
            "weeklyLow": min(bar["low"] for bar in weeklyData) if weeklyData else None
        }

    def detectSweep(self, currentPrice, zoneName, tickSize=0.25, toleranceTicks=4):
        """
        Detects a potential liquidity sweep based on proximity to a session low/high.

        :param currentPrice: Latest price
        :param zoneName: e.g. 'nyLow', 'londonHigh'
        :param tickSize: Futures tick size (e.g. 0.25 for NQ)
        :param toleranceTicks: Max distance from zone to still count as a sweep
        :return: True if sweep detected, else False
        """
        zoneLevel = self.zones.get(zoneName)
        if zoneLevel is None:
            return False

        distance = abs(currentPrice - zoneLevel)

        isLowSweep = "Low" in zoneName and currentPrice < zoneLevel
        isHighSweep = "High" in zoneName and currentPrice > zoneLevel

        return (isLowSweep or isHighSweep) and distance <= tickSize * toleranceTicks

    def isSweepConfirmed(self, currentPrice, zoneName):
        """
        Confirms a sweep if price has moved back past the swept zone.
        :param currentPrice: Latest price
        :param zoneName: Zone that was swept (e.g. 'nyLow', 'londonHigh')
        :return: True if confirmed reversal
        """
        zoneLevel = self.zones.get(zoneName)
        if zoneLevel is None:
            return False

        if "Low" in zoneName:
            return currentPrice > zoneLevel
        elif "High" in zoneName:
            return currentPrice < zoneLevel
        return False
