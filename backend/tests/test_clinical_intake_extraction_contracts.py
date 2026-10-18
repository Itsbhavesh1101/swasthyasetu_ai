"""Strict P8-B clinical-intake extraction contract tests."""

from __future__ import annotations

from hashlib import sha256

import pytest
from pydantic import ValidationError

from app.modules.ai_orchestration.contracts import SourceReference
from app.modules.clinical_intake.extraction.contracts import (
    EXTRACTION_PROMPT_ID,
    EXTRACTION_PROMPT_VERSION,
    EXTRACTION_SCHEMA_ID,
    EXTRACTION_SCHEMA_VERSION,
    CandidateFact,
    CandidateFieldKey,
    ClinicalExtractionTask,
    ContradictionCandidate,
    EvidenceSpan,
    ExtractionDisposition,
    ExtractionEnvelope,
    ExtractionProvenance,
    MissingInformationCandidate,
    MissingReason,
    SourceInput,
    TaskUncertainty,
    UncertaintyCode,
    VerificationState,
    derive_candidate_id,
    derive_contradiction_candidate_id,
    derive_missing_candidate_id,
)

SOURCE_TEXT = "I have a synthetic headache"
SOURCE_HASH = sha256(SOURCE_TEXT.encode()).hexdigest()
SOURCE = SourceInput(
    source_id="source_synthetic_001",
    source_version="1.0.0",
    content_hash=SOURCE_HASH,
    text=SOURCE_TEXT,
)


def evidence(start: int = 9, end: int = 27, quote: str = "synthetic headache") -> EvidenceSpan:
    return EvidenceSpan(
        source_id=SOURCE.source_id,
        source_version=SOURCE.source_version,
        content_hash=SOURCE.content_hash,
        start=start,
        end=end,
        quote=quote,
    )


def provenance() -> ExtractionProvenance:
    return ExtractionProvenance(
        provider_id="offline_fake",
        provider_model_id="fixture_model",
        provider_model_version="1.0.0",
        source_references=(
            SourceReference(SOURCE.source_id, SOURCE.source_version, SOURCE.content_hash),
        ),
    )


def fact() -> CandidateFact:
    span = evidence()
    value = "synthetic headache"
    return CandidateFact(
        candidate_id=derive_candidate_id(CandidateFieldKey.CHIEF_COMPLAINT_TEXT, span, value),
        field_key=CandidateFieldKey.CHIEF_COMPLAINT_TEXT,
        value=value,
        evidence=span,
        verification_state=VerificationState.AI_EXTRACTED_UNCONFIRMED,
        confidence=0.75,
    )


def envelope(**updates: object) -> ExtractionEnvelope:
    values: dict[str, object] = {
        "schema_id": EXTRACTION_SCHEMA_ID,
        "schema_version": EXTRACTION_SCHEMA_VERSION,
        "prompt_id": EXTRACTION_PROMPT_ID,
        "prompt_version": EXTRACTION_PROMPT_VERSION,
        "disposition": ExtractionDisposition.CANDIDATES,
        "candidate_facts": (fact(),),
        "missing_information_candidates": (),
        "contradiction_candidates": (),
        "uncertainty": (),
        "abstention_reason": None,
        "refusal_reason": None,
        "provenance": provenance(),
    }
    values.update(updates)
    return ExtractionEnvelope.model_validate(values)


def test_task_accepts_one_bounded_normalized_source_and_derives_reference() -> None:
    task = ClinicalExtractionTask(
        request_id="req_synthetic_0001", language_code="en", source=SOURCE
    )

    assert task.source_reference == SourceReference("source_synthetic_001", "1.0.0", SOURCE_HASH)
    assert "synthetic headache" not in repr(task)


@pytest.mark.parametrize(
    ("change", "match"),
    [
        ({"content_hash": "0" * 64}, "content hash"),
        ({"text": "not normalized\r\ntext"}, "normalized"),
        ({"text": "x" * 2001}, "at most"),
        ({"extra": "smuggled"}, "Extra inputs"),
    ],
)
def test_source_rejects_hash_drift_non_normalized_oversize_and_extra_fields(
    change: dict[str, object], match: str
) -> None:
    raw = SOURCE.model_dump()
    raw.update(change)
    if "text" in change and change["text"] != SOURCE_TEXT:
        raw["content_hash"] = sha256(str(change["text"]).encode()).hexdigest()
    with pytest.raises(ValidationError, match=match):
        SourceInput.model_validate(raw)


@pytest.mark.parametrize("invalid_text", ["invalid-\ud800-source", "invalid-\udfff-source"])
def test_source_rejects_lone_surrogates_with_a_safe_validation_error(
    invalid_text: str,
) -> None:
    with pytest.raises(ValidationError) as captured:
        SourceInput(
            source_id="source_synthetic_001",
            source_version="1.0.0",
            content_hash="0" * 64,
            text=invalid_text,
        )

    rendered = str(captured.value)
    assert "valid UTF-8" in rendered
    assert "invalid-" not in rendered


