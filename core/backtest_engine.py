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

    def run(self, data: Optional[pd.DataFrame] = None, strategy: Optional[str] = None, initial_balance: float = 10000.0, entry_prob: float = 0.02, seed: Optional[int] = None):
        """Run backtest using either a strategy module or the signal_engine.

        If `data` is None, generates a random walk DataFrame for demonstration.
        Returns a dict containing summary metrics and the raw trades list.
        """
        if data is None:
            # Generate random walk OHLCV data
            import numpy as np
            np.random.seed(seed or 42)
            n = 10000  # number of bars
            price = 100 + np.cumsum(np.random.randn(n))
            df = pd.DataFrame({
                'open': price + np.random.uniform(-0.5, 0.5, n),
                'high': price + np.random.uniform(0, 1, n),
                'low': price - np.random.uniform(0, 1, n),
                'close': price,
                'volume': np.random.randint(100, 1000, n)
            })
        else:
            df = data.copy().reset_index(drop=True)
        """Run backtest using either a strategy module or the signal_engine.

        Returns a dict containing summary metrics and the raw trades list.
        """


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

            # Use MES tick value from config (default 1.25)
            tick_value = float(getattr(self.system.exec, "tick_value", 1.25))
            pos_size = self.risk_engine.calculate_position_size(balance, stop_loss_ticks, tick_value=tick_value)

            # default exit to last row
            exit_price = float(df.iloc[-1].close)
            exit_idx = n - 1

            exit_reason = None
            # print(f"\n[DEBUG] New trade: idx={i}, sig={sig}, entry={entry_price:.2f}, sl={sl:.2f}, tp={tp:.2f}, pos_size={pos_size}")
            # # Print price action for this trade
            # for j in range(i + 1, min(i + 21, n)):
            #     fut = df.iloc[j]
            #     low = _get(fut, "low", fut.close)
            #     high = _get(fut, "high", fut.close)
            #     close = _get(fut, "close", fut.close)
            #     print(f"  idx={j} high={high:.2f} low={low:.2f} close={close:.2f}")
            # print("  ... (showing up to 20 bars after entry)")
            for j in range(i + 1, n):
                fut = df.iloc[j]
                low = _get(fut, "low", fut.close)
                high = _get(fut, "high", fut.close)

                if sig > 0:
                    if low <= sl:
                        exit_price = sl
                        exit_idx = j
                        exit_reason = 'sl'
                        break
                    if high >= tp:
                        exit_price = tp
                        exit_idx = j
                        exit_reason = 'tp'
                        break
                else:
                    if high >= sl:
                        exit_price = sl
                        exit_idx = j
                        exit_reason = 'sl'
                        break
                    if low <= tp:
                        exit_price = tp
                        exit_idx = j
                        exit_reason = 'tp'
                        break

            # MES PnL: (exit - entry) * contracts * (tick_value / tick_size)
            pnl = (exit_price - entry_price) * sig * pos_size * (tick_value / tick_size)
            balance += pnl

            # Win is True if pnl > 0, else False
            win = pnl > 0

            trades.append({
                "entry_idx": i,
                "exit_idx": exit_idx,
                "entry": entry_price,
                "exit": exit_price,
                "pnl": pnl,
                "pos_size": pos_size,
                "win": win,
                "exit_reason": exit_reason,
            })

            # move to the next bar after the exit
            i = exit_idx + 1

        total_pnl = sum(t["pnl"] for t in trades)
        wins = sum(1 for t in trades if t["win"]) if trades else 0

        # Calculate trades per day and per week
        trades_per_day = None
        trades_per_week = None
        if trades:
            # Try to infer date index from df if present
            if 'date' in df.columns:
                entry_dates = [df.loc[t['entry_idx'], 'date'] for t in trades]
                entry_dates = pd.to_datetime(entry_dates)
                days = (entry_dates.max() - entry_dates.min()).days + 1
                weeks = max(1, days // 7)
                trades_per_day = len(trades) / days if days > 0 else None
                trades_per_week = len(trades) / weeks if weeks > 0 else None
            elif df.index.inferred_type == 'datetime64':
                entry_dates = [df.index[t['entry_idx']] for t in trades]
                entry_dates = pd.to_datetime(entry_dates)
                days = (entry_dates.max() - entry_dates.min()).days + 1
                weeks = max(1, days // 7)
                trades_per_day = len(trades) / days if days > 0 else None
                trades_per_week = len(trades) / weeks if weeks > 0 else None
        return {
            "num_trades": len(trades),
            "total_pnl": total_pnl,
            "win_rate": wins / len(trades) if trades else 0.0,
            "avg_pnl": total_pnl / len(trades) if trades else 0.0,
            "ending_balance": balance,
            "trades": trades,
            "trades_per_day": trades_per_day,
            "trades_per_week": trades_per_week,
        }
