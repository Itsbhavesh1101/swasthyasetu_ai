"""Provider port, health, normalized failures, and orchestration outcomes."""

import math
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, runtime_checkable

from app.modules.ai_orchestration.contracts import StructuredLLMRequest, StructuredLLMResult

_DIAGNOSTIC_CODE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


class LLMFailureCategory(StrEnum):
    """Closed internal failure taxonomy; intentionally not an HTTP error enum."""

    TIMEOUT = "LLM_TIMEOUT"
    RATE_LIMIT = "LLM_RATE_LIMIT"
    AUTH_FAILURE = "LLM_AUTH_FAILURE"
    PROVIDER_UNAVAILABLE = "LLM_PROVIDER_UNAVAILABLE"
    REFUSAL = "LLM_REFUSAL"
    SCHEMA_INVALID = "LLM_SCHEMA_INVALID"
    CONTENT_POLICY_BLOCK = "LLM_CONTENT_POLICY_BLOCK"
    UNKNOWN = "LLM_UNKNOWN"


class ProviderHealthStatus(StrEnum):
    """Non-billable provider configuration/health states."""

    DISABLED = "disabled"
    UNCONFIGURED = "unconfigured"
    CONFIGURED = "configured"
    DEGRADED = "degraded"


class ProviderSafetyClass(StrEnum):
    """Composition-time guard classification for provider adapters."""

    SAFE_DEFAULT = "safe_default"
    ENGINEERING_ONLY = "engineering_only"
    APPROVED_EXTERNAL = "approved_external"


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    """Content-free provider health without a network/model probe."""

    status: ProviderHealthStatus
    provider_id: str
    clinically_approved: bool = False

    def __post_init__(self) -> None:
        if self.clinically_approved:
            raise ValueError("AI health cannot assert clinical approval")


class ProviderFailure(Exception):
    """Safe adapter failure containing no provider exception or payload text."""

    __slots__ = ("category", "retryable", "retry_after_seconds", "diagnostic_code")

    def __init__(
        self,
        category: LLMFailureCategory,
        *,
        retryable: bool = False,
        retry_after_seconds: float | None = None,
        diagnostic_code: str | None = None,
    ) -> None:
        allowed_retry = {
            LLMFailureCategory.TIMEOUT,
            LLMFailureCategory.RATE_LIMIT,
            LLMFailureCategory.PROVIDER_UNAVAILABLE,
        }
        if retryable and category not in allowed_retry:
            raise ValueError(f"{category.value} cannot be retried")
        if retry_after_seconds is not None:
            if (
                isinstance(retry_after_seconds, bool)
                or not isinstance(retry_after_seconds, (int, float))
                or not math.isfinite(retry_after_seconds)
                or retry_after_seconds < 0
            ):
                raise ValueError("retry_after_seconds must be finite and non-negative")
            if category is not LLMFailureCategory.RATE_LIMIT:
                raise ValueError("retry_after_seconds is only valid for rate limits")
        if diagnostic_code is not None and not _DIAGNOSTIC_CODE.fullmatch(diagnostic_code):
            raise ValueError("diagnostic_code must be a bounded machine code")
        self.category = category
        self.retryable = retryable
        self.retry_after_seconds = retry_after_seconds
        self.diagnostic_code = diagnostic_code
        super().__init__(category.value)

    def __repr__(self) -> str:
        return f"ProviderFailure(category={self.category.value!r}, retryable={self.retryable!r})"


@dataclass(frozen=True, slots=True)
class NormalizedLLMFailure:
    """Safe application-facing failure after provider isolation."""

    category: LLMFailureCategory
    operation_id: str
    request_id: str
    attempt_count: int
    retryable: bool
    diagnostic_code: str | None = None

    def __str__(self) -> str:
        return self.category.value


@dataclass(frozen=True, slots=True)
class OrchestrationOutcome:
    """Exactly one structured candidate result or normalized failure."""

    result: StructuredLLMResult | None = field(default=None)
    failure: NormalizedLLMFailure | None = field(default=None)

    def __post_init__(self) -> None:
        if (self.result is None) == (self.failure is None):
            raise ValueError("outcome must contain exactly one result or failure")

    @classmethod
    def success(cls, result: StructuredLLMResult) -> "OrchestrationOutcome":
        return cls(result=result)

    @classmethod
    def failure_outcome(
        cls,
        *,
        category: LLMFailureCategory,
        operation_id: str,
        request_id: str,
        attempt_count: int,
        retryable: bool,
        diagnostic_code: str | None = None,
    ) -> "OrchestrationOutcome":
        return cls(
            failure=NormalizedLLMFailure(
                category=category,
                operation_id=operation_id,
                request_id=request_id,
                attempt_count=attempt_count,
                retryable=retryable,
                diagnostic_code=diagnostic_code,
            )
        )


@runtime_checkable
class LLMProvider(Protocol):
    """Asynchronous project-owned provider port."""

    @property
    def provider_id(self) -> str: ...

    @property
    def safety_class(self) -> ProviderSafetyClass: ...

    def health(self) -> ProviderHealth: ...

    async def generate_structured(self, request: StructuredLLMRequest) -> StructuredLLMResult: ...


class StructuredGenerationCapability(Protocol):
    """Public module capability consumed by future approved task services."""

    async def generate_structured(self, request: StructuredLLMRequest) -> OrchestrationOutcome: ...


class AIHealthCapability(Protocol):
    """Public content-free, non-billable health capability."""

    def health(self) -> ProviderHealth: ...