def test_source_accepts_valid_nfc_unicode_and_emoji() -> None:
    text = "I report café pain 😊"

    source = SourceInput(
        source_id="source_synthetic_001",
        source_version="1.0.0",
        content_hash=sha256(text.encode("utf-8")).hexdigest(),
        text=text,
    )

    assert source.text == text


@pytest.mark.parametrize("language", ["hi", "en-US", "EN", "", "unknown"])
def test_task_rejects_every_unapproved_language(language: str) -> None:
    with pytest.raises(ValidationError, match="language"):
        ClinicalExtractionTask(
            request_id="req_synthetic_0001", language_code=language, source=SOURCE
        )


def test_candidate_contract_is_closed_frozen_and_unconfirmed_only() -> None:
    candidate = fact()
    with pytest.raises(ValidationError, match="frozen"):
        candidate.value = "changed"  # type: ignore[misc]
    raw = candidate.model_dump()
    raw["verification_state"] = "CLINICIAN_VERIFIED"
    with pytest.raises(ValidationError):
        CandidateFact.model_validate(raw)
    raw = candidate.model_dump()
    raw["diagnosis"] = "invented"
    with pytest.raises(ValidationError, match="Extra inputs"):
        CandidateFact.model_validate(raw)


@pytest.mark.parametrize("confidence", [float("nan"), float("inf"), -0.01, 1.01, "0.5"])
def test_candidate_rejects_non_finite_out_of_range_or_wrong_type_confidence(
    confidence: object,
) -> None:
    raw = fact().model_dump()
    raw["confidence"] = confidence
    with pytest.raises(ValidationError):
        CandidateFact.model_validate(raw)


def test_envelope_supports_explicit_missing_contradiction_and_uncertainty_candidates() -> None:
    second = EvidenceSpan(
        source_id=SOURCE.source_id,
        source_version=SOURCE.source_version,
        content_hash=SOURCE.content_hash,
        start=2,
        end=6,
        quote="have",
    )
    result = envelope(
        disposition=ExtractionDisposition.ABSTAINED,
        candidate_facts=(),
        missing_information_candidates=(
            MissingInformationCandidate(
                candidate_id=derive_missing_candidate_id(
                    CandidateFieldKey.HPI_DESCRIPTIVE_TEXT,
                    MissingReason.NOT_STATED_IN_SOURCE,
                    (evidence(),),
                ),
                field_key=CandidateFieldKey.HPI_DESCRIPTIVE_TEXT,
                reason=MissingReason.NOT_STATED_IN_SOURCE,
                source_references=(evidence(),),
            ),
        ),
        contradiction_candidates=(
            ContradictionCandidate(
                candidate_id=derive_contradiction_candidate_id(
                    CandidateFieldKey.HISTORY_SECTION_TEXT, second, evidence()
                ),
                field_key=CandidateFieldKey.HISTORY_SECTION_TEXT,
                left=second,
                right=evidence(),
            ),
        ),
        uncertainty=(TaskUncertainty(code=UncertaintyCode.AMBIGUOUS_ATTRIBUTION),),
        abstention_reason="INSUFFICIENT_LITERAL_SUPPORT",
    )

    assert result.missing_information_candidates[0].reason is MissingReason.NOT_STATED_IN_SOURCE
    assert result.contradiction_candidates[0].left != result.contradiction_candidates[0].right


def test_every_proposal_identity_is_deterministic_and_cannot_be_spoofed() -> None:
    with pytest.raises(ValidationError, match="identity"):
        MissingInformationCandidate(
            candidate_id="missing_fake",
            field_key=CandidateFieldKey.HPI_DESCRIPTIVE_TEXT,
            reason=MissingReason.NOT_STATED_IN_SOURCE,
            source_references=(evidence(),),
        )


def test_incompatible_duplicate_field_claims_require_a_contradiction_candidate() -> None:
    second_span = evidence(start=2, end=6, quote="have")
    second = CandidateFact(
        candidate_id=derive_candidate_id(
            CandidateFieldKey.CHIEF_COMPLAINT_TEXT, second_span, "have"
        ),
        field_key=CandidateFieldKey.CHIEF_COMPLAINT_TEXT,
        value="have",
        evidence=second_span,
        verification_state=VerificationState.AI_EXTRACTED_UNCONFIRMED,
    )
    with pytest.raises(ValidationError, match="incompatible"):
        envelope(candidate_facts=(fact(), second))


def test_envelope_rejects_duplicates_incoherent_disposition_and_oversize_collections() -> None:
    with pytest.raises(ValidationError, match="duplicate"):
        envelope(candidate_facts=(fact(), fact()))
    with pytest.raises(ValidationError, match="requires no candidate facts"):
        envelope(disposition=ExtractionDisposition.ABSTAINED, abstention_reason="SAFE_ABSTENTION")
    with pytest.raises(ValidationError):
        envelope(candidate_facts=tuple(fact() for _ in range(17)))
