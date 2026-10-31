from collections.abc import Iterator, Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone

import pytest
from abdm_support.mock_adapter import (
    DeterministicMockABDMAdapter,
    MockABDMCode,
    MockABDMError,
    MockABDMScenario,
)

from app.config.settings import Environment
from app.modules.interoperability.abdm.contracts import (
    ABDMAdapterPort,
    ABDMBoundaryCode,
    ABDMBoundaryError,
    ABDMIntegrationMode,
    SyntheticABDMArtifactReference,
    SyntheticABDMIssue,
    SyntheticABDMOperation,
    SyntheticABDMRequest,
    SyntheticABDMResultState,
    synthetic_abdm_request_fingerprint,
    validate_synthetic_abdm_result,
)

NOW = datetime(2026, 11, 1, 18, 0, tzinfo=UTC)


def request(suffix: str = "alpha") -> SyntheticABDMRequest:
    operation = SyntheticABDMOperation.ALPHA if suffix == "alpha" else SyntheticABDMOperation.BETA
    return SyntheticABDMRequest(
        request_id=f"syn_abdm_request_{suffix}",
        mode=ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK,
        operation=operation,
        artifact=SyntheticABDMArtifactReference(
            artifact_id=f"syn_abdm_artifact_{suffix}",
            artifact_version="engineering.v1",
            content_hash=("a" if suffix == "alpha" else "b") * 64,
        ),
        idempotency_key=("c" if suffix == "alpha" else "d") * 64,
        created_at=NOW,
    )


def adapter(
    value: SyntheticABDMRequest,
    scenario: MockABDMScenario,
    *,
    clock: object = None,
) -> DeterministicMockABDMAdapter:
    selected_clock = clock if clock is not None else lambda: NOW + timedelta(seconds=1)
    return DeterministicMockABDMAdapter(
        fixtures={synthetic_abdm_request_fingerprint(value): scenario},
        environment=Environment.TEST,
        clock=selected_clock,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    ("scenario", "state", "issues"),
    [
        (MockABDMScenario.ACCEPTED, SyntheticABDMResultState.SYNTHETIC_ACCEPTED, ()),
        (
            MockABDMScenario.REJECTED,
            SyntheticABDMResultState.SYNTHETIC_REJECTED,
            (SyntheticABDMIssue.SYNTHETIC_REJECTED,),
        ),
        (
            MockABDMScenario.UNAVAILABLE,
            SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE,
            (SyntheticABDMIssue.SYNTHETIC_UNAVAILABLE,),
        ),
    ],
)
def test_scripted_scenarios_return_exact_content_free_results(
    scenario: MockABDMScenario,
    state: SyntheticABDMResultState,
    issues: tuple[SyntheticABDMIssue, ...],
) -> None:
    value = request()
    mock = adapter(value, scenario)

    result = mock.execute(value)

    assert isinstance(mock, ABDMAdapterPort)
    assert result.state is state
    assert result.issues == issues
    assert result.request_id == "syn_abdm_request_alpha"
    assert result.operation is SyntheticABDMOperation.ALPHA
    assert result.completed_at == NOW + timedelta(seconds=1)
    assert validate_synthetic_abdm_result(request=value, result=result) == result
    for forbidden in ("payload", "endpoint", "credential", "callback", "patient", "abha"):
        assert not hasattr(result, forbidden)


def test_unknown_request_fails_closed_as_unavailable() -> None:
    known = request("alpha")
    unknown = request("beta")

    result = adapter(known, MockABDMScenario.ACCEPTED).execute(unknown)

    assert result.state is SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE
    assert result.issues == (SyntheticABDMIssue.SYNTHETIC_UNAVAILABLE,)
    assert validate_synthetic_abdm_result(request=unknown, result=result) == result


def test_fixture_mapping_is_snapshotted_and_replay_is_deterministic() -> None:
    value = request()
    fingerprint = synthetic_abdm_request_fingerprint(value)
    fixtures = {fingerprint: MockABDMScenario.ACCEPTED}
    mock = DeterministicMockABDMAdapter(
        fixtures=fixtures,
        environment=Environment.LOCAL,
        clock=lambda: NOW + timedelta(seconds=1),
    )
    fixtures[fingerprint] = MockABDMScenario.REJECTED

    first = mock.execute(value)
    second = mock.execute(value)

    assert first == second
    assert first.state is SyntheticABDMResultState.SYNTHETIC_ACCEPTED


class HostileMapping(Mapping[str, MockABDMScenario]):
    def __getitem__(self, key: str) -> MockABDMScenario:
        raise AssertionError(f"fixture-read:{key}")

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("fixture-iterated")

    def __len__(self) -> int:
        raise AssertionError("fixture-sized")


