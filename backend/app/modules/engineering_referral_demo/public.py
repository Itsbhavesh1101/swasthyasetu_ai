"""Explicit registration for the local/test-only P13 engineering preview."""

from fastapi import APIRouter

from app.modules.engineering_referral_demo.api import build_engineering_referral_demo_router
from app.modules.engineering_referral_demo.application import EngineeringReferralDemoService
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration

ENGINEERING_REFERRAL_DEMO_FEATURE = "engineering_referral_demo_wave4"

ENGINEERING_REFERRAL_DEMO_MANIFEST = ModuleManifest(
    module_id=ModuleId("engineering_referral_demo"),
    version=1,
    required_capabilities=frozenset(),
    api_prefixes=("/engineering-demo/referral-discovery",),
)


def build_engineering_referral_demo_registration() -> ModuleRegistration[APIRouter]:
    service = EngineeringReferralDemoService()
    return ModuleRegistration(
        manifest=ENGINEERING_REFERRAL_DEMO_MANIFEST,
        routers=(build_engineering_referral_demo_router(service=service),),
    )


__all__ = [
    "ENGINEERING_REFERRAL_DEMO_FEATURE",
    "ENGINEERING_REFERRAL_DEMO_MANIFEST",
    "build_engineering_referral_demo_registration",
]
