"""Explicit inert processor metadata registry tests."""

import traceback
from dataclasses import FrozenInstanceError, replace
from itertools import permutations
from typing import Any, cast

import pytest
from test_document_classification import candidate, request

from app.modules.documents.classification import (
    ClassificationDecision,
    ClassificationDisposition,
    ClassificationReason,
    DocumentType,
    SyntheticClassificationCandidate,
    classify_synthetic,
)
from app.modules.documents.contracts import (
    OCR_REQUEST_CONTRACT_VERSION,
    PARSER_REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    OCRMode,
    ParserMode,
)
from app.modules.documents.registry import (
    MAX_PROCESSOR_DESCRIPTORS,
    PROCESSOR_RECEIPT_SCHEMA_VERSION,
    PROCESSOR_REGISTRY_SCHEMA_VERSION,
    ProcessorAuthority,
    ProcessorDescriptor,
    ProcessorDisposition,
    ProcessorPin,
    ProcessorRegistry,
    ProcessorRegistryCode,
    ProcessorRegistryError,
    RegistryReason,
    RegistryResolutionStatus,
    build_synthetic_processor_registry,
)


def descriptor(
    processor_id: str = "LabReportProcessor",
    *,
    version: str = "v1",
    document_type: DocumentType = DocumentType.LAB_REPORT,
    **changes: Any,
) -> ProcessorDescriptor:
    values: dict[str, object] = {
        "processor_id": processor_id,
        "processor_version": version,
        "accepted_types": (document_type,),
        "parser_modes": (),
        "ocr_modes": (OCRMode.TEXT,),
        "input_schema_versions": (OCR_REQUEST_CONTRACT_VERSION,),
        "output_schema_version": RESULT_CONTRACT_VERSION,
        "authority": ProcessorAuthority.ENGINEERING_ONLY,
        "disposition": ProcessorDisposition.NOOP_ABSTAIN,
    }
    values.update(changes)
    return ProcessorDescriptor(**values)  # type: ignore[arg-type]


def pin(
    *,
    document_type: DocumentType = DocumentType.LAB_REPORT,
    processor_id: str = "LabReportProcessor",
    version: str = "v1",
) -> ProcessorPin:
    return ProcessorPin(
        document_type=document_type,
        processor_id=processor_id,
        processor_version=version,
    )


def selected(
    document_type: DocumentType = DocumentType.LAB_REPORT,
) -> ClassificationDecision:
    return classify_synthetic(request((candidate(document_type),)))


def test_factory_contains_exact_six_inactive_future_processor_names() -> None:
    registry = build_synthetic_processor_registry()
    assert tuple(item.processor_id for item in registry.descriptors) == (
        "DiagnosticReportProcessor",
        "DischargeSummaryProcessor",
        "ImagingReportProcessor",
        "LabReportProcessor",
        "PrescriptionProcessor",
        "ReferralLetterProcessor",
    )
    assert all(
        item.authority is ProcessorAuthority.ENGINEERING_ONLY for item in registry.descriptors
    )
    assert all(
        item.disposition is ProcessorDisposition.NOOP_ABSTAIN for item in registry.descriptors
    )


def test_exact_pin_yields_nonexecuting_metadata_receipt() -> None:
    receipt = build_synthetic_processor_registry().resolve(selected())
    assert receipt.status is RegistryResolutionStatus.PINNED_METADATA
    assert receipt.reason is RegistryReason.EXACT_PIN
    assert receipt.processor_id == "LabReportProcessor"
    assert receipt.processor_version == "v1"
    assert receipt.document_type is DocumentType.LAB_REPORT
    assert receipt.parser_modes == ()
    assert receipt.ocr_modes == (OCRMode.TEXT,)
    assert receipt.registry_schema_version == PROCESSOR_REGISTRY_SCHEMA_VERSION
    assert receipt.receipt_schema_version == PROCESSOR_RECEIPT_SCHEMA_VERSION
    assert receipt.processor_disposition is ProcessorDisposition.NOOP_ABSTAIN
    for forbidden in ("process", "execute", "extract", "parse", "dispatch", "handler"):
        assert not hasattr(receipt, forbidden)


