"""
Example usage of ExecutionEngine with Tradovate paper trading.
"""
from core.execution_engine import ExecutionEngine
import os

# It's best to load credentials from environment variables for security
TRADOVATE_USERNAME = os.getenv('TRADOVATE_USERNAME')
TRADOVATE_PASSWORD = os.getenv('TRADOVATE_PASSWORD')
TRADOVATE_APP_ID = os.getenv('TRADOVATE_APP_ID')
TRADOVATE_APP_SECRET = os.getenv('TRADOVATE_APP_SECRET')

# Initialize the execution engine for Tradovate paper trading
env = ExecutionEngine(
    mode='paper',
    tradovate_username=TRADOVATE_USERNAME,
    tradovate_password=TRADOVATE_PASSWORD,
    tradovate_app_id=TRADOVATE_APP_ID,
    tradovate_app_secret=TRADOVATE_APP_SECRET,
    tradovate_demo=True  # True for paper/demo, False for live
)

# Example signal (adapt as needed)
signal = {
    'symbol': 'ESM6',  # Example: E-mini S&P 500 futures
    'action': 'Buy',   # 'Buy' or 'Sell'
    'quantity': 1,
    'orderType': 'Market',
    # 'price': 4200.0, # Only for limit/stop orders
}

env.execute(signal)
