"""Explicit registration for the local/test-only P11 engineering receipt."""

from fastapi import APIRouter

from app.modules.engineering_document_demo.api import build_engineering_document_demo_router
from app.modules.engineering_document_demo.application import EngineeringDocumentDemoService
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration

ENGINEERING_DOCUMENT_DEMO_FEATURE = "engineering_document_demo_wave2"

ENGINEERING_DOCUMENT_DEMO_MANIFEST = ModuleManifest(
    module_id=ModuleId("engineering_document_demo"),
    version=1,
    required_capabilities=frozenset(),
    api_prefixes=("/engineering-demo/document-review",),
)


def build_engineering_document_demo_registration() -> ModuleRegistration[APIRouter]:
    service = EngineeringDocumentDemoService()
    return ModuleRegistration(
        manifest=ENGINEERING_DOCUMENT_DEMO_MANIFEST,
        routers=(build_engineering_document_demo_router(service=service),),
    )


__all__ = [
    "ENGINEERING_DOCUMENT_DEMO_FEATURE",
    "ENGINEERING_DOCUMENT_DEMO_MANIFEST",
    "build_engineering_document_demo_registration",
]
