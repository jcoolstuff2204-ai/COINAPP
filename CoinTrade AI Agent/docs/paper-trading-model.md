# Paper Trading Model

Paper execution is a simulation for discipline training and strategy validation.

## Fill Assumptions

- Marketable orders fill at requested price plus slippage.
- Fees are applied as a configurable basis-point rate.
- Partial fills are supported by the domain model and should be implemented in persistence during the paper-trading milestone.

## Slippage

The initial deterministic model accepts a supplied slippage value and records it on the fill. Later milestones should estimate slippage from order-book depth.

Current fixture behavior creates a filled paper-market order at the high end of the recommended entry zone. This is intentionally deterministic for repeatable tests.

## Risk

Position size is capped by:

- Risk per trade
- Available cash
- Maximum open positions
- Daily loss limit
- Signal invalidation distance

## Backtest Limitations

Backtests must not access future candles, tune parameters on the final test period, or treat fixture universes as survivorship-free live universes.
