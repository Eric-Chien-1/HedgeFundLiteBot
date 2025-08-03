# HedgeFundLiteBot 🚀📈

Welcome to the **Phase 1** backtesting engine for your HedgeFundLite futures trading bot!  
This modular project combines price data, news sentiment, and smart trade quality scoring (TQS) to simulate and analyze trading performance.

---

## ✨ Features

- 📊 Historical price scraping via yfinance (MES, MNQ, others)  
- 📰 News scraping with NewsAPI + TextBlob sentiment analysis  
- 🔍 Pattern detection: BOS, Sweep, Breakout, Support/Resistance Bounce  
- ✅ Confirmation scoring: RVOL, MACD, RSI  
- 🤖 Sentiment integration (auto-disabled for long backtests)  
- 🎲 Monte Carlo simulations for robustness testing  
- 🕐 Quick / Medium / Long test modes for flexible backtesting  
- 🛠️ TQS Debug tool with detailed logs and CSV output  

---

## 🗂️ Project Structure

```bash
HedgeFundLiteBot/
├── Config.py
├── Main.py
├── requirements.txt
├── README.md

├── Backtester/
│ ├── Engine.py
│ ├── MonteCarlo.py
│ ├── RollingBacttesting.py

├── Strategy/
│ ├── Scanner.py

├── Analysis/
│ ├── Sentiment.py
│ ├── Correlation.py

├── Scrapers/
│ ├── NewsScraper.py
│ ├── PriceScraper.py

└── Tests/
├── TqsDebugTest.py
```
---

## ⚙️ Installation

Install dependencies with:  
```bash
pip install -r requirements.txt
```
---

## 🏁 Running Backtests

Run backtests easily with test modes:

```bash
python Main.py --mode backtest --symbol MES --testMode quick
```

Test modes:

• 🟢 quick (last 30 days, sentiment + technical)

• 🟡 medium (last 60 days, sentiment + technical)

• 🔴 long (last 365 days, technical-only, sentiment disabled)

Or custom date ranges:

```bash
python Main.py --mode backtest --symbol MES --start 2023-01-01 --end 2023-06-01
```

---

## 🏁 Running Multi-Symbol Backtests

You can now run backtests on multiple symbols in one go by using the `--symbols` argument with a comma-separated list:

```bash
python Main.py --mode backtest --symbols MES,NQ,ES --testMode quick
```

This will run the backtest sequentially for MES, NQ, and ES with the quick 30-day test mode.

## Output

• Individual trade logs will be saved as TradeLog_MES.csv, TradeLog_NQ.csv, TradeLog_ES.csv, etc.

• An aggregated summary CSV BacktestSummary.csv will be created with the key metrics for all symbols.

## Single Symbol Backtest

If you prefer to backtest a single symbol, use --symbol:

```bash
python Main.py --mode backtest --symbol MES --testMode medium
```
If neither --symbol nor --symbols is specified, the backtester defaults to the symbol set in Config.py (defaultSymbol).

## Custom Date Ranges

You can also specify exact start and end dates instead of using test modes:

```bash
python Main.py --mode backtest --symbol MES --start 2023-01-01 --end 2023-06-01

```
---

## 🔍 TQS Debug Tool

See detailed TQS scoring with:

```bash
python Tests/TqsDebugTest.py
```
Logs and CSV export let you explore exactly how trades are scored.

---

## 🚀 Phase 2: Live & Paper Trading (Planned)

Stay tuned for:

•⚡ Real-time price & news feeds

• 🤖 Live sentiment scoring (Benzinga or similar)

• 💹 Trade execution and position management

• 📊 Monitoring dashboards

• 🗄️ Persistent data storage

---

## 📬 Questions?

Reach out anytime — happy to help!

Thanks for choosing HedgeFundLiteBot! 🎉