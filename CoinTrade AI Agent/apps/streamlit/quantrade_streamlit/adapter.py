from __future__ import annotations

from quantrade_api import services
from quantrade_persistence import InMemoryQuanTradeRepository


def reset_demo_repository() -> None:
    services.repository = InMemoryQuanTradeRepository()


def load_dashboard_data(mode: str = "fixture") -> dict[str, object]:
    reset_demo_repository()
    scanner = services.scanner_payload(mode)
    signal_id = scanner["signals"][0]["signal_id"]
    paper_order = services.paper_order_payload(mode)
    return {
        "system": {
            "mode": mode,
            "paper_trading_only": True,
            "live_order_submission": False,
            "scanner": "fixture-ready",
        },
        "scanner": scanner,
        "signal_detail": services.signal_detail_payload(str(signal_id)),
        "replay": services.fixture_replay_payload(mode),
        "data_health": services.data_health_payload(mode),
        "paper_order": paper_order,
        "positions": services.paper_positions_payload(mode),
        "portfolio": services.portfolio_payload(mode),
        "journal": services.journal_payload(mode),
        "performance": services.performance_payload(mode),
    }

