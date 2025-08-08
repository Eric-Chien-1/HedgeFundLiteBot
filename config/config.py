import os
from dotenv import load_dotenv

load_dotenv()

# Tradovate Config
TRADOVATE_CLIENT_ID = os.getenv("TRADOVATE_CLIENT_ID")
TRADOVATE_ACCESS_TOKEN = os.getenv("TRADOVATE_ACCESS_TOKEN")
TRADOVATE_BASE_URL = "https://demo.tradovateapi.com/v1"
TRADOVATE_WS_URL = "wss://md-demo.tradovateapi.com/v1/websocket"

# Benzinga Config
BENZINGA_API_KEY = os.getenv("BENZINGA_API_KEY")
BENZINGA_BASE_URL = os.getenv("BENZINGA_BASE_URL", "https://api.benzinga.com/api/v2/news")

# TQS Thresholds
TQS_TRADE_THRESHOLD = float(os.getenv("TQS_TRADE_THRESHOLD", 5.0))
TQS_WATCHLIST_THRESHOLD = float(os.getenv("TQS_WATCHLIST_THRESHOLD", 3.5))
DEFAULT_SWEEP_ZONE = os.getenv("TQS_SWEEP_ZONE", "londonLow")

# Logging
TQS_LOG_PATH = os.getenv("TQS_LOG_PATH", "signals_log.csv")
