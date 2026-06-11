from __future__ import annotations

import unittest

from quantrade_api import services
from quantrade_persistence import InMemoryQuanTradeRepository


class ApiServicePayloadTests(unittest.TestCase):
    def setUp(self) -> None:
        services.repository = InMemoryQuanTradeRepository()

    def test_scanner_payload_contains_grounded_signal(self) -> None:
        payload = services.scanner_payload("fixture")
        signal = payload["signals"][0]

        self.assertTrue(payload["demo_data"])
        self.assertEqual(signal["symbol"], "BTC-USD")
        self.assertIn("explanation", signal)
        self.assertNotIn("buy now", signal["explanation"]["execution_guidance"].lower())

    def test_data_health_payload_persists_health_state(self) -> None:
        payload = services.data_health_payload("fixture")

        self.assertTrue(payload["demo_data"])
        self.assertEqual(payload["items"][0]["symbol"], "BTC-USD")
        self.assertEqual(payload["items"][0]["status"], "healthy")

    def test_paper_payloads_share_repository_state(self) -> None:
        order_payload = services.paper_order_payload("fixture")
        positions_payload = services.paper_positions_payload("fixture")
        portfolio_payload = services.portfolio_payload("fixture")
        journal_payload = services.journal_payload("fixture")
        performance_payload = services.performance_payload("fixture")

        self.assertTrue(order_payload["paper_trading_only"])
        self.assertEqual(len(positions_payload["positions"]), 1)
        self.assertTrue(portfolio_payload["portfolio"]["paper_trading_only"])
        self.assertEqual(len(journal_payload["entries"]), 1)
        self.assertEqual(performance_payload["performance"]["trade_count"], 1)


if __name__ == "__main__":
    unittest.main()

