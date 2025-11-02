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
        return pd.read_csv(source)

