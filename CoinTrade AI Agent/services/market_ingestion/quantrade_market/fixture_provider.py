from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Iterator

from quantrade_schemas.models import BookSide, ReplayEventType

from .order_book import LocalOrderBook


FIXTURE_EVENTS_PATH = (
    Path(__file__).resolve().parents[3]
    / "packages"
    / "test_fixtures"
    / "fixtures"
    / "market_replay_events.json"
)


@dataclass(frozen=True)
class ReplayEvent:
    type: ReplayEventType
    timestamp: datetime
    payload: dict[str, object]


@dataclass(frozen=True)
class ReplayResult:
    events_processed: int
    book: LocalOrderBook
    messages: tuple[str, ...]

    def to_api_dict(self) -> dict[str, object]:
        snapshot = self.book.snapshot()
        return {
            "events_processed": self.events_processed,
            "messages": list(self.messages),
            "book": {
                "exchange": snapshot.exchange,
                "symbol": snapshot.symbol,
                "valid": snapshot.valid,
                "checksum_status": snapshot.checksum_status,
                "best_bid": float(snapshot.best_bid) if snapshot.best_bid is not None else None,
                "best_ask": float(snapshot.best_ask) if snapshot.best_ask is not None else None,
                "mid_price": float(snapshot.mid_price) if snapshot.mid_price is not None else None,
                "spread_bps": float(snapshot.spread_bps) if snapshot.spread_bps is not None else None,
                "bids": [[float(level.price), float(level.quantity)] for level in snapshot.bids[:5]],
                "asks": [[float(level.price), float(level.quantity)] for level in snapshot.asks[:5]],
            },
        }


def iter_fixture_events(path: Path = FIXTURE_EVENTS_PATH) -> Iterator[ReplayEvent]:
    raw_events = json.loads(path.read_text())
    for event in raw_events:
        yield ReplayEvent(
            type=ReplayEventType(event["type"]),
            timestamp=datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")),
            payload=event,
        )


def replay_fixture(path: Path = FIXTURE_EVENTS_PATH, stop_after: int | None = None) -> ReplayResult:
    book = LocalOrderBook(exchange="fixture", symbol="BTC-USD")
    messages: list[str] = []
    processed = 0
    for event in iter_fixture_events(path):
        if stop_after is not None and processed >= stop_after:
            break
        processed += 1
        if event.type == ReplayEventType.snapshot:
            book.load_snapshot(
                bids=[(Decimal(price), Decimal(qty)) for price, qty in event.payload["bids"]],
                asks=[(Decimal(price), Decimal(qty)) for price, qty in event.payload["asks"]],
                timestamp=event.timestamp,
                checksum_status=str(event.payload.get("checksum_status", "not_supported")),
            )
            messages.append("snapshot_loaded")
        elif event.type == ReplayEventType.update:
            book.apply_update(
                side=BookSide(event.payload["side"]),
                price=Decimal(str(event.payload["price"])),
                quantity=Decimal(str(event.payload["quantity"])),
                timestamp=event.timestamp,
                checksum_status=str(event.payload.get("checksum_status", "not_supported")),
            )
            messages.append("update_applied" if book.valid else "update_suspended_book")
        elif event.type == ReplayEventType.checksum_failure:
            book.mark_checksum_failure(event.timestamp)
            messages.append("checksum_failure_detected")
        elif event.type == ReplayEventType.disconnect:
            book.valid = False
            book.reconnect_count += 1
            messages.append("feed_disconnected")
        else:
            messages.append(f"{event.type.value}_observed")
    return ReplayResult(events_processed=processed, book=book, messages=tuple(messages))

