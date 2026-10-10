"""Sealable, per-composition capability provider registry."""

from typing import cast

from app.shared.capabilities.keys import CapabilityBinding, CapabilityIdentifier, CapabilityKey


class CapabilityRegistryError(Exception):
    """Base for deterministic capability-composition failures."""


class DuplicateCapabilityError(CapabilityRegistryError):
    """Raised when more than one provider binds the same capability."""


class CapabilityNotFoundError(CapabilityRegistryError):
    """Raised when a required typed capability cannot be resolved."""


class RegistrySealedError(CapabilityRegistryError):
    """Raised when composition attempts to mutate a sealed registry."""


class RegistryNotSealedError(CapabilityRegistryError):
    """Raised when runtime resolution is attempted before finalization."""


class CapabilityRegistry:
    """Register providers during composition and resolve them after sealing."""

    def __init__(self) -> None:
        self._providers: dict[CapabilityIdentifier, object] = {}
        self._owners: dict[CapabilityIdentifier, str] = {}
        self._sealed = False

    @property
    def is_sealed(self) -> bool:
        return self._sealed

    @property
    def registered_names(self) -> tuple[str, ...]:
        """Return stable capability names without exposing provider objects."""
        return tuple(sorted(str(identifier) for identifier in self._providers))

    def register_bindings(
        self,
        *,
        module_id: str,
        bindings: tuple[CapabilityBinding, ...],
    ) -> None:
        """Atomically register a module's explicitly supplied bindings."""
        self._ensure_mutable()
        identifiers = tuple(binding.key.identifier for binding in bindings)
        if len(set(identifiers)) != len(identifiers):
            raise DuplicateCapabilityError(
                f"Module '{module_id}' binds the same capability more than once"
            )
        for identifier in identifiers:
            if identifier in self._providers:
                owner = self._owners[identifier]
                raise DuplicateCapabilityError(
                    f"Capability '{identifier}' is already provided by module '{owner}'"
                )
        for binding in bindings:
            self._providers[binding.key.identifier] = binding.provider
            self._owners[binding.key.identifier] = module_id

    def seal(self) -> None:
        """Prevent all further provider registration."""
        self._sealed = True

    def resolve[T](self, key: CapabilityKey[T]) -> T:
        """Resolve a typed public capability after composition is sealed."""
        if not self._sealed:
            raise RegistryNotSealedError("Capability registry must be sealed before resolution")
        try:
            provider = self._providers[key.identifier]
        except KeyError as error:
            raise CapabilityNotFoundError(
                f"Capability '{key.identifier}' has no registered provider"
            ) from error
        return cast(T, provider)

    def _ensure_mutable(self) -> None:
        if self._sealed:
            raise RegistrySealedError("Capability registry is sealed")
