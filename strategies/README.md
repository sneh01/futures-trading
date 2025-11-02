# Strategies
Contains trading strategies, entry/exit logic, and parameter definitions.

## Strategy module requirements

- Each strategy file should live under `strategies/` and export a callable:
	- `generate_signals(df: pandas.DataFrame, system, entry_prob: float = 0.02, seed: Optional[int] = None) -> pd.DataFrame`
		- Must return a DataFrame with a `signal` column (1 for long, -1 for short, 0 for flat).
		- Optional columns the strategy can set per-entry: `sl`, `tp`, `stop_loss_ticks`.

## Configuration

Prefer to configure the strategy in `config/settings.yaml` using `name` + `params`:

```yaml
strategy:
	name: simple_random
	params:
		ema_fast: 9
		ema_slow: 21
		rsi_period: 14
		rsi_entry_threshold: 60
```

The runner will pass `strategy.name` into the `SignalEngine` so the engine can import `strategies.<name>`.