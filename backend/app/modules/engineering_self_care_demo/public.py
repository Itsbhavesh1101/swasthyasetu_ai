"""Explicit registration for the local/test-only P15 engineering preview."""

from fastapi import APIRouter

from app.config.settings import Environment
from app.modules.engineering_self_care_demo.api import build_engineering_self_care_demo_router
from app.modules.engineering_self_care_demo.application import EngineeringSelfCareDemoService
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration

ENGINEERING_SELF_CARE_DEMO_FEATURE = "engineering_self_care_demo_wave6"

ENGINEERING_SELF_CARE_DEMO_MANIFEST = ModuleManifest(
    module_id=ModuleId("engineering_self_care_demo"),
    version=1,
    required_capabilities=frozenset(),
    api_prefixes=("/engineering-demo/self-care-preview",),
)


def build_engineering_self_care_demo_registration(
    *, environment: Environment
) -> ModuleRegistration[APIRouter]:
    service = EngineeringSelfCareDemoService(environment=environment)
    return ModuleRegistration(
        manifest=ENGINEERING_SELF_CARE_DEMO_MANIFEST,
        routers=(build_engineering_self_care_demo_router(service=service),),
    )


__all__ = [
    "ENGINEERING_SELF_CARE_DEMO_FEATURE",
    "ENGINEERING_SELF_CARE_DEMO_MANIFEST",
    "build_engineering_self_care_demo_registration",
]
