"""Synthetic-only document label normalization tests."""

import traceback
from dataclasses import FrozenInstanceError, replace
from typing import Any, cast
from uuid import UUID

import pytest

from app.modules.documents.classification import (
    CLASSIFICATION_CONFIG_VERSION,
    CLASSIFICATION_SCHEMA_VERSION,
    MAX_CLASSIFICATION_CANDIDATES,
    ClassificationAuthority,
    ClassificationContractError,
    ClassificationDecision,
    ClassificationDisposition,
    ClassificationErrorCode,
    ClassificationReason,
    ClassificationRequest,
    DocumentType,
    SyntheticClassificationCandidate,
    SyntheticClassificationRef,
    classify_synthetic,
)
from app.modules.documents.contracts import SyntheticSourceRef
from app.shared.types import OpaqueId


def oid(number: int) -> OpaqueId:
    return OpaqueId(UUID(int=number))


def candidate(
    document_type: DocumentType = DocumentType.LAB_REPORT,
    *,
    number: int = 1,
    **changes: Any,
) -> SyntheticClassificationCandidate:
    values: dict[str, object] = {
        "candidate_ref": SyntheticClassificationRef(f"SYNTHETIC_CLASSIFICATION_{number}"),
        "request_id": oid(1),
        "document_id": oid(2),
        "processing_attempt_id": oid(3),
        "source": SyntheticSourceRef("SYNTHETIC_SOURCE_CLASSIFICATION"),
        "document_type": document_type,
        "schema_version": CLASSIFICATION_SCHEMA_VERSION,
        "config_version": CLASSIFICATION_CONFIG_VERSION,
    }
    values.update(changes)
    return SyntheticClassificationCandidate(**values)  # type: ignore[arg-type]


def request(
    base_candidates: tuple[SyntheticClassificationCandidate, ...], **changes: Any
) -> ClassificationRequest:
    values: dict[str, object] = {
        "request_id": oid(1),
        "document_id": oid(2),
        "processing_attempt_id": oid(3),
        "source": SyntheticSourceRef("SYNTHETIC_SOURCE_CLASSIFICATION"),
        "candidates": base_candidates,
        "schema_version": CLASSIFICATION_SCHEMA_VERSION,
        "config_version": CLASSIFICATION_CONFIG_VERSION,
    }
    values.update(changes)
    return ClassificationRequest(**values)  # type: ignore[arg-type]


def test_document_type_vocabulary_is_exact_and_closed() -> None:
    assert tuple(item.value for item in DocumentType) == (
        "PRESCRIPTION",
        "LAB_REPORT",
        "DISCHARGE_SUMMARY",
        "DIAGNOSTIC_REPORT",
        "IMAGING_REPORT",
        "REFERRAL_LETTER",
        "OTHER",
        "UNKNOWN",
    )


@pytest.mark.parametrize(
    ("candidates", "disposition", "reason"),
    [
        ((), ClassificationDisposition.ABSTAINED, ClassificationReason.ABSENT_EVIDENCE),
        (
            (candidate(DocumentType.UNKNOWN),),
            ClassificationDisposition.ABSTAINED,
            ClassificationReason.UNKNOWN_DECLARATION,
        ),
        (
            (candidate(DocumentType.OTHER),),
            ClassificationDisposition.UNSUPPORTED,
            ClassificationReason.OTHER_DECLARATION,
        ),
        (
            (candidate(DocumentType.UNKNOWN), candidate(DocumentType.OTHER, number=2)),
            ClassificationDisposition.CONFLICT,
            ClassificationReason.CONFLICTING_DECLARATIONS,
        ),
    ],
)
def test_absent_unknown_other_and_mixed_declarations_never_select(
    candidates: tuple[SyntheticClassificationCandidate, ...],
    disposition: ClassificationDisposition,
    reason: ClassificationReason,
) -> None:
    decision = classify_synthetic(request(candidates))
    assert decision.disposition is disposition
    assert decision.reason is reason
    assert decision.selected_type is None
    assert decision.authority is ClassificationAuthority.ENGINEERING_ONLY


def test_exact_same_type_candidates_select_without_confidence() -> None:
    decision = classify_synthetic(request((candidate(number=2), candidate(number=1))))
    assert decision.disposition is ClassificationDisposition.SELECTED
    assert decision.selected_type is DocumentType.LAB_REPORT
    assert decision.reason is ClassificationReason.EXACT_SYNTHETIC_LABEL
    assert tuple(item.candidate_ref.value for item in decision.candidates) == (
        "SYNTHETIC_CLASSIFICATION_1",
        "SYNTHETIC_CLASSIFICATION_2",
    )
    assert not hasattr(decision, "confidence")


def test_conflict_is_not_resolved_by_alphabetic_or_input_order() -> None:
    left = candidate(DocumentType.PRESCRIPTION, number=1)
    right = candidate(DocumentType.LAB_REPORT, number=2)
    first = classify_synthetic(request((left, right)))
    second = classify_synthetic(request((right, left)))
    assert first == second
    assert first.disposition is ClassificationDisposition.CONFLICT
    assert first.selected_type is None


