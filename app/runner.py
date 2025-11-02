from core.risk_engine import RiskEngine
from core.signal_engine import SignalEngine
from core.execution_engine import ExecutionEngine
from core.backtest_engine import BacktestEngine
from core.data_loader import load_price_data

class TradingSystemRunner:
    def __init__(self, config):
        self.config = config
        self.risk_engine = RiskEngine(config.risk)
        self.signal_engine = SignalEngine(config.strategy)
        self.execution_engine = ExecutionEngine(config.exec)
        self.backtester = BacktestEngine(config, self.signal_engine, self.risk_engine, self.execution_engine)

    def run_backtest(self, data_source=None):
        data = load_price_data(data_source)
        result = self.backtester.run(data)
        print(f"\n✅ Backtest complete:\n{result}")
        return result

    def run_live(self):
        raise NotImplementedError("Live trading integration not implemented yet.")

