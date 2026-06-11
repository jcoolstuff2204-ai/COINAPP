from __future__ import annotations

import unittest

from quantrade_streamlit.adapter import load_dashboard_data


class StreamlitAdapterTests(unittest.TestCase):
    def test_dashboard_data_contains_core_testing_views(self) -> None:
        data = load_dashboard_data("fixture")

        self.assertEqual(data["system"]["mode"], "fixture")
        self.assertTrue(data["system"]["paper_trading_only"])
        self.assertEqual(data["scanner"]["signals"][0]["symbol"], "BTC-USD")
        self.assertTrue(data["replay"]["book"]["valid"])
        self.assertEqual(data["data_health"]["items"][0]["status"], "healthy")
        self.assertEqual(len(data["positions"]["positions"]), 1)
        self.assertEqual(data["performance"]["performance"]["trade_count"], 1)


if __name__ == "__main__":
    unittest.main()

