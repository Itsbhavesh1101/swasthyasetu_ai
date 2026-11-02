"""Stable clinical-intake exports and explicit P7-C composition."""

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter

from app.modules.clinical_intake.contracts import (
    AnswerIntakeCapability,
    CompleteIntakeCapability,
    HistoryReusePolicy,
    NextQuestionCapability,
    PackRegistry,
    ReadIntakeCapability,
    StartIntakeCapability,
)
from app.modules.clinical_intake.engine import (
    ENGINE_VERSION,
    AdaptiveIntakeEngine,
    ClarificationRequired,
    CompletionReady,
    EngineInput,
    EngineResult,
    Incomplete,
    InvalidAnswerForQuestionError,
    InvalidEngineInputError,
    NextQuestion,
)
from app.modules.clinical_intake.history import HistoryContext
from app.modules.consent.public import CONSENT_CHECK
from app.modules.encounters.public import ENCOUNTERS_READ
from app.modules.sessions.public import SESSIONS_VALIDATE
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
from app.shared.persistence import DatabaseRuntime

if TYPE_CHECKING:
    from app.modules.clinical_intake.application import ClinicalIntakeService

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
        )
    ),
    api_prefixes=("/encounters/{encounter_id}/intake", "/intakes"),
    data_ownership=("clinical_intakes", "intake_answers", "questionnaire_instances"),
)


def build_clinical_intake_registration(
    *,
    database: DatabaseRuntime | None,
    engineering_content_enabled: bool,
    clock: Callable[[], datetime] | None = None,
    service: "ClinicalIntakeService | None" = None,
) -> ModuleRegistration[APIRouter]:
    """Build isolated runtime dependencies from explicit compile-time content."""
    from app.modules.clinical_intake.api import build_clinical_intake_router

    resolved_service = service or build_clinical_intake_service(
        database=database,
        engineering_content_enabled=engineering_content_enabled,
        clock=clock,
    )
    return ModuleRegistration(
        manifest=CLINICAL_INTAKE_MANIFEST,
        routers=(build_clinical_intake_router(service=resolved_service),),
        capability_bindings=(
            INTAKE_START.bind(resolved_service),
            INTAKE_READ.bind(resolved_service),
            INTAKE_ANSWER.bind(resolved_service),
            INTAKE_COMPLETE.bind(resolved_service),
            INTAKE_NEXT_QUESTION.bind(resolved_service),
        ),
    )


def build_clinical_intake_service(
    *,
    database: DatabaseRuntime | None,
    engineering_content_enabled: bool,
    clock: Callable[[], datetime] | None = None,
) -> "ClinicalIntakeService":
    """Build the service for explicit composition by adjacent local/test modules."""
    from app.modules.clinical_intake.application import ClinicalIntakeService
    from app.modules.clinical_intake.content import engineering_packs

    packs = engineering_packs() if engineering_content_enabled else ()
    registry = PackRegistry(packs)
    allowed = {pack.pack_id: pack.version for pack in packs}
    kwargs = {} if clock is None else {"clock": clock}
    return ClinicalIntakeService(
        database=database,
        registry=registry,
        allowed_pack_versions=allowed,
        **kwargs,
    )


__all__ = [
    "AdaptiveIntakeEngine",
    "CLINICAL_INTAKE_MANIFEST",
    "ClarificationRequired",
    "CompletionReady",
    "ENGINE_VERSION",
    "EngineInput",
    "EngineResult",
    "HistoryContext",
    "HistoryReusePolicy",
    "INTAKE_ANSWER",
    "INTAKE_COMPLETE",
    "INTAKE_NEXT_QUESTION",
    "INTAKE_READ",
    "INTAKE_START",
    "Incomplete",
    "InvalidAnswerForQuestionError",
    "InvalidEngineInputError",
    "NextQuestion",
    "PackRegistry",
    "build_clinical_intake_registration",
    "build_clinical_intake_service",
]
