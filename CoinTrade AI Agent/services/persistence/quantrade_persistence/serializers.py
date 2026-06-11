from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from quantrade_schemas.models import BehavioralState, ComponentScore, Signal, SignalStatus


def signal_record_payload(signal: Signal) -> dict[str, Any]:
    return {
        "signal_id": signal.signal_id,
        "exchange": signal.exchange,
        "symbol": signal.symbol,
        "strategy": signal.strategy,
        "strategy_version": signal.strategy_version,
        "generated_at": signal.generated_at,
        "expires_at": signal.expires_at,
        "behavioral_state": signal.behavioral_state.value,
        "direction": signal.direction,
        "opportunity_score": signal.opportunity_score,
        "risk_score": signal.risk_score,
        "manipulation_score": signal.manipulation_score,
        "confidence": signal.confidence,
        "status": signal.status.value,
        "block_reasons": list(signal.block_reasons),
        "plan": {
            "entry_zone": [str(signal.entry_zone[0]), str(signal.entry_zone[1])],
            "invalidation_price": str(signal.invalidation_price),
            "targets": [str(target) for target in signal.targets],
            "maximum_holding_minutes": signal.maximum_holding_minutes,
            "estimated_reward_risk": str(signal.estimated_reward_risk),
            "thesis": signal.thesis,
            "counter_thesis": signal.counter_thesis,
            "warnings": list(signal.warnings),
        },
    }


def signal_component_payloads(signal: Signal) -> list[dict[str, Any]]:
    return [
        {
            "signal_id": signal.signal_id,
            "name": component.name,
            "raw_value": component.raw_value,
            "normalized_score": component.normalized_score,
            "weight": component.weight,
            "contribution": component.contribution,
        }
        for component in signal.components
    ]


def signal_from_record_payload(
    record: dict[str, Any],
    component_records: list[dict[str, Any]],
) -> Signal:
    plan = record["plan"]
    components = tuple(
        ComponentScore(
            name=str(component["name"]),
            raw_value=Decimal(str(component["raw_value"])),
            normalized_score=Decimal(str(component["normalized_score"])),
            weight=Decimal(str(component["weight"])),
        )
        for component in component_records
    )
    return Signal(
        signal_id=str(record["signal_id"]),
        symbol=str(record["symbol"]),
        exchange=str(record["exchange"]),
        strategy=str(record["strategy"]),
        strategy_version=str(record["strategy_version"]),
        generated_at=_datetime(record["generated_at"]),
        expires_at=_datetime(record["expires_at"]),
        behavioral_state=BehavioralState(str(record["behavioral_state"])),
        direction=str(record["direction"]),
        opportunity_score=Decimal(str(record["opportunity_score"])),
        risk_score=Decimal(str(record["risk_score"])),
        manipulation_score=Decimal(str(record["manipulation_score"])),
        confidence=Decimal(str(record["confidence"])),
        entry_zone=(Decimal(str(plan["entry_zone"][0])), Decimal(str(plan["entry_zone"][1]))),
        invalidation_price=Decimal(str(plan["invalidation_price"])),
        targets=tuple(Decimal(str(target)) for target in plan["targets"]),
        maximum_holding_minutes=int(plan["maximum_holding_minutes"]),
        estimated_reward_risk=Decimal(str(plan["estimated_reward_risk"])),
        components=components,
        thesis=str(plan["thesis"]),
        counter_thesis=str(plan["counter_thesis"]),
        warnings=tuple(str(warning) for warning in plan["warnings"]),
        status=SignalStatus(str(record["status"])),
        block_reasons=tuple(str(reason) for reason in record["block_reasons"]),
    )


def paper_order_record_payload(result: dict[str, Any]) -> dict[str, Any]:
    order = result["order"]
    return {
        "order_id": order["order_id"],
        "signal_id": order["signal_id"],
        "symbol": order["symbol"],
        "side": order["side"],
        "order_type": order["order_type"],
        "requested_quantity": Decimal(str(order["requested_quantity"])),
        "requested_price": Decimal(str(order["requested_price"])),
        "submitted_at": _datetime(order["submitted_at"]),
        "status": order["status"],
        "time_in_force": order["time_in_force"],
    }


def paper_position_record_payload(result: dict[str, Any]) -> dict[str, Any]:
    position = result["position"]
    order = result["order"]
    return {
        "position_id": position["position_id"],
        "symbol": position["symbol"],
        "strategy": "momentum_ignition",
        "side": position["side"],
        "quantity": Decimal(str(position["quantity"])),
        "average_entry": Decimal(str(position["average_entry"])),
        "stop_price": Decimal(str(position["stop_price"])),
        "targets": {"levels": [str(target) for target in position["targets"]]},
        "realized_pnl": Decimal("0"),
        "unrealized_pnl": Decimal("0"),
        "fees": Decimal(str(position["fees"])),
        "opened_at": _datetime(position["opened_at"]),
        "closed_at": None,
        "status": position["status"],
        "source_order_id": order["order_id"],
    }


def journal_record_payload(result: dict[str, Any]) -> dict[str, Any]:
    journal = result["journal_entry"]
    return {
        "signal_id": journal["signal_id"],
        "position_id": journal["position_id"],
        "created_at": datetime_from_order_result(result),
        "pnl": Decimal("0"),
        "r_multiple": Decimal("0"),
        "rule_compliance": journal["rule_compliance"],
        "user_note": None,
        "emotion_tag": None,
        "ai_review": {"review": journal["ai_review"]},
    }


def datetime_from_order_result(result: dict[str, Any]) -> datetime:
    return _datetime(result["order"]["submitted_at"])


def _datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

