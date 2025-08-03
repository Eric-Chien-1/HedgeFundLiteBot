import logging
from datetime import datetime, timedelta
from Scrapers.PriceScraper import PriceScraper
from Strategy.Scanner import Scanner
from config import Config
from utils.DataCleaner import clean_ohlcv

# ===== Logging setup =====
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ===== Test settings =====
symbol = "MES=F"
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)

log.info(f"Testing Quick mode for {symbol} from {start_date} to {end_date}...")

# ===== Step 1: Get historical price data =====
scraper = PriceScraper(symbol)
price_data = scraper.getHistoricalData(start_date, end_date)

if price_data.empty:
    log.error("❌ PriceScraper returned no data. Check your internet connection or symbol.")
    exit()
else:
    log.info(f"Retrieved {len(price_data)} rows of raw price data.")

# ===== Step 2: Clean OHLCV data before using it anywhere =====
cleaned_data = clean_ohlcv(price_data, source_name="QuickModeTest")

# ===== Step 3: Run through Scanner indicators =====
scanner = Scanner(Config)
indicators_df = scanner._calculateIndicators(cleaned_data)

# ===== Step 4: Check if dummy RVOL is in use =====
if "rvol" in indicators_df.columns:
    if indicators_df["rvol"].nunique() == 1 and indicators_df["rvol"].iloc[0] == 1:
        log.warning("⚠️ RVOL is running on dummy values — weekend/holiday or missing volume data detected.")
        log.warning("⚠️ Backtest results may be less meaningful until live market data is available.")

# ===== Step 5: Display sample output =====
log.info("Indicator calculation completed successfully.")
log.info(f"Sample output:\n{indicators_df.head(10)}")

# ===== Step 6: Final result =====
log.info("✅ Quick mode test finished without Pandas Series ambiguity or KeyError issues.")
