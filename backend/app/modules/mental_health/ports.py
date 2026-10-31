"""Provider-neutral port for detached synthetic signal extraction."""

from typing import Protocol, runtime_checkable

from app.modules.mental_health.contracts import (
    SyntheticExtractionRequest,
    SyntheticExtractionResult,
)


@runtime_checkable
class SyntheticSignalExtractorPort(Protocol):
    """Engineering-only extraction boundary with no route or clinical authority."""

    async def extract(self, request: SyntheticExtractionRequest) -> SyntheticExtractionResult: ...


__all__ = ["SyntheticSignalExtractorPort"]
