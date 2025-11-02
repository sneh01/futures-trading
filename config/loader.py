import yaml
from pydantic import BaseModel
from typing import Literal

class RiskConfig(BaseModel):
    risk_per_trade: float
    risk_to_reward: float
    stop_loss_ticks: int

class ExecutionConfig(BaseModel):
    mode: Literal["backtest", "live"]
    broker: Literal["mock", "ibkr", "tradovate", "ninjatrader"]
    symbol: str
    tick_value: float
    tick_size: float

class StrategyConfig(BaseModel):
    ema_fast: int
    ema_slow: int
    rsi_period: int
    rsi_entry_threshold: int

class SystemConfig(BaseModel):
    risk: RiskConfig
    exec: ExecutionConfig
    strategy: StrategyConfig


def load_config(path: str = "config/settings.yaml") -> SystemConfig:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return SystemConfig(**data)

