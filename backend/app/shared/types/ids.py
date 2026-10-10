"""Opaque UUID-backed identifiers for later domain specialization."""

from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class OpaqueId:
    """An immutable UUID value without domain-specific meaning."""

    value: UUID

    @classmethod
    def new(cls) -> Self:
        """Generate a new random UUID4 identifier."""
        return cls(uuid4())

    @classmethod
    def parse(cls, value: str | UUID) -> Self:
        """Parse an existing UUID or raise ``ValueError`` deterministically."""
        return cls(value if isinstance(value, UUID) else UUID(value))

    def __str__(self) -> str:
        return str(self.value)
