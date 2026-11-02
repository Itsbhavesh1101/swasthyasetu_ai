"""Explicit composition for the local/test-only engineering demo module."""

from fastapi import APIRouter

from app.modules.clinical_intake.contracts import ReadIntakeCapability
from app.modules.clinical_intake.public import INTAKE_READ
from app.modules.consent.public import CONSENT_CHECK
from app.modules.encounters.public import ENCOUNTERS_READ
from app.modules.engineering_demo.api import build_engineering_demo_router
from app.modules.engineering_demo.application import EngineeringDemoService
from app.modules.sessions.public import SESSIONS_VALIDATE
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration

ENGINEERING_DEMO_FEATURE = "engineering_demo_wave1"

ENGINEERING_DEMO_MANIFEST = ModuleManifest(
    module_id=ModuleId("engineering_demo"),
    version=1,
    required_capabilities=frozenset(
        key.identifier for key in (INTAKE_READ, ENCOUNTERS_READ, SESSIONS_VALIDATE, CONSENT_CHECK)
    ),
    api_prefixes=("/engineering-demo/intakes",),
)


def build_engineering_demo_registration(
    *, intake_reader: ReadIntakeCapability
) -> ModuleRegistration[APIRouter]:
    service = EngineeringDemoService()
    return ModuleRegistration(
        manifest=ENGINEERING_DEMO_MANIFEST,
        routers=(build_engineering_demo_router(intake_reader=intake_reader, service=service),),
    )


__all__ = [
    "ENGINEERING_DEMO_FEATURE",
    "ENGINEERING_DEMO_MANIFEST",
    "build_engineering_demo_registration",
]
