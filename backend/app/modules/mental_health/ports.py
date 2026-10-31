"""Provider-neutral port for detached synthetic signal extraction."""

from typing import Protocol, runtime_checkable

from app.modules.mental_health.backstop import (
    SyntheticBackstopRequest,
    SyntheticBackstopResponse,
)
from app.modules.mental_health.contracts import (
    SyntheticExtractionRequest,
    SyntheticExtractionResult,
)


@runtime_checkable
class SyntheticSignalExtractorPort(Protocol):
    """Engineering-only extraction boundary with no route or clinical authority."""

    async def extract(self, request: SyntheticExtractionRequest) -> SyntheticExtractionResult: ...


@runtime_checkable
class SyntheticSafetyBackstopPort(Protocol):
    """Independent engineering-only backstop boundary with no route authority."""

    async def evaluate(self, request: SyntheticBackstopRequest) -> SyntheticBackstopResponse: ...


__all__ = ["SyntheticSafetyBackstopPort", "SyntheticSignalExtractorPort"]
