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


    # Flexible SL/TP logic
    # Defaults
    sl_type = kwargs.get('sl_type', 'percent')
    sl_value = kwargs.get('sl_value', 0.10)
    tp_type = kwargs.get('tp_type', 'percent')
    tp_value = kwargs.get('tp_value', 0.20)
    # Prefer config if present
    if system and hasattr(system, 'strategy') and hasattr(system.strategy, 'params'):
        params = system.strategy.params
        sl_type = getattr(params, 'sl_type', sl_type)
        sl_value = getattr(params, 'sl_value', sl_value)
        tp_type = getattr(params, 'tp_type', tp_type)
        tp_value = getattr(params, 'tp_value', tp_value)

    entry_mask = df['signal'] == 1
    # Get tick size and tick value from system config if needed
    tick_size = 0.25
    tick_value = 1.25
    if system and hasattr(system, 'exec'):
        tick_size = getattr(system.exec, 'tick_size', tick_size)
        tick_value = getattr(system.exec, 'tick_value', tick_value)

    # Calculate SL/TP for each entry
    for idx in df[entry_mask].index:
        entry_price = df.at[idx, 'close']
        # Stop loss
        if sl_type == 'percent':
            sl = entry_price * (1 - sl_value)
        elif sl_type == 'dollar':
            sl = entry_price - sl_value / tick_value * tick_size
        elif sl_type == 'ticks':
            sl = entry_price - sl_value * tick_size
        else:
            sl = entry_price * (1 - 0.10)
        # Take profit
        if tp_type == 'percent':
            tp = entry_price * (1 + tp_value)
        elif tp_type == 'dollar':
            tp = entry_price + tp_value / tick_value * tick_size
        elif tp_type == 'ticks':
            tp = entry_price + tp_value * tick_size
        else:
            tp = entry_price * (1 + 0.20)
        df.at[idx, 'sl'] = sl
        df.at[idx, 'tp'] = tp

    return df
