import pandas as pd

class BacktestEngine:
    def __init__(self, system, signal_engine, risk_engine, execution_engine):
        self.system = system
        self.signal_engine = signal_engine
        self.risk_engine = risk_engine
        self.execution_engine = execution_engine

    def run(self, data: pd.DataFrame, initial_balance=10000):
        df = self.signal_engine.generate_signals(data.copy())
        trades = []
        balance = initial_balance

        for i, row in df.iterrows():
            if row.signal == 0:
                continue

            stop_loss_ticks = self.system.risk.stop_loss_ticks
            pos_size = self.risk_engine.calculate_position_size(balance, stop_loss_ticks)
            entry = row.close
            sl = entry - stop_loss_ticks * 0.25 * row.signal
            tp = entry + stop_loss_ticks * self.system.risk.risk_to_reward * 0.25 * row.signal

            pnl = self.execution_engine.execute_trade(row.signal, entry, sl, tp)
            balance += pnl * pos_size
            trades.append(pnl)

        summary = {
            "num_trades": len(trades),
            "total_pnl": sum(trades),
            "win_rate": sum(p > 0 for p in trades) / len(trades) if trades else 0,
            "avg_pnl": sum(trades) / len(trades) if trades else 0,
        }
        return summary
