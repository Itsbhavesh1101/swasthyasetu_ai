"""Deterministic no-data adapter used only by P20 synthetic boundary tests."""

from datetime import datetime

from app.modules.care_orchestration.sources import (
    SyntheticEvidenceSourceDescriptor,
    SyntheticEvidenceSourceQuery,
    SyntheticEvidenceSourceReceipt,
    synthetic_source_query_fingerprint,
)


class DeterministicSyntheticEvidenceSource:
    """Echo structural metadata without retrieving or interpreting any payload."""

    def __init__(
        self,
        *,
        descriptor: SyntheticEvidenceSourceDescriptor,
        completed_at: datetime,
    ) -> None:
        self.descriptor = descriptor
        self._completed_at = completed_at
        self.calls = 0

    def inspect(self, query: SyntheticEvidenceSourceQuery) -> SyntheticEvidenceSourceReceipt:
        self.calls += 1
        return SyntheticEvidenceSourceReceipt(
            query_id=query.query_id,
            query_fingerprint=synthetic_source_query_fingerprint(query),
            request_id=query.request_id,
            request_fingerprint=query.request_fingerprint,
            descriptor_fingerprint=query.descriptor_fingerprint,
            channel=query.channel,
            evidence_id=query.evidence_id,
            evidence_version=query.evidence_version,
            evidence_hash=query.evidence_hash,
            availability=query.availability,
            completed_at=self._completed_at,
        )


__all__ = ["DeterministicSyntheticEvidenceSource"]
