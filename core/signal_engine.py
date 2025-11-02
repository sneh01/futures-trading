import importlib
import pandas as pd
from typing import Optional


class SignalEngine:
    def __init__(self, strategy: Optional[object] = None):
        """Signal engine that can either use an internal fallback or a strategy module.

        Accepts either:
        - a string strategy module name (e.g. "simple_random")
        - or a config/object describing strategy parameters (pydantic model or dict).

        If a module name is provided the engine will import `strategies.<name>` and
        delegate `generate_signals` to that module. If a config object is provided
        we will *not* attempt to import using its string representation (which caused
        ModuleNotFoundError in some cases); instead we store the params for use by
        callers or by live wiring.
        """
        print("Initializing Signal Engine")
        self.strategy_name = None
        self.strategy_module = None
        self.strategy_params = None

        if strategy is None:
            return

        # If user passed a plain string, treat it as a module name
        if isinstance(strategy, str):
            self.strategy_name = strategy
            try:
                self.strategy_module = importlib.import_module(f"strategies.{strategy}")
            except ModuleNotFoundError:
                # Don't crash here; keep engine functional with fallback behavior.
                print(f"Warning: strategy module 'strategies.{strategy}' not found. Using fallback signals.")
                self.strategy_module = None
            return

        # If it's an object with a `.name` attribute, try that first (allows config to specify name)
        name = getattr(strategy, "name", None)
        if isinstance(name, str) and name:
            self.strategy_name = name
            try:
                self.strategy_module = importlib.import_module(f"strategies.{name}")
            except ModuleNotFoundError:
                print(f"Warning: strategy module 'strategies.{name}' not found. Using fallback signals.")
                self.strategy_module = None
            # keep the full config available
            self.strategy_params = strategy
            return

        # Otherwise assume a config-like object (pydantic model or dict) with parameters only.
        # We won't attempt to import a module using its repr (which caused the ModuleNotFoundError).
        self.strategy_params = strategy

    def generate_signals(self, data: pd.DataFrame, system=None, entry_prob: float = 0.02, seed: Optional[int] = None) -> pd.DataFrame:
        """Return dataframe with `signal` column. If a strategy module is configured,
        delegate to its `generate_signals` function so the same strategy files can be used
        for both backtest and live (when appropriate).
        """
        if self.strategy_module and hasattr(self.strategy_module, "generate_signals"):
            # Delegate to the strategy module's signal generator
            return self.strategy_module.generate_signals(data.copy(), system=system, entry_prob=entry_prob, seed=seed)

        df = data.copy()
        df['signal'] = 0
        df.loc[df['close'] > df['close'].rolling(window=5).mean(), 'signal'] = 1
        df.loc[df['close'] < df['close'].rolling(window=5).mean(), 'signal'] = -1
        return df

