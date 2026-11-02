"""Deterministic, zero-egress P17 engineering demonstration."""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.config.settings import Environment
from app.modules.interoperability.abdm.contracts import (
    ABDMBoundaryCode,
    ABDMBoundaryError,
    ABDMIntegrationMode,
    SyntheticABDMArtifactReference,
    SyntheticABDMIssue,
    SyntheticABDMOperation,
    SyntheticABDMRequest,
    SyntheticABDMResult,
    SyntheticABDMResultState,
    synthetic_abdm_request_fingerprint,
    validate_synthetic_abdm_environment,
    validate_synthetic_abdm_request,
    validate_synthetic_abdm_result,
)

_DEMO_TIME = datetime(2026, 11, 3, 8, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class EngineeringABDMPreviewResult:
    classification: str
    authority: str
    verification: str
    mode: str
    operation: str
    scripted_state: str
    scripted_issue: str
    unknown_state: str
    unknown_issue: str
    zero_egress: bool
    official_protocol_adopted: bool
    abha_identity_processed: bool
    consent_evaluated: bool
    fhir_payload_present: bool
    sandbox_connected: bool
    patient_data_processed: bool
    local_intake_accessed: bool
    local_intake_mutated: bool
    external_transport: bool
    persistence_written: bool
    notice: str


class _DeterministicEngineeringABDMAdapter:
    """Exact local/test adapter with no I/O or official operation semantics."""

    __slots__ = ("_scripted_fingerprint",)

    def __init__(self, *, scripted_fingerprint: str, environment: Environment) -> None:
        validate_synthetic_abdm_environment(
            mode=ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK,
            environment=environment,
        )
        self._scripted_fingerprint = scripted_fingerprint

    def execute(self, request: SyntheticABDMRequest) -> SyntheticABDMResult:
        snapshot = validate_synthetic_abdm_request(request)
        fingerprint = synthetic_abdm_request_fingerprint(snapshot)
        if fingerprint == self._scripted_fingerprint:
            state = SyntheticABDMResultState.SYNTHETIC_REJECTED
            issues = (SyntheticABDMIssue.SYNTHETIC_REJECTED,)
        else:
            state = SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE
            issues = (SyntheticABDMIssue.SYNTHETIC_UNAVAILABLE,)
        result = SyntheticABDMResult(
            request_id=snapshot.request_id,
            operation=snapshot.operation,
            request_fingerprint=fingerprint,
            state=state,
            issues=issues,
            completed_at=_DEMO_TIME,
        )
        return validate_synthetic_abdm_result(request=snapshot, result=result)


class EngineeringABDMDemoService:
    """Compose detached failure outcomes over fixed content-free tokens."""

    def __init__(self, *, environment: Environment) -> None:
        if type(environment) is not Environment:
            raise TypeError("environment must be an Environment")
        self._environment = environment

    def project(self) -> EngineeringABDMPreviewResult:
        if self._environment not in {Environment.LOCAL, Environment.TEST}:
            raise ABDMBoundaryError(ABDMBoundaryCode.PROTECTED_ENVIRONMENT)
        scripted = self._request("alpha")
        unknown = self._request("beta")
        adapter = _DeterministicEngineeringABDMAdapter(
            scripted_fingerprint=synthetic_abdm_request_fingerprint(scripted),
            environment=self._environment,
        )
        rejected = adapter.execute(scripted)
        unavailable = adapter.execute(unknown)
        if (
            rejected.state is not SyntheticABDMResultState.SYNTHETIC_REJECTED
            or rejected.issues != (SyntheticABDMIssue.SYNTHETIC_REJECTED,)
            or unavailable.state is not SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE
            or unavailable.issues != (SyntheticABDMIssue.SYNTHETIC_UNAVAILABLE,)
        ):
            raise RuntimeError("synthetic ABDM composition invariant failed")
        return EngineeringABDMPreviewResult(
            classification="ENGINEERING_SYNTHETIC",
            authority=rejected.authority.value,
            verification=rejected.verification.value,
            mode=scripted.mode.value,
            operation=scripted.operation.value,
            scripted_state=rejected.state.value,
            scripted_issue=rejected.issues[0].value,
            unknown_state=unavailable.state.value,
            unknown_issue=unavailable.issues[0].value,
            zero_egress=True,
            official_protocol_adopted=False,
            abha_identity_processed=False,
            consent_evaluated=False,
            fhir_payload_present=False,
            sandbox_connected=False,
            patient_data_processed=False,
            local_intake_accessed=False,
            local_intake_mutated=False,
            external_transport=False,
            persistence_written=False,
            notice=(
                "Synthetic offline engineering tokens only. No official ABDM protocol or ABHA "
                "identity is used, no consent or FHIR payload is processed, and no sandbox, "
                "patient data, local intake, network transport, or persistence is accessed."
            ),
        )

    @staticmethod
    def _request(suffix: str) -> SyntheticABDMRequest:
        return SyntheticABDMRequest(
            request_id=f"syn_abdm_request_{suffix}",
            mode=ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK,
            operation=SyntheticABDMOperation.ALPHA,
            artifact=SyntheticABDMArtifactReference(
                artifact_id=f"syn_abdm_artifact_{suffix}",
                artifact_version="engineering.v1",
                content_hash=("a" if suffix == "alpha" else "b") * 64,
            ),
            idempotency_key=("c" if suffix == "alpha" else "d") * 64,
            created_at=_DEMO_TIME,
        )
