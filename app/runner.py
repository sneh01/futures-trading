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
        import os
        import pandas as pd
        import matplotlib.pyplot as plt
        from datetime import datetime
        print("\n++ Running Backtest ++")
        data = load_price_data(data_source)
        result = self.backtester.run(data)
        print(f"\n✅ Backtest complete:\n{result}")

        # Assume results directory already exists

        # Save results in a unique subfolder per run

        strategy_name = getattr(self.config.strategy, 'name', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        run_dir = f"results/{strategy_name}_{timestamp}"
        os.makedirs(run_dir, exist_ok=True)

        # Save trades to CSV
        trades_df = pd.DataFrame(result['trades'])
        csv_path = f"{run_dir}/trades.csv"
        trades_df.to_csv(csv_path, index=False)
        print(f"Trades saved to {csv_path}")

        # Save summary stats and config details to a text file
        stats = {
            'num_trades': result.get('num_trades'),
            'total_pnl': result.get('total_pnl'),
            'win_rate': result.get('win_rate'),
            'avg_pnl': result.get('avg_pnl'),
            'ending_balance': result.get('ending_balance'),
            'trades_per_day': result.get('trades_per_day'),
            'trades_per_week': result.get('trades_per_week'),
            'timestamp': timestamp
        }
        stats_path = f"{run_dir}/stats.txt"
        with open(stats_path, 'w') as f:
            for k, v in stats.items():
                f.write(f"{k}: {v}\n")
            f.write("\nConfig details:\n")
            import yaml
            yaml.dump(self.config, f, default_flow_style=False)
        print(f"Stats and config saved to {stats_path}")

        # Plot equity curve
        equity = [self.backtester.run.__defaults__[2]]  # initial_balance
        for t in result['trades']:
            equity.append(equity[-1] + t['pnl'])
        plt.figure(figsize=(10, 5))
        plt.plot(equity, label='Equity Curve')
        plt.title('Backtest Equity Curve')
        plt.xlabel('Trade #')
        plt.ylabel('Equity')
        plt.legend()
        chart_path = f"{run_dir}/equity_curve.png"
        plt.savefig(chart_path)
        plt.close()
        print(f"Equity curve saved to {chart_path}")

        return result

    def run_live(self):
        raise NotImplementedError("Live trading integration not implemented yet.")

