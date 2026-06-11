"""Initial QuanTrade schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-11
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    sql_path = Path(__file__).resolve().parents[1] / "0001_initial_schema.sql"
    op.execute(sql_path.read_text())


def downgrade() -> None:
    for table_name in reversed(
        [
            "system_health_events",
            "audit_logs",
            "ai_explanations",
            "alerts",
            "discipline_events",
            "journal_entries",
            "portfolio_snapshots",
            "paper_positions",
            "paper_fills",
            "paper_orders",
            "watchlist_items",
            "signal_events",
            "signal_components",
            "signals",
            "strategy_versions",
            "strategy_definitions",
            "market_regimes",
            "feature_snapshots",
            "feature_definitions",
            "data_quality_events",
            "order_book_snapshots",
            "candles",
            "trades",
            "asset_eligibility_history",
            "assets",
            "exchanges",
            "user_settings",
            "users",
        ]
    ):
        op.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")

