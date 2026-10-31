from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest
from mental_health_support.mock_backstop import (
    DeterministicSyntheticBackstop,
    SyntheticBackstopMode,
)

from app.modules.mental_health.backstop import (
    BackstopContractCode,
    BackstopContractError,
    SyntheticBackstopArtifact,
    SyntheticBackstopFailure,
    SyntheticBackstopFailureCode,
    SyntheticBackstopOutcome,
    SyntheticBackstopRequest,
    SyntheticBackstopResult,
    SyntheticEvidenceToken,
    validate_synthetic_backstop_result,
)
from app.modules.mental_health.contracts import (
    SyntheticArtifactReference,
    SyntheticSignalCode,
    SyntheticSignalState,
)
from app.modules.mental_health.ports import SyntheticSafetyBackstopPort

NOW = datetime(2026, 10, 31, 16, 0, tzinfo=UTC)
INPUT_HASH = "a" * 64
BACKSTOP_HASH = "c" * 64


def input_artifact() -> SyntheticArtifactReference:
    return SyntheticArtifactReference(
        artifact_id="syn_mh_input_fixture_alpha",
        artifact_version="engineering.v1",
        content_hash=INPUT_HASH,
        created_at=NOW,
    )


def backstop_artifact() -> SyntheticBackstopArtifact:
    return SyntheticBackstopArtifact(
        artifact_id="syn_mh_backstop_fixture",
        artifact_version="engineering.v1",
        content_hash=BACKSTOP_HASH,
        created_at=NOW,
    )


def request(
    *tokens: SyntheticEvidenceToken,
    deadline_at: datetime = NOW + timedelta(seconds=10),
) -> SyntheticBackstopRequest:
    return SyntheticBackstopRequest(
        request_id="syn_mh_backstop_request_alpha",
        input_artifact=input_artifact(),
        backstop_artifact=backstop_artifact(),
        evidence_tokens=tokens,
        created_at=NOW + timedelta(seconds=1),
        deadline_at=deadline_at,
    )


@pytest.mark.asyncio
async def test_test_only_backstop_maps_toy_tokens_without_route_authority() -> None:
    adapter = DeterministicSyntheticBackstop(clock=lambda: NOW + timedelta(seconds=2))

    result = await adapter.evaluate(
        request(SyntheticEvidenceToken.ALPHA, SyntheticEvidenceToken.GAMMA)
    )

    assert type(result) is SyntheticBackstopResult
    assert result.outcome is SyntheticBackstopOutcome.SYNTHETIC_MATCHED
    assert tuple(item.code for item in result.signals) == (
        SyntheticSignalCode.ALPHA,
        SyntheticSignalCode.GAMMA,
    )
    assert all(item.state is SyntheticSignalState.PRESENT for item in result.signals)
    assert not hasattr(result, "route")
    assert not hasattr(result, "risk")
    with pytest.raises(FrozenInstanceError):
        result.outcome = SyntheticBackstopOutcome.SYNTHETIC_NO_MATCH  # type: ignore[misc]


@pytest.mark.asyncio
async def test_empty_toy_evidence_returns_no_match_without_a_signal() -> None:
    result = await DeterministicSyntheticBackstop(
        clock=lambda: NOW + timedelta(seconds=2)
    ).evaluate(request())

    assert type(result) is SyntheticBackstopResult
    assert result.outcome is SyntheticBackstopOutcome.SYNTHETIC_NO_MATCH
    assert result.signals == ()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("mode", "code"),
    [
        (SyntheticBackstopMode.TIMEOUT, SyntheticBackstopFailureCode.SIMULATED_TIMEOUT),
        (SyntheticBackstopMode.UNAVAILABLE, SyntheticBackstopFailureCode.SIMULATED_UNAVAILABLE),
        (SyntheticBackstopMode.CANCELLED, SyntheticBackstopFailureCode.SIMULATED_CANCELLED),
    ],
)
async def test_failures_are_content_free_and_never_fabricate_signals(
    mode: SyntheticBackstopMode,
    code: SyntheticBackstopFailureCode,
) -> None:
    observed = (
        NOW + timedelta(seconds=10)
        if mode is SyntheticBackstopMode.TIMEOUT
        else NOW + timedelta(seconds=2)
    )
    failure = await DeterministicSyntheticBackstop(mode=mode, clock=lambda: observed).evaluate(
        request(SyntheticEvidenceToken.ALPHA)
    )

    assert type(failure) is SyntheticBackstopFailure
    assert failure.code is code
    assert not hasattr(failure, "message")
    assert not hasattr(failure, "signals")
    assert not hasattr(failure, "route")


