"""Fail-closed disabled and unconfigured provider adapter."""

from app.modules.ai_orchestration.contracts import StructuredLLMRequest, StructuredLLMResult
from app.modules.ai_orchestration.providers import (
    LLMFailureCategory,
    ProviderFailure,
    ProviderHealth,
    ProviderHealthStatus,
    ProviderSafetyClass,
)


class DisabledLLMProvider:
    """Default provider that performs no network/model operation."""

    def __init__(self, *, unconfigured: bool = False) -> None:
        self._status = (
            ProviderHealthStatus.UNCONFIGURED if unconfigured else ProviderHealthStatus.DISABLED
        )

    @property
    def provider_id(self) -> str:
        return "disabled"

    @property
    def safety_class(self) -> ProviderSafetyClass:
        return ProviderSafetyClass.SAFE_DEFAULT

    def health(self) -> ProviderHealth:
        return ProviderHealth(status=self._status, provider_id=self.provider_id)

    async def generate_structured(self, request: StructuredLLMRequest) -> StructuredLLMResult:
        del request
        raise ProviderFailure(LLMFailureCategory.PROVIDER_UNAVAILABLE)