class DuplicateFingerprintMapping(Mapping[str, MockABDMScenario]):
    def __init__(self, fingerprint: str) -> None:
        self._fingerprint = fingerprint

    def __getitem__(self, key: str) -> MockABDMScenario:
        return MockABDMScenario.ACCEPTED

    def __iter__(self) -> Iterator[str]:
        yield self._fingerprint
        yield self._fingerprint

    def __len__(self) -> int:
        return 2


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_protected_environment_is_denied_before_fixture_or_clock_access(
    environment: Environment,
) -> None:
    def hostile_clock() -> datetime:
        raise AssertionError("clock-read")

    with pytest.raises(ABDMBoundaryError) as caught:
        DeterministicMockABDMAdapter(
            fixtures=HostileMapping(),
            environment=environment,
            clock=hostile_clock,
        )
    assert caught.value.code is ABDMBoundaryCode.PROTECTED_ENVIRONMENT


@pytest.mark.parametrize(
    "fixtures",
    [
        {"not-a-fingerprint": MockABDMScenario.ACCEPTED},
        {"a" * 64: "ACCEPTED"},
        {1: MockABDMScenario.ACCEPTED},
    ],
)
def test_malformed_fixture_entries_fail_with_content_free_error(
    fixtures: object,
) -> None:
    with pytest.raises(MockABDMError) as caught:
        DeterministicMockABDMAdapter(
            fixtures=fixtures,  # type: ignore[arg-type]
            environment=Environment.TEST,
            clock=lambda: NOW,
        )
    assert caught.value.code is MockABDMCode.INVALID_FIXTURE
    assert str(caught.value) == "INVALID_FIXTURE"


def test_duplicate_fingerprint_entries_are_rejected_as_ambiguous() -> None:
    fingerprint = synthetic_abdm_request_fingerprint(request())
    with pytest.raises(MockABDMError) as caught:
        DeterministicMockABDMAdapter(
            fixtures=DuplicateFingerprintMapping(fingerprint),
            environment=Environment.TEST,
            clock=lambda: NOW,
        )
    assert caught.value.code is MockABDMCode.INVALID_FIXTURE


def test_mutated_request_is_rejected_before_fixture_or_clock_access() -> None:
    value = request()

    def hostile_clock() -> datetime:
        raise AssertionError("clock-read")

    mock = adapter(value, MockABDMScenario.ACCEPTED, clock=hostile_clock)
    object.__setattr__(value.artifact, "artifact_id", "private-canary")

    with pytest.raises(ABDMBoundaryError) as caught:
        mock.execute(value)
    assert caught.value.code is ABDMBoundaryCode.INVALID_VALUE
    assert "private-canary" not in str(caught.value)


def test_aware_clock_is_normalized_to_utc_and_naive_clock_is_rejected() -> None:
    value = request()
    indian_time = (NOW + timedelta(seconds=1)).astimezone(timezone(timedelta(hours=5, minutes=30)))
    result = adapter(value, MockABDMScenario.ACCEPTED, clock=lambda: indian_time).execute(value)
    assert result.completed_at == NOW + timedelta(seconds=1)
    assert result.completed_at.tzinfo is UTC

    with pytest.raises(ABDMBoundaryError) as caught:
        adapter(
            value,
            MockABDMScenario.ACCEPTED,
            clock=lambda: datetime(2026, 11, 1, 18, 0, 1),
        ).execute(value)
    assert caught.value.code is ABDMBoundaryCode.INVALID_TYPE


def test_clock_failure_is_wrapped_without_leaking_provider_text() -> None:
    value = request()

    def broken_clock() -> datetime:
        raise RuntimeError("private-clock-canary")

    with pytest.raises(MockABDMError) as caught:
        adapter(value, MockABDMScenario.ACCEPTED, clock=broken_clock).execute(value)
    assert caught.value.code is MockABDMCode.CLOCK_FAILURE
    assert "private-clock-canary" not in str(caught.value)


def test_noncallable_clock_is_rejected_at_construction() -> None:
    with pytest.raises(MockABDMError) as caught:
        DeterministicMockABDMAdapter(
            fixtures={},
            environment=Environment.TEST,
            clock=object(),  # type: ignore[arg-type]
        )
    assert caught.value.code is MockABDMCode.INVALID_CLOCK


def test_request_fingerprint_drift_does_not_reuse_an_accepted_fixture() -> None:
    value = request()
    mock = adapter(value, MockABDMScenario.ACCEPTED)
    drifted = replace(value, idempotency_key="e" * 64)

    result = mock.execute(drifted)

    assert result.state is SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE
    assert result.issues == (SyntheticABDMIssue.SYNTHETIC_UNAVAILABLE,)
