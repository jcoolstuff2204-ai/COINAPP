from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from quantrade_persistence.serializers import (
    journal_record_payload,
    paper_order_record_payload,
    paper_position_record_payload,
    signal_component_payloads,
    signal_from_record_payload,
    signal_record_payload,
)
from quantrade_schemas.models import DataHealth, Signal

from .models import (
    DataQualityEventRecord,
    JournalEntryRecord,
    PaperOrderRecord,
    PaperPositionRecord,
    SignalComponentRecord,
    SignalRecord,
)


class SqlAlchemyQuanTradeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_signal(self, signal: Signal) -> None:
        payload = signal_record_payload(signal)
        existing = self.session.scalar(select(SignalRecord).where(SignalRecord.signal_id == signal.signal_id))
        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            self.session.execute(delete(SignalComponentRecord).where(SignalComponentRecord.signal_id == signal.signal_id))
        else:
            self.session.add(SignalRecord(**payload))
        self.session.add_all(SignalComponentRecord(**payload) for payload in signal_component_payloads(signal))
        self.session.commit()

    def list_signals(self) -> list[Signal]:
        records = list(
            self.session.scalars(
                select(SignalRecord).order_by(SignalRecord.opportunity_score.desc(), SignalRecord.generated_at.desc())
            )
        )
        signals: list[Signal] = []
        for record in records:
            components = list(
                self.session.scalars(
                    select(SignalComponentRecord).where(SignalComponentRecord.signal_id == record.signal_id)
                )
            )
            signals.append(
                signal_from_record_payload(
                    _model_dict(record),
                    [_model_dict(component) for component in components],
                )
            )
        return signals

    def save_data_health(self, health: DataHealth) -> None:
        self.session.add(
            DataQualityEventRecord(
                exchange=health.exchange,
                symbol=health.symbol,
                event_type="health_status",
                severity="info" if health.status == "healthy" else "warning",
                occurred_at=health.last_event_at,
                details=health.to_api_dict(),
            )
        )
        self.session.commit()

    def list_data_health(self) -> list[DataHealth]:
        records = list(
            self.session.scalars(
                select(DataQualityEventRecord).order_by(DataQualityEventRecord.occurred_at.desc()).limit(50)
            )
        )
        return [
            DataHealth(
                exchange=str(record.details["exchange"]),
                symbol=str(record.details["symbol"]),
                status=str(record.details["status"]),
                last_event_at=record.occurred_at,
                order_book_valid=bool(record.details["order_book_valid"]),
                checksum_status=str(record.details["checksum_status"]),
                invalid_message_count=int(record.details["invalid_message_count"]),
                reconnect_count=int(record.details["reconnect_count"]),
                missing_sequence_count=int(record.details["missing_sequence_count"]),
                feed_age_seconds=record.details["feed_age_seconds"],
            )
            for record in records
        ]

    def save_paper_order_result(self, result: dict[str, object]) -> None:
        self.session.add(PaperOrderRecord(**paper_order_record_payload(result)))
        position_payload = paper_position_record_payload(result)
        position_payload.pop("source_order_id", None)
        self.session.add(PaperPositionRecord(**position_payload))
        self.session.add(JournalEntryRecord(**journal_record_payload(result)))
        self.session.commit()

    def list_paper_positions(self) -> list[dict[str, object]]:
        records = list(self.session.scalars(select(PaperPositionRecord).order_by(PaperPositionRecord.opened_at.desc())))
        return [
            {
                "position_id": record.position_id,
                "symbol": record.symbol,
                "side": record.side,
                "quantity": float(record.quantity),
                "average_entry": float(record.average_entry),
                "stop_price": float(record.stop_price),
                "targets": [float(target) for target in record.targets["levels"]],
                "fees": float(record.fees),
                "opened_at": record.opened_at.isoformat(),
                "status": record.status,
            }
            for record in records
        ]

    def latest_portfolio(self) -> dict[str, object] | None:
        positions = self.list_paper_positions()
        if not positions:
            return None
        fees = sum(float(position["fees"]) for position in positions)
        return {
            "equity": 10000.0 - fees,
            "cash": None,
            "open_risk": None,
            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "fees": fees,
            "paper_trading_only": True,
        }

    def list_journal_entries(self) -> list[dict[str, object]]:
        records = list(self.session.scalars(select(JournalEntryRecord).order_by(JournalEntryRecord.created_at.desc())))
        return [
            {
                "signal_id": record.signal_id,
                "position_id": record.position_id,
                "pnl": float(record.pnl),
                "r_multiple": float(record.r_multiple),
                "rule_compliance": record.rule_compliance,
                "user_note": record.user_note,
                "emotion_tag": record.emotion_tag,
                "ai_review": record.ai_review,
            }
            for record in records
        ]

    def latest_performance(self) -> dict[str, object] | None:
        positions = self.list_paper_positions()
        if not positions:
            return None
        return {
            "trade_count": len(positions),
            "open_positions": len([position for position in positions if position["status"] == "open"]),
            "closed_positions": len([position for position in positions if position["status"] == "closed"]),
            "win_rate": None,
            "profit_factor": None,
            "expectancy": None,
            "fees": sum(float(position["fees"]) for position in positions),
            "max_drawdown": 0.0,
        }


def _model_dict(model: object) -> dict[str, object]:
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}

