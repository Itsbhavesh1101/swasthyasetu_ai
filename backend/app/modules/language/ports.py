"""Independent provider-neutral ports for P12 language operations."""

from typing import Protocol, runtime_checkable

from app.modules.language.contracts import (
    LanguageDetectionRequest,
    LanguageDetectionResult,
    SpeechToTextRequest,
    SpeechToTextResult,
    TextToSpeechRequest,
    TextToSpeechResult,
    TranslationRequest,
    TranslationResult,
    TransliterationRequest,
    TransliterationResult,
)


@runtime_checkable
class SpeechToTextPort(Protocol):
    """Batch speech-to-text boundary; streaming requires a separate future port."""

    async def transcribe(self, request: SpeechToTextRequest) -> SpeechToTextResult: ...


@runtime_checkable
class LanguageDetectionPort(Protocol):
    """Language/script candidate boundary with explicit uncertainty."""

    async def detect(self, request: LanguageDetectionRequest) -> LanguageDetectionResult: ...


@runtime_checkable
class TransliterationPort(Protocol):
    """Script-representation boundary that does not claim semantic translation."""

    async def transliterate(self, request: TransliterationRequest) -> TransliterationResult: ...


@runtime_checkable
class TranslationPort(Protocol):
    """Source-preserving translation boundary without clinical authority."""

    async def translate(self, request: TranslationRequest) -> TranslationResult: ...


@runtime_checkable
class TextToSpeechPort(Protocol):
    """Versioned-text synthesis boundary with no arbitrary reference-audio input."""

    async def synthesize(self, request: TextToSpeechRequest) -> TextToSpeechResult: ...
