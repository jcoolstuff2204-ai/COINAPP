from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from quantrade_schemas.models import BookSide, DataHealth, OrderBookLevel, OrderBookSnapshot


@dataclass
class LocalOrderBook:
    exchange: str
    symbol: str
    bids: dict[Decimal, Decimal] = field(default_factory=dict)
    asks: dict[Decimal, Decimal] = field(default_factory=dict)
    last_update_at: datetime | None = None
    valid: bool = False
    checksum_status: str = "not_checked"
    invalid_message_count: int = 0
    reconnect_count: int = 0
    missing_sequence_count: int = 0

    def load_snapshot(
        self,
        bids: list[tuple[Decimal, Decimal]],
        asks: list[tuple[Decimal, Decimal]],
        timestamp: datetime,
        checksum_status: str = "not_supported",
    ) -> None:
        self.bids = self._clean_levels(bids)
        self.asks = self._clean_levels(asks)
        self.last_update_at = timestamp
        self.checksum_status = checksum_status
        self.valid = self._crossed_book_reason() is None
        if not self.valid:
            self.invalid_message_count += 1

    def apply_update(
        self,
        side: BookSide,
        price: Decimal,
        quantity: Decimal,
        timestamp: datetime,
        checksum_status: str = "not_supported",
    ) -> None:
        if self.last_update_at and timestamp < self.last_update_at:
            self.missing_sequence_count += 1
            self.valid = False
            return
        levels = self.bids if side == BookSide.bid else self.asks
        if quantity < 0:
            self.invalid_message_count += 1
            self.valid = False
            return
        if quantity == 0:
            levels.pop(price, None)
        else:
            levels[price] = quantity
        self.last_update_at = timestamp
        self.checksum_status = checksum_status
        self.valid = self._crossed_book_reason() is None
        if not self.valid:
            self.invalid_message_count += 1

    def mark_checksum_failure(self, timestamp: datetime) -> None:
        self.last_update_at = timestamp
        self.checksum_status = "failed"
        self.valid = False
        self.invalid_message_count += 1

    def snapshot(self) -> OrderBookSnapshot:
        timestamp = self.last_update_at or datetime.fromtimestamp(0)
        bids = tuple(
            OrderBookLevel(price=price, quantity=qty, side=BookSide.bid, updated_at=timestamp)
            for price, qty in sorted(self.bids.items(), reverse=True)
        )
        asks = tuple(
            OrderBookLevel(price=price, quantity=qty, side=BookSide.ask, updated_at=timestamp)
            for price, qty in sorted(self.asks.items())
        )
        return OrderBookSnapshot(
            exchange=self.exchange,
            symbol=self.symbol,
            timestamp=timestamp,
            bids=bids,
            asks=asks,
            valid=self.valid,
            checksum_status=self.checksum_status,
        )

    def health(self, now: datetime) -> DataHealth:
        age = None
        if self.last_update_at:
            age = max(0, int((now - self.last_update_at).total_seconds()))
        status = "healthy" if self.valid else "suspended"
        return DataHealth(
            exchange=self.exchange,
            symbol=self.symbol,
            status=status,
            last_event_at=self.last_update_at,
            order_book_valid=self.valid,
            checksum_status=self.checksum_status,
            invalid_message_count=self.invalid_message_count,
            reconnect_count=self.reconnect_count,
            missing_sequence_count=self.missing_sequence_count,
            feed_age_seconds=age,
        )

    @staticmethod
    def _clean_levels(levels: list[tuple[Decimal, Decimal]]) -> dict[Decimal, Decimal]:
        return {price: qty for price, qty in levels if qty > 0}

    def _crossed_book_reason(self) -> str | None:
        if not self.bids or not self.asks:
            return "empty_side"
        if max(self.bids) >= min(self.asks):
            return "crossed_book"
        return None

