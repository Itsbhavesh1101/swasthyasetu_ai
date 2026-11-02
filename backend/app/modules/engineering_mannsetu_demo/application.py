"""Deterministic, content-free P14 engineering demonstration."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.config.settings import Environment
from app.modules.mental_health.backstop import (
    SyntheticBackstopArtifact,
    SyntheticBackstopOutcome,
    SyntheticBackstopRequest,
    SyntheticBackstopResult,
    SyntheticEvidenceToken,
    synthetic_backstop_request_fingerprint,
    validate_synthetic_backstop_result,
)
from app.modules.mental_health.contracts import (
    SYNTHETIC_RESULT_CONTRACT_VERSION,
    SyntheticArtifactReference,
    SyntheticExtractionRequest,
    SyntheticExtractionResult,
    SyntheticExtractionStatus,
    SyntheticSignalCode,
    SyntheticSignalObservation,
    SyntheticSignalState,
    validate_synthetic_result_binding,
)
from app.modules.mental_health.policy import (
    SyntheticMentalHealthRouteEngine,
    SyntheticPolicyArtifact,
    SyntheticPolicyReasonCode,
    SyntheticPolicyRule,
    SyntheticPolicyState,
    SyntheticRouteEvaluation,
    SyntheticRouteState,
    SyntheticRuleKind,
)


@dataclass(frozen=True, slots=True)
class EngineeringMannSetuPreviewResult:
    classification: str
    authority: str
    verification: str
    extraction_status: str
    extractor_signal: str
    backstop_outcome: str
    backstop_signal: str
    precedence: str
    route: str
    reason_code: str
    policy_state: str
    clinical_meaning_assigned: bool
    mental_health_assessment_performed: bool
    patient_data_processed: bool
    resource_contacts_available: bool
    referral_created: bool
    external_delivery: bool
    notice: str


class EngineeringMannSetuDemoService:
    """Compose reviewed P14 mechanics over fixed nonmedical symbols only."""

    def __init__(self, *, environment: Environment) -> None:
        if type(environment) is not Environment:
            raise TypeError("environment must be an Environment")
        self._environment = environment

    def project(self, *, clock: datetime | None = None) -> EngineeringMannSetuPreviewResult:
        now = (clock or datetime.now(UTC)).astimezone(UTC)
        artifact_time = now - timedelta(seconds=3)
        completed_at = now - timedelta(seconds=1)
        input_artifact = SyntheticArtifactReference(
            artifact_id="syn_mh_input_fixture_alpha",
            artifact_version="engineering.v1",
            content_hash="a" * 64,
            created_at=artifact_time,
        )
        schema_artifact = SyntheticArtifactReference(
            artifact_id="syn_mh_schema_fixture",
            artifact_version="engineering.v1",
            content_hash="b" * 64,
            created_at=artifact_time,
        )
        extraction_request = SyntheticExtractionRequest(
            request_id="syn_mh_request_alpha",
            input_artifact=input_artifact,
            schema_artifact=schema_artifact,
            created_at=now - timedelta(seconds=2),
            deadline_at=now,
        )
        extractor_signal = SyntheticSignalObservation(
            code=SyntheticSignalCode.ALPHA,
            state=SyntheticSignalState.PRESENT,
        )
        extraction = validate_synthetic_result_binding(
            extraction_request,
            SyntheticExtractionResult(
                contract_version=SYNTHETIC_RESULT_CONTRACT_VERSION,
                result_id="syn_mh_result_alpha",
                request_id=extraction_request.request_id,
                input_artifact_id=input_artifact.artifact_id,
                input_artifact_version=input_artifact.artifact_version,
                input_artifact_hash=input_artifact.content_hash,
                schema_artifact_id=schema_artifact.artifact_id,
                schema_artifact_version=schema_artifact.artifact_version,
                schema_artifact_hash=schema_artifact.content_hash,
                status=SyntheticExtractionStatus.SYNTHETIC_PARSED,
                signals=(extractor_signal,),
                completed_at=completed_at,
            ),
        )
        backstop_artifact = SyntheticBackstopArtifact(
            artifact_id="syn_mh_backstop_fixture",
            artifact_version="engineering.v1",
            content_hash="c" * 64,
            created_at=artifact_time,
        )
        backstop_request = SyntheticBackstopRequest(
            request_id="syn_mh_backstop_request_alpha",
            input_artifact=input_artifact,
            backstop_artifact=backstop_artifact,
            evidence_tokens=(SyntheticEvidenceToken.DELTA,),
            created_at=now - timedelta(seconds=2),
            deadline_at=now,
        )
        backstop_signal = SyntheticSignalObservation(
            code=SyntheticSignalCode.DELTA,
            state=SyntheticSignalState.PRESENT,
        )
        backstop = validate_synthetic_backstop_result(
            backstop_request,
            SyntheticBackstopResult(
                result_id="syn_mh_backstop_result_alpha",
                request_id=backstop_request.request_id,
                request_fingerprint=synthetic_backstop_request_fingerprint(backstop_request),
                input_artifact_id=input_artifact.artifact_id,
                input_artifact_version=input_artifact.artifact_version,
                input_artifact_hash=input_artifact.content_hash,
                backstop_artifact_id=backstop_artifact.artifact_id,
                backstop_artifact_version=backstop_artifact.artifact_version,
                backstop_artifact_hash=backstop_artifact.content_hash,
                outcome=SyntheticBackstopOutcome.SYNTHETIC_MATCHED,
                signals=(backstop_signal,),
                completed_at=completed_at,
            ),
        )
        policy = SyntheticPolicyArtifact.create(
            policy_id="syn_mh_policy_fixture",
            policy_version="engineering.v1",
            effective_at=now - timedelta(days=1),
            expires_at=now + timedelta(days=1),
            state=SyntheticPolicyState.TEST_ONLY_ENABLED,
            rules=(
                SyntheticPolicyRule(
                    rule_id="syn_mh_policy_rule_alpha",
                    signal_code=SyntheticSignalCode.ALPHA,
                    signal_state=SyntheticSignalState.PRESENT,
                    kind=SyntheticRuleKind.STANDARD,
                    route=SyntheticRouteState.ALPHA,
                    reason_code=SyntheticPolicyReasonCode.ALPHA,
                ),
                SyntheticPolicyRule(
                    rule_id="syn_mh_policy_rule_delta",
                    signal_code=SyntheticSignalCode.DELTA,
                    signal_state=SyntheticSignalState.PRESENT,
                    kind=SyntheticRuleKind.OVERRIDE,
                    route=SyntheticRouteState.GAMMA,
                    reason_code=SyntheticPolicyReasonCode.DELTA,
                ),
            ),
        )
        decision = SyntheticMentalHealthRouteEngine().evaluate(
            evaluation=SyntheticRouteEvaluation(
                evaluation_id="syn_mh_policy_evaluation_alpha",
                extractor_signals=extraction.signals,
                backstop_signals=backstop.signals,
                evaluated_at=now,
            ),
            policy=policy,
            environment=self._environment,
        )
        return EngineeringMannSetuPreviewResult(
            classification=decision.classification.value,
            authority=decision.authority.value,
            verification=decision.verification.value,
            extraction_status=extraction.status.value,
            extractor_signal=extraction.signals[0].code.value,
            backstop_outcome=backstop.outcome.value,
            backstop_signal=backstop.signals[0].code.value,
            precedence=SyntheticRuleKind.OVERRIDE.value,
            route=decision.route.value,
            reason_code=decision.reason_codes[0].value,
            policy_state=policy.state.value,
            clinical_meaning_assigned=False,
            mental_health_assessment_performed=False,
            patient_data_processed=False,
            resource_contacts_available=False,
            referral_created=False,
            external_delivery=False,
            notice=(
                "Synthetic engineering symbols only. No mental-health assessment is performed, "
                "no clinical meaning is assigned, and no resource, referral, or external delivery "
                "is available."
            ),
        )
