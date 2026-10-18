"""Stable P8-A exports and explicit AI orchestration composition."""

from fastapi import APIRouter

from app.adapters.ai.disabled import DisabledLLMProvider
from app.config import Environment
from app.modules.ai_orchestration.application import AIOrchestrationService
from app.modules.ai_orchestration.providers import (
    AIHealthCapability,
    LLMProvider,
    ProviderSafetyClass,
    StructuredGenerationCapability,
)
from app.modules.ai_orchestration.telemetry import OpenTelemetryAIOrchestration
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
from app.shared.observability import ObservabilityRuntime

AI_GENERATE_STRUCTURED = CapabilityKey[StructuredGenerationCapability](
    CapabilityIdentifier("llm.generate_structured")
)
AI_HEALTH = CapabilityKey[AIHealthCapability](CapabilityIdentifier("llm.health"))

AI_ORCHESTRATION_MANIFEST = ModuleManifest(
    module_id=ModuleId("ai_orchestration"),
    version=1,
    provided_capabilities=frozenset(key.identifier for key in (AI_GENERATE_STRUCTURED, AI_HEALTH)),
    configuration_keys=("llm.enabled",),
)


class UnsafeProviderCompositionError(ValueError):
    """Raised when runtime composition could activate an unsafe adapter."""


def build_ai_orchestration_registration(
    *,
    environment: Environment,
    enabled: bool,
    observability: ObservabilityRuntime,
    provider: LLMProvider | None = None,
) -> ModuleRegistration[APIRouter]:
    """Build one explicit provider binding; default is disabled/unconfigured."""
    if provider is not None and not enabled:
        raise UnsafeProviderCompositionError("an AI provider cannot be composed while disabled")
    selected = provider or DisabledLLMProvider(unconfigured=enabled)
    protected_environments = {
        Environment.STAGING,
        Environment.PILOT,
        Environment.PRODUCTION,
    }
    if (
        environment in protected_environments
        and selected.safety_class is ProviderSafetyClass.ENGINEERING_ONLY
    ):
        raise UnsafeProviderCompositionError(
            "engineering-only AI providers are prohibited in protected environments"
        )
    service = AIOrchestrationService(
        provider=selected,
        telemetry=OpenTelemetryAIOrchestration(observability),
    )
    return ModuleRegistration(
        manifest=AI_ORCHESTRATION_MANIFEST,
        capability_bindings=(
            AI_GENERATE_STRUCTURED.bind(service),
            AI_HEALTH.bind(service),
        ),
    )


__all__ = [
    "AI_GENERATE_STRUCTURED",
    "AI_HEALTH",
    "AI_ORCHESTRATION_MANIFEST",
    "LLMProvider",
    "UnsafeProviderCompositionError",
    "build_ai_orchestration_registration",
]
