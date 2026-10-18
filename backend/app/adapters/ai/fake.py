"""Deterministic, network-free provider for tests and local engineering."""

import json
from dataclasses import dataclass

from app.modules.ai_orchestration.contracts import StructuredLLMRequest, StructuredLLMResult
from app.modules.ai_orchestration.providers import (
    LLMFailureCategory,
    ProviderFailure,
    ProviderHealth,
    ProviderHealthStatus,
    ProviderSafetyClass,
)


@dataclass(frozen=True, slots=True)
class DeterministicLLMFixture:
    """Exact versioned request key and deterministic scripted outcomes."""

    request: StructuredLLMRequest
    outcomes: tuple[StructuredLLMResult | ProviderFailure, ...]

    def __post_init__(self) -> None:
        if not self.outcomes:
            raise ValueError("a deterministic fixture requires at least one outcome")


class DeterministicOfflineLLMProvider:
    """Exact-match fake with no network, randomness, or time dependency."""

    def __init__(
        self,
        fixtures: tuple[DeterministicLLMFixture, ...],
        *,
        degraded: bool = False,
    ) -> None:
        keys = tuple(self._key(fixture.request) for fixture in fixtures)
        if len(set(keys)) != len(keys):
            raise ValueError("deterministic fixture request keys must be unique")
        self._fixtures = dict(zip(keys, fixtures, strict=True))
        self._positions: dict[str, int] = {}
        self._requests: list[StructuredLLMRequest] = []
        self._status = (
            ProviderHealthStatus.DEGRADED if degraded else ProviderHealthStatus.CONFIGURED
        )

    @property
    def provider_id(self) -> str:
        return "offline_fake"

    @property
    def safety_class(self) -> ProviderSafetyClass:
        return ProviderSafetyClass.ENGINEERING_ONLY

    @property
    def requests(self) -> tuple[StructuredLLMRequest, ...]:
        return tuple(self._requests)

    def health(self) -> ProviderHealth:
        return ProviderHealth(status=self._status, provider_id=self.provider_id)

    async def generate_structured(self, request: StructuredLLMRequest) -> StructuredLLMResult:
        self._requests.append(request)
        key = self._key(request)
        fixture = self._fixtures.get(key)
        if fixture is None:
            raise ProviderFailure(
                LLMFailureCategory.UNKNOWN, diagnostic_code="FAKE_FIXTURE_NOT_FOUND"
            )
        position = self._positions.get(key, 0)
        if position >= len(fixture.outcomes):
            raise ProviderFailure(
                LLMFailureCategory.UNKNOWN, diagnostic_code="FAKE_FIXTURE_EXHAUSTED"
            )
        self._positions[key] = position + 1
        outcome = fixture.outcomes[position]
        if isinstance(outcome, ProviderFailure):
            raise outcome
        return outcome

    @staticmethod
    def _key(request: StructuredLLMRequest) -> str:
        value = request.to_dict()
        value["attempt"] = 1
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
