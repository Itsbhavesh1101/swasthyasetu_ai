"""Conservative source/evidence validation for P8-B candidates."""

from __future__ import annotations

import re

from app.modules.clinical_intake.extraction.contracts import (
    CandidateFact,
    ClinicalExtractionTask,
    EvidenceSpan,
    ExtractionEnvelope,
    derive_candidate_id,
)


class ExtractionValidationError(ValueError):
    """Safe machine validation failure without patient or provider content."""


_ABSTENTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(?:no|not|never|without|deny|denies|denied|cannot|can't|don't|doesn't|didn't)\b",
        r"\b(?:maybe|might|could|possibly|unsure|uncertain|if|hypothetical)\b",
        r"\b(?:previously|last year|years? ago|history of|used to)\b",
        r"\bmy (?:mother|father|sister|brother|friend|caregiver)\b",
        r"\b(?:he|she|they) (?:said|has|have|had)\b",
        (
            r"ignore previous|developer message|system\s*(?::|message|>)|<system|"
            r"tool(?:s|_call)?|reveal secrets"
        ),
        r"swdub3j",
    )
)


def _validate_span(task: ClinicalExtractionTask, span: EvidenceSpan) -> str:
    source = task.source
    if (
        span.source_id != source.source_id
        or span.source_version != source.source_version
        or span.content_hash != source.content_hash
    ):
        raise ExtractionValidationError("EXTRACTION_SOURCE_MISMATCH")
    if span.start < 0 or span.end <= span.start or span.end > len(source.text):
        raise ExtractionValidationError("EXTRACTION_EVIDENCE_SPAN_INVALID")
    literal = source.text[span.start : span.end]
    if literal != span.quote:
        raise ExtractionValidationError("EXTRACTION_EVIDENCE_QUOTE_INVALID")
    return literal


def _validate_candidate(task: ClinicalExtractionTask, candidate: CandidateFact) -> None:
    literal = _validate_span(task, candidate.evidence)
    if candidate.value != literal:
        raise ExtractionValidationError("EXTRACTION_LITERAL_SUPPORT_INVALID")
    expected_id = derive_candidate_id(candidate.field_key, candidate.evidence, candidate.value)
    if candidate.candidate_id != expected_id:
        raise ExtractionValidationError("EXTRACTION_CANDIDATE_IDENTITY_INVALID")


def validate_extraction(
    task: ClinicalExtractionTask, envelope: ExtractionEnvelope
) -> ExtractionEnvelope:
    """Reject the complete result when any candidate or reference lacks authority."""
    if envelope.provenance.source_references != (task.source_reference,):
        raise ExtractionValidationError("EXTRACTION_SOURCE_PROVENANCE_INVALID")
    for candidate in envelope.candidate_facts:
        _validate_candidate(task, candidate)
    for missing in envelope.missing_information_candidates:
        for reference in missing.source_references:
            _validate_span(task, reference)
    for contradiction in envelope.contradiction_candidates:
        _validate_span(task, contradiction.left)
        _validate_span(task, contradiction.right)
    if envelope.candidate_facts and any(
        pattern.search(task.source.text) for pattern in _ABSTENTION_PATTERNS
    ):
        raise ExtractionValidationError("EXTRACTION_REQUIRES_ABSTENTION")
    return envelope
