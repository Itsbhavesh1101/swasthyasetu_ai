"""P7-A immutable clinical-intake domain and closed-contract tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal
from typing import cast

import pytest

from app.modules.clinical_intake.contracts import (
    AnswerReference,
    AnswerType,
    ApprovalState,
    DuplicateQuestionPackError,
    InputMode,
    IntakeAnswer,
    IntakeAnswerSourceType,
    PackRegistry,
    QuestionDefinition,
    QuestionnaireResponses,
    QuestionPack,
    QuestionPackKind,
    QuestionSection,
    Requiredness,
    ResponseDisposition,
    SeverityValidation,
    SkippedQuestionReference,
    TextValidation,
)
from app.modules.clinical_intake.domain import (
    ChiefComplaint,
    ClinicalIntake,
    ClinicalIntakeStatus,
    ConfirmationState,
    Contradiction,
    ContradictionStatus,
    DurationValue,
    HistoryOfPresentIllness,
    HistoryReference,
    HistorySections,
    HistorySourceKind,
    InvalidClinicalIntakeTransitionError,
    MissingInformation,
    MissingReason,
    PriorInvestigation,
    ResolutionState,
    ReviewOfSystemsEntry,
    ReviewOfSystemsState,
    SeverityValue,
    SourceReference,
    StructuredValue,
)
from app.modules.clinical_intake.public import (
    CLINICAL_INTAKE_MANIFEST,
    INTAKE_ANSWER,
    INTAKE_COMPLETE,
    INTAKE_NEXT_QUESTION,
    INTAKE_READ,
    INTAKE_START,
)
from app.modules.clinical_intake.serialization import (
    deserialize_answer,
    deserialize_chief_complaint,
    deserialize_contradictions,
    deserialize_history_sections,
    deserialize_hpi,
    deserialize_missing_information,
    deserialize_questionnaire_responses,
    serialize_answer,
    serialize_chief_complaint,
    serialize_contradictions,
    serialize_history_sections,
    serialize_hpi,
    serialize_missing_information,
    serialize_questionnaire_responses,
)
from app.shared.types import OpaqueId

NOW = datetime(2026, 10, 17, 8, tzinfo=UTC)


def test_clinical_intake_lifecycle_is_immutable_and_normalizes_utc() -> None:
    intake = ClinicalIntake(
        intake_id=OpaqueId.new(),
        encounter_id=OpaqueId.new(),
        status=ClinicalIntakeStatus.IN_PROGRESS,
        started_at=NOW.astimezone(timezone(timedelta(hours=5, minutes=30))),
        version=1,
    )
    assert intake.started_at.tzinfo is UTC
    with pytest.raises(FrozenInstanceError):
        intake.version = 2  # type: ignore[misc]
    completed = intake.transition_to(ClinicalIntakeStatus.COMPLETED, at=NOW + timedelta(minutes=2))
    assert completed.status is ClinicalIntakeStatus.COMPLETED
    assert completed.completed_at == NOW + timedelta(minutes=2)
    with pytest.raises(InvalidClinicalIntakeTransitionError):
        completed.transition_to(ClinicalIntakeStatus.ABANDONED)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"started_at": datetime(2026, 1, 1)}, "timezone-aware"),
        ({"version": 0}, "positive"),
        ({"status": ClinicalIntakeStatus.COMPLETED}, "completed_at"),
        (
            {
                "status": ClinicalIntakeStatus.ABANDONED,
                "completed_at": NOW,
            },
            "only for COMPLETED",
        ),
    ],
)
def test_clinical_intake_rejects_invalid_invariants(kwargs: object, message: str) -> None:
    values = {
        "intake_id": OpaqueId.new(),
        "encounter_id": OpaqueId.new(),
        "status": ClinicalIntakeStatus.IN_PROGRESS,
        "started_at": NOW,
        "version": 1,
    }
    values.update(cast(dict[str, object], kwargs))
    with pytest.raises(ValueError, match=message):
        ClinicalIntake(**values)  # type: ignore[arg-type]


def test_chief_complaint_and_hpi_strict_round_trip() -> None:
    answer_id = OpaqueId.new()
    complaint = ChiefComplaint(
        patient_wording="Synthetic concern",
        display_key="chief.synthetic",
        source_answer_id=answer_id,
    )
    complaint_json = serialize_chief_complaint(complaint)
    assert complaint_json == {
        "schema_version": "chief-complaint.v1",
        "patient_wording": "Synthetic concern",
        "display_key": "chief.synthetic",
        "normalized_code": None,
        "coding_system": None,
        "source_answer_id": str(answer_id),
    }
    assert deserialize_chief_complaint(complaint_json) == complaint

    hpi = HistoryOfPresentIllness(
        onset=StructuredValue(value="Synthetic onset", source_answer_id=answer_id),
        duration=DurationValue(value=Decimal("2.50"), unit="day", source_answer_id=answer_id),
        location=StructuredValue(value="Synthetic location", source_answer_id=answer_id),
        character=StructuredValue(value="Synthetic character", source_answer_id=answer_id),
        severity=SeverityValue(
            scale_id="synthetic.scale",
            scale_version="1.0.0",
            value=Decimal("3"),
            source_answer_id=answer_id,
        ),
        progression=StructuredValue(value="Synthetic progression", source_answer_id=answer_id),
        associated_symptoms=(
            StructuredValue(value="Synthetic associated item", source_answer_id=answer_id),
        ),
        aggravating_factors=(
            StructuredValue(value="Synthetic aggravator", source_answer_id=answer_id),
        ),
        relieving_factors=(
            StructuredValue(value="Synthetic reliever", source_answer_id=answer_id),
        ),
    )
    assert deserialize_hpi(serialize_hpi(hpi)) == hpi


def test_serializers_reject_unknown_shape_without_echoing_sensitive_value() -> None:
    malformed = {
        "schema_version": "chief-complaint.v2",
        "patient_wording": "do not echo this",
        "display_key": "chief.synthetic",
        "normalized_code": None,
        "coding_system": None,
        "source_answer_id": str(OpaqueId.new()),
        "unexpected": True,
    }
    with pytest.raises(ValueError) as exc:
        deserialize_chief_complaint(malformed)
    assert str(exc.value) == "clinical intake persistence shape is invalid"
    assert "do not echo this" not in str(exc.value)


def test_history_sections_ros_and_investigation_round_trip() -> None:
    answer_id = OpaqueId.new()
    reference = HistoryReference(
        entry_id=OpaqueId.new(),
        display_value="Synthetic history",
        source_kind=HistorySourceKind.ANSWER,
        source_answer_id=answer_id,
        confirmation_state=ConfirmationState.CONFIRMED,
    )
    ros = ReviewOfSystemsEntry(
        entry_id=OpaqueId.new(),
        system_key="synthetic.system",
        state=ReviewOfSystemsState.UNKNOWN,
        patient_wording="Synthetic wording",
        source=SourceReference(answer_id=answer_id),
    )
    investigation = PriorInvestigation(
        entry_id=OpaqueId.new(),
        investigation_type="synthetic.test",
        performed_at=NOW,
        result_summary="Synthetic summary",
        document_reference="synthetic-document",
        source=SourceReference(answer_id=answer_id),
        verification_state="PATIENT_CONFIRMED",
    )
    sections = HistorySections(
        past_medical=(reference,),
        past_surgical=(reference,),
        medications=(reference,),
        allergies=(reference,),
        family=(reference,),
        personal=(reference,),
        review_of_systems=(ros,),
        prior_investigations=(investigation,),
    )
    assert deserialize_history_sections(serialize_history_sections(sections)) == sections


def test_history_reference_requires_exactly_matching_source_reference() -> None:
    with pytest.raises(ValueError, match="source_answer_id"):
        HistoryReference(
            entry_id=OpaqueId.new(),
            display_value="Synthetic",
            source_kind=HistorySourceKind.ANSWER,
            confirmation_state=ConfirmationState.PENDING,
        )
    with pytest.raises(ValueError, match="source_fact_id"):
        HistoryReference(
            entry_id=OpaqueId.new(),
            display_value="Synthetic",
            source_kind=HistorySourceKind.REUSED_HISTORY,
            source_answer_id=OpaqueId.new(),
            confirmation_state=ConfirmationState.PENDING,
        )


def test_missing_information_and_contradiction_structural_states() -> None:
    answer_id = OpaqueId.new()
    missing = MissingInformation(
        missing_id=OpaqueId.new(),
        field_or_question_key="synthetic.question",
        reason_code=MissingReason.CLARIFICATION_REQUIRED,
        requiredness=Requiredness.REQUIRED,
        source_pack_id="synthetic.core",
        source_pack_version="1.0.0",
        source_rule_id="synthetic.rule",
        resolution_state=ResolutionState.RESOLVED,
        resolution_answer_id=answer_id,
    )
    assert missing.resolution_answer_id == answer_id
    contradiction = Contradiction(
        contradiction_id=OpaqueId.new(),
        field_key="synthetic.field",
        left_ref=SourceReference(answer_id=answer_id),
        right_ref=SourceReference(fact_id=OpaqueId.new(), verification_state="PATIENT_CONFIRMED"),
        source_pack_id="synthetic.core",
        source_rule_id="synthetic.rule",
        status=ContradictionStatus.RESOLVED,
        resolution_ref=answer_id,
        created_at=NOW,
        resolved_at=NOW + timedelta(minutes=1),
    )
    assert contradiction.resolved_at == NOW + timedelta(minutes=1)


def test_intake_answer_closed_discriminator_and_strict_round_trip() -> None:
    answer = IntakeAnswer(
        answer_id=OpaqueId.new(),
        intake_id=OpaqueId.new(),
        question_id="synthetic.duration",
        question_version="1.0.0",
        answer_type=AnswerType.DURATION,
        value=Decimal("2.50"),
        unit="day",
        response_disposition=ResponseDisposition.ANSWERED,
        language_code="en",
        source_type=IntakeAnswerSourceType.PATIENT_TOUCH,
        answered_at=NOW,
        created_at=NOW,
    )
    assert deserialize_answer(serialize_answer(answer), outer=answer) == answer
    with pytest.raises(ValueError, match="selected_option_ids"):
        IntakeAnswer(
            answer_id=OpaqueId.new(),
            intake_id=OpaqueId.new(),
            question_id="synthetic.text",
            question_version="1.0.0",
            answer_type=AnswerType.TEXT,
            value="Synthetic",
            selected_option_ids=("not-valid-for-text",),
            response_disposition=ResponseDisposition.ANSWERED,
            language_code="en",
            source_type=IntakeAnswerSourceType.PATIENT_TEXT,
            answered_at=NOW,
            created_at=NOW,
        )


@pytest.mark.parametrize(
    ("answer_type", "value", "selected", "unit"),
    [
        (AnswerType.TEXT, "Synthetic response", None, None),
        (AnswerType.SINGLE_CHOICE, None, ("synthetic.one",), None),
        (AnswerType.MULTI_CHOICE, None, ("synthetic.one", "synthetic.two"), None),
        (AnswerType.BOOLEAN, True, None, None),
        (AnswerType.NUMBER, Decimal("2.50"), None, None),
        (AnswerType.DATE, date(2026, 1, 1), None, None),
        (AnswerType.DURATION, Decimal("2.50"), None, "day"),
        (AnswerType.SEVERITY_SCALE, Decimal("3"), None, None),
    ],
)
def test_all_closed_answer_discriminators_round_trip(
    answer_type: AnswerType,
    value: object,
    selected: tuple[str, ...] | None,
    unit: str | None,
) -> None:
    answer = IntakeAnswer(
        answer_id=OpaqueId.new(),
        intake_id=OpaqueId.new(),
        question_id="synthetic.question",
        question_version="1.0.0",
        answer_type=answer_type,
        value=value,  # type: ignore[arg-type]
        selected_option_ids=selected,
        unit=unit,
        response_disposition=ResponseDisposition.ANSWERED,
        language_code="en",
        source_type=IntakeAnswerSourceType.PATIENT_TOUCH,
        answered_at=NOW,
        created_at=NOW,
    )
    assert deserialize_answer(serialize_answer(answer), outer=answer) == answer


def test_non_answered_dispositions_forbid_payload_and_answer_times_are_aware() -> None:
    with pytest.raises(ValueError, match="cannot carry"):
        IntakeAnswer(
            answer_id=OpaqueId.new(),
            intake_id=OpaqueId.new(),
            question_id="synthetic.question",
            question_version="1.0.0",
            answer_type=AnswerType.TEXT,
            value="Synthetic",
            response_disposition=ResponseDisposition.UNKNOWN,
            language_code="en",
            source_type=IntakeAnswerSourceType.PATIENT_TEXT,
            answered_at=NOW,
            created_at=NOW,
        )
    with pytest.raises(ValueError, match="timezone-aware"):
        IntakeAnswer(
            answer_id=OpaqueId.new(),
            intake_id=OpaqueId.new(),
            question_id="synthetic.question",
            question_version="1.0.0",
            answer_type=AnswerType.TEXT,
            value="Synthetic",
            response_disposition=ResponseDisposition.ANSWERED,
            language_code="en",
            source_type=IntakeAnswerSourceType.PATIENT_TEXT,
            answered_at=datetime(2026, 1, 1),
            created_at=NOW,
        )


def _question(question_id: str = "synthetic.question") -> QuestionDefinition:
    return QuestionDefinition(
        question_id=question_id,
        question_version="1.0.0",
        section=QuestionSection.EXTENSION,
        content_key=f"{question_id}.prompt",
        answer_type=AnswerType.TEXT,
        requiredness=Requiredness.OPTIONAL,
        input_modes=(InputMode.TEXT,),
        validation=TextValidation(min_length=1, max_length=80),
        order=0,
    )


def test_question_and_pack_contracts_are_closed_and_registry_is_explicit() -> None:
    question = _question()
    assert isinstance(question.validation, TextValidation)
    severity_question = QuestionDefinition(
        question_id="synthetic.severity",
        question_version="1.0.0",
        section=QuestionSection.HPI,
        content_key="synthetic.severity.prompt",
        answer_type=AnswerType.SEVERITY_SCALE,
        requiredness=Requiredness.CONDITIONAL,
        input_modes=(InputMode.TOUCH,),
        validation=SeverityValidation(
            scale_id="synthetic.scale",
            scale_version="1.0.0",
            allowed_values=(Decimal("1"), Decimal("2")),
        ),
        order=1,
    )
    packs = tuple(
        QuestionPack(
            pack_id=f"synthetic.{kind.value.lower()}",
            version="1.0.0",
            kind=kind,
            approval_state=ApprovalState.CLINICAL_APPROVAL_REQUIRED,
            content_version="1.0.0",
            supported_languages=("en",),
            questions=(question, severity_question),
            order=index,
        )
        for index, kind in enumerate(
            (QuestionPackKind.CORE, QuestionPackKind.SPECIALTY, QuestionPackKind.AYUSH_EXTENSION)
        )
    )
    registry = PackRegistry(packs)
    assert registry.get(packs[1].pack_id, packs[1].version) == packs[1]
    assert registry.all() == packs
    with pytest.raises(DuplicateQuestionPackError):
        PackRegistry((packs[0], packs[0]))


def test_remaining_jsonb_shapes_round_trip_strictly() -> None:
    answer_id = OpaqueId.new()
    missing = (
        MissingInformation(
            missing_id=OpaqueId.new(),
            field_or_question_key="synthetic.question",
            reason_code=MissingReason.REQUIRED_UNANSWERED,
            requiredness=Requiredness.REQUIRED,
            source_pack_id="synthetic.core",
            source_pack_version="1.0.0",
            source_rule_id="synthetic.required",
            resolution_state=ResolutionState.OPEN,
        ),
    )
    contradiction = (
        Contradiction(
            contradiction_id=OpaqueId.new(),
            field_key="synthetic.field",
            left_ref=SourceReference(answer_id=answer_id),
            right_ref=SourceReference(
                fact_id=OpaqueId.new(), verification_state="PATIENT_CONFIRMED"
            ),
            source_pack_id="synthetic.core",
            source_rule_id="synthetic.conflict",
            status=ContradictionStatus.OPEN,
            created_at=NOW,
        ),
    )
    responses = QuestionnaireResponses(
        pack_id="synthetic.core",
        pack_version="1.0.0",
        answer_refs=(AnswerReference("synthetic.question", "1.0.0", answer_id),),
        skipped_question_refs=(
            SkippedQuestionReference("synthetic.optional", "1.0.0", ResponseDisposition.SKIPPED),
        ),
        last_selected_question_id="synthetic.optional",
        engine_version="structural-only.v1",
    )
    assert deserialize_missing_information(serialize_missing_information(missing)) == missing
    assert deserialize_contradictions(serialize_contradictions(contradiction)) == contradiction
    assert (
        deserialize_questionnaire_responses(serialize_questionnaire_responses(responses))
        == responses
    )
    malformed = serialize_questionnaire_responses(responses) | {"unexpected": True}
    with pytest.raises(ValueError, match="clinical intake persistence shape is invalid"):
        deserialize_questionnaire_responses(malformed)


def test_manifest_declares_future_surface_without_runtime_binding() -> None:
    assert str(CLINICAL_INTAKE_MANIFEST.module_id) == "clinical_intake"
    assert CLINICAL_INTAKE_MANIFEST.version == 1
    assert CLINICAL_INTAKE_MANIFEST.data_ownership == (
        "clinical_intakes",
        "intake_answers",
        "questionnaire_instances",
    )
    assert CLINICAL_INTAKE_MANIFEST.provided_capabilities == frozenset(
        key.identifier
        for key in (
            INTAKE_START,
            INTAKE_READ,
            INTAKE_ANSWER,
            INTAKE_COMPLETE,
            INTAKE_NEXT_QUESTION,
        )
    )


def test_domain_collections_reject_arbitrary_mapping_elements() -> None:
    with pytest.raises(TypeError, match="missing_information"):
        ClinicalIntake(
            intake_id=OpaqueId.new(),
            encounter_id=OpaqueId.new(),
            status=ClinicalIntakeStatus.IN_PROGRESS,
            started_at=NOW,
            version=1,
            missing_information=({},),  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError, match="past_medical"):
        HistorySections(past_medical=({},))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="answer_refs"):
        QuestionnaireResponses(
            pack_id="synthetic.core",
            pack_version="1.0.0",
            answer_refs=({},),  # type: ignore[arg-type]
            skipped_question_refs=(),
            engine_version="structural-only.v1",
        )
    with pytest.raises(TypeError, match="questions"):
        QuestionPack(
            pack_id="synthetic.core",
            version="1.0.0",
            kind=QuestionPackKind.CORE,
            approval_state=ApprovalState.CLINICAL_APPROVAL_REQUIRED,
            content_version="1.0.0",
            supported_languages=("en",),
            questions=({},),  # type: ignore[arg-type]
            order=0,
        )
