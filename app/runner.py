from core.risk_engine import RiskEngine
from core.signal_engine import SignalEngine
from core.execution_engine import ExecutionEngine
from core.backtest_engine import BacktestEngine
from core.data_loader import load_price_data

class TradingSystemRunner:
    def __init__(self, config):
        print("\n++ Initializing Trading System ++")
        self.config = config
        self.risk_engine = RiskEngine(config.risk)
        # Prefer an explicit strategy name when available so SignalEngine imports
        # `strategies.<name>`. Fallback to passing the full strategy config object
        # (SignalEngine handles both forms).
        # Pass the full strategy config object so SignalEngine can both import the
        # named module (if `name` is set) and keep access to `params` for the
        # strategy module or downstream code.
        self.signal_engine = SignalEngine(config.strategy)
        self.execution_engine = ExecutionEngine(config.exec)
        self.backtester = BacktestEngine(config, self.signal_engine, self.risk_engine, self.execution_engine)

    def run_backtest(self, data_source=None):
        print("\n++ Running Backtest ++")
        data = load_price_data(data_source)
        result = self.backtester.run(data)
        print(f"\n✅ Backtest complete:\n{result}")
        return result

    def run_live(self):
        raise NotImplementedError("Live trading integration not implemented yet.")

