import argparse
from config.loader import load_config
from app.runner import TradingSystemRunner

def main():
    parser = argparse.ArgumentParser(description="Futures Trading Bot")
    parser.add_argument("--mode", choices=["backtest", "live"], help="Run mode")
    parser.add_argument("--config", default="config/settings.yaml", help="Path to config file")
    parser.add_argument("--data", help="Path to price data CSV (for backtest)")
    args = parser.parse_args()

    # Load config
    cfg = load_config(args.config)
    if args.mode:
        cfg.exec.mode = args.mode

    # Initialize system
    system = TradingSystemRunner(cfg)

    if cfg.exec.mode == "backtest":
        system.run_backtest(args.data)
    elif cfg.exec.mode == "live":
        system.run_live()

if __name__ == "__main__":
    main()

