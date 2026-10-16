"""Stable P7-A clinical-intake exports without runtime registration."""

from app.modules.clinical_intake.contracts import (
    AnswerIntakeCapability,
    CompleteIntakeCapability,
    NextQuestionCapability,
    ReadIntakeCapability,
    StartIntakeCapability,
)
from app.modules.consent.public import CONSENT_CHECK
from app.modules.encounters.public import ENCOUNTERS_READ, ENCOUNTERS_TRANSITION
from app.modules.patients.public import PATIENTS_FACTS_LIST, PATIENTS_READ
from app.modules.sessions.public import SESSIONS_VALIDATE
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest

INTAKE_START = CapabilityKey[StartIntakeCapability](CapabilityIdentifier("intake.start"))
INTAKE_READ = CapabilityKey[ReadIntakeCapability](CapabilityIdentifier("intake.read"))
INTAKE_ANSWER = CapabilityKey[AnswerIntakeCapability](CapabilityIdentifier("intake.answer"))
INTAKE_COMPLETE = CapabilityKey[CompleteIntakeCapability](CapabilityIdentifier("intake.complete"))
INTAKE_NEXT_QUESTION = CapabilityKey[NextQuestionCapability](
    CapabilityIdentifier("intake.next_question")
)

CLINICAL_INTAKE_MANIFEST = ModuleManifest(
    module_id=ModuleId("clinical_intake"),
    version=1,
    provided_capabilities=frozenset(
        key.identifier
        for key in (
            INTAKE_START,
            INTAKE_READ,
            INTAKE_ANSWER,
            INTAKE_COMPLETE,
            INTAKE_NEXT_QUESTION,
        )
    ),
    required_capabilities=frozenset(
        key.identifier
        for key in (
            SESSIONS_VALIDATE,
            CONSENT_CHECK,
            ENCOUNTERS_READ,
            ENCOUNTERS_TRANSITION,
            PATIENTS_READ,
            PATIENTS_FACTS_LIST,
        )
    ),
    data_ownership=("clinical_intakes", "intake_answers", "questionnaire_instances"),
)

__all__ = [
    "CLINICAL_INTAKE_MANIFEST",
    "INTAKE_ANSWER",
    "INTAKE_COMPLETE",
    "INTAKE_NEXT_QUESTION",
    "INTAKE_READ",
    "INTAKE_START",
]
