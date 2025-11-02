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


    return df