@pytest.mark.parametrize("document_type", [DocumentType.UNKNOWN, DocumentType.OTHER])
def test_unknown_and_other_classifications_always_abstain(document_type: DocumentType) -> None:
    decision = classify_synthetic(request((candidate(document_type),)))
    receipt = build_synthetic_processor_registry().resolve(decision)
    assert decision.disposition is not ClassificationDisposition.SELECTED
    assert receipt.status is RegistryResolutionStatus.ABSTAINED
    assert receipt.processor_id is None


def test_conflict_and_absent_evidence_always_abstain() -> None:
    decisions = (
        classify_synthetic(request(())),
        classify_synthetic(
            request(
                (
                    candidate(DocumentType.LAB_REPORT),
                    candidate(DocumentType.PRESCRIPTION, number=2),
                )
            )
        ),
    )
    assert all(
        build_synthetic_processor_registry().resolve(item).status
        is RegistryResolutionStatus.ABSTAINED
        for item in decisions
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"processor_id": "bad.module:Processor"},
        {"processor_id": "APPROVED"},
        {"processor_version": "latest"},
        {"accepted_types": [DocumentType.LAB_REPORT]},
        {"accepted_types": (DocumentType.OTHER,)},
        {"accepted_types": (DocumentType.UNKNOWN,)},
        {"accepted_types": (DocumentType.LAB_REPORT, DocumentType.LAB_REPORT)},
        {"parser_modes": (cast(Any, "NATIVE_TEXT"),)},
        {"ocr_modes": (cast(Any, ["private-canary"]),)},
        {"parser_modes": (), "ocr_modes": ()},
        {"input_schema_versions": ("future-p11d-candidates.v1",)},
        {"output_schema_version": "future-p11d-candidates.v1"},
        {"authority": cast(Any, "CLINICIAN_CONFIRMED")},
        {"disposition": cast(Any, "MOCK_ACTIVATED")},
    ],
)
def test_descriptor_rejects_hostile_or_authority_claiming_metadata(
    changes: dict[str, object],
) -> None:
    with pytest.raises(ProcessorRegistryError) as raised:
        descriptor(**cast(Any, changes))
    rendered = "".join(traceback.format_exception(raised.value))
    assert "private-canary" not in rendered
    assert raised.value.code in set(ProcessorRegistryCode)


def test_descriptor_and_registry_reject_unexpected_fields_with_closed_errors() -> None:
    with pytest.raises(ProcessorRegistryError) as descriptor_error:
        descriptor(clinical_status="APPROVED")
    assert descriptor_error.value.code is ProcessorRegistryCode.UNEXPECTED_FIELD
    with pytest.raises(ProcessorRegistryError) as registry_error:
        ProcessorRegistry(descriptors=(), runtime_provider="private-canary")
    assert registry_error.value.code is ProcessorRegistryCode.UNEXPECTED_FIELD


def test_descriptor_rejects_string_and_tuple_subclass_lookalikes() -> None:
    class StringLookalike(str):
        pass

    class TupleLookalike(tuple[DocumentType, ...]):
        pass

    with pytest.raises(ProcessorRegistryError) as text_error:
        descriptor(processor_id=StringLookalike("LabReportProcessor"))
    assert text_error.value.code is ProcessorRegistryCode.INVALID_VALUE
    with pytest.raises(ProcessorRegistryError) as tuple_error:
        descriptor(accepted_types=TupleLookalike((DocumentType.LAB_REPORT,)))
    assert tuple_error.value.code is ProcessorRegistryCode.INVALID_TYPE


def test_descriptor_accepts_existing_parser_contract_only_when_declared() -> None:
    value = descriptor(
        parser_modes=(ParserMode.NATIVE_TEXT,),
        ocr_modes=(),
        input_schema_versions=(PARSER_REQUEST_CONTRACT_VERSION,),
    )
    assert value.parser_modes == (ParserMode.NATIVE_TEXT,)
    assert value.output_schema_version == RESULT_CONTRACT_VERSION


