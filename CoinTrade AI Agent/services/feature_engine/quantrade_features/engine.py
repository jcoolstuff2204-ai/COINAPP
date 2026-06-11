from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from quantrade_schemas.models import FeatureSnapshot


FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "packages"
    / "test_fixtures"
    / "fixtures"
    / "momentum_ignition.json"
)


def _decimalize(value: object) -> Decimal | bool | str:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return Decimal(value)
        except Exception:
            return value
    return Decimal(str(value))


def calculate_fixture_features(path: Path = FIXTURE_PATH) -> FeatureSnapshot:
    payload = json.loads(path.read_text())
    timestamp = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    values = {
        key: _decimalize(value)
        for key, value in payload.items()
        if key
        not in {
            "label",
            "symbol",
            "exchange",
            "timestamp",
            "data_quality_valid",
            "order_book_valid",
            "feed_age_seconds",
        }
    }
    return FeatureSnapshot(
        symbol=payload["symbol"],
        timestamp=timestamp,
        feature_version="fixture-momentum-v0.1",
        values=values,
        data_quality={
            "label": payload["label"],
            "valid": payload["data_quality_valid"],
            "order_book_valid": payload["order_book_valid"],
            "feed_age_seconds": payload["feed_age_seconds"],
        },
    )


def normalize(value: Decimal, low: Decimal, high: Decimal) -> Decimal:
    if high <= low:
        raise ValueError("high must be greater than low")
    score = (value - low) / (high - low) * Decimal("100")
    return max(Decimal("0"), min(Decimal("100"), score))

