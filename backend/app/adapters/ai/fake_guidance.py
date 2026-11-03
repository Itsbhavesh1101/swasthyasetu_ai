"""Deterministic network-free guidance provider for tests and local demos."""

from app.modules.self_care.guidance_contracts import (
    GuidanceProviderError,
    GuidanceProviderFailureCode,
    GuidanceProviderRequest,
    GuidanceProviderResult,
)


class FakeGuidanceProvider:
    def __init__(
        self, outcomes: tuple[GuidanceProviderResult | GuidanceProviderError, ...]
    ) -> None:
        if not outcomes:
            raise ValueError("fake guidance provider requires at least one outcome")
        self._outcomes = outcomes
        self._requests: list[GuidanceProviderRequest] = []

    @property
    def requests(self) -> tuple[GuidanceProviderRequest, ...]:
        return tuple(self._requests)

    async def generate(self, request: GuidanceProviderRequest) -> GuidanceProviderResult:
        self._requests.append(request)
        position = len(self._requests) - 1
        if position >= len(self._outcomes):
            raise GuidanceProviderError(GuidanceProviderFailureCode.UNAVAILABLE)
        outcome = self._outcomes[position]
        if isinstance(outcome, GuidanceProviderError):
            raise outcome
        return outcome


__all__ = ["FakeGuidanceProvider"]
