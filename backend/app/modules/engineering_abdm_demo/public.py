"""Explicit registration for the local/test-only P17 engineering preview."""

from fastapi import APIRouter

from app.config.settings import Environment
from app.modules.engineering_abdm_demo.api import build_engineering_abdm_demo_router
from app.modules.engineering_abdm_demo.application import EngineeringABDMDemoService
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration

ENGINEERING_ABDM_DEMO_FEATURE = "engineering_abdm_demo_wave8"

ENGINEERING_ABDM_DEMO_MANIFEST = ModuleManifest(
    module_id=ModuleId("engineering_abdm_demo"),
    version=1,
    required_capabilities=frozenset(),
    api_prefixes=("/engineering-demo/abdm-preview",),
)


def build_engineering_abdm_demo_registration(
    *, environment: Environment
) -> ModuleRegistration[APIRouter]:
    service = EngineeringABDMDemoService(environment=environment)
    return ModuleRegistration(
        manifest=ENGINEERING_ABDM_DEMO_MANIFEST,
        routers=(build_engineering_abdm_demo_router(service=service),),
    )


__all__ = [
    "ENGINEERING_ABDM_DEMO_FEATURE",
    "ENGINEERING_ABDM_DEMO_MANIFEST",
    "build_engineering_abdm_demo_registration",
]
