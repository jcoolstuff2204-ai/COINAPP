from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from quantrade_features.engine import normalize
from quantrade_risk.engine import evaluate_risk
from quantrade_schemas.models import BehavioralState, ComponentScore, FeatureSnapshot, Signal, SignalStatus


WEIGHTS = {
    "order_flow": Decimal("0.20"),
    "volume_anomaly": Decimal("0.15"),
    "order_book_structure": Decimal("0.15"),
    "momentum_acceleration": Decimal("0.15"),
    "cross_market_confirmation": Decimal("0.10"),
    "market_context": Decimal("0.10"),
    "volatility_setup": Decimal("0.10"),
    "attention_positioning": Decimal("0.05"),
}


def _component_scores(features: FeatureSnapshot) -> tuple[ComponentScore, ...]:
    values = features.values
    components = (
        ComponentScore(
            "order_flow",
            Decimal(values["trade_imbalance_5m"]),
            normalize(Decimal(values["trade_imbalance_5m"]), Decimal("-0.25"), Decimal("0.60")),
            WEIGHTS["order_flow"],
        ),
        ComponentScore(
            "volume_anomaly",
            Decimal(values["volume_z_score"]),
            normalize(Decimal(values["volume_z_score"]), Decimal("0"), Decimal("4")),
            WEIGHTS["volume_anomaly"],
        ),
        ComponentScore(
            "order_book_structure",
            Decimal(values["book_imbalance_025"]),
            normalize(Decimal(values["book_imbalance_025"]), Decimal("-0.20"), Decimal("0.55")),
            WEIGHTS["order_book_structure"],
        ),
        ComponentScore(
            "momentum_acceleration",
            Decimal(values["return_5m"]),
            normalize(Decimal(values["return_5m"]), Decimal("-0.005"), Decimal("0.025")),
            WEIGHTS["momentum_acceleration"],
        ),
        ComponentScore("cross_market_confirmation", Decimal("1"), Decimal("75"), WEIGHTS["cross_market_confirmation"]),
        ComponentScore("market_context", Decimal("1"), Decimal("72"), WEIGHTS["market_context"]),
        ComponentScore(
            "volatility_setup",
            Decimal(values["volatility_percentile"]),
            normalize(Decimal(values["volatility_percentile"]), Decimal("25"), Decimal("90")),
            WEIGHTS["volatility_setup"],
        ),
        ComponentScore("attention_positioning", Decimal("0"), Decimal("50"), WEIGHTS["attention_positioning"]),
    )
    total_weight = sum((c.weight for c in components), Decimal("0"))
    if total_weight != Decimal("1.00"):
        raise ValueError(f"strategy weights must sum to 1, got {total_weight}")
    return components


def generate_momentum_signal(features: FeatureSnapshot) -> Signal:
    components = _component_scores(features)
    opportunity_score = sum((c.contribution for c in components), Decimal("0")).quantize(Decimal("0.01"))
    risk = evaluate_risk(features)
    price = Decimal(features.values["price"])
    atr_proxy = price * Decimal("0.006")
    entry_low = (price - atr_proxy * Decimal("0.35")).quantize(Decimal("0.01"))
    entry_high = (price + atr_proxy * Decimal("0.15")).quantize(Decimal("0.01"))
    invalidation = (price - atr_proxy * Decimal("1.15")).quantize(Decimal("0.01"))
    targets = (
        (price + atr_proxy * Decimal("1.25")).quantize(Decimal("0.01")),
        (price + atr_proxy * Decimal("2.25")).quantize(Decimal("0.01")),
    )
    if not risk.approved:
        status = SignalStatus.blocked
    elif opportunity_score >= Decimal("75"):
        status = SignalStatus.strong_candidate
    elif opportunity_score >= Decimal("65"):
        status = SignalStatus.watch
    else:
        status = SignalStatus.developing

    return Signal(
        signal_id=f"fixture-{features.symbol}-momentum-v01",
        symbol=features.symbol,
        exchange="fixture",
        strategy="momentum_ignition",
        strategy_version="0.1.0",
        generated_at=features.timestamp,
        expires_at=features.timestamp + timedelta(minutes=45),
        behavioral_state=BehavioralState.momentum_ignition,
        direction="long_spot_paper_only",
        opportunity_score=opportunity_score,
        risk_score=risk.risk_score,
        manipulation_score=risk.manipulation_score,
        confidence=min(Decimal("95"), opportunity_score - risk.risk_score / Decimal("4")).quantize(Decimal("0.01")),
        entry_zone=(entry_low, entry_high),
        invalidation_price=invalidation,
        targets=targets,
        maximum_holding_minutes=180,
        estimated_reward_risk=Decimal("1.86"),
        components=components,
        thesis="Participation is increasing with positive trade imbalance, stronger volume, and supportive book structure.",
        counter_thesis="The move can fail if price extends above the entry zone, order-flow weakens, or spread/slippage expands.",
        warnings=tuple(["DEMO DATA"] + list(risk.warnings)),
        status=status,
        block_reasons=risk.block_reasons,
    )

