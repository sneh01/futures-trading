# Futures Trading Bot

This project is a modular futures trading bot framework designed for both **backtesting** and **live trading**.
It supports configurable risk/reward, pluggable strategies, and clear separation between engines.

## Features
- Risk Engine for consistent R:R trades
- Signal Engine (MA crossover example)
- Execution Engine (MockBroker + Live adapter)
- Config-driven design
- Backtest mode switchable to Live mode
- Expandable structure for future frontend or API integrations

## Folder Structure
```
core/        -> shared models and config
engines/     -> risk, signal, execution modules
data/        -> data adapters and loaders
strategies/  -> trading strategies and logic
backtest/    -> backtesting engine and reports
live/        -> live trading adapters (brokers)
frontend/    -> dashboard or control panel
```

## How to Run Backtest
1. Install dependencies:
   ```bash
   pip install pydantic pandas numpy matplotlib
   ```
2. Run:
   ```bash
   python main.py
   ```
3. Check the console output for results.

## How to Switch to Live Mode
Edit `config/config.json`:
```json
{
  "mode": "live"
}
```
Then run `python main.py` again.

## Next Steps
- Implement a frontend dashboard (e.g., Streamlit)
- Add more strategies
- Connect to real broker APIs
