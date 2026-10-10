"""Explicit compile-time module composition contracts."""

from app.shared.modules.manifest import ModuleId, ModuleManifest
from app.shared.modules.registry import (
    CapabilityDeclarationError,
    DuplicateModuleError,
    MissingRequiredCapabilityError,
    ModuleRegistration,
    ModuleRegistrationError,
    ModuleRegistry,
)

__all__ = [
    "CapabilityDeclarationError",
    "DuplicateModuleError",
    "MissingRequiredCapabilityError",
    "ModuleId",
    "ModuleManifest",
    "ModuleRegistration",
    "ModuleRegistrationError",
    "ModuleRegistry",
]
