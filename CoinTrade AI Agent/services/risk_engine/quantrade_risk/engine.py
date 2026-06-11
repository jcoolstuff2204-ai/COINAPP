from __future__ import annotations

from decimal import Decimal

from quantrade_schemas.models import FeatureSnapshot, RiskDecision


MAX_SPREAD_BPS = Decimal("12")
MAX_SLIPPAGE_BPS = Decimal("25")
MAX_MANIPULATION_SCORE = Decimal("65")
MAX_FEED_AGE_SECONDS = 10


def evaluate_risk(features: FeatureSnapshot) -> RiskDecision:
    block_reasons: list[str] = []
    warnings: list[str] = []

    if not features.data_quality.get("valid"):
        block_reasons.append("data_quality_failed")
    if not features.data_quality.get("order_book_valid"):
        block_reasons.append("order_book_invalid")
    if int(features.data_quality.get("feed_age_seconds", 999)) > MAX_FEED_AGE_SECONDS:
        block_reasons.append("feed_stale")

    spread = Decimal(features.values["spread_bps"])
    slippage = Decimal(features.values["estimated_slippage_bps"])
    manipulation = Decimal(features.values["manipulation_score"])

    if spread > MAX_SPREAD_BPS:
        block_reasons.append("spread_too_wide")
    if slippage > MAX_SLIPPAGE_BPS:
        block_reasons.append("slippage_too_high")
    if manipulation > MAX_MANIPULATION_SCORE:
        block_reasons.append("manipulation_risk_too_high")

    risk_score = min(Decimal("100"), spread * Decimal("2") + slippage + manipulation)
    if risk_score > Decimal("45"):
        warnings.append("risk_elevated")

    return RiskDecision(
        approved=not block_reasons,
        risk_score=risk_score,
        manipulation_score=manipulation,
        block_reasons=tuple(block_reasons),
        warnings=tuple(warnings),
    )

