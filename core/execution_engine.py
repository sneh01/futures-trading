class ExecutionEngine:
    def __init__(self, mode='backtest'):
        print("Initializing Execution Engine")
        self.mode = mode

    def execute(self, signals):
        if self.mode == 'backtest':
            print(f"Simulating trade execution: {signals}")
        else:
            print(f"Placing live trade: {signals}")
