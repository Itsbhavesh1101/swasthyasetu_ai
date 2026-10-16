"""Bounded, immutable history context consumed by the pure intake engine."""

from dataclasses import dataclass, field

from app.modules.clinical_intake.domain import bounded_text
from app.modules.provenance.domain import VerificationState
from app.shared.types import OpaqueId


@dataclass(frozen=True, slots=True)
class HistoryContext:
    fact_id: OpaqueId
    fact_type: str
    section_key: str
    display_value: str = field(repr=False)
    verification_state: VerificationState

    def __post_init__(self) -> None:
        bounded_text("fact_type", self.fact_type, 64)
        bounded_text("section_key", self.section_key, 128)
        bounded_text("display_value", self.display_value, 2000)


def reusable_history(history: tuple[HistoryContext, ...]) -> tuple[HistoryContext, ...]:
    return tuple(
        item
        for item in history
        if item.verification_state not in {VerificationState.REJECTED, VerificationState.SUPERSEDED}
    )
