# HedgeFundLiteBot - Phase 1 Backtester

This project is the Phase 1 modular backtesting engine for the HedgeFundLite futures trading bot.  
It combines historical price data, news sentiment analysis, and trade quality scoring (TQS) to simulate trades and evaluate performance.

---

## Features

- Historical price data scraping via yfinance (MES, MNQ, and others)
- News scraping via NewsAPI with sentiment scoring using TextBlob
- Pattern-based trade detection (BOS, Sweep, Breakout, S/R Bounce)
- Confirmation scoring with RVOL, MACD, RSI
- Sentiment integration with auto-disable for long backtests
- Monte Carlo simulations for robustness testing
- Quick / Medium / Long test modes for flexible backtesting windows
- Trade Quality Score (TQS) debugging tool with detailed logs and CSV output

---

## Project Structure

HedgeFundLiteBot/
│
├── Config.py
├── Main.py
├── requirements.txt
├── README.md
│
├── Backtester/
│ ├── Engine.py
│ ├── MonteCarlo.py
│
├── Strategy/
│ ├── Scanner.py
│
├── Analysis/
│ ├── Sentiment.py
│ ├── Correlation.py
│
├── Scrapers/
│ ├── NewsScraper.py
│ ├── PriceScraper.py
│
└── Tests/
├── TqsDebugTest.py


---

## Installation

Install all dependencies:

```bash
pip install -r requirements.txt
Running Backtests
Run a backtest for a symbol over a date range or a test mode window:

bash
Copy
python Main.py --mode backtest --symbol MES --testMode quick
Options for --testMode:

quick: Last 30 days (sentiment + technical)

medium: Last 60 days (sentiment + technical)

long: Last 365 days (technical-only; sentiment disabled)

Or specify custom dates:

bash
Copy
python Main.py --mode backtest --symbol MES --start 2023-01-01 --end 2023-06-01
TQS Debug Tool
Run the TQS debugging tool to see detailed scoring on real MES data:

bash
Copy
python Tests/TqsDebugTest.py
This prints detailed pattern, confirmation, and sentiment scores per trade and saves a CSV TqsDebugResults.csv.

Phase 2: Live & Paper Trading (Planned)
The Phase 2 extension will add:

Live price and news feeds from Rithmic, IBKR, or Tradovate

Real-time sentiment scoring with Benzinga or similar

Order execution with stop loss, take profit, and scaling

Real-time PnL and performance monitoring dashboard

Persistent data storage for model improvement

Backtester entry point will be extended with:

bash
Copy
python Main.py --mode live --symbol MES
Notes
Sentiment filtering is disabled automatically in long test mode due to NewsAPI historical data limits.

Confirmation factors (RVOL, MACD, RSI) help reduce false signals and improve quality scoring.

The project is modular and designed for easy extension into live trading and paper trading.

Contact: ericchien123@gmail.com
For questions or contributions, reach out anytime.

Thank you for using HedgeFundLiteBot!