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

        # Plot both equity curves: by trade number and by exit date (if available)
        import pandas as pd
        initial_balance = self.backtester.run.__defaults__[2]
        # By trade number
        equity_trade = [initial_balance]
        for t in result['trades']:
            equity_trade.append(equity_trade[-1] + t['pnl'])
        plt.figure(figsize=(10, 5))
        plt.plot(equity_trade, label='Equity Curve (by trade #)')
        plt.title('Backtest Equity Curve (by trade #)')
        plt.xlabel('Trade #')
        plt.ylabel('Equity')
        plt.legend()
        chart_path_trade = f"{run_dir}/equity_curve_by_trade.png"
        plt.savefig(chart_path_trade)
        plt.close()
        print(f"Equity curve (by trade #) saved to {chart_path_trade}")

        # By exit date (if possible)
        equity_time = [initial_balance]
        dates = []
        if not trades_df.empty and 'exit_idx' in trades_df.columns and 'pnl' in trades_df.columns:
            data_for_dates = load_price_data(data_source)
            if 'date' in data_for_dates.columns:
                for _, t in trades_df.iterrows():
                    idx = int(t['exit_idx'])
                    dates.append(data_for_dates.loc[idx, 'date'])
                    equity_time.append(equity_time[-1] + t['pnl'])
                equity_time = equity_time[1:]
                dates = pd.to_datetime(dates)
                plt.figure(figsize=(10, 5))
                plt.plot(dates, equity_time, label='Equity Curve (by exit date)')
                plt.title('Backtest Equity Curve (by exit date)')
                plt.xlabel('Date')
                plt.ylabel('Equity')
                plt.legend()
                chart_path_time = f"{run_dir}/equity_curve_by_time.png"
                plt.savefig(chart_path_time)
                plt.close()
                print(f"Equity curve (by exit date) saved to {chart_path_time}")

        return result

    def run_live(self):
        raise NotImplementedError("Live trading integration not implemented yet.")

