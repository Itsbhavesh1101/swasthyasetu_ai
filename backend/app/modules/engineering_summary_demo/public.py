"""Explicit registration for the local/test-only P10 engineering draft."""

from fastapi import APIRouter

from app.modules.engineering_summary_demo.api import build_engineering_summary_demo_router
from app.modules.engineering_summary_demo.application import EngineeringSummaryDemoService
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration

ENGINEERING_SUMMARY_DEMO_FEATURE = "engineering_summary_demo_wave3"

ENGINEERING_SUMMARY_DEMO_MANIFEST = ModuleManifest(
    module_id=ModuleId("engineering_summary_demo"),
    version=1,
    required_capabilities=frozenset(),
    api_prefixes=("/engineering-demo/summary-review",),
)


def build_engineering_summary_demo_registration() -> ModuleRegistration[APIRouter]:
    service = EngineeringSummaryDemoService()
    return ModuleRegistration(
        manifest=ENGINEERING_SUMMARY_DEMO_MANIFEST,
        routers=(build_engineering_summary_demo_router(service=service),),
    )


__all__ = [
    "ENGINEERING_SUMMARY_DEMO_FEATURE",
    "ENGINEERING_SUMMARY_DEMO_MANIFEST",
    "build_engineering_summary_demo_registration",
]
