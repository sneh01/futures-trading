import yaml
from pydantic import BaseModel
from typing import Literal, Optional, Dict, Any

class RiskConfig(BaseModel):
    risk_per_trade: float
    risk_to_reward: float
    stop_loss_ticks: int
    max_drawdown: float
    max_position_size: int

class ExecutionConfig(BaseModel):
    mode: Literal["backtest", "live"]
    broker: Literal["mock", "ibkr", "tradovate", "ninjatrader"]
    symbol: str
    tick_value: float
    tick_size: float

class StrategyConfig(BaseModel):
        """Flexible strategy descriptor.

        Two supported forms in `config/settings.yaml`:
        1) Simple params-only (backwards compatible):
                 strategy:
                     ema_fast: 9
                     ema_slow: 21
                     rsi_period: 14
                     rsi_entry_threshold: 60

        2) Explicit named strategy with params (recommended):
                 strategy:
                     name: "simple_random"
                     params:
                         ema_fast: 9
                         ema_slow: 21
                         rsi_period: 14
                         rsi_entry_threshold: 60

        Callers should prefer `strategy.name` when they want the engine to import
        a module from `strategies.<name>`. The `params` mapping is optional and
        preserved for strategy configuration.
        """
        name: Optional[str] = None
        params: Optional[Dict[str, Any]] = None

class SystemConfig(BaseModel):
    risk: RiskConfig
    exec: ExecutionConfig
    strategy: StrategyConfig


def load_config(path: str = "config/settings.yaml") -> SystemConfig:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return SystemConfig(**data)