@pytest.mark.asyncio
async def test_deadline_is_checked_before_any_toy_evidence_evaluation() -> None:
    request_value = request(SyntheticEvidenceToken.ALPHA)
    adapter = DeterministicSyntheticBackstop(clock=lambda: request_value.deadline_at)

    outcome = await adapter.evaluate(request_value)

    assert type(outcome) is SyntheticBackstopFailure
    assert outcome.code is SyntheticBackstopFailureCode.SIMULATED_TIMEOUT


def test_request_requires_sorted_unique_closed_toy_tokens() -> None:
    with pytest.raises(BackstopContractError) as duplicate:
        request(SyntheticEvidenceToken.ALPHA, SyntheticEvidenceToken.ALPHA)
    assert duplicate.value.code is BackstopContractCode.DUPLICATE_TOKEN

    with pytest.raises(BackstopContractError) as unordered:
        request(SyntheticEvidenceToken.GAMMA, SyntheticEvidenceToken.ALPHA)
    assert unordered.value.code is BackstopContractCode.INVALID_VALUE

    with pytest.raises(BackstopContractError):
        replace(request(), evidence_tokens=cast(Any, ("SYN_MH_EVIDENCE_ALPHA",)))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_id", "syn_mh_backstop_clinical"),
        ("artifact_version", "production.v1"),
        ("content_hash", "not-a-hash"),
        ("created_at", datetime(2026, 10, 31, 16, 0)),
    ],
)
def test_backstop_artifact_rejects_nonfixture_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "artifact_id": "syn_mh_backstop_fixture",
        "artifact_version": "engineering.v1",
        "content_hash": BACKSTOP_HASH,
        "created_at": NOW,
    }
    values[field] = value
    with pytest.raises(BackstopContractError):
        SyntheticBackstopArtifact(**cast(Any, values))


def test_aware_non_utc_clocks_normalize_and_naive_clocks_fail() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    normalized = replace(
        request(),
        created_at=(NOW + timedelta(seconds=1)).astimezone(offset),
        deadline_at=(NOW + timedelta(seconds=10)).astimezone(offset),
    )
    assert normalized.created_at.tzinfo is UTC
    assert normalized.deadline_at.tzinfo is UTC

    with pytest.raises(BackstopContractError):
        replace(request(), created_at=datetime(2026, 10, 31, 16, 0, 1))


@pytest.mark.asyncio
async def test_result_binding_rejects_cross_request_artifact_and_chronology() -> None:
    request_value = request(SyntheticEvidenceToken.ALPHA)
    result = await DeterministicSyntheticBackstop(
        clock=lambda: NOW + timedelta(seconds=2)
    ).evaluate(request_value)
    assert type(result) is SyntheticBackstopResult
    assert validate_synthetic_backstop_result(request_value, result) == result

    for hostile in (
        replace(result, request_id="syn_mh_backstop_request_beta"),
        replace(result, input_artifact_hash="d" * 64),
        replace(result, backstop_artifact_version="engineering.v2"),
    ):
        with pytest.raises(BackstopContractError) as raised:
            validate_synthetic_backstop_result(request_value, hostile)
        assert raised.value.code is BackstopContractCode.IDENTITY_MISMATCH

    with pytest.raises(BackstopContractError) as late:
        validate_synthetic_backstop_result(
            request_value,
            replace(result, completed_at=request_value.deadline_at + timedelta(microseconds=1)),
        )
    assert late.value.code is BackstopContractCode.INVALID_CHRONOLOGY