def test_registry_rejects_duplicates_and_cross_processor_ownership_in_both_orders() -> None:
    first = descriptor()
    duplicate = descriptor()
    collision = descriptor("AlternateLabProcessor")
    for values in ((first, duplicate), (duplicate, first)):
        with pytest.raises(ProcessorRegistryError) as raised:
            ProcessorRegistry(descriptors=values)
        assert raised.value.code is ProcessorRegistryCode.DUPLICATE_IDENTITY
    for values in ((first, collision), (collision, first)):
        with pytest.raises(ProcessorRegistryError) as raised:
            ProcessorRegistry(descriptors=values)
        assert raised.value.code is ProcessorRegistryCode.AMBIGUOUS_OWNERSHIP


def test_separately_registered_versions_require_one_exact_pin() -> None:
    versions = (descriptor(version="v1"), descriptor(version="v2"))
    unpinned = ProcessorRegistry(descriptors=versions)
    receipt = unpinned.resolve(selected())
    assert receipt.status is RegistryResolutionStatus.AMBIGUOUS
    assert receipt.reason is RegistryReason.MULTIPLE_UNPINNED_VERSIONS
    assert receipt.processor_id is None

    pinned = ProcessorRegistry(descriptors=versions, pins=(pin(version="v2"),))
    assert pinned.resolve(selected()).processor_version == "v2"


def test_single_unpinned_descriptor_is_unavailable_not_implicitly_latest() -> None:
    receipt = ProcessorRegistry(descriptors=(descriptor(),)).resolve(selected())
    assert receipt.status is RegistryResolutionStatus.UNAVAILABLE
    assert receipt.reason is RegistryReason.NO_PIN
    assert receipt.processor_id is None


def test_pin_rejects_unknown_wrong_category_duplicate_and_unprocessable_type() -> None:
    registered = (descriptor(),)
    cases = (
        (pin(version="v2"), ProcessorRegistryCode.UNKNOWN_PROCESSOR),
        (
            pin(document_type=DocumentType.PRESCRIPTION),
            ProcessorRegistryCode.INCOMPATIBLE_DECLARATION,
        ),
    )
    for selection, code in cases:
        with pytest.raises(ProcessorRegistryError) as raised:
            ProcessorRegistry(descriptors=registered, pins=(selection,))
        assert raised.value.code is code
    with pytest.raises(ProcessorRegistryError) as duplicate:
        ProcessorRegistry(descriptors=registered, pins=(pin(), pin()))
    assert duplicate.value.code is ProcessorRegistryCode.AMBIGUOUS_OWNERSHIP
    with pytest.raises(ProcessorRegistryError):
        pin(document_type=DocumentType.UNKNOWN)


def test_registry_order_never_changes_descriptors_or_resolution() -> None:
    descriptors = (
        descriptor(),
        descriptor("PrescriptionProcessor", document_type=DocumentType.PRESCRIPTION),
    )
    expected = None
    for ordered in permutations(descriptors):
        registry = ProcessorRegistry(descriptors=ordered, pins=(pin(),))
        result = (registry.descriptors, registry.resolve(selected()))
        expected = result if expected is None else expected
        assert result == expected


def test_registry_snapshots_and_revalidates_caller_owned_descriptor() -> None:
    original = descriptor()
    registry = ProcessorRegistry(descriptors=(original,), pins=(pin(),))
    object.__setattr__(original, "processor_id", "PrivateCanaryProcessor")
    assert registry.descriptors[0].processor_id == "LabReportProcessor"
    assert registry.resolve(selected()).processor_id == "LabReportProcessor"
    with pytest.raises(FrozenInstanceError):
        registry.descriptors[0].processor_version = "v9"  # type: ignore[misc]