@pytest.mark.parametrize(
    "changes",
    [
        {"document_type": "LAB_REPORT"},
        {"document_type": object()},
        {"schema_version": "synthetic-document-classification.v2"},
        {"config_version": "production.v1"},
        {"request_id": "private-canary"},
        {"source": "private-canary"},
    ],
)
def test_candidate_rejects_wrong_types_and_versions_content_free(
    changes: dict[str, object],
) -> None:
    with pytest.raises(ClassificationContractError) as raised:
        candidate(**cast(Any, changes))
    assert "private-canary" not in "".join(traceback.format_exception(raised.value))


def test_candidate_rejects_unexpected_authority_field_with_closed_error() -> None:
    with pytest.raises(ClassificationContractError) as raised:
        candidate(authority="APPROVED")
    assert raised.value.code is ClassificationErrorCode.UNEXPECTED_FIELD


def test_candidate_rejects_string_subclasses_and_mutated_opaque_id_content_free() -> None:
    class StringLookalike(str):
        pass

    with pytest.raises(ClassificationContractError) as text_error:
        SyntheticClassificationRef(StringLookalike("SYNTHETIC_CLASSIFICATION_PRIVATE"))
    assert text_error.value.code is ClassificationErrorCode.INVALID_VALUE

    hostile = candidate()
    object.__setattr__(hostile.request_id, "value", ["private-canary"])
    with pytest.raises(ClassificationContractError) as id_error:
        request((hostile,))
    assert id_error.value.code is ClassificationErrorCode.INVALID_TYPE
    assert "private-canary" not in str(id_error.value)


@pytest.mark.parametrize(
    "changes",
    [
        {"candidates": []},
        {"candidates": (cast(Any, ["unhashable-private-canary"]),)},
        {"schema_version": "wrong.v1"},
        {"config_version": "wrong.v1"},
    ],
)
def test_request_rejects_hostile_containers_before_hash_or_sort(
    changes: dict[str, object],
) -> None:
    with pytest.raises(ClassificationContractError) as raised:
        request((), **changes)
    assert "private-canary" not in "".join(traceback.format_exception(raised.value))


def test_request_rejects_duplicate_overflow_and_wrong_context() -> None:
    one = candidate()
    with pytest.raises(ClassificationContractError) as duplicate:
        request((one, one))
    assert duplicate.value.code is ClassificationErrorCode.DUPLICATE_IDENTITY
    with pytest.raises(ClassificationContractError) as overflow:
        request(
            tuple(candidate(number=index + 1) for index in range(MAX_CLASSIFICATION_CANDIDATES + 1))
        )
    assert overflow.value.code is ClassificationErrorCode.LIMIT_EXCEEDED
    with pytest.raises(ClassificationContractError) as context:
        request((candidate(document_id=oid(99)),))
    assert context.value.code is ClassificationErrorCode.CONTEXT_MISMATCH


def test_decision_direct_constructor_cannot_forge_selection_or_authority() -> None:
    valid = classify_synthetic(request((candidate(),)))
    for change in (
        {"selected_type": DocumentType.PRESCRIPTION},
        {"disposition": ClassificationDisposition.ABSTAINED},
        {"reason": ClassificationReason.ABSENT_EVIDENCE},
        {"authority": cast(Any, "APPROVED")},
    ):
        with pytest.raises(ClassificationContractError):
            replace(valid, **change)


def test_contracts_are_immutable_detached_and_hide_sensitive_handles() -> None:
    original = candidate()
    value = request((original,))
    decision = classify_synthetic(value)
    with pytest.raises(FrozenInstanceError):
        decision.selected_type = DocumentType.PRESCRIPTION  # type: ignore[misc]
    object.__setattr__(original.candidate_ref, "value", "PRIVATE_CANARY")
    assert decision.candidates[0].candidate_ref.value == "SYNTHETIC_CLASSIFICATION_1"
    rendered = repr(decision)
    assert "SYNTHETIC_SOURCE" not in rendered
    assert "SYNTHETIC_CLASSIFICATION" not in rendered


def test_classifier_accepts_only_typed_request_and_has_no_text_input() -> None:
    with pytest.raises(ClassificationContractError) as raised:
        classify_synthetic(cast(Any, {"text": "SYNTHETIC_LAB_REPORT"}))
    assert raised.value.code is ClassificationErrorCode.INVALID_TYPE
    assert tuple(ClassificationRequest.__dataclass_fields__) == (
        "request_id",
        "document_id",
        "processing_attempt_id",
        "source",
        "candidates",
        "schema_version",
        "config_version",
    )


def test_direct_decision_constructor_revalidates_candidate_context() -> None:
    valid = classify_synthetic(request((candidate(),)))
    with pytest.raises(ClassificationContractError) as raised:
        ClassificationDecision(
            request_id=valid.request_id,
            document_id=valid.document_id,
            processing_attempt_id=valid.processing_attempt_id,
            source=valid.source,
            candidates=(candidate(document_id=oid(90)),),
            schema_version=valid.schema_version,
            config_version=valid.config_version,
            authority=valid.authority,
            disposition=valid.disposition,
            reason=valid.reason,
            selected_type=valid.selected_type,
        )
    assert raised.value.code is ClassificationErrorCode.CONTEXT_MISMATCH
