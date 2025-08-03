# Main.py

import argparse
import logging
from datetime import datetime, timedelta
from Config import Config
from Backtester.Engine import Engine

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# Mode → date range mapping
TEST_MODE_RANGES = {
    "quick": 30,    # 30 days sentiment + technical
    "medium": 60,   # 60 days sentiment + technical
    "long": 365     # 1 year technical-only
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hedge-Fund-Lite Backtester")
    parser.add_argument("--mode", choices=["backtest"], required=True)
    parser.add_argument("--symbol", type=str, required=True)
    parser.add_argument("--start", type=str, default=None, help="YYYY-MM-DD")
    parser.add_argument("--end", type=str, default=None, help="YYYY-MM-DD")
    parser.add_argument("--testMode", choices=["quick", "medium", "long"], help="Pre-set test duration")
    args = parser.parse_args()

    # Determine date range and sentiment setting
    use_sentiment = True
    if args.testMode:
        days = TEST_MODE_RANGES[args.testMode]
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        if args.testMode == "long":
            use_sentiment = False
            log.warning("Long mode selected → Sentiment filtering DISABLED for reliability.")

        log.info(f"Test mode: {args.testMode.upper()} → {days} days ({start_date} to {end_date})")
    else:
        if not args.start or not args.end:
            raise ValueError("Must provide --start and --end if not using --testMode")
        start_date = args.start
        end_date = args.end

    # Run backtest
    if args.mode == "backtest":
        log.info(f"Starting backtest for {args.symbol} from {start_date} to {end_date}...")
        Config.useSentiment = use_sentiment
        engine = Engine(Config)
        results = engine.runBacktest(args.symbol, start_date, end_date)

        log.info("===== BACKTEST RESULTS =====")
        log.info(f"Final Balance: ${results['finalBalance']:,.2f}")
        log.info(f"Win Rate: {results['winRate']*100:.2f}%")
        log.info(f"Expected Value: {results['expectedValue']:.2f}R")
        log.info(f"Monte Carlo (5% / 50% / 95%): {results['monteCarlo']}")
