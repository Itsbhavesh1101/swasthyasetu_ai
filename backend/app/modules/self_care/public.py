"""Runtime composition for consent-gated, source-backed wellness guidance."""

from collections.abc import Callable

from fastapi import APIRouter

from app.adapters.ai.gemini_guidance import GeminiGuidanceProvider
from app.api.security.patient_authentication import PatientAuthenticator
from app.config import GuidanceSettings
from app.modules.consent.application import ConsentService
from app.modules.consent.public import CONSENT_CHECK, CONSENT_GRANT, CONSENT_LIST, CONSENT_REVOKE
from app.modules.self_care.guidance_api import build_guidance_router
from app.modules.self_care.guidance_contracts import (
    GuidanceProvider,
    GuidanceProviderError,
    GuidanceProviderFailureCode,
    GuidanceProviderRequest,
    GuidanceProviderResult,
)
from app.modules.self_care.guidance_policy import GuidancePolicy
from app.modules.self_care.guidance_service import GuidanceService
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
from app.shared.types import utc_now


class UnavailableGuidanceProvider:
    async def generate(self, request: GuidanceProviderRequest) -> GuidanceProviderResult:
        del request
        raise GuidanceProviderError(GuidanceProviderFailureCode.UNAVAILABLE)


SELF_CARE_GUIDANCE = CapabilityKey[GuidanceService](CapabilityIdentifier("self_care.guidance"))
SELF_CARE_MANIFEST = ModuleManifest(
    module_id=ModuleId("self_care"),
    version=1,
    provided_capabilities=frozenset({SELF_CARE_GUIDANCE.identifier}),
    required_capabilities=frozenset(
        key.identifier for key in (CONSENT_CHECK, CONSENT_GRANT, CONSENT_LIST, CONSENT_REVOKE)
    ),
    api_prefixes=("/guidance",),
    required_permissions=("patient:read:self",),
    configuration_keys=("guidance",),
)


def build_guidance_service(
    *,
    settings: GuidanceSettings,
    consent: ConsentService,
    provider_factory: Callable[[], GuidanceProvider] | None = None,
) -> GuidanceService:
    resolved_factory = provider_factory
    if resolved_factory is None:
        if settings.enabled and settings.api_key is not None and settings.model is not None:
            api_key = settings.api_key
            model = settings.model

            def create_gemini() -> GuidanceProvider:
                return GeminiGuidanceProvider(
                    api_key=api_key,
                    model=model,
                    deadline_seconds=settings.deadline_seconds,
                    clock=utc_now,
                )

            resolved_factory = create_gemini
        else:
            resolved_factory = UnavailableGuidanceProvider
    return GuidanceService(
        consent=consent,
        provider_factory=resolved_factory,
        policy=GuidancePolicy(settings.allowed_source_domains),
    )


def build_self_care_registration(
    *,
    service: GuidanceService,
    consent: ConsentService,
    authenticator: PatientAuthenticator,
) -> ModuleRegistration[APIRouter]:
    return ModuleRegistration(
        manifest=SELF_CARE_MANIFEST,
        routers=(
            build_guidance_router(service=service, consent=consent, authenticator=authenticator),
        ),
        capability_bindings=(SELF_CARE_GUIDANCE.bind(service),),
    )


__all__ = [
    "SELF_CARE_GUIDANCE",
    "SELF_CARE_MANIFEST",
    "GuidanceService",
    "build_guidance_service",
    "build_self_care_registration",
]
