from __future__ import annotations

import unittest
from decimal import Decimal
from pathlib import Path

from quantrade_features.engine import calculate_fixture_features, normalize
from quantrade_market.fixture_provider import replay_fixture
from quantrade_market.order_book import LocalOrderBook
from quantrade_paper.engine import open_long_position, position_size, simulate_fixture_order
from quantrade_persistence import (
    InMemoryQuanTradeRepository,
    journal_record_payload,
    paper_order_record_payload,
    paper_position_record_payload,
    signal_component_payloads,
    signal_from_record_payload,
    signal_record_payload,
)
from quantrade_risk.engine import evaluate_risk
from quantrade_schemas.models import BookSide
from quantrade_signals.momentum import generate_momentum_signal
from quantrade_schemas.models import SignalStatus


class CoreEngineTests(unittest.TestCase):
    def test_normalize_clamps_bounds(self) -> None:
        self.assertEqual(normalize(Decimal("-1"), Decimal("0"), Decimal("10")), Decimal("0"))
        self.assertEqual(normalize(Decimal("11"), Decimal("0"), Decimal("10")), Decimal("100"))
        self.assertEqual(normalize(Decimal("5"), Decimal("0"), Decimal("10")), Decimal("50.0"))

    def test_fixture_signal_is_reproducible_and_explainable(self) -> None:
        features = calculate_fixture_features()
        signal = generate_momentum_signal(features)
        self.assertEqual(signal.symbol, "BTC-USD")
        self.assertEqual(signal.status, SignalStatus.strong_candidate)
        self.assertGreaterEqual(signal.opportunity_score, Decimal("75"))
        self.assertEqual(sum((c.weight for c in signal.components), Decimal("0")), Decimal("1.00"))

    def test_risk_blocks_stale_feed(self) -> None:
        features = calculate_fixture_features()
        features.data_quality["feed_age_seconds"] = 99
        decision = evaluate_risk(features)
        self.assertFalse(decision.approved)
        self.assertIn("feed_stale", decision.block_reasons)

    def test_position_size_respects_cash_and_stop_distance(self) -> None:
        quantity = position_size(
            cash=Decimal("1000"),
            risk_per_trade=Decimal("0.01"),
            entry=Decimal("100"),
            stop=Decimal("95"),
        )
        self.assertEqual(quantity, Decimal("2.00000000"))

    def test_blocked_signal_cannot_create_position(self) -> None:
        features = calculate_fixture_features()
        features.data_quality["valid"] = False
        signal = generate_momentum_signal(features)
        self.assertEqual(signal.status, SignalStatus.blocked)
        with self.assertRaises(ValueError):
            open_long_position(signal, Decimal("1000"), Decimal("0.01"))

    def test_order_book_snapshot_and_update_preserve_invariants(self) -> None:
        features = calculate_fixture_features()
        book = LocalOrderBook(exchange="fixture", symbol="BTC-USD")
        book.load_snapshot(
            bids=[(Decimal("100.00"), Decimal("1.0"))],
            asks=[(Decimal("100.10"), Decimal("1.0"))],
            timestamp=features.timestamp,
            checksum_status="passed",
        )
        book.apply_update(
            side=BookSide.bid,
            price=Decimal("100.05"),
            quantity=Decimal("2.0"),
            timestamp=features.timestamp,
            checksum_status="passed",
        )
        snapshot = book.snapshot()
        self.assertTrue(snapshot.valid)
        self.assertEqual(snapshot.best_bid, Decimal("100.05"))
        self.assertEqual(snapshot.best_ask, Decimal("100.10"))
        self.assertEqual(snapshot.spread_bps, Decimal("5.00"))

    def test_crossed_order_book_is_invalid(self) -> None:
        features = calculate_fixture_features()
        book = LocalOrderBook(exchange="fixture", symbol="BTC-USD")
        book.load_snapshot(
            bids=[(Decimal("101.00"), Decimal("1.0"))],
            asks=[(Decimal("100.00"), Decimal("1.0"))],
            timestamp=features.timestamp,
            checksum_status="passed",
        )
        self.assertFalse(book.snapshot().valid)
        self.assertEqual(book.invalid_message_count, 1)

    def test_fixture_replay_returns_valid_book(self) -> None:
        replay = replay_fixture()
        snapshot = replay.book.snapshot()
        self.assertEqual(replay.events_processed, 5)
        self.assertTrue(snapshot.valid)
        self.assertEqual(snapshot.checksum_status, "passed")
        self.assertIsNotNone(snapshot.spread_bps)

    def test_checksum_failure_suspends_book(self) -> None:
        path = Path("packages/test_fixtures/fixtures/checksum_failure_events.json")
        replay = replay_fixture(path=path)
        snapshot = replay.book.snapshot()
        self.assertFalse(snapshot.valid)
        self.assertEqual(snapshot.checksum_status, "failed")
        self.assertIn("checksum_failure_detected", replay.messages)

    def test_simulated_paper_order_creates_portfolio_and_journal(self) -> None:
        signal = generate_momentum_signal(calculate_fixture_features())
        result = simulate_fixture_order(signal, cash=Decimal("10000"), risk_per_trade=Decimal("0.01"))
        api = result.to_api_dict()
        self.assertEqual(api["order"]["status"], "filled")
        self.assertEqual(api["position"]["status"], "open")
        self.assertTrue(api["portfolio"]["paper_trading_only"])
        self.assertEqual(api["journal_entry"]["rule_compliance"]["paper_trade_only"], True)
        self.assertGreater(api["portfolio"]["open_risk"], 0)

    def test_in_memory_repository_persists_fixture_slice(self) -> None:
        repo = InMemoryQuanTradeRepository()
        signal = generate_momentum_signal(calculate_fixture_features())
        replay = replay_fixture()
        order_result = simulate_fixture_order(signal).to_api_dict()
        repo.save_signal(signal)
        repo.save_data_health(replay.book.health(signal.generated_at))
        repo.save_paper_order_result(order_result)

        self.assertEqual(repo.list_signals()[0].signal_id, signal.signal_id)
        self.assertEqual(repo.list_data_health()[0].symbol, "BTC-USD")
        self.assertEqual(repo.list_paper_positions()[0]["position_id"], order_result["position"]["position_id"])
        self.assertEqual(repo.latest_portfolio(), order_result["portfolio"])
        self.assertEqual(repo.list_journal_entries()[0], order_result["journal_entry"])
        self.assertEqual(repo.latest_performance(), order_result["performance"])

    def test_signal_serializers_round_trip_database_payload(self) -> None:
        signal = generate_momentum_signal(calculate_fixture_features())
        record = signal_record_payload(signal)
        components = signal_component_payloads(signal)
        restored = signal_from_record_payload(record, components)

        self.assertEqual(restored.signal_id, signal.signal_id)
        self.assertEqual(restored.opportunity_score, signal.opportunity_score)
        self.assertEqual(restored.entry_zone, signal.entry_zone)
        self.assertEqual(restored.targets, signal.targets)
        self.assertEqual(len(restored.components), len(signal.components))

    def test_paper_serializers_create_database_payloads(self) -> None:
        signal = generate_momentum_signal(calculate_fixture_features())
        result = simulate_fixture_order(signal).to_api_dict()
        order = paper_order_record_payload(result)
        position = paper_position_record_payload(result)
        journal = journal_record_payload(result)

        self.assertEqual(order["order_id"], result["order"]["order_id"])
        self.assertEqual(position["position_id"], result["position"]["position_id"])
        self.assertIn("levels", position["targets"])
        self.assertEqual(journal["signal_id"], signal.signal_id)
        self.assertEqual(journal["r_multiple"], Decimal("0"))


if __name__ == "__main__":
    unittest.main()