@pytest.mark.asyncio
async def test_responses_reject_same_id_requests_with_different_evidence_or_deadline() -> None:
    original = request(SyntheticEvidenceToken.ALPHA)
    result = await DeterministicSyntheticBackstop(
        clock=lambda: NOW + timedelta(seconds=2)
    ).evaluate(original)
    assert type(result) is SyntheticBackstopResult
    failure = await DeterministicSyntheticBackstop(
        mode=SyntheticBackstopMode.UNAVAILABLE,
        clock=lambda: NOW + timedelta(seconds=2),
    ).evaluate(original)
    assert type(failure) is SyntheticBackstopFailure

    changed_evidence = request(SyntheticEvidenceToken.BETA)
    changed_deadline = request(
        SyntheticEvidenceToken.ALPHA,
        deadline_at=NOW + timedelta(seconds=20),
    )
    for changed in (changed_evidence, changed_deadline):
        with pytest.raises(BackstopContractError) as result_error:
            validate_synthetic_backstop_result(changed, result)
        assert result_error.value.code is BackstopContractCode.IDENTITY_MISMATCH
        with pytest.raises(BackstopContractError) as failure_error:
            failure.validate_for(changed)
        assert failure_error.value.code is BackstopContractCode.IDENTITY_MISMATCH


@pytest.mark.asyncio
async def test_forced_nested_mutation_is_revalidated() -> None:
    request_value = request(SyntheticEvidenceToken.ALPHA)
    result = await DeterministicSyntheticBackstop(
        clock=lambda: NOW + timedelta(seconds=2)
    ).evaluate(request_value)
    assert type(result) is SyntheticBackstopResult
    hostile = result.signals[0]
    object.__setattr__(hostile, "code", "SYN_MH_SIGNAL_CRISIS")
    object.__setattr__(result, "signals", (hostile,))

    with pytest.raises(BackstopContractError):
        validate_synthetic_backstop_result(request_value, result)


@pytest.mark.asyncio
async def test_mock_revalidates_request_before_reading_toy_evidence() -> None:
    hostile = request(SyntheticEvidenceToken.ALPHA)
    object.__setattr__(hostile, "evidence_tokens", ("SYN_MH_EVIDENCE_ALPHA",))

    with pytest.raises(BackstopContractError):
        await DeterministicSyntheticBackstop(clock=lambda: NOW + timedelta(seconds=2)).evaluate(
            hostile
        )


def test_request_has_no_text_patient_language_policy_or_route_fields() -> None:
    values = {
        "request_id": "syn_mh_backstop_request_alpha",
        "input_artifact": input_artifact(),
        "backstop_artifact": backstop_artifact(),
        "evidence_tokens": (),
        "created_at": NOW + timedelta(seconds=1),
        "deadline_at": NOW + timedelta(seconds=10),
    }
    for forbidden in (
        "text",
        "message",
        "patient_id",
        "session_id",
        "language",
        "locale",
        "lexicon",
        "patterns",
        "policy",
        "route",
        "score",
        "confidence",
    ):
        with pytest.raises(TypeError):
            cast(Any, SyntheticBackstopRequest)(**values, **{forbidden: "canary"})


def test_backstop_port_is_independent_and_mock_is_test_only() -> None:
    import app.modules.mental_health.backstop as backstop_module

    assert isinstance(DeterministicSyntheticBackstop(), SyntheticSafetyBackstopPort)
    for forbidden in (
        "DefaultBackstop",
        "ProductionBackstop",
        "DEFAULT_LEXICON",
        "ROUTE_A",
        "ROUTE_B",
        "ROUTE_C",
    ):
        assert not hasattr(backstop_module, forbidden)

    production_root = Path(__file__).parents[1] / "app" / "modules" / "mental_health"
    production_source = "\n".join(
        path.read_text(encoding="utf-8") for path in production_root.glob("*.py")
    )
    assert "DeterministicSyntheticBackstop" not in production_source
    assert "mental_health_support" not in production_source
