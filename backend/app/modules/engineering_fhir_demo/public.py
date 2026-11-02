"""Explicit registration for the local/test-only P16 engineering preview."""

from fastapi import APIRouter

from app.config.settings import Environment
from app.modules.engineering_fhir_demo.api import build_engineering_fhir_demo_router
from app.modules.engineering_fhir_demo.application import EngineeringFHIRDemoService
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration

ENGINEERING_FHIR_DEMO_FEATURE = "engineering_fhir_demo_wave7"

ENGINEERING_FHIR_DEMO_MANIFEST = ModuleManifest(
    module_id=ModuleId("engineering_fhir_demo"),
    version=1,
    required_capabilities=frozenset(),
    api_prefixes=("/engineering-demo/fhir-preview",),
)


def build_engineering_fhir_demo_registration(
    *, environment: Environment
) -> ModuleRegistration[APIRouter]:
    service = EngineeringFHIRDemoService(environment=environment)
    return ModuleRegistration(
        manifest=ENGINEERING_FHIR_DEMO_MANIFEST,
        routers=(build_engineering_fhir_demo_router(service=service),),
    )


__all__ = [
    "ENGINEERING_FHIR_DEMO_FEATURE",
    "ENGINEERING_FHIR_DEMO_MANIFEST",
    "build_engineering_fhir_demo_registration",
]
