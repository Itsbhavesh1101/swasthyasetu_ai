from datetime import UTC, datetime

import pytest
from mental_health_support.adversarial_harness import run_synthetic_adversarial_case

from app.config.settings import Environment
from app.modules.mental_health.backstop import SyntheticEvidenceToken
from app.modules.mental_health.contracts import (
    MentalHealthContractCode,
    MentalHealthContractError,
    SyntheticSignalCode,
    SyntheticSignalObservation,
    SyntheticSignalState,
    parse_synthetic_extraction_result,
)
from app.modules.mental_health.policy import (
    SyntheticMentalHealthRouteEngine,
    SyntheticPolicyCode,
    SyntheticPolicyError,
    SyntheticPolicyReasonCode,
    SyntheticRouteState,
)

NOW = datetime(2026, 10, 31, 18, 0, tzinfo=UTC)
HASH = "a" * 64


def observation(
    code: SyntheticSignalCode,
    state: SyntheticSignalState = SyntheticSignalState.PRESENT,
) -> SyntheticSignalObservation:
    return SyntheticSignalObservation(code=code, state=state)


@pytest.mark.parametrize(
    ("extractor", "backstop", "policy_present", "route", "reason"),
    [
        (
            (observation(SyntheticSignalCode.ALPHA),),
            (SyntheticEvidenceToken.ALPHA,),
            True,
            SyntheticRouteState.ALPHA,
            SyntheticPolicyReasonCode.ALPHA,
        ),
        (
            (observation(SyntheticSignalCode.ALPHA),),
            (SyntheticEvidenceToken.DELTA,),
            True,
            SyntheticRouteState.GAMMA,
            SyntheticPolicyReasonCode.DELTA,
        ),
        (
            (observation(SyntheticSignalCode.GAMMA, SyntheticSignalState.UNCERTAIN),),
            (),
            True,
            SyntheticRouteState.CLARIFICATION_REQUIRED,
            SyntheticPolicyReasonCode.GAMMA,
        ),
        (
            (),
            (),
            True,
            SyntheticRouteState.DEGRADED_SAFE_FALLBACK,
            SyntheticPolicyReasonCode.NO_MATCH,
        ),
        (
            (observation(SyntheticSignalCode.ALPHA),),
            (),
            False,
            SyntheticRouteState.DEGRADED_SAFE_FALLBACK,
            SyntheticPolicyReasonCode.POLICY_UNAVAILABLE,
        ),
    ],
)
async def test_offline_matrix_is_deterministic_and_fail_closed(
    extractor: tuple[SyntheticSignalObservation, ...],
    backstop: tuple[SyntheticEvidenceToken, ...],
    policy_present: bool,
    route: SyntheticRouteState,
    reason: SyntheticPolicyReasonCode,
) -> None:
    decision = await run_synthetic_adversarial_case(
        extractor_signals=extractor,
        backstop_tokens=backstop,
        policy_present=policy_present,
        evaluated_at=NOW,
    )

    assert decision.route is route
    assert decision.reason_codes == (reason,)
    assert not hasattr(decision, "patient_message")
    assert not hasattr(decision, "diagnosis")


async def test_extractor_backstop_disagreement_degrades_without_downgrade() -> None:
    decision = await run_synthetic_adversarial_case(
        extractor_signals=(observation(SyntheticSignalCode.ALPHA),),
        backstop_tokens=(SyntheticEvidenceToken.ALPHA,),
        backstop_state=SyntheticSignalState.CONTRADICTORY,
        policy_present=True,
        evaluated_at=NOW,
    )

    assert decision.route is SyntheticRouteState.DEGRADED_SAFE_FALLBACK
    assert decision.reason_codes == (SyntheticPolicyReasonCode.EVIDENCE_CONFLICT,)


@pytest.mark.parametrize("forbidden", ["route", "patient_text", "score", "prompt"])
def test_untrusted_extraction_cannot_add_authority_or_prose(forbidden: str) -> None:
    payload: dict[str, object] = {
        "contract_version": "synthetic-mental-health-signals.v1",
        "result_id": "syn_mh_result_alpha",
        "request_id": "syn_mh_request_alpha",
        "input_artifact_id": "syn_mh_input_fixture_alpha",
        "input_artifact_version": "engineering.v1",
        "input_artifact_hash": HASH,
        "schema_artifact_id": "syn_mh_schema_fixture",
        "schema_artifact_version": "engineering.v1",
        "schema_artifact_hash": HASH,
        "status": "SYNTHETIC_PARSED",
        "signals": [{"code": "SYN_MH_SIGNAL_ALPHA", "state": "PRESENT"}],
        "completed_at": "2026-10-31T18:00:00Z",
        forbidden: "private-canary",
    }

    with pytest.raises(MentalHealthContractError) as caught:
        parse_synthetic_extraction_result(payload)

    assert caught.value.code is MentalHealthContractCode.UNKNOWN_FIELD
    assert "private-canary" not in str(caught.value)


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environment_denies_before_hostile_inputs_are_read(
    environment: Environment,
) -> None:
    class Hostile:
        def __getattribute__(self, name: str) -> object:
            raise AssertionError(f"input-read:{name}")

    with pytest.raises(SyntheticPolicyError) as caught:
        SyntheticMentalHealthRouteEngine().evaluate(
            evaluation=Hostile(),  # type: ignore[arg-type]
            policy=Hostile(),  # type: ignore[arg-type]
            environment=environment,
        )

    assert caught.value.code is SyntheticPolicyCode.PROTECTED_ENVIRONMENT
