"""Exact-mapping, deterministic and test-only OCR adapter."""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType

from app.modules.documents.contracts import (
    DocumentContractError,
    DocumentProcessingResult,
    OCRRequest,
)
from app.shared.types import OpaqueId


class MockFailureCode(StrEnum):
    UNKNOWN_REQUEST = "UNKNOWN_REQUEST"
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
    REFUSED = "REFUSED"
    ENGINE_UNAVAILABLE = "ENGINE_UNAVAILABLE"
    FALLBACK_REQUIRED = "FALLBACK_REQUIRED"
    MALFORMED_RESULT = "MALFORMED_RESULT"
    INJECTED_EXCEPTION = "INJECTED_EXCEPTION"


class MockFailure(RuntimeError):
    """Content-free test failure."""

    def __init__(self, code: MockFailureCode) -> None:
        self.code = code
        super().__init__(code.value)


type MockOutcome = DocumentProcessingResult | MockFailure | object


class MockOCRAdapter:
    """No-I/O OCRPort implementation available only below ``tests``."""

    def __init__(self, fixtures: Mapping[OpaqueId, MockOutcome]) -> None:
        self._fixtures = MappingProxyType(dict(fixtures))

    async def extract(self, request: OCRRequest) -> DocumentProcessingResult:
        outcome = self._fixtures.get(request.request_id)
        if outcome is None:
            raise MockFailure(MockFailureCode.UNKNOWN_REQUEST)
        if isinstance(outcome, MockFailure):
            raise MockFailure(outcome.code) from None
        if not isinstance(outcome, DocumentProcessingResult):
            raise MockFailure(MockFailureCode.MALFORMED_RESULT)
        try:
            outcome.assert_matches(request)
        except DocumentContractError:
            raise MockFailure(MockFailureCode.MALFORMED_RESULT) from None
        return outcome
