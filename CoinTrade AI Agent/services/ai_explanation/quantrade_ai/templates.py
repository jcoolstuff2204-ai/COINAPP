from __future__ import annotations

from datetime import UTC, datetime

from quantrade_schemas.models import Signal, SignalExplanation, SignalStatus


class TemplateExplanationProvider:
    model = "template-only"
    prompt_version = "template-v0.1"

    def explain(self, signal: Signal) -> SignalExplanation:
        risk_text = "Risk engine approved the setup." if signal.status != SignalStatus.blocked else "Risk engine blocked the setup."
        return SignalExplanation(
            summary=f"{signal.symbol} is classified as {signal.behavioral_state.value.replace('_', ' ')} with a {signal.opportunity_score} opportunity score.",
            thesis=signal.thesis,
            counter_thesis=signal.counter_thesis,
            evidence=[
                f"{component.name}: {component.normalized_score} normalized score"
                for component in signal.components
                if component.normalized_score >= 60
            ],
            risks=[risk_text, *signal.warnings, *signal.block_reasons],
            invalidation=f"The setup is invalid below {signal.invalidation_price} or if data quality degrades.",
            execution_guidance="Use paper trading only. Do not chase above the entry zone, and respect the invalidation level.",
            confidence_language="Evidence is structured and limited to the supplied fixture snapshot; it is not a prediction.",
            generated_at=datetime.now(UTC),
            model=self.model,
            prompt_version=self.prompt_version,
        )

