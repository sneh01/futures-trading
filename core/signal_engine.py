import pandas as pd

class SignalEngine:
    def __init__(self, strategy):
        self.strategy = strategy

    def generate_signals(self, data: pd.DataFrame):
        return self.strategy.generate(data)
