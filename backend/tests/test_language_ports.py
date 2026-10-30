from typing import Any

import app.modules.language.ports as language_ports
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
from app.modules.language.ports import (
    LanguageDetectionPort,
    SpeechToTextPort,
    TextToSpeechPort,
    TranslationPort,
    TransliterationPort,
)


class DetectionOnlyAdapter:
    async def detect(self, request: LanguageDetectionRequest) -> LanguageDetectionResult:
        raise NotImplementedError


class SpeechToTextOnlyAdapter:
    async def transcribe(self, request: SpeechToTextRequest) -> SpeechToTextResult:
        raise NotImplementedError


class TransliterationOnlyAdapter:
    async def transliterate(self, request: TransliterationRequest) -> TransliterationResult:
        raise NotImplementedError


class TranslationOnlyAdapter:
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        raise NotImplementedError


class TextToSpeechOnlyAdapter:
    async def synthesize(self, request: TextToSpeechRequest) -> TextToSpeechResult:
        raise NotImplementedError


def test_each_adapter_matches_only_its_narrow_runtime_protocol() -> None:
    adapters: tuple[tuple[Any, type[Any]], ...] = (
        (DetectionOnlyAdapter(), LanguageDetectionPort),
        (SpeechToTextOnlyAdapter(), SpeechToTextPort),
        (TransliterationOnlyAdapter(), TransliterationPort),
        (TranslationOnlyAdapter(), TranslationPort),
        (TextToSpeechOnlyAdapter(), TextToSpeechPort),
    )
    ports = {
        LanguageDetectionPort,
        SpeechToTextPort,
        TransliterationPort,
        TranslationPort,
        TextToSpeechPort,
    }

    for adapter, expected_port in adapters:
        assert isinstance(adapter, expected_port)
        assert all(not isinstance(adapter, port) for port in ports - {expected_port})


def test_language_module_does_not_define_a_god_provider_interface() -> None:
    assert not hasattr(language_ports, "LanguageAIProvider")
    assert not hasattr(language_ports, "LanguageProvider")
