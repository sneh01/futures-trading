"""Clean BacktestEngine implementation.

Loads a strategy from `strategies.<name>` (if requested) or falls back to
the provided `signal_engine`. Simulates trades by forward-scanning each
entry for SL / TP hits and returns a summary and the trade list.
"""
from typing import Optional
import importlib
import pandas as pd


class BacktestEngine:
    def __init__(self, system, signal_engine, risk_engine, execution_engine):
        self.system = system
        self.signal_engine = signal_engine
        self.risk_engine = risk_engine
        self.execution_engine = execution_engine

    def _load_strategy_module(self, name: str):
        return importlib.import_module(f"strategies.{name}")

    def run(self, data: pd.DataFrame, strategy: Optional[str] = None, initial_balance: float = 10000.0, entry_prob: float = 0.02, seed: Optional[int] = None):
        """Run backtest using either a strategy module or the signal_engine.

        Returns a dict containing summary metrics and the raw trades list.
        """
        df = data.copy().reset_index(drop=True)

        # generate signals
        if strategy:
            mod = self._load_strategy_module(strategy)
            # validate strategy interface (raises on error)
            try:
                from strategies.base import validate_strategy

                validate_strategy(mod)
            except Exception:
                # re-raise with context
                raise

            df = mod.generate_signals(df, system=self.system, entry_prob=entry_prob, seed=seed)
        else:
            df = self.signal_engine.generate_signals(df)

        trades = []
        balance = float(initial_balance)
        i = 0
        n = len(df)

        def _get(s, col, default=None):
            return s[col] if col in s and not pd.isna(s[col]) else default

        while i < n:
            row = df.iloc[i]
            sig = int(_get(row, "signal", 0) or 0)
            if sig == 0:
                i += 1
                continue

            entry_price = float(row.close)
            stop_loss_ticks = int(_get(row, "stop_loss_ticks", getattr(self.system.risk, "stop_loss_ticks", 20)))
            rr = float(getattr(self.system.risk, "risk_to_reward", 2.0))
            tick_size = float(getattr(self.system.exec, "tick_size", 0.25))

            sl = _get(row, "sl", entry_price - stop_loss_ticks * tick_size * (1 if sig > 0 else -1))
            tp = _get(row, "tp", entry_price + stop_loss_ticks * tick_size * rr * (1 if sig > 0 else -1))

            pos_size = self.risk_engine.calculate_position_size(balance, stop_loss_ticks)

            # default exit to last row
            exit_price = float(df.iloc[-1].close)
            exit_idx = n - 1
            win = False

            for j in range(i + 1, n):
                fut = df.iloc[j]
                low = _get(fut, "low", fut.close)
                high = _get(fut, "high", fut.close)

                if sig > 0:
                    if low <= sl:
                        exit_price = sl
                        exit_idx = j
                        win = False
                        break
                    if high >= tp:
                        exit_price = tp
                        exit_idx = j
                        win = True
                        break
                else:
                    if high >= sl:
                        exit_price = sl
                        exit_idx = j
                        win = False
                        break
                    if low <= tp:
                        exit_price = tp
                        exit_idx = j
                        win = True
                        break

            pnl = (exit_price - entry_price) * sig * pos_size
            balance += pnl

            trades.append({
                "entry_idx": i,
                "exit_idx": exit_idx,
                "entry": entry_price,
                "exit": exit_price,
                "pnl": pnl,
                "pos_size": pos_size,
                "win": win,
            })

            # move to the next bar after the exit
            i = exit_idx + 1

        total_pnl = sum(t["pnl"] for t in trades)
        wins = sum(1 for t in trades if t["win"]) if trades else 0

        return {
            "num_trades": len(trades),
            "total_pnl": total_pnl,
            "win_rate": wins / len(trades) if trades else 0.0,
            "avg_pnl": total_pnl / len(trades) if trades else 0.0,
            "ending_balance": balance,
            "trades": trades,
        }
