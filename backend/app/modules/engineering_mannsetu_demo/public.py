"""Explicit registration for the local/test-only P14 engineering preview."""

from fastapi import APIRouter

from app.config.settings import Environment
from app.modules.engineering_mannsetu_demo.api import build_engineering_mannsetu_demo_router
from app.modules.engineering_mannsetu_demo.application import EngineeringMannSetuDemoService
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration

ENGINEERING_MANNSETU_DEMO_FEATURE = "engineering_mannsetu_demo_wave5"

ENGINEERING_MANNSETU_DEMO_MANIFEST = ModuleManifest(
    module_id=ModuleId("engineering_mannsetu_demo"),
    version=1,
    required_capabilities=frozenset(),
    api_prefixes=("/engineering-demo/mannsetu-preview",),
)


def build_engineering_mannsetu_demo_registration(
    *, environment: Environment
) -> ModuleRegistration[APIRouter]:
    service = EngineeringMannSetuDemoService(environment=environment)
    return ModuleRegistration(
        manifest=ENGINEERING_MANNSETU_DEMO_MANIFEST,
        routers=(build_engineering_mannsetu_demo_router(service=service),),
    )


__all__ = [
    "ENGINEERING_MANNSETU_DEMO_FEATURE",
    "ENGINEERING_MANNSETU_DEMO_MANIFEST",
    "build_engineering_mannsetu_demo_registration",
]
