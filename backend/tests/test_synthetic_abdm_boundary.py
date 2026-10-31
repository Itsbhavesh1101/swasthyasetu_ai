from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

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

NOW = datetime(2026, 11, 1, 17, 0, tzinfo=UTC)


def request() -> SyntheticABDMRequest:
    return SyntheticABDMRequest(
        request_id="syn_abdm_request_alpha",
        mode=ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK,
        operation=SyntheticABDMOperation.ALPHA,
        artifact=SyntheticABDMArtifactReference(
            artifact_id="syn_abdm_artifact_alpha",
            artifact_version="engineering.v1",
            content_hash="a" * 64,
        ),
        idempotency_key="b" * 64,
        created_at=NOW,
    )


def result_for(value: SyntheticABDMRequest) -> SyntheticABDMResult:
    return SyntheticABDMResult(
        request_id=value.request_id,
        operation=value.operation,
        request_fingerprint=synthetic_abdm_request_fingerprint(value),
        state=SyntheticABDMResultState.SYNTHETIC_ACCEPTED,
        issues=(),
        completed_at=NOW + timedelta(seconds=1),
    )


def test_request_is_opaque_immutable_and_content_free() -> None:
    value = request()
    assert validate_synthetic_abdm_request(value) == value
    with pytest.raises(FrozenInstanceError):
        value.request_id = "syn_abdm_request_beta"  # type: ignore[misc]
    for forbidden in (
        "abha_number",
        "health_id",
        "patient",
        "consent_artifact",
        "endpoint",
        "credential",
        "payload",
        "callback",
    ):
        assert not hasattr(value, forbidden)


def test_request_normalizes_aware_clock_and_rejects_naive_clock() -> None:
    aware = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))
    assert replace(request(), created_at=aware).created_at == NOW
    with pytest.raises(ABDMBoundaryError) as caught:
        replace(request(), created_at=datetime(2026, 11, 1, 17, 0))
    assert caught.value.code is ABDMBoundaryCode.INVALID_TYPE


def test_disabled_mode_cannot_be_used_as_an_operation_request() -> None:
    with pytest.raises(ABDMBoundaryError) as caught:
        replace(request(), mode=ABDMIntegrationMode.DISABLED)
    assert caught.value.code is ABDMBoundaryCode.INVALID_VALUE


@pytest.mark.parametrize("environment", [Environment.LOCAL, Environment.TEST])
def test_offline_mock_mode_is_limited_to_local_and_test(environment: Environment) -> None:
    validate_synthetic_abdm_environment(
        mode=ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK,
        environment=environment,
    )


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_offline_mock_mode_is_denied_in_protected_environments(
    environment: Environment,
) -> None:
    with pytest.raises(ABDMBoundaryError) as caught:
        validate_synthetic_abdm_environment(
            mode=ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK,
            environment=environment,
        )
    assert caught.value.code is ABDMBoundaryCode.PROTECTED_ENVIRONMENT


@pytest.mark.parametrize("environment", list(Environment))
def test_disabled_mode_is_safe_in_every_environment(environment: Environment) -> None:
    validate_synthetic_abdm_environment(
        mode=ABDMIntegrationMode.DISABLED,
        environment=environment,
    )


def test_result_is_bound_to_exact_request_and_chronology() -> None:
    value = request()
    result = result_for(value)
    assert validate_synthetic_abdm_result(request=value, result=result) == result

    with pytest.raises(ABDMBoundaryError) as drift:
        validate_synthetic_abdm_result(
            request=replace(value, idempotency_key="c" * 64),
            result=result,
        )
    assert drift.value.code is ABDMBoundaryCode.IDENTITY_MISMATCH

    with pytest.raises(ABDMBoundaryError) as chronology:
        validate_synthetic_abdm_result(
            request=value,
            result=replace(result, completed_at=NOW - timedelta(seconds=1)),
        )
    assert chronology.value.code is ABDMBoundaryCode.IDENTITY_MISMATCH


@pytest.mark.parametrize(
    ("state", "issues"),
    [
        (
            SyntheticABDMResultState.SYNTHETIC_ACCEPTED,
            (SyntheticABDMIssue.SYNTHETIC_REJECTED,),
        ),
        (SyntheticABDMResultState.SYNTHETIC_REJECTED, ()),
        (SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE, ()),
    ],
)
def test_result_rejects_inconsistent_issue_shape(
    state: SyntheticABDMResultState,
    issues: tuple[SyntheticABDMIssue, ...],
) -> None:
    with pytest.raises(ABDMBoundaryError) as caught:
        replace(result_for(request()), state=state, issues=issues)
    assert caught.value.code is ABDMBoundaryCode.INVALID_VALUE


@pytest.mark.parametrize(
    ("state", "issue"),
    [
        (
            SyntheticABDMResultState.SYNTHETIC_REJECTED,
            SyntheticABDMIssue.SYNTHETIC_UNAVAILABLE,
        ),
        (
            SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE,
            SyntheticABDMIssue.SYNTHETIC_REJECTED,
        ),
    ],
)
def test_result_requires_the_issue_matching_its_non_success_state(
    state: SyntheticABDMResultState,
    issue: SyntheticABDMIssue,
) -> None:
    with pytest.raises(ABDMBoundaryError) as caught:
        replace(result_for(request()), state=state, issues=(issue,))
    assert caught.value.code is ABDMBoundaryCode.INVALID_VALUE


def test_result_revalidation_rejects_forced_identity_mutation() -> None:
    value = request()
    result = result_for(value)
    object.__setattr__(result, "request_id", "syn_abdm_request_beta")
    with pytest.raises(ABDMBoundaryError) as caught:
        validate_synthetic_abdm_result(request=value, result=result)
    assert caught.value.code is ABDMBoundaryCode.IDENTITY_MISMATCH


def test_forced_nested_mutation_fails_revalidation_without_value_leak() -> None:
    value = request()
    object.__setattr__(value.artifact, "artifact_id", "private-canary")
    with pytest.raises(ABDMBoundaryError) as caught:
        validate_synthetic_abdm_request(value)
    assert caught.value.code is ABDMBoundaryCode.INVALID_VALUE
    assert "private-canary" not in str(caught.value)


def test_plain_strings_cannot_impersonate_closed_modes_or_operations() -> None:
    with pytest.raises(ABDMBoundaryError) as mode:
        replace(request(), mode="SYNTHETIC_OFFLINE_MOCK")  # type: ignore[arg-type]
    assert mode.value.code is ABDMBoundaryCode.INVALID_TYPE
    with pytest.raises(ABDMBoundaryError) as operation:
        replace(request(), operation="SYNTHETIC_OPERATION_ALPHA")  # type: ignore[arg-type]
    assert operation.value.code is ABDMBoundaryCode.INVALID_TYPE
