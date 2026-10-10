"""Explicit, order-independent module registration and validation."""

from dataclasses import dataclass

from app.shared.capabilities import (
    CapabilityBinding,
    CapabilityIdentifier,
    CapabilityRegistry,
    RegistryNotSealedError,
    RegistrySealedError,
)
from app.shared.modules.manifest import ModuleId, ModuleManifest


class ModuleRegistrationError(Exception):
    """Base for deterministic module-composition failures."""


class DuplicateModuleError(ModuleRegistrationError):
    """Raised when a module identifier is registered more than once."""


class CapabilityDeclarationError(ModuleRegistrationError):
    """Raised when provider bindings disagree with manifest declarations."""


class MissingRequiredCapabilityError(ModuleRegistrationError):
    """Raised when final composition lacks a module's required capability."""


@dataclass(frozen=True, slots=True)
class ModuleRegistration[RouterT]:
    """Explicit composition input supplied by a future module public interface."""

    manifest: ModuleManifest
    routers: tuple[RouterT, ...] = ()
    capability_bindings: tuple[CapabilityBinding, ...] = ()


class ModuleRegistry[RouterT]:
    """Collect explicit module registrations, validate them, and seal composition."""

    def __init__(self) -> None:
        self._registrations: dict[ModuleId, ModuleRegistration[RouterT]] = {}
        self._capabilities = CapabilityRegistry()
        self._sealed = False

    @property
    def is_sealed(self) -> bool:
        return self._sealed

    @property
    def capability_registry(self) -> CapabilityRegistry:
        if not self._sealed:
            raise RegistryNotSealedError(
                "Module registry must be finalized before capabilities are exposed"
            )
        return self._capabilities

    @property
    def module_ids(self) -> tuple[str, ...]:
        return tuple(sorted(str(module_id) for module_id in self._registrations))

    @property
    def routers(self) -> tuple[RouterT, ...]:
        if not self._sealed:
            raise RegistryNotSealedError(
                "Module registry must be finalized before routers are exposed"
            )
        return tuple(
            router
            for registration in self._registrations.values()
            for router in registration.routers
        )

    def register(self, registration: ModuleRegistration[RouterT]) -> None:
        """Register one explicitly imported module during startup composition."""
        if self._sealed:
            raise RegistrySealedError("Module registry is sealed")
        manifest = registration.manifest
        if manifest.module_id in self._registrations:
            raise DuplicateModuleError(f"Module '{manifest.module_id}' is already registered")

        bound = frozenset(binding.key.identifier for binding in registration.capability_bindings)
        if bound != manifest.provided_capabilities:
            undeclared = bound - manifest.provided_capabilities
            unbound = manifest.provided_capabilities - bound
            raise CapabilityDeclarationError(
                f"Module '{manifest.module_id}' capability declarations do not match bindings; "
                f"undeclared={self._names(undeclared)}, unbound={self._names(unbound)}"
            )

        self._capabilities.register_bindings(
            module_id=str(manifest.module_id),
            bindings=registration.capability_bindings,
        )
        self._registrations[manifest.module_id] = registration

    def get_manifest(self, module_id: ModuleId) -> ModuleManifest:
        """Return registered immutable metadata or raise ``KeyError``."""
        return self._registrations[module_id].manifest

    def finalize(self) -> None:
        """Validate the complete dependency set and prohibit later mutation."""
        if self._sealed:
            return
        available = {
            binding.key.identifier
            for registration in self._registrations.values()
            for binding in registration.capability_bindings
        }
        for registration in self._registrations.values():
            missing = registration.manifest.required_capabilities - available
            if missing:
                raise MissingRequiredCapabilityError(
                    f"Module '{registration.manifest.module_id}' requires missing capabilities "
                    f"{self._names(missing)}"
                )
        self._capabilities.seal()
        self._sealed = True

    @staticmethod
    def _names(identifiers: frozenset[CapabilityIdentifier] | set[CapabilityIdentifier]) -> str:
        return ",".join(sorted(str(identifier) for identifier in identifiers)) or "none"
