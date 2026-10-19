"""Provider-neutral document parser and OCR boundaries."""

from typing import Protocol

from app.modules.documents.contracts import (
    DocumentParserRequest,
    DocumentProcessingResult,
    OCRRequest,
)


class DocumentParserPort(Protocol):
    """Recognize native/born-digital structure; never authorizes source access."""

    async def parse(self, request: DocumentParserRequest) -> DocumentProcessingResult: ...


class OCRPort(Protocol):
    """Recognize synthetic raster-page input; never classifies clinical truth."""

    async def extract(self, request: OCRRequest) -> DocumentProcessingResult: ...
