import random
import pandas as pd
from typing import Optional


def generate_signals(data: pd.DataFrame, system=None, entry_prob: float = 0.02, seed: Optional[int] = None) -> pd.DataFrame:
    """
    Simple random strategy:
    - Randomly opens a long position with probability `entry_prob` when not already in a position.
    - Marks the entry row with `signal` == 1 and writes `sl`, `tp`, and `stop_loss_ticks` based
      on `system.risk` settings (if provided).

    Note: the backtest engine will perform the forward-scan to determine whether SL or TP is hit.
    """
    if seed is not None:
        random.seed(seed)

    df = data.copy()
    df = df.reset_index(drop=True)
    df["signal"] = 0
    df["sl"] = pd.NA
    df["tp"] = pd.NA
    df["stop_loss_ticks"] = pd.NA

    in_position = False
    stop_loss_ticks_cfg = getattr(system.risk, "stop_loss_ticks", 20) if system is not None else 20
    rr_cfg = getattr(system.risk, "risk_to_reward", 2.0) if system is not None else 2.0
    tick_size = getattr(system.exec, "tick_size", 0.25) if system is not None else 0.25

    for i, row in df.iterrows():
        if in_position:
            # wait for backtest engine to resolve exits; strategy doesn't place multiple overlapping entries
            continue

        if random.random() < entry_prob:
            entry = float(row.close)
            sl = entry - stop_loss_ticks_cfg * tick_size
            tp = entry + stop_loss_ticks_cfg * tick_size * rr_cfg

            df.at[i, "signal"] = 1
            df.at[i, "sl"] = sl
            df.at[i, "tp"] = tp
            df.at[i, "stop_loss_ticks"] = stop_loss_ticks_cfg
            in_position = True

    return df
