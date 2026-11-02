"""Deterministic P8-P10 demo composition with no network or clinical authority."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import cast
from uuid import NAMESPACE_URL, uuid5

from app.config.settings import Environment
from app.modules.ai_orchestration.contracts import (
    RESULT_CONTRACT_VERSION,
    FinishReason,
    JsonValue,
    ResultProvenance,
    StructuredLLMRequest,
    StructuredLLMResult,
)
from app.modules.ai_orchestration.providers import (
    OrchestrationOutcome,
    StructuredGenerationCapability,
)
from app.modules.clinical_intake.domain import ClinicalIntake, ClinicalIntakeStatus
from app.modules.clinical_intake.extraction.application import ClinicalIntakeExtractor
from app.modules.clinical_intake.extraction.contracts import (
    EXTRACTION_PROMPT_ID,
    EXTRACTION_PROMPT_VERSION,
    EXTRACTION_SCHEMA_ID,
    EXTRACTION_SCHEMA_VERSION,
    CandidateFieldKey,
    ClinicalExtractionTask,
    EvidenceSpan,
    ExtractionDisposition,
    SourceInput,
    derive_candidate_id,
)
from app.modules.safety.contracts import SyntheticSafetyInput, SyntheticSignal
from app.modules.safety.engine import SyntheticSafetyEngine
from app.modules.safety.policies import build_synthetic_policy_registry
from app.modules.safety.synthetic import SYNTHETIC_RULE_SET
from app.modules.summaries.contracts import SummaryProjectionInput, SyntheticSourceProjection
from app.modules.summaries.domain import (
    PatientReportedMarker,
    SummarySectionId,
    SummarySourceKind,
    SummarySourceReference,
)
from app.modules.summaries.projection import build_engineering_draft
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId

DEMO_PHRASE = "I report synthetic pain"
DEMO_PROVIDER_ID = "college_demo_offline"


@dataclass(frozen=True, slots=True)
class DemoResult:
    intake_id: str
    encounter_id: str
    status: str
    classification: str
    extracted_label: str | None
    verification_state: str | None
    safety_decision: Mapping[str, object] | None
    summary_sections: tuple[Mapping[str, object], ...]
    notice: str


class _DeterministicDemoCapability(StructuredGenerationCapability):
    """Exact-fixture structured generator; it performs no I/O."""

    async def generate_structured(self, request: StructuredLLMRequest) -> OrchestrationOutcome:
        source = request.input.get("source")
        text = source.get("text") if isinstance(source, Mapping) else None
        reference = request.provenance_context[0]
        common: dict[str, object] = {
            "schema_id": EXTRACTION_SCHEMA_ID,
            "schema_version": EXTRACTION_SCHEMA_VERSION,
            "prompt_id": EXTRACTION_PROMPT_ID,
            "prompt_version": EXTRACTION_PROMPT_VERSION,
            "missing_information_candidates": [],
            "contradiction_candidates": [],
            "uncertainty": [],
            "provenance": {
                "provider_id": DEMO_PROVIDER_ID,
                "provider_model_id": "deterministic_fixture",
                "provider_model_version": "1.0.0",
                "source_references": [reference.to_dict()],
            },
        }
        if text == DEMO_PHRASE:
            literal = "synthetic pain"
            start = DEMO_PHRASE.index(literal)
            evidence = EvidenceSpan(
                source_id=reference.source_id,
                source_version=reference.source_version,
                content_hash=reference.content_hash,
                start=start,
                end=start + len(literal),
                quote=literal,
            )
            payload = {
                **common,
                "disposition": ExtractionDisposition.CANDIDATES.value,
                "candidate_facts": [
                    {
                        "candidate_id": derive_candidate_id(
                            CandidateFieldKey.CHIEF_COMPLAINT_TEXT, evidence, literal
                        ),
                        "field_key": CandidateFieldKey.CHIEF_COMPLAINT_TEXT.value,
                        "value": literal,
                        "evidence": evidence.model_dump(),
                        "verification_state": "AI_EXTRACTED_UNCONFIRMED",
                        "confidence": None,
                    }
                ],
                "abstention_reason": None,
                "refusal_reason": None,
            }
        else:
            payload = {
                **common,
                "disposition": ExtractionDisposition.ABSTAINED.value,
                "candidate_facts": [],
                "abstention_reason": "LITERAL_SUPPORT_INSUFFICIENT",
                "refusal_reason": None,
            }
        result = StructuredLLMResult(
            result_contract_version=RESULT_CONTRACT_VERSION,
            request_id=request.request_id,
            operation_id=request.operation_id,
            request_contract_version=request.request_contract_version,
            schema_id=request.schema_id,
            schema_version=request.schema_version,
            prompt_id=request.prompt_id,
            prompt_version=request.prompt_version,
            provider_id=DEMO_PROVIDER_ID,
            provider_model_id="deterministic_fixture",
            provider_model_version="1.0.0",
            provider_request_id=None,
            validated_payload=cast(Mapping[str, JsonValue], payload),
            finish_reason=FinishReason.STOP,
            usage=None,
            latency_ms=0.0,
            attempt_count=1,
            provenance=ResultProvenance(
                schema_id=request.schema_id,
                schema_version=request.schema_version,
                prompt_id=request.prompt_id,
                prompt_version=request.prompt_version,
                provider_id=DEMO_PROVIDER_ID,
                provider_model_id="deterministic_fixture",
                provider_model_version="1.0.0",
                source_references=request.provenance_context,
            ),
        )
        return OrchestrationOutcome.success(result)


class EngineeringDemoService:
    def __init__(self) -> None:
        self._capability = _DeterministicDemoCapability()

    async def project(self, intake: ClinicalIntake) -> DemoResult:
        if intake.status is not ClinicalIntakeStatus.COMPLETED:
            raise ApplicationError(
                code=ErrorCode.INVALID_STATE_TRANSITION,
                message="Complete the intake draft before opening the synthetic preview.",
            )
        complaint = intake.chief_complaint
        if complaint is None:
            raise ApplicationError(
                code=ErrorCode.INSUFFICIENT_INFORMATION,
                message="The completed intake has no supported source for this preview.",
            )
        now = datetime.now(UTC)
        text = complaint.patient_wording
        task = ClinicalExtractionTask(
            request_id=f"req_{intake.intake_id.value.hex}",
            language_code="en",
            source=SourceInput(
                source_id=f"source_{intake.intake_id.value.hex}",
                source_version=f"v{intake.version}",
                content_hash=sha256(text.encode("utf-8")).hexdigest(),
                text=text,
            ),
        )
        extraction = await ClinicalIntakeExtractor(
            capability=self._capability,
            engineering_mode=True,
            clock=lambda: now,
        ).extract(task)
        if extraction.failure is not None or extraction.result is None:
            return self._abstained(intake)
        candidates = extraction.result.candidate_facts
        if not candidates:
            return self._abstained(intake)

        candidate = candidates[0]
        safety = SyntheticSafetyEngine(
            registry=build_synthetic_policy_registry(),
            rule_set=SYNTHETIC_RULE_SET,
            clock=lambda: now,
        ).evaluate(
            synthetic_input=SyntheticSafetyInput(
                signals=(
                    SyntheticSignal.SYNTHETIC_COMPLETE_A,
                    SyntheticSignal.SYNTHETIC_ROUTINE_A,
                )
            ),
            environment=Environment.LOCAL,
        )
        source = SummarySourceReference(
            source_id=complaint.source_answer_id,
            encounter_id=intake.encounter_id,
            section_id=SummarySectionId.CHIEF_COMPLAINT,
            source_kind=SummarySourceKind.P7_PATIENT_REPORTED,
            source_version=f"v{intake.version}",
            p7_marker=PatientReportedMarker.PATIENT_REPORTED,
        )
        summary = build_engineering_draft(
            SummaryProjectionInput(
                summary_id=OpaqueId(uuid5(NAMESPACE_URL, f"summary:{intake.intake_id.value}")),
                encounter_id=intake.encounter_id,
                snapshot_token=f"intake-v{intake.version}",
                generated_at=now,
                sources=(
                    SyntheticSourceProjection(
                        assertion_id=OpaqueId(
                            uuid5(NAMESPACE_URL, f"assertion:{candidate.candidate_id}")
                        ),
                        label="SYNTHETIC_PAIN",
                        source=source,
                    ),
                ),
            )
        )
        sections = tuple(
            {
                "section_id": section.section_id.value,
                "readiness": section.readiness.value,
                "labels": tuple(assertion.label for assertion in section.assertions),
                "review_required": section.review_required,
            }
            for section in summary.sections
            if section.assertions
        )
        return DemoResult(
            intake_id=str(intake.intake_id.value),
            encounter_id=str(intake.encounter_id.value),
            status="SYNTHETIC_PREVIEW",
            classification="ENGINEERING_ONLY",
            extracted_label="SYNTHETIC_PAIN",
            verification_state=candidate.verification_state.value,
            safety_decision={
                "route": safety.route.value,
                "reason_codes": safety.reason_codes,
                "policy_id": safety.policy_id,
                "policy_version": safety.policy_version,
                "requires_clarification": safety.requires_clarification,
                "blocks_self_care": safety.blocks_self_care,
                "created_at": safety.created_at.isoformat().replace("+00:00", "Z"),
            },
            summary_sections=sections,
            notice="Engineering test data only. This is not a diagnosis or medical assessment.",
        )

    @staticmethod
    def _abstained(intake: ClinicalIntake) -> DemoResult:
        return DemoResult(
            intake_id=str(intake.intake_id.value),
            encounter_id=str(intake.encounter_id.value),
            status="ABSTAINED",
            classification="ENGINEERING_ONLY",
            extracted_label=None,
            verification_state=None,
            safety_decision=None,
            summary_sections=(),
            notice="No synthetic fixture matched. No clinical assessment was performed.",
        )
