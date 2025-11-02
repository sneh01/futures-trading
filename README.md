// ...existing code...
# Futures Trading Bot

A modular futures trading bot framework for both backtesting and live trading. The project separates concerns into engines (signal, risk, execution), supports pluggable strategies, and is config-driven so you can iterate quickly between backtesting and live execution.

## Key Features
- Risk Engine for consistent risk:reward management
- Signal Engine (example: moving-average crossover)
- Execution Engine with a MockBroker and live adapter hooks
- Config-driven design (switch modes via config/settings.yaml)
- Clear folders to add strategies, data adapters, and brokers

## Repository layout
- main.py                         -> entry point to run backtests or live (root)
- config/
  - settings.yaml                  -> runtime configuration (mode, instruments, risk)
- core/                            -> shared models, types, and config helpers
- engines/
  - risk.py                        -> risk sizing and position management
  - signal.py                      -> signal generation interface & examples
  - execution.py                   -> execution abstractions
- strategies/
  - ma_crossover.py                -> example strategy implementation
- data/
  - adapters/                      -> CSV / exchange data loader adapters
  - loaders.py                     -> data loader helpers used by backtester
- backtest/
  - backtester.py                  -> backtest orchestration and report generation
  - reports/                       -> generated backtest artifacts
- live/
  - brokers/
    - mock_broker.py               -> simulated broker for local testing
    - live_adapter_template.py     -> template for real broker adapters
- frontend/                        -> (optional) dashboard or control panel
- requirements.txt                 -> pinned python dependencies
- README.md

## Quick setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS
   pip install -r requirements.txt
   ```
   If requirements.txt is not present, install the common libs:
   ```bash
   pip install pydantic pandas numpy matplotlib PyYAML
   ```

2. Edit configuration (optional):
   ```
   config/settings.yaml
   ```
   Example snippet:
   ```yaml
   mode: backtest   # or "live"
   instrument: "ES"
   start_date: "2023-01-01"
   end_date: "2023-12-31"
   risk:
     account_size: 100000
     risk_per_trade: 0.01
   strategy:
     name: "ma_crossover"
     params:
       fast: 10
       slow: 50
   ```

## Running

- Backtest (default):
  ```bash
  python main.py
  ```
  The backtester reads config/settings.yaml and runs using the specified data adapter and strategy. Results and basic reports are printed to the console and saved under backtest/reports/.

- Switch to Live Mode:
  Update `config/settings.yaml` setting `mode: live` and configure your broker adapter settings under `live/brokers/`. Then run:
  ```bash
  python app/main.py
  ```

## Adding a new strategy
1. Create a file under `strategies/`, e.g. `my_strategy.py`.
2. Implement the strategy following the required interface (export a `generate_signals(df, system, entry_prob=..., seed=None)` function). Register the strategy module name in the config under `strategy.name` and place any strategy parameters under `strategy.params`.
   Example `config/settings.yaml`:
   ```yaml
   strategy:
     name: "my_strategy"
     params:
       fast: 10
       slow: 50
   ```
3. Run the backtester to validate behavior on historical data.

## Adding a broker adapter
1. Copy `live/brokers/live_adapter_template.py` to a new file for your broker.
2. Implement required methods: connect, place_order, cancel_order, get_positions.
3. Wire credentials in `config/settings.yaml` (avoid committing secrets).

## Tests
If a tests directory exists, run:
```bash
pip install pytest
pytest
```

## Next steps / TODO
- Add more example strategies and parameter sweep utilities
- Implement realtime data adapters and order routing to real brokers
- Add a lightweight frontend (Streamlit) for strategy control and visualization

## Contributing
PRs welcome. Follow typical GitHub workflow: open an issue, create a branch, add tests/examples, and submit a PR.

## License
Add a LICENSE file to indicate project license.

```// filepath: /Users/snehpatel/Documents/code/futures-trading/README.md
// ...existing code...
# Futures Trading Bot

A modular futures trading bot framework for both backtesting and live trading. The project separates concerns into engines (signal, risk, execution), supports pluggable strategies, and is config-driven so you can iterate quickly between backtesting and live execution.

## Key Features
- Risk Engine for consistent risk:reward management
- Signal Engine (example: moving-average crossover)
- Execution Engine with a MockBroker and live adapter hooks
- Config-driven design (switch modes via config/settings.yaml)
- Clear folders to add strategies, data adapters, and brokers

## Repository layout
- main.py                         -> entry point to run backtests or live (root)
- config/
  - settings.yaml                  -> runtime configuration (mode, instruments, risk)
- core/                            -> shared models, types, and config helpers
- engines/
  - risk.py                        -> risk sizing and position management
  - signal.py                      -> signal generation interface & examples
  - execution.py                   -> execution abstractions
- strategies/
  - ma_crossover.py                -> example strategy implementation
- data/
  - adapters/                      -> CSV / exchange data loader adapters
  - loaders.py                     -> data loader helpers used by backtester
- backtest/
  - backtester.py                  -> backtest orchestration and report generation
  - reports/                       -> generated backtest artifacts
- live/
  - brokers/
    - mock_broker.py               -> simulated broker for local testing
    - live_adapter_template.py     -> template for real broker adapters
- frontend/                        -> (optional) dashboard or control panel
- requirements.txt                 -> pinned python dependencies
- README.md

## Quick setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS
   pip install -r requirements.txt
   ```
   If requirements.txt is not present, install the common libs:
   ```bash
   pip install pydantic pandas numpy matplotlib
   ```

2. Edit configuration (optional):
   ```
   config/settings.yaml
   ```
   Example snippet:
   ```yaml
   mode: backtest   # or "live"
   instrument: "ES"
   start_date: "2023-01-01"
   end_date: "2023-12-31"
   risk:
     account_size: 100000
     risk_per_trade: 0.01
   strategy:
     name: "ma_crossover"
     params:
       fast: 10
       slow: 50
   ```

## Running

- Backtest (default):
  ```bash
  python main.py
  ```
  The backtester reads config/settings.yaml and runs using the specified data adapter and strategy. Results and basic reports are printed to the console and saved under backtest/reports/.

- Switch to Live Mode:
  Update `config/settings.yaml` setting `mode: live` and configure your broker adapter settings under `live/brokers/`. Then run:
  ```bash
  python main.py
  ```

## Adding a new strategy
1. Create a file under `strategies/`, e.g. `my_strategy.py`.
2. Implement the strategy class following the example in `strategies/ma_crossover.py` and register its name in the config under `strategy.name`.
3. Run the backtester to validate behavior on historical data.

## Adding a broker adapter
1. Copy `live/brokers/live_adapter_template.py` to a new file for your broker.
2. Implement required methods: connect, place_order, cancel_order, get_positions.
3. Wire credentials in `config/settings.yaml` (avoid committing secrets).

## Tests
If a tests directory exists, run:
```bash
pip install pytest
pytest
```

## Next steps / TODO
- Add more example strategies and parameter sweep utilities
- Implement realtime data adapters and order routing to real brokers
- Add a lightweight frontend (Streamlit) for strategy control and visualization

## Contributing
PRs welcome. Follow typical GitHub workflow: open an issue, create a branch, add tests/examples, and submit a PR.

## License
Add a LICENSE file to indicate project license.
