class RiskEngine:
    def __init__(self, max_drawdown, max_position_size, reward_to_risk):
        self.max_drawdown = max_drawdown
        self.max_position_size = max_position_size
        self.reward_to_risk = reward_to_risk

    def validate_trade(self, trade):
        return True  # Simplified placeholder
    
    def calculate_position_size(self, account_balance, stop_loss_ticks):
        risk_amount = account_balance * self.config.risk_per_trade
        tick_value = 12.5
        stop_loss_value = stop_loss_ticks * tick_value
        size = risk_amount / stop_loss_value
        return max(1, int(size))