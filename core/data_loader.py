import pandas as pd

def load_price_data(source: str = None):
    """Load data from CSV, database, or API."""
    if source is None:
        # mock data for testing
        df = pd.DataFrame({
            "close": [4300 + i * 0.5 for i in range(200)],
        })
        df["timestamp"] = pd.date_range("2024-01-01", periods=len(df), freq="1min")
        print("Loaded mock price data")
        return df
    else:
        # If the file is the Kibot bid/ask 1min format (no header, 10 columns), assign names and map to OHLCV
        if source.endswith("IVE_bidask1min.txt"):
            colnames = [
                'Date', 'Time',
                'BidOpen', 'BidHigh', 'BidLow', 'BidClose',
                'AskOpen', 'AskHigh', 'AskLow', 'AskClose'
            ]
            df = pd.read_csv(source, names=colnames, header=None)
            # Use Bid prices for OHLCV
            df = df.rename(columns={
                'BidOpen': 'open',
                'BidHigh': 'high',
                'BidLow': 'low',
                'BidClose': 'close'
            })
            df = df[['open', 'high', 'low', 'close']].copy()
            df['volume'] = 1000  # dummy volume
            return df


        return pd.read_csv(source)

