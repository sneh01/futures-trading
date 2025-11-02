class RiskEngine:
    def __init__(self, risk_config):
        print("Initializing Risk Engine")
        self.risk_per_trade = risk_config.risk_per_trade
        self.max_drawdown = risk_config.max_drawdown
        self.max_position_size = risk_config.max_position_size
        self.risk_to_reward = risk_config.risk_to_reward
        self.stop_loss_ticks = risk_config.stop_loss_ticks

    def validate_trade(self, trade):
        return True  # Simplified placeholder
    
    def calculate_position_size(self, account_balance, stop_loss_ticks, tick_value=1.25):
        # For MES: tick_size=0.25, tick_value=1.25, contract size is 1
        # Position size = contracts = floor((account_balance * risk_per_trade) / (stop_loss_ticks * tick_value))
        risk_amount = account_balance * self.risk_per_trade
        stop_loss_value = stop_loss_ticks * tick_value
        contracts = int(risk_amount // stop_loss_value)
        contracts = max(1, min(contracts, self.max_position_size))
        return contracts