import requests
import websocket
import threading
import json
from datetime import datetime
from config.config import config  # Assuming config.py is in the config/ folder

class TradovateData:
    def __init__(self, clientId: str, accessToken: str):
        self.clientId = clientId
        self.accessToken = accessToken
        self.baseUrl = config.TRADOVATE_BASE_URL
        self.wsUrl = config.TRADOVATE_WS_URL
        self.headers = {
            "Authorization": f"Bearer {self.accessToken}"
        }

    def getHistoricalData(self, symbol: str, interval: str, start: str, end: str):
        """
        Fetch historical data from Tradovate.

        :param symbol: e.g., 'MNQU4'
        :param interval: 'Minute', 'Daily', etc.
        :param start: ISO 8601 timestamp (e.g., '2024-08-01T13:30:00Z')
        :param end: ISO 8601 timestamp
        :return: List of OHLCV bars
        """
        instrumentUrl = f"{self.baseUrl}/contracts"
        r = requests.get(instrumentUrl, headers=self.headers)
        contracts = r.json()
        contractId = next((c['id'] for c in contracts if c['symbol'] == symbol), None)
        if not contractId:
            raise ValueError(f"Symbol '{symbol}' not found in Tradovate contracts.")

        url = f"{self.baseUrl}/md/history/{contractId}"
        params = {
            "startTimestamp": start,
            "endTimestamp": end,
            "interval": interval
        }
        resp = requests.get(url, headers=self.headers, params=params)
        if not resp.ok:
            raise Exception(f"Failed to fetch historical data: {resp.status_code} - {resp.text}")
        return resp.json()

    def streamTicks(self, symbol: str, callback):
        """
        Stream real-time quote data from Tradovate and pass each tick to callback.

        :param symbol: Symbol to subscribe (e.g., 'MNQU4')
        :param callback: Function to process each tick (dict)
        """
        def onOpen(ws):
            print("[Tradovate WS] Connected.")
            ws.send(json.dumps({
                "e": "authorize",
                "d": {"token": self.accessToken}
            }))
            ws.send(json.dumps({
                "e": "md/subscribeQuote",
                "d": {"symbol": symbol}
            }))

        def onMessage(ws, message):
            data = json.loads(message)
            if data.get("e") == "quote" and "d" in data:
                callback(data["d"])

        def onError(ws, error):
            print("[Tradovate WS] Error:", error)

        def onClose(ws, code, reason):
            print("[Tradovate WS] Closed:", code, reason)

        ws = websocket.WebSocketApp(
            self.wsUrl,
            on_open=onOpen,
            on_message=onMessage,
            on_error=onError,
            on_close=onClose
        )

        thread = threading.Thread(target=ws.run_forever)
        thread.daemon = True
        thread.start()
