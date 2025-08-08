import time
from datetime import datetime, date, time as dtime, timedelta
import pytz

from config.config import Config
from Backtester.BacktestEngine import Engine
from Scrapers.PriceScraper import PriceScraper
from utils.DataCleaner import clean_ohlcv

# 1) Define your trading window in CST
CST = pytz.timezone("America/Chicago")
MARKET_OPEN  = dtime(8, 30)
MARKET_CLOSE = dtime(17, 0)

def is_market_open(now: datetime) -> bool:
    # only Monday–Friday
    if now.weekday() >= 5:  
        return False
    local = now.astimezone(CST)
    return MARKET_OPEN <= local.time() <= MARKET_CLOSE

def seconds_until(target: dtime, now: datetime) -> int:
    local = now.astimezone(CST)
    today_target = datetime.combine(local.date(), target, tzinfo=CST)
    if local.time() >= target:
        # schedule for tomorrow
        today_target += timedelta(days=1)
    return int((today_target - local).total_seconds())

def run_trading_cycle():
    # replace with your live/paper trading call instead of backtest
    today = date.today().strftime("%Y-%m-%d")
    scraper = PriceScraper(Config.symbol)
    raw = scraper.getHistoricalData(today, today)
    df = clean_ohlcv(raw, source_name="RunLoop")
    
    engine = Engine(Config)
    # engine.runLive or engine.runBacktest(...) as appropriate
    results = engine.runBacktest(Config.symbol, today, today, priceData=df)
    # you can log or act on results here

if __name__ == "__main__":
    print("Starting market‐watcher. Ctrl+C to quit.")
    while True:
        now = datetime.now(pytz.utc)
        if is_market_open(now):
            try:
                run_trading_cycle()
            except Exception as e:
                logging.exception("Error during trading cycle:")
            # wait until next bar close (e.g. 30m bars): 
            time.sleep(60 * 60 * 0.5)  # sleep 30 minutes
        else:
            # sleep until next market open
            sec = seconds_until(MARKET_OPEN, now)
            print(f"Market closed. Sleeping {sec//3600}h{(sec%3600)//60}m until open.")
            time.sleep(sec + 5)  # small buffer