@pytest.mark.parametrize("reverse_candidates", [False, True])
@pytest.mark.parametrize(
    ("target", "attribute", "forged_value"),
    [
        ("decision", "selected_type", DocumentType.PRESCRIPTION),
        ("decision", "disposition", ClassificationDisposition.ABSTAINED),
        ("decision", "reason", ClassificationReason.ABSENT_EVIDENCE),
        ("candidate", "document_type", DocumentType.PRESCRIPTION),
        ("candidate", "source", ["private-canary"]),
        ("candidate", "candidate_ref", {"private-canary": "reference"}),
        ("candidate_source", "value", ["private-canary"]),
        ("candidate_ref", "value", ["private-canary"]),
    ],
)
def test_resolve_revalidates_hostile_decision_graph_before_routing(
    reverse_candidates: bool,
    target: str,
    attribute: str,
    forged_value: object,
) -> None:
    candidates: tuple[SyntheticClassificationCandidate, ...] = (
        candidate(DocumentType.LAB_REPORT),
        candidate(DocumentType.LAB_REPORT, number=2),
    )
    if reverse_candidates:
        candidates = tuple(reversed(candidates))
    decision = classify_synthetic(request(candidates))
    selected_candidate = decision.candidates[0]
    mutation_target: object = {
        "decision": decision,
        "candidate": selected_candidate,
        "candidate_source": selected_candidate.source,
        "candidate_ref": selected_candidate.candidate_ref,
    }[target]
    object.__setattr__(mutation_target, attribute, forged_value)

    with pytest.raises(ProcessorRegistryError) as raised:
        build_synthetic_processor_registry().resolve(decision)

    assert raised.value.code is ProcessorRegistryCode.INCOMPATIBLE_DECLARATION
    assert "private-canary" not in "".join(traceback.format_exception(raised.value))


def test_resolve_preserves_all_fresh_decision_outcomes_after_snapshot() -> None:
    registry = build_synthetic_processor_registry()
    outcomes = (
        (selected(), RegistryResolutionStatus.PINNED_METADATA),
        (
            classify_synthetic(request((candidate(DocumentType.UNKNOWN),))),
            RegistryResolutionStatus.ABSTAINED,
        ),
        (
            classify_synthetic(request((candidate(DocumentType.OTHER),))),
            RegistryResolutionStatus.ABSTAINED,
        ),
        (classify_synthetic(request(())), RegistryResolutionStatus.ABSTAINED),
        (
            classify_synthetic(
                request(
                    (
                        candidate(DocumentType.LAB_REPORT),
                        candidate(DocumentType.PRESCRIPTION, number=2),
                    )
                )
            ),
            RegistryResolutionStatus.ABSTAINED,
        ),
    )
    assert tuple(registry.resolve(value).status for value, _ in outcomes) == tuple(
        expected for _, expected in outcomes
    )


@pytest.mark.parametrize(
    ("attribute", "forged_value"),
    [
        ("processor_version", ["private-canary"]),
        ("processor_id", {"private-canary": "v1"}),
        ("document_type", "LAB_REPORT"),
        ("document_type", DocumentType.OTHER),
        ("processor_version", "latest"),
    ],
)
def test_registry_revalidates_hostile_pins_before_hashing_in_both_orders(
    attribute: str, forged_value: object
) -> None:
    forged = pin(
        document_type=DocumentType.PRESCRIPTION,
        processor_id="PrescriptionProcessor",
    )
    object.__setattr__(forged, attribute, forged_value)
    valid = pin()
    descriptors = (
        descriptor(),
        descriptor("PrescriptionProcessor", document_type=DocumentType.PRESCRIPTION),
    )

    for pins in ((valid, forged), (forged, valid)):
        with pytest.raises(ProcessorRegistryError) as raised:
            ProcessorRegistry(descriptors=descriptors, pins=pins)
        assert raised.value.code in {
            ProcessorRegistryCode.INVALID_TYPE,
            ProcessorRegistryCode.INVALID_VALUE,
            ProcessorRegistryCode.INVALID_VERSION,
            ProcessorRegistryCode.INCOMPATIBLE_DECLARATION,
        }
        assert "private-canary" not in "".join(traceback.format_exception(raised.value))

    assert (
        ProcessorRegistry(descriptors=descriptors, pins=(valid,)).resolve(selected()).processor_id
        == "LabReportProcessor"
    )


