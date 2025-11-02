"""Strategy base helpers and interface validation.

Standard requirements for a strategy module (minimal):
- A callable `generate_signals(df: pandas.DataFrame, system, entry_prob: float = 0.02, seed: Optional[int] = None)`
  that returns a DataFrame with a `signal` column containing 1 (long), -1 (short), or 0 (no entry).
  It may optionally populate `sl`, `tp`, and `stop_loss_ticks` columns per-entry.

Optional live hooks:
- `on_live_tick(tick: dict, state: dict, system) -> Optional[dict]` — called by a live wrapper when
  a new tick/bar arrives; should return an order dict or None. This is optional so the same strategy
  file can be used for backtest and live.

This module provides a `validate_strategy` helper to check the minimal requirements.
"""
from typing import Optional
import inspect


def validate_strategy(module) -> None:
    """Raise AttributeError if module doesn't implement the minimal required API."""
    if not hasattr(module, "generate_signals"):
        raise AttributeError("Strategy module must implement `generate_signals(df, system, entry_prob=..., seed=...)`")
    if not callable(module.generate_signals):
        raise AttributeError("`generate_signals` must be callable")

    # optional: if on_live_tick exists it must be callable
    if hasattr(module, "on_live_tick") and not callable(module.on_live_tick):
        raise AttributeError("`on_live_tick` exists but is not callable")

