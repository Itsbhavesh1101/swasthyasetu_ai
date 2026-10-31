"""Offline composition helper for P14 engineering-only adversarial tests."""

from datetime import datetime, timedelta

from app.config.settings import Environment
from app.modules.mental_health.backstop import (
    SyntheticBackstopArtifact,
    SyntheticBackstopRequest,
    SyntheticBackstopResult,
    SyntheticEvidenceToken,
)
from app.modules.mental_health.contracts import (
    SyntheticArtifactReference,
    SyntheticSignalObservation,
    SyntheticSignalState,
)
from app.modules.mental_health.policy import (
    SyntheticMentalHealthRouteEngine,
    SyntheticRouteDecision,
    SyntheticRouteEvaluation,
)
from mental_health_support.mock_backstop import DeterministicSyntheticBackstop
from mental_health_support.policy_fixture import synthetic_policy_fixture

_INPUT_HASH = "a" * 64
_BACKSTOP_HASH = "b" * 64


async def run_synthetic_adversarial_case(
    *,
    extractor_signals: tuple[SyntheticSignalObservation, ...],
    backstop_tokens: tuple[SyntheticEvidenceToken, ...],
    policy_present: bool,
    evaluated_at: datetime,
    backstop_state: SyntheticSignalState = SyntheticSignalState.PRESENT,
) -> SyntheticRouteDecision:
    """Compose existing toy boundaries without introducing a runtime workflow."""

    artifact_time = evaluated_at - timedelta(seconds=3)
    input_artifact = SyntheticArtifactReference(
        artifact_id="syn_mh_input_fixture_alpha",
        artifact_version="engineering.v1",
        content_hash=_INPUT_HASH,
        created_at=artifact_time,
    )
    request = SyntheticBackstopRequest(
        request_id="syn_mh_backstop_request_alpha",
        input_artifact=input_artifact,
        backstop_artifact=SyntheticBackstopArtifact(
            artifact_id="syn_mh_backstop_fixture",
            artifact_version="engineering.v1",
            content_hash=_BACKSTOP_HASH,
            created_at=artifact_time,
        ),
        evidence_tokens=backstop_tokens,
        created_at=evaluated_at - timedelta(seconds=2),
        deadline_at=evaluated_at,
    )
    response = await DeterministicSyntheticBackstop(
        clock=lambda: evaluated_at - timedelta(seconds=1)
    ).evaluate(request)
    if type(response) is not SyntheticBackstopResult:
        raise AssertionError("adversarial harness requires a synthetic result")
    backstop_signals = tuple(
        SyntheticSignalObservation(code=item.code, state=backstop_state)
        for item in response.signals
    )
    evaluation = SyntheticRouteEvaluation(
        evaluation_id="syn_mh_policy_evaluation_alpha",
        extractor_signals=extractor_signals,
        backstop_signals=backstop_signals,
        evaluated_at=evaluated_at,
    )
    policy = (
        synthetic_policy_fixture(
            effective_at=evaluated_at - timedelta(days=1),
            expires_at=evaluated_at + timedelta(days=1),
        )
        if policy_present
        else None
    )
    return SyntheticMentalHealthRouteEngine().evaluate(
        evaluation=evaluation,
        policy=policy,
        environment=Environment.TEST,
    )


__all__ = ["run_synthetic_adversarial_case"]
