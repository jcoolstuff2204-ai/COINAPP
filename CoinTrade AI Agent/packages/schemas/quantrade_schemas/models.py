from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Mode(StrEnum):
    fixture = "fixture"
    live = "live"
    test = "test"


class SignalStatus(StrEnum):
    strong_candidate = "strong_candidate"
    developing = "developing"
    watch = "watch"
    avoid = "avoid"
    blocked = "blocked"
    expired = "expired"


class BehavioralState(StrEnum):
    dormant = "dormant"
    accumulation_like = "accumulation_like_activity"
    momentum_ignition = "momentum_ignition"
    expansion = "expansion"
    exhaustion = "exhaustion"
    uncertain = "uncertain"


class BookSide(StrEnum):
    bid = "bid"
    ask = "ask"


class ReplayEventType(StrEnum):
    snapshot = "snapshot"
    update = "update"
    trade = "trade"
    candle = "candle"
    disconnect = "disconnect"
    checksum_failure = "checksum_failure"


class HealthStatus(BaseModel):
    status: str
    mode: Mode
    generated_at: datetime
    checks: dict[str, str]


class SignalExplanation(BaseModel):
    summary: str
    thesis: str
    counter_thesis: str
    evidence: list[str]
    risks: list[str]
    invalidation: str
    execution_guidance: str
    confidence_language: str
    generated_at: datetime
    model: str
    prompt_version: str


@dataclass(frozen=True)
class Trade:
    exchange: str
    symbol: str
    trade_id: str
    timestamp: datetime
    price: Decimal
    quantity: Decimal
    maker_side: str
    aggressor_side: str

    @property
    def notional(self) -> Decimal:
        return self.price * self.quantity


@dataclass(frozen=True)
class Candle:
    symbol: str
    exchange: str
    timeframe: str
    start_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    trade_count: int
    buy_volume: Decimal
    sell_volume: Decimal


@dataclass(frozen=True)
class OrderBookLevel:
    price: Decimal
    quantity: Decimal
    side: BookSide
    updated_at: datetime


@dataclass(frozen=True)
class OrderBookSnapshot:
    exchange: str
    symbol: str
    timestamp: datetime
    bids: tuple[OrderBookLevel, ...]
    asks: tuple[OrderBookLevel, ...]
    valid: bool
    checksum_status: str

    @property
    def best_bid(self) -> Decimal | None:
        return max((level.price for level in self.bids if level.quantity > 0), default=None)

    @property
    def best_ask(self) -> Decimal | None:
        return min((level.price for level in self.asks if level.quantity > 0), default=None)

    @property
    def mid_price(self) -> Decimal | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid + self.best_ask) / Decimal("2")

    @property
    def spread_bps(self) -> Decimal | None:
        mid = self.mid_price
        if mid is None or mid == 0:
            return None
        return ((self.best_ask - self.best_bid) / mid * Decimal("10000")).quantize(Decimal("0.01"))


@dataclass(frozen=True)
class DataHealth:
    exchange: str
    symbol: str
    status: str
    last_event_at: datetime | None
    order_book_valid: bool
    checksum_status: str
    invalid_message_count: int
    reconnect_count: int
    missing_sequence_count: int
    feed_age_seconds: int | None

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "status": self.status,
            "last_event_at": self.last_event_at.isoformat() if self.last_event_at else None,
            "order_book_valid": self.order_book_valid,
            "checksum_status": self.checksum_status,
            "invalid_message_count": self.invalid_message_count,
            "reconnect_count": self.reconnect_count,
            "missing_sequence_count": self.missing_sequence_count,
            "feed_age_seconds": self.feed_age_seconds,
        }


@dataclass(frozen=True)
class ComponentScore:
    name: str
    raw_value: Decimal
    normalized_score: Decimal
    weight: Decimal

    @property
    def contribution(self) -> Decimal:
        return self.normalized_score * self.weight


@dataclass(frozen=True)
class FeatureSnapshot:
    symbol: str
    timestamp: datetime
    feature_version: str
    values: dict[str, Decimal | bool | str]
    data_quality: dict[str, bool | int | str]


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    risk_score: Decimal
    manipulation_score: Decimal
    block_reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Signal:
    signal_id: str
    symbol: str
    exchange: str
    strategy: str
    strategy_version: str
    generated_at: datetime
    expires_at: datetime
    behavioral_state: BehavioralState
    direction: str
    opportunity_score: Decimal
    risk_score: Decimal
    manipulation_score: Decimal
    confidence: Decimal
    entry_zone: tuple[Decimal, Decimal]
    invalidation_price: Decimal
    targets: tuple[Decimal, ...]
    maximum_holding_minutes: int
    estimated_reward_risk: Decimal
    components: tuple[ComponentScore, ...]
    thesis: str
    counter_thesis: str
    warnings: tuple[str, ...]
    status: SignalStatus
    block_reasons: tuple[str, ...] = ()

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "strategy": self.strategy,
            "strategy_version": self.strategy_version,
            "generated_at": self.generated_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "behavioral_state": self.behavioral_state.value,
            "direction": self.direction,
            "opportunity_score": float(self.opportunity_score),
            "risk_score": float(self.risk_score),
            "manipulation_score": float(self.manipulation_score),
            "confidence": float(self.confidence),
            "entry_zone": [float(self.entry_zone[0]), float(self.entry_zone[1])],
            "invalidation_price": float(self.invalidation_price),
            "targets": [float(t) for t in self.targets],
            "maximum_holding_minutes": self.maximum_holding_minutes,
            "estimated_reward_risk": float(self.estimated_reward_risk),
            "components": [
                {
                    "name": c.name,
                    "raw_value": float(c.raw_value),
                    "normalized_score": float(c.normalized_score),
                    "weight": float(c.weight),
                    "contribution": float(c.contribution),
                }
                for c in self.components
            ],
            "thesis": self.thesis,
            "counter_thesis": self.counter_thesis,
            "warnings": list(self.warnings),
            "status": self.status.value,
            "block_reasons": list(self.block_reasons),
        }


@dataclass
class PaperPosition:
    position_id: str
    symbol: str
    side: str
    quantity: Decimal
    average_entry: Decimal
    stop_price: Decimal
    targets: tuple[Decimal, ...]
    fees: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    opened_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    closed_at: datetime | None = None

    def unrealized_pnl(self, current_price: Decimal) -> Decimal:
        if self.side != "long":
            raise ValueError("MVP supports spot long paper positions only")
        return (current_price - self.average_entry) * self.quantity - self.fees

    def close(self, exit_price: Decimal, fee: Decimal, closed_at: datetime | None = None) -> Decimal:
        self.closed_at = closed_at or datetime.now(UTC)
        self.fees += fee
        self.realized_pnl = (exit_price - self.average_entry) * self.quantity - self.fees
        return self.realized_pnl


def utc_now_plus(minutes: int) -> datetime:
    return datetime.now(UTC) + timedelta(minutes=minutes)
