"""P7-C application authority and persisted-pack integrity regressions."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from app.modules.clinical_intake.application import ClinicalIntakeService
from app.modules.clinical_intake.contracts import (
    AnswerType,
    ApprovalState,
    InputMode,
    IntakeAnswer,
    IntakeAnswerSourceType,
    PackRegistry,
    QuestionDefinition,
    QuestionnaireInstance,
    QuestionnaireResponses,
    QuestionnaireStatus,
    QuestionPack,
    QuestionPackKind,
    QuestionSection,
    ResponseDisposition,
    RuleDefinition,
    RuleOperator,
    TextValidation,
)
from app.modules.clinical_intake.domain import (
    ClinicalIntake,
    ClinicalIntakeStatus,
    Requiredness,
)
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId

NOW = datetime(2026, 10, 18, 8, tzinfo=UTC)


def _question(
    question_id: str,
    order: int,
    *,
    dependencies: tuple[str, ...] = (),
    applicability: tuple[str, ...] = (),
    requiredness: Requiredness = Requiredness.REQUIRED,
) -> QuestionDefinition:
    return QuestionDefinition(
        question_id=question_id,
        question_version="1.0.0",
        section=QuestionSection.EXTENSION,
        content_key=f"{question_id}.prompt",
        answer_type=AnswerType.TEXT,
        requiredness=requiredness,
        input_modes=(InputMode.TEXT,),
        validation=TextValidation(1, 80),
        order=order,
        dependency_question_ids=dependencies,
        applicability_rule_ids=applicability,
    )


def _setup() -> tuple[
    ClinicalIntakeService,
    ClinicalIntake,
    QuestionnaireInstance,
    tuple[QuestionDefinition, QuestionDefinition, QuestionDefinition],
]:
    first = _question("synthetic.first", 0)
    second = _question("synthetic.second", 1, dependencies=(first.question_id,))
    rule = RuleDefinition(
        "synthetic.first.yes",
        RuleOperator.EQUALS,
        ("question:synthetic.first", "value:yes"),
    )
    conditional = _question(
        "synthetic.conditional",
        2,
        applicability=(rule.rule_id,),
        requiredness=Requiredness.CONDITIONAL,
    )
    pack = QuestionPack(
        pack_id="synthetic.intake",
        version="1.0.0",
        kind=QuestionPackKind.CORE,
        approval_state=ApprovalState.APPROVED,
        content_version="1.0.0",
        supported_languages=("en",),
        questions=(first, second, conditional),
        order=0,
        applicability_rules=(rule,),
    )
    intake = ClinicalIntake(
        intake_id=OpaqueId.new(),
        encounter_id=OpaqueId.new(),
        status=ClinicalIntakeStatus.IN_PROGRESS,
        started_at=NOW,
        version=1,
    )
    instance = QuestionnaireInstance(
        instance_id=OpaqueId.new(),
        encounter_id=intake.encounter_id,
        questionnaire_id=pack.pack_id,
        questionnaire_version=pack.version,
        status=QuestionnaireStatus.ACTIVE,
        responses=QuestionnaireResponses(
            pack_id=pack.pack_id,
            pack_version=pack.version,
            answer_refs=(),
            skipped_question_refs=(),
            engine_version="deterministic-intake.v1",
        ),
        started_at=NOW,
    )
    service = ClinicalIntakeService(
        database=None,
        registry=PackRegistry((pack,)),
        allowed_pack_versions={pack.pack_id: pack.version},
    )
    return service, intake, instance, (first, second, conditional)


def _answer(intake: ClinicalIntake, question: QuestionDefinition, value: str) -> IntakeAnswer:
    return IntakeAnswer(
        answer_id=OpaqueId.new(),
        intake_id=intake.intake_id,
        question_id=question.question_id,
        question_version=question.question_version,
        answer_type=question.answer_type,
        value=value,
        selected_option_ids=None,
        unit=None,
        response_disposition=ResponseDisposition.ANSWERED,
        language_code="en",
        source_type=IntakeAnswerSourceType.PATIENT_TEXT,
        answered_at=NOW,
        created_at=NOW,
        original_text=value,
    )


def test_answer_authority_rejects_dependency_blocked_and_early_conditional_questions() -> None:
    service, intake, instance, (first, second, conditional) = _setup()
    with pytest.raises(ApplicationError) as blocked:
        service._require_answer_authority(
            intake,
            (instance,),
            (),
            question_id=second.question_id,
            question_version=second.question_version,
            language="en",
        )
    assert blocked.value.code is ErrorCode.VALIDATION_ERROR

    first_answer = _answer(intake, first, "yes")
    with pytest.raises(ApplicationError) as early:
        service._require_answer_authority(
            intake,
            (instance,),
            (first_answer,),
            question_id=conditional.question_id,
            question_version=conditional.question_version,
            language="en",
        )
    assert early.value.code is ErrorCode.VALIDATION_ERROR


def test_answer_authority_allows_selected_question_and_eligible_correction() -> None:
    service, intake, instance, (first, second, _) = _setup()
    service._require_answer_authority(
        intake,
        (instance,),
        (),
        question_id=first.question_id,
        question_version=first.question_version,
        language="en",
    )
    first_answer = _answer(intake, first, "yes")
    service._require_answer_authority(
        intake,
        (instance,),
        (first_answer,),
        question_id=second.question_id,
        question_version=second.question_version,
        language="en",
    )
    service._require_answer_authority(
        intake,
        (instance,),
        (first_answer,),
        question_id=first.question_id,
        question_version=first.question_version,
        language="en",
    )


@pytest.mark.parametrize("corruption", ["empty", "duplicate", "wrong_status", "unresolvable"])
def test_completed_result_rejects_corrupt_persisted_pack_instances(corruption: str) -> None:
    service, intake, instance, _ = _setup()
    completed = intake.transition_to(ClinicalIntakeStatus.COMPLETED, at=NOW)
    completed_instance = replace(instance, status=QuestionnaireStatus.COMPLETED, completed_at=NOW)
    instances: tuple[QuestionnaireInstance, ...] = (completed_instance,)
    if corruption == "empty":
        instances = ()
    elif corruption == "duplicate":
        instances = (completed_instance, replace(completed_instance, instance_id=OpaqueId.new()))
    elif corruption == "wrong_status":
        instances = (instance,)
    else:
        service = ClinicalIntakeService(
            database=None,
            registry=PackRegistry(),
            allowed_pack_versions={},
        )
    with pytest.raises(ApplicationError) as raised:
        service._result(completed, instances, (), language="en")
    assert raised.value.code in {ErrorCode.PROCESSING_FAILED, ErrorCode.POLICY_UNAVAILABLE}
