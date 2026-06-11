from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from quantrade_schemas.models import PaperPosition, Signal, SignalStatus


def position_size(cash: Decimal, risk_per_trade: Decimal, entry: Decimal, stop: Decimal) -> Decimal:
    if cash <= 0:
        raise ValueError("cash must be positive")
    if not Decimal("0") < risk_per_trade <= Decimal("0.05"):
        raise ValueError("risk_per_trade must be between 0 and 5%")
    risk_per_unit = entry - stop
    if risk_per_unit <= 0:
        raise ValueError("stop must be below entry for spot long paper positions")
    max_loss = cash * risk_per_trade
    quantity = max_loss / risk_per_unit
    affordable = cash / entry
    return min(quantity, affordable).quantize(Decimal("0.00000001"))


def open_long_position(
    signal: Signal,
    cash: Decimal,
    risk_per_trade: Decimal,
    fee_bps: Decimal = Decimal("10"),
) -> PaperPosition:
    if signal.status == SignalStatus.blocked:
        raise ValueError("blocked signals cannot create paper positions")
    entry = signal.entry_zone[1]
    quantity = position_size(cash, risk_per_trade, entry, signal.invalidation_price)
    fee = (entry * quantity * fee_bps / Decimal("10000")).quantize(Decimal("0.01"))
    return PaperPosition(
        position_id=f"paper-{signal.signal_id}",
        symbol=signal.symbol,
        side="long",
        quantity=quantity,
        average_entry=entry,
        stop_price=signal.invalidation_price,
        targets=signal.targets,
        fees=fee,
    )


@dataclass(frozen=True)
class PaperOrderResult:
    order: dict[str, object]
    position: PaperPosition
    portfolio: dict[str, object]
    journal_entry: dict[str, object]
    performance: dict[str, object]

    def to_api_dict(self) -> dict[str, object]:
        return {
            "order": self.order,
            "position": {
                "position_id": self.position.position_id,
                "symbol": self.position.symbol,
                "side": self.position.side,
                "quantity": float(self.position.quantity),
                "average_entry": float(self.position.average_entry),
                "stop_price": float(self.position.stop_price),
                "targets": [float(target) for target in self.position.targets],
                "fees": float(self.position.fees),
                "opened_at": self.position.opened_at.isoformat(),
                "status": "open" if self.position.closed_at is None else "closed",
            },
            "portfolio": self.portfolio,
            "journal_entry": self.journal_entry,
            "performance": self.performance,
        }


def simulate_fixture_order(
    signal: Signal,
    cash: Decimal = Decimal("10000"),
    risk_per_trade: Decimal = Decimal("0.01"),
    fee_bps: Decimal = Decimal("10"),
) -> PaperOrderResult:
    position = open_long_position(signal, cash, risk_per_trade, fee_bps)
    submitted_at = datetime.now(UTC)
    notional = position.average_entry * position.quantity
    open_risk = (position.average_entry - position.stop_price) * position.quantity
    available_cash = cash - notional - position.fees
    portfolio = {
        "equity": float(cash - position.fees),
        "cash": float(available_cash),
        "open_risk": float(open_risk.quantize(Decimal("0.01"))),
        "realized_pnl": 0.0,
        "unrealized_pnl": 0.0,
        "fees": float(position.fees),
        "paper_trading_only": True,
    }
    order = {
        "order_id": f"order-{signal.signal_id}",
        "signal_id": signal.signal_id,
        "symbol": signal.symbol,
        "side": "buy",
        "order_type": "paper_market",
        "requested_quantity": float(position.quantity),
        "requested_price": float(position.average_entry),
        "submitted_at": submitted_at.isoformat(),
        "status": "filled",
        "time_in_force": "immediate_or_cancel",
    }
    journal_entry = {
        "signal_id": signal.signal_id,
        "position_id": position.position_id,
        "entry_plan": {
            "entry_zone": [float(signal.entry_zone[0]), float(signal.entry_zone[1])],
            "invalidation_price": float(signal.invalidation_price),
            "targets": [float(target) for target in signal.targets],
        },
        "actual_execution": {
            "entry_price": float(position.average_entry),
            "quantity": float(position.quantity),
            "fees": float(position.fees),
        },
        "rule_compliance": {
            "entered_inside_recommended_zone": True,
            "respected_position_size": True,
            "paper_trade_only": True,
        },
        "ai_review": "Trade opened in paper mode from deterministic fixture signal. Review remains pending until exit.",
    }
    performance = {
        "trade_count": 1,
        "open_positions": 1,
        "closed_positions": 0,
        "win_rate": None,
        "profit_factor": None,
        "expectancy": None,
        "fees": float(position.fees),
        "max_drawdown": 0.0,
    }
    return PaperOrderResult(
        order=order,
        position=position,
        portfolio=portfolio,
        journal_entry=journal_entry,
        performance=performance,
    )
