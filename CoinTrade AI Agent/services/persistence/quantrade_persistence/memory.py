from __future__ import annotations

from dataclasses import dataclass, field

from quantrade_schemas.models import DataHealth, Signal


@dataclass
class InMemoryQuanTradeRepository:
    signals: dict[str, Signal] = field(default_factory=dict)
    data_health: dict[str, DataHealth] = field(default_factory=dict)
    paper_results: list[dict[str, object]] = field(default_factory=list)

    def save_signal(self, signal: Signal) -> None:
        self.signals[signal.signal_id] = signal

    def list_signals(self) -> list[Signal]:
        return sorted(self.signals.values(), key=lambda signal: signal.opportunity_score, reverse=True)

    def save_data_health(self, health: DataHealth) -> None:
        self.data_health[f"{health.exchange}:{health.symbol}"] = health

    def list_data_health(self) -> list[DataHealth]:
        return list(self.data_health.values())

    def save_paper_order_result(self, result: dict[str, object]) -> None:
        self.paper_results.append(result)

    def list_paper_positions(self) -> list[dict[str, object]]:
        return [dict(result["position"]) for result in self.paper_results if "position" in result]

    def latest_portfolio(self) -> dict[str, object] | None:
        if not self.paper_results:
            return None
        return dict(self.paper_results[-1]["portfolio"])

    def list_journal_entries(self) -> list[dict[str, object]]:
        return [dict(result["journal_entry"]) for result in self.paper_results if "journal_entry" in result]

    def latest_performance(self) -> dict[str, object] | None:
        if not self.paper_results:
            return None
        return dict(self.paper_results[-1]["performance"])

