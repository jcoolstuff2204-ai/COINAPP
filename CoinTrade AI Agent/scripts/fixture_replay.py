from __future__ import annotations

import argparse
import json

from quantrade_ai.templates import TemplateExplanationProvider
from quantrade_features.engine import calculate_fixture_features
from quantrade_market.fixture_provider import replay_fixture
from quantrade_paper.engine import simulate_fixture_order
from quantrade_signals.momentum import generate_momentum_signal


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay deterministic QuanTrade fixture data.")
    parser.add_argument("--summary", action="store_true", help="Print compact replay summary.")
    args = parser.parse_args()

    features = calculate_fixture_features()
    signal = generate_momentum_signal(features)
    explanation = TemplateExplanationProvider().explain(signal)
    replay = replay_fixture()
    paper = simulate_fixture_order(signal)
    if args.summary:
        book = replay.book.snapshot()
        print(
            f"{features.data_quality['label']} | {signal.symbol} | {signal.status.value} "
            f"| score={signal.opportunity_score} | book_valid={book.valid} | spread_bps={book.spread_bps}"
        )
        return
    print(
        json.dumps(
            {
                "signal": signal.to_api_dict(),
                "explanation": explanation.model_dump(mode="json"),
                "replay": replay.to_api_dict(),
                "paper": paper.to_api_dict(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
