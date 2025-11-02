import pandas as pd
import numpy as np

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def generate_signals(df, system=None, rsi_period=14, rsi_entry=30, entry_prob=1.0, seed=None, **kwargs):
    # entry_prob is kept for interface compatibility, but not used here
    df = df.copy()
    df['rsi'] = compute_rsi(df['close'], period=rsi_period)
    df['signal'] = 0
    # Buy when RSI is below rsi_entry threshold
    df.loc[df['rsi'] < rsi_entry, 'signal'] = 1

    # Get stop loss and take profit percentages from config/params or use defaults
    sl_pct = kwargs.get('sl_pct', 0.10)
    tp_pct = kwargs.get('tp_pct', 0.20)
    # If called from system with params dict, prefer that
    if system and hasattr(system, 'strategy') and hasattr(system.strategy, 'params'):
        sl_pct = getattr(system.strategy.params, 'sl_pct', sl_pct)
        tp_pct = getattr(system.strategy.params, 'tp_pct', tp_pct)

    # Set stop loss and take profit for each entry
    entry_mask = df['signal'] == 1
    df.loc[entry_mask, 'sl'] = df.loc[entry_mask, 'close'] * (1 - sl_pct)
    df.loc[entry_mask, 'tp'] = df.loc[entry_mask, 'close'] * (1 + tp_pct)

    return df
