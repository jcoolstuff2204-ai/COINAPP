# Strategy Specification

## Score Formula

Opportunity score is the weighted sum of normalized components:

```text
score = sum(weight_i * component_score_i)
```

Weights are centralized in strategy configuration and must sum to `1`.

## Momentum Ignition v0.1

Initial components:

- Order flow: 20%
- Volume anomaly: 15%
- Order-book structure: 15%
- Momentum acceleration: 15%
- Cross-market confirmation: 10%
- Market context: 10%
- Volatility setup: 10%
- Attention or positioning: 5%

The MVP omits unavailable social or derivatives data transparently.

## Mandatory Blocks

Signals are blocked for:

- Ineligible asset
- Stale feed
- Invalid order book
- Excessive spread
- Excessive estimated slippage
- Excessive manipulation risk
- Daily loss limit reached
- Maximum open positions reached
- Missing required history

## Language Policy

Use signal language such as `watch`, `entry zone active`, `risk too high`, and `data insufficient`. Do not use profit-promising or urgency language.

