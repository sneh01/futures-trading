import pandas as pd
import numpy as np

def generate_signals(df, system=None, entry_prob=0.02, seed=None):
    """
    Generate entry signals based on RSI reversal logic, but add a cooldown period after a stop loss before allowing new buys.
    """
    np.random.seed(seed or 42)
    df = df.copy()
    df['rsi'] = compute_rsi(df['close'], period=14)
    df['signal'] = 0
    df['sl'] = np.nan
    df['tp'] = np.nan

    # Configurable parameters
    rsi_entry = getattr(system, 'rsi_entry', 30) if system else 30
    rsi_exit = getattr(system, 'rsi_exit', 70) if system else 70
    sl_type = getattr(system, 'sl_type', 'ticks') if system else 'ticks'
    sl_value = getattr(system, 'sl_value', 1) if system else 1
    tp_type = getattr(system, 'tp_type', 'ticks') if system else 'ticks'
    tp_value = getattr(system, 'tp_value', 2) if system else 2
    tick_size = getattr(system.exec, 'tick_size', 0.25) if system and hasattr(system, 'exec') else 0.25
    cooldown_bars = getattr(system, 'cooldown_bars', 10) if system else 10

    last_sl_idx = -cooldown_bars - 1

    for i in range(1, len(df)):
        # Cooldown logic: skip if within cooldown_bars after last stop loss
        if i - last_sl_idx <= cooldown_bars:
            continue
        # Entry signal: RSI below entry threshold
        if df.loc[i, 'rsi'] < rsi_entry:
            df.at[i, 'signal'] = 1
            entry = df.loc[i, 'close']
            # Stop loss
            if sl_type == 'ticks':
                sl = entry - sl_value * tick_size
            elif sl_type == 'percent':
                sl = entry * (1 - sl_value / 100)
            elif sl_type == 'dollar':
                sl = entry - sl_value
            else:
                sl = entry - sl_value * tick_size
            # Take profit
            if tp_type == 'ticks':
                tp = entry + tp_value * tick_size
            elif tp_type == 'percent':
                tp = entry * (1 + tp_value / 100)
            elif tp_type == 'dollar':
                tp = entry + tp_value
            else:
                tp = entry + tp_value * tick_size
            df.at[i, 'sl'] = sl
            df.at[i, 'tp'] = tp
        # Exit signal: RSI above exit threshold
        if df.loc[i, 'rsi'] > rsi_exit:
            df.at[i, 'signal'] = 0
        # If a stop loss was hit on the previous bar, set cooldown
        if i > 1 and df.at[i-1, 'signal'] == 1 and df.at[i-1, 'close'] <= df.at[i-1, 'sl']:
            last_sl_idx = i
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def strategy_name():
    return "rsi_cooldown"
