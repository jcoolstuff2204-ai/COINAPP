from __future__ import annotations

from datetime import UTC, datetime

from quantrade_ai.templates import TemplateExplanationProvider
from quantrade_features.engine import calculate_fixture_features
from quantrade_market.fixture_provider import replay_fixture
from quantrade_paper.engine import simulate_fixture_order
from quantrade_persistence import InMemoryQuanTradeRepository, QuanTradeRepository
from quantrade_schemas.models import Signal
from quantrade_signals.momentum import generate_momentum_signal


repository: QuanTradeRepository = InMemoryQuanTradeRepository()


def current_fixture_signal() -> Signal:
    signal = generate_momentum_signal(calculate_fixture_features())
    repository.save_signal(signal)
    return signal


def scanner_payload(mode: str) -> dict[str, object]:
    signal = current_fixture_signal()
    explanation = TemplateExplanationProvider().explain(signal)
    return {
        "mode": mode,
        "demo_data": mode == "fixture",
        "signals": [{**signal.to_api_dict(), "explanation": explanation.model_dump()}],
    }


def signal_detail_payload(signal_id: str) -> dict[str, object]:
    features = calculate_fixture_features()
    signal = generate_momentum_signal(features)
    repository.save_signal(signal)
    explanation = TemplateExplanationProvider().explain(signal)
    return {
        "signal": signal.to_api_dict(),
        "explanation": explanation.model_dump(),
        "timeline": [
            {"event": "fixture_replay_started", "at": features.timestamp.isoformat()},
            {"event": "score_calculated", "at": signal.generated_at.isoformat()},
        ],
        "requested_id": signal_id,
    }


def fixture_replay_payload(mode: str) -> dict[str, object]:
    replay = replay_fixture()
    repository.save_data_health(replay.book.health(datetime.now(UTC)))
    return {"mode": mode, "demo_data": True, **replay.to_api_dict()}


def data_health_payload(mode: str) -> dict[str, object]:
    replay = replay_fixture()
    health = replay.book.health(datetime.now(UTC))
    repository.save_data_health(health)
    return {"mode": mode, "demo_data": True, "items": [item.to_api_dict() for item in repository.list_data_health()]}


def paper_order_payload(mode: str) -> dict[str, object]:
    result = simulate_fixture_order(current_fixture_signal())
    api_result = result.to_api_dict()
    repository.save_paper_order_result(api_result)
    return {
        "mode": mode,
        "demo_data": True,
        "paper_trading_only": True,
        **api_result,
    }


def paper_positions_payload(mode: str) -> dict[str, object]:
    if not repository.list_paper_positions():
        paper_order_payload(mode)
    return {"mode": mode, "demo_data": True, "positions": repository.list_paper_positions()}


def portfolio_payload(mode: str) -> dict[str, object]:
    if repository.latest_portfolio() is None:
        paper_order_payload(mode)
    return {"mode": mode, "demo_data": True, "portfolio": repository.latest_portfolio()}


def journal_payload(mode: str) -> dict[str, object]:
    if not repository.list_journal_entries():
        paper_order_payload(mode)
    return {"mode": mode, "demo_data": True, "entries": repository.list_journal_entries()}


def performance_payload(mode: str) -> dict[str, object]:
    if repository.latest_performance() is None:
        paper_order_payload(mode)
    return {"mode": mode, "demo_data": True, "performance": repository.latest_performance()}