def test_registry_rejects_hostile_containers_and_size_before_hashing() -> None:
    with pytest.raises(ProcessorRegistryError) as wrong_container:
        ProcessorRegistry(descriptors=cast(Any, [descriptor()]))
    assert wrong_container.value.code is ProcessorRegistryCode.INVALID_TYPE
    with pytest.raises(ProcessorRegistryError) as unhashable:
        ProcessorRegistry(descriptors=(cast(Any, ["private-canary"]),))
    assert unhashable.value.code is ProcessorRegistryCode.INVALID_TYPE
    many = tuple(
        descriptor(
            f"Synthetic{index}Processor",
            version=f"v{index + 1}",
        )
        for index in range(MAX_PROCESSOR_DESCRIPTORS + 1)
    )
    with pytest.raises(ProcessorRegistryError) as overflow:
        ProcessorRegistry(descriptors=many)
    assert overflow.value.code is ProcessorRegistryCode.LIMIT_EXCEEDED


def test_exact_lookup_is_version_pinned_and_content_free_on_failure() -> None:
    registry = ProcessorRegistry(descriptors=(descriptor(),))
    assert registry.lookup(processor_id="LabReportProcessor", processor_version="v1").identity == (
        "LabReportProcessor",
        "v1",
    )
    canary = "private-canary"
    with pytest.raises(ProcessorRegistryError) as unknown:
        registry.lookup(processor_id=canary, processor_version="latest")
    assert unknown.value.code is ProcessorRegistryCode.UNKNOWN_PROCESSOR
    assert "private-canary" not in "".join(traceback.format_exception(unknown.value))
    with pytest.raises(ProcessorRegistryError) as wrong_type:
        registry.lookup(processor_id=cast(Any, []), processor_version="v1")
    assert wrong_type.value.code is ProcessorRegistryCode.INVALID_TYPE


def test_receipt_direct_constructor_cannot_claim_execution_or_fake_selection() -> None:
    receipt = build_synthetic_processor_registry().resolve(selected())
    for changes in (
        {"processor_disposition": cast(Any, "EXECUTE")},
        {"authority": cast(Any, "APPROVED")},
        {"processor_id": None},
        {"registry_schema_version": "document-processor-registry.v2"},
        {"input_schema_versions": ("future-p11d-candidates.v1",)},
        {"output_schema_version": "future-p11d-candidates.v1"},
        {"ocr_modes": (OCRMode.LAYOUT,), "input_schema_versions": ()},
        {"ocr_modes": (), "parser_modes": ()},
        {"reason": RegistryReason.NO_PIN},
    ):
        with pytest.raises(ProcessorRegistryError):
            replace(receipt, **changes)


def test_nonselected_receipts_require_exact_immutable_empty_tuples() -> None:
    registry = ProcessorRegistry(descriptors=(descriptor(),))
    receipts = (
        build_synthetic_processor_registry().resolve(classify_synthetic(request(()))),
        registry.resolve(selected()),
        ProcessorRegistry(descriptors=(descriptor(), descriptor(version="v2"))).resolve(selected()),
    )
    assert tuple(receipt.status for receipt in receipts) == (
        RegistryResolutionStatus.ABSTAINED,
        RegistryResolutionStatus.UNAVAILABLE,
        RegistryResolutionStatus.AMBIGUOUS,
    )

    class FalsyList(list[object]):
        def __bool__(self) -> bool:
            return False

    corruptions = (
        {"parser_modes": cast(Any, [])},
        {"ocr_modes": cast(Any, {})},
        {"input_schema_versions": cast(Any, set())},
        {"parser_modes": cast(Any, FalsyList())},
    )
    for receipt in receipts:
        for changes in corruptions:
            with pytest.raises(ProcessorRegistryError) as raised:
                replace(receipt, **changes)
            assert raised.value.code is ProcessorRegistryCode.INVALID_TYPE
            assert "private-canary" not in "".join(traceback.format_exception(raised.value))
        with pytest.raises(FrozenInstanceError):
            receipt.parser_modes = ()  # type: ignore[misc]


def test_registry_has_no_runtime_execution_api_or_callable_metadata() -> None:
    registry = build_synthetic_processor_registry()
    for value in (registry, *registry.descriptors):
        for forbidden in ("process", "execute", "extract", "parse", "dispatch", "handler"):
            assert not hasattr(value, forbidden)
    assert all(
        not callable(getattr(item, field_name))
        for item in registry.descriptors
        for field_name in item.__dataclass_fields__
    )
