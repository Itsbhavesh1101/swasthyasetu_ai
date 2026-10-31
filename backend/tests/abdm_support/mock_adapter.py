"""Deterministic zero-egress test adapter for the opaque ABDM boundary."""

from collections.abc import Callable, Mapping
from datetime import datetime
from enum import StrEnum
from re import Pattern, compile
from types import MappingProxyType

from app.config.settings import Environment
from app.modules.interoperability.abdm.contracts import (
    ABDMIntegrationMode,
    SyntheticABDMIssue,
    SyntheticABDMRequest,
    SyntheticABDMResult,
    SyntheticABDMResultState,
    synthetic_abdm_request_fingerprint,
    validate_synthetic_abdm_environment,
    validate_synthetic_abdm_request,
    validate_synthetic_abdm_result,
)

_SHA256: Pattern[str] = compile(r"^[a-f0-9]{64}$")


class MockABDMScenario(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    UNAVAILABLE = "UNAVAILABLE"


class MockABDMCode(StrEnum):
    INVALID_FIXTURE = "INVALID_FIXTURE"
    INVALID_CLOCK = "INVALID_CLOCK"
    CLOCK_FAILURE = "CLOCK_FAILURE"


class MockABDMError(RuntimeError):
    """Stable content-free failure from test-support setup or execution."""

    def __init__(self, code: MockABDMCode) -> None:
        self.code = code
        super().__init__(code.value)


class DeterministicMockABDMAdapter:
    """Exact-mapping test adapter with no network or official protocol behavior."""

    __slots__ = ("_clock", "_fixtures")

    def __init__(
        self,
        *,
        fixtures: Mapping[str, MockABDMScenario],
        environment: Environment,
        clock: Callable[[], datetime],
    ) -> None:
        validate_synthetic_abdm_environment(
            mode=ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK,
            environment=environment,
        )
        if not callable(clock):
            raise MockABDMError(MockABDMCode.INVALID_CLOCK)
        self._fixtures = MappingProxyType(self._snapshot(fixtures))
        self._clock = clock

    @staticmethod
    def _snapshot(
        fixtures: Mapping[str, MockABDMScenario],
    ) -> dict[str, MockABDMScenario]:
        if not isinstance(fixtures, Mapping):
            raise MockABDMError(MockABDMCode.INVALID_FIXTURE)
        detached: dict[str, MockABDMScenario] = {}
        try:
            entries = fixtures.items()
            for fingerprint, scenario in entries:
                if (
                    type(fingerprint) is not str
                    or _SHA256.fullmatch(fingerprint) is None
                    or type(scenario) is not MockABDMScenario
                    or fingerprint in detached
                ):
                    raise MockABDMError(MockABDMCode.INVALID_FIXTURE)
                detached[fingerprint] = scenario
        except MockABDMError:
            raise
        except Exception:
            raise MockABDMError(MockABDMCode.INVALID_FIXTURE) from None
        return detached

    def execute(self, request: SyntheticABDMRequest) -> SyntheticABDMResult:
        snapshot = validate_synthetic_abdm_request(request)
        fingerprint = synthetic_abdm_request_fingerprint(snapshot)
        scenario = self._fixtures.get(fingerprint, MockABDMScenario.UNAVAILABLE)
        try:
            completed_at = self._clock()
        except Exception:
            raise MockABDMError(MockABDMCode.CLOCK_FAILURE) from None
        state, issues = self._outcome(scenario)
        result = SyntheticABDMResult(
            request_id=snapshot.request_id,
            operation=snapshot.operation,
            request_fingerprint=fingerprint,
            state=state,
            issues=issues,
            completed_at=completed_at,
        )
        return validate_synthetic_abdm_result(request=snapshot, result=result)

    @staticmethod
    def _outcome(
        scenario: MockABDMScenario,
    ) -> tuple[SyntheticABDMResultState, tuple[SyntheticABDMIssue, ...]]:
        if scenario is MockABDMScenario.ACCEPTED:
            return SyntheticABDMResultState.SYNTHETIC_ACCEPTED, ()
        if scenario is MockABDMScenario.REJECTED:
            return SyntheticABDMResultState.SYNTHETIC_REJECTED, (
                SyntheticABDMIssue.SYNTHETIC_REJECTED,
            )
        return SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE, (
            SyntheticABDMIssue.SYNTHETIC_UNAVAILABLE,
        )


__all__ = [
    "DeterministicMockABDMAdapter",
    "MockABDMCode",
    "MockABDMError",
    "MockABDMScenario",
]
