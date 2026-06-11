from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UuidPkMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class User(UuidPkMixin, Base):
    __tablename__ = "users"

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    display_name: Mapped[str] = mapped_column(Text)
    development_auth_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    virtual_starting_balance: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    risk_per_trade: Mapped[Decimal] = mapped_column(Numeric(8, 6))
    daily_loss_limit: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    maximum_open_positions: Mapped[int] = mapped_column(Integer)
    preferred_holding_minutes: Mapped[int] = mapped_column(Integer)
    paper_trading_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Asset(UuidPkMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("exchange", "symbol"),)

    symbol: Mapped[str] = mapped_column(String(32))
    base_currency: Mapped[str] = mapped_column(String(16))
    quote_currency: Mapped[str] = mapped_column(String(16))
    display_name: Mapped[str] = mapped_column(Text)
    exchange: Mapped[str] = mapped_column(String(64))
    product_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    eligibility_status: Mapped[str] = mapped_column(String(32))
    exclusion_reason: Mapped[str | None] = mapped_column(Text)


class Trade(Base):
    __tablename__ = "trades"

    exchange: Mapped[str] = mapped_column(String(64), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    trade_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    quantity: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    maker_side: Mapped[str] = mapped_column(String(16))
    aggressor_side: Mapped[str] = mapped_column(String(16))
    notional: Mapped[Decimal] = mapped_column(Numeric(28, 12))


class Candle(Base):
    __tablename__ = "candles"

    exchange: Mapped[str] = mapped_column(String(64), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    timeframe: Mapped[str] = mapped_column(String(16), primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    open: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    high: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    low: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    close: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    volume: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    trade_count: Mapped[int] = mapped_column(Integer)
    buy_volume: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    sell_volume: Mapped[Decimal] = mapped_column(Numeric(28, 12))


class SignalRecord(UuidPkMixin, Base):
    __tablename__ = "signals"

    signal_id: Mapped[str] = mapped_column(String(128), unique=True)
    exchange: Mapped[str] = mapped_column(String(64))
    symbol: Mapped[str] = mapped_column(String(32))
    strategy: Mapped[str] = mapped_column(String(64))
    strategy_version: Mapped[str] = mapped_column(String(32))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    behavioral_state: Mapped[str] = mapped_column(String(64))
    direction: Mapped[str] = mapped_column(String(64))
    opportunity_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    risk_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    manipulation_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    confidence: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    status: Mapped[str] = mapped_column(String(64))
    block_reasons: Mapped[dict[str, object]] = mapped_column(JSONB)
    plan: Mapped[dict[str, object]] = mapped_column(JSONB)


class SignalComponentRecord(UuidPkMixin, Base):
    __tablename__ = "signal_components"

    signal_id: Mapped[str] = mapped_column(ForeignKey("signals.signal_id"))
    name: Mapped[str] = mapped_column(String(128))
    raw_value: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    normalized_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    weight: Mapped[Decimal] = mapped_column(Numeric(8, 6))
    contribution: Mapped[Decimal] = mapped_column(Numeric(8, 4))


class PaperOrderRecord(UuidPkMixin, Base):
    __tablename__ = "paper_orders"

    order_id: Mapped[str] = mapped_column(String(128), unique=True)
    signal_id: Mapped[str] = mapped_column(String(128))
    symbol: Mapped[str] = mapped_column(String(32))
    side: Mapped[str] = mapped_column(String(16))
    order_type: Mapped[str] = mapped_column(String(32))
    requested_quantity: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    requested_price: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32))
    time_in_force: Mapped[str] = mapped_column(String(32))


class PaperPositionRecord(UuidPkMixin, Base):
    __tablename__ = "paper_positions"

    position_id: Mapped[str] = mapped_column(String(128), unique=True)
    symbol: Mapped[str] = mapped_column(String(32))
    strategy: Mapped[str] = mapped_column(String(64))
    side: Mapped[str] = mapped_column(String(16))
    quantity: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    average_entry: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    stop_price: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    targets: Mapped[dict[str, object]] = mapped_column(JSONB)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    fees: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32))


class JournalEntryRecord(UuidPkMixin, Base):
    __tablename__ = "journal_entries"

    signal_id: Mapped[str] = mapped_column(String(128))
    position_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    pnl: Mapped[Decimal] = mapped_column(Numeric(28, 12))
    r_multiple: Mapped[Decimal] = mapped_column(Numeric(12, 6))
    rule_compliance: Mapped[dict[str, object]] = mapped_column(JSONB)
    user_note: Mapped[str | None] = mapped_column(Text)
    emotion_tag: Mapped[str | None] = mapped_column(Text)
    ai_review: Mapped[dict[str, object] | None] = mapped_column(JSONB)


class DataQualityEventRecord(UuidPkMixin, Base):
    __tablename__ = "data_quality_events"

    exchange: Mapped[str] = mapped_column(String(64))
    symbol: Mapped[str] = mapped_column(String(32))
    event_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(32))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    details: Mapped[dict[str, object]] = mapped_column(JSONB)


Index("idx_trades_symbol_time", Trade.symbol, Trade.timestamp)
Index("idx_signals_status_score", SignalRecord.status, SignalRecord.opportunity_score)

