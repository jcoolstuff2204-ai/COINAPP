from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from quantrade_market.fixture_provider import replay_fixture
from quantrade_schemas.models import HealthStatus, Mode

from .config import settings
from .services import (
    data_health_payload,
    fixture_replay_payload,
    journal_payload,
    paper_order_payload,
    paper_positions_payload,
    performance_payload,
    portfolio_payload,
    scanner_payload,
    signal_detail_payload,
)

app = FastAPI(title="QuanTrade AI Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", response_model=HealthStatus)
def health() -> HealthStatus:
    return HealthStatus(
        status="ok",
        mode=Mode(settings.mode),
        generated_at=datetime.now(UTC),
        checks={"api": "ok", "live_trading": "unavailable"},
    )


@app.get("/api/v1/system/status")
def system_status() -> dict[str, object]:
    replay = replay_fixture()
    health = replay.book.health(datetime.now(UTC))
    return {
        "mode": settings.mode,
        "paper_trading_only": True,
        "live_order_submission": False,
        "scanner": "fixture-ready" if settings.mode == "fixture" else "pending-provider",
        "data_health": health.to_api_dict(),
    }


@app.get("/api/v1/scanner/signals")
def scanner_signals() -> dict[str, object]:
    return scanner_payload(settings.mode)


@app.get("/api/v1/signals/{signal_id}")
def signal_detail(signal_id: str) -> dict[str, object]:
    return signal_detail_payload(signal_id)


@app.get("/api/v1/fixture/replay")
def fixture_replay() -> dict[str, object]:
    return fixture_replay_payload(settings.mode)


@app.get("/api/v1/assets/{symbol}/order-book")
def order_book(symbol: str) -> dict[str, object]:
    replay = replay_fixture()
    response = replay.to_api_dict()["book"]
    return {
        "requested_symbol": symbol,
        "demo_data": True,
        "order_book": response,
    }


@app.get("/api/v1/data-health")
def data_health() -> dict[str, object]:
    return data_health_payload(settings.mode)


@app.post("/api/v1/paper/orders")
def create_paper_order() -> dict[str, object]:
    return paper_order_payload(settings.mode)


@app.get("/api/v1/paper/positions")
def paper_positions() -> dict[str, object]:
    return paper_positions_payload(settings.mode)


@app.get("/api/v1/portfolio")
def portfolio() -> dict[str, object]:
    return portfolio_payload(settings.mode)


@app.get("/api/v1/journal")
def journal() -> dict[str, object]:
    return journal_payload(settings.mode)


@app.get("/api/v1/performance")
def performance() -> dict[str, object]:
    return performance_payload(settings.mode)
