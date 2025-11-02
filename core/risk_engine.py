class RiskEngine:
    def __init__(self, max_drawdown, max_position_size, reward_to_risk):
        self.max_drawdown = max_drawdown
        self.max_position_size = max_position_size
        self.reward_to_risk = reward_to_risk

    def validate_trade(self, trade):
        return True  # Simplified placeholder
