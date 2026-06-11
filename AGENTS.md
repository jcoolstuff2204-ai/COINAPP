# QuanTrade Coding Agent Instructions

## Product Boundaries

- Build paper-trading and decision-support software only.
- Do not add live order placement, leverage, margin, or real-money execution.
- Do not fake market data, scores, AI recommendations, fills, or performance.
- When data is unavailable, show a suspended or unavailable state.

## Architecture Rules

- Deterministic engines calculate values.
- AI explains validated structured evidence only.
- Risk controls outrank opportunity scores.
- Keep domain logic outside notebooks and UI components.
- Reuse production strategy logic in backtests.
- Route handlers should stay thin. Put orchestration in `quantrade_api.services` and persistence behind `QuanTradeRepository`.

## Testing Rules

- Critical scoring, risk, position sizing, and accounting logic needs deterministic tests.
- Normal CI must not require external exchange access.
- Tests must use fixed timestamps and fixtures.

## Commands

```bash
make setup
make dev
make streamlit
make test-unit
make test
make build
```

## Documentation Rules

Update `docs/implementation-plan.md` when milestones change. Update strategy and risk docs when formulas or thresholds change.
