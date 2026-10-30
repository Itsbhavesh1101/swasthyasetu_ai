import builtins
import socket
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from language_support.mocks import (
    MockFailureCode,
    MockLanguageDetectionAdapter,
    MockLanguageFailure,
    MockSpeechToTextAdapter,
    MockTextToSpeechAdapter,
    MockTranslationAdapter,
    MockTransliterationAdapter,
)

from app.modules.language.contracts import (
    LANGUAGE_DETECTION_REQUEST_VERSION,
    LANGUAGE_DETECTION_RESULT_VERSION,
    SPEECH_TO_TEXT_REQUEST_VERSION,
    SPEECH_TO_TEXT_RESULT_VERSION,
    TEXT_TO_SPEECH_REQUEST_VERSION,
    TEXT_TO_SPEECH_RESULT_VERSION,
    TRANSLATION_REQUEST_VERSION,
    TRANSLATION_RESULT_VERSION,
    TRANSLITERATION_REQUEST_VERSION,
    TRANSLITERATION_RESULT_VERSION,
    ArtifactReference,
    LanguageCandidate,
    LanguageDetectionRequest,
    LanguageDetectionResult,
    LanguageOutcome,
    OperationContext,
    OperationKind,
    ProcessingStatus,
    ProviderProvenance,
    QualityEvidence,
    QualityKind,
    ResultFinality,
    SpeechSegment,
    SpeechToTextRequest,
    SpeechToTextResult,
    TextArtifact,
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

NOW = datetime(2026, 10, 30, 10, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64


def ctx(kind: OperationKind, operation_id: str) -> OperationContext:
    return OperationContext(
        operation_id=operation_id,
        correlation_id="corr_synthetic_0001",
        operation=kind,
        created_at=NOW,
        deadline_at=NOW + timedelta(seconds=5),
        idempotency_key="idem_aaaaaaaa",
        cancelled=False,
    )


def ref(generation: int = 1, digest: str = HASH_A) -> ArtifactReference:
    return ArtifactReference("artifact_synthetic_0001", "v1", generation, digest)


def text() -> TextArtifact:
    return TextArtifact(ref(), "synthetic hello")


def quality() -> QualityEvidence:
    return QualityEvidence(QualityKind.UNKNOWN, None)


def language() -> LanguageCandidate:
    return LanguageCandidate("en", "Latn", LanguageOutcome.KNOWN, 1, quality())


def prov(kind: OperationKind) -> ProviderProvenance:
    return ProviderProvenance(
        kind,
        "synthetic.provider",
        "v1",
        "synthetic.model",
        "rev-1",
        HASH_B,
        NOW,
    )


def stt_pair(
    operation_id: str = "op_synthetic_0001",
) -> tuple[SpeechToTextRequest, SpeechToTextResult]:
    request = SpeechToTextRequest(
        SPEECH_TO_TEXT_REQUEST_VERSION,
        ctx(OperationKind.SPEECH_TO_TEXT, operation_id),
        ref(),
        "audio/synthetic",
        (language(),),
        False,
    )
    result = SpeechToTextResult(
        SPEECH_TO_TEXT_RESULT_VERSION,
        operation_id,
        SPEECH_TO_TEXT_REQUEST_VERSION,
        ref(),
        ProcessingStatus.SUCCEEDED,
        ResultFinality.FINAL,
        "synthetic hello",
        (SpeechSegment(0, 500, "synthetic hello", (language(),), quality()),),
        (language(),),
        (),
        prov(OperationKind.SPEECH_TO_TEXT),
        quality(),
    )
    return request, result


def detection_pair() -> tuple[LanguageDetectionRequest, LanguageDetectionResult]:
    operation_id = "op_synthetic_0002"
    request = LanguageDetectionRequest(
        LANGUAGE_DETECTION_REQUEST_VERSION,
        ctx(OperationKind.LANGUAGE_DETECTION, operation_id),
        text(),
    )
    result = LanguageDetectionResult(
        LANGUAGE_DETECTION_RESULT_VERSION,
        operation_id,
        LANGUAGE_DETECTION_REQUEST_VERSION,
        text(),
        ProcessingStatus.SUCCEEDED,
        (language(),),
        (),
        prov(OperationKind.LANGUAGE_DETECTION),
    )
    return request, result


def transliteration_pair() -> tuple[TransliterationRequest, TransliterationResult]:
    operation_id = "op_synthetic_0003"
    request = TransliterationRequest(
        TRANSLITERATION_REQUEST_VERSION,
        ctx(OperationKind.TRANSLITERATION, operation_id),
        text(),
        "Latn",
        "Deva",
        (),
    )
    result = TransliterationResult(
        TRANSLITERATION_RESULT_VERSION,
        operation_id,
        TRANSLITERATION_REQUEST_VERSION,
        text(),
        "सिंथेटिक नमस्ते",
        "Latn",
        "Deva",
        (),
        ProcessingStatus.SUCCEEDED,
        (),
        prov(OperationKind.TRANSLITERATION),
        quality(),
    )
    return request, result


def translation_pair() -> tuple[TranslationRequest, TranslationResult]:
    operation_id = "op_synthetic_0004"
    request = TranslationRequest(
        TRANSLATION_REQUEST_VERSION,
        ctx(OperationKind.TRANSLATION, operation_id),
        text(),
        "en",
        "hi",
    )
    result = TranslationResult(
        TRANSLATION_RESULT_VERSION,
        operation_id,
        TRANSLATION_REQUEST_VERSION,
        text(),
        "सिंथेटिक नमस्ते",
        "en",
        "hi",
        ProcessingStatus.SUCCEEDED,
        (),
        prov(OperationKind.TRANSLATION),
        quality(),
    )
    return request, result


def tts_pair() -> tuple[TextToSpeechRequest, TextToSpeechResult]:
    operation_id = "op_synthetic_0005"
    request = TextToSpeechRequest(
        TEXT_TO_SPEECH_REQUEST_VERSION,
        ctx(OperationKind.TEXT_TO_SPEECH, operation_id),
        text(),
        "en",
        "synthetic.voice",
        "v1",
    )
    result = TextToSpeechResult(
        TEXT_TO_SPEECH_RESULT_VERSION,
        operation_id,
        TEXT_TO_SPEECH_REQUEST_VERSION,
        ref(),
        ref(2, HASH_B),
        "en",
        "synthetic.voice",
        "v1",
        "audio/synthetic",
        ProcessingStatus.SUCCEEDED,
        (),
        prov(OperationKind.TEXT_TO_SPEECH),
    )
    return request, result


@pytest.mark.asyncio
async def test_all_five_mocks_return_deterministic_detached_results() -> None:
    pairs: tuple[tuple[Any, Any, str], ...] = (
        (MockSpeechToTextAdapter, stt_pair(), "transcribe"),
        (MockLanguageDetectionAdapter, detection_pair(), "detect"),
        (MockTransliterationAdapter, transliteration_pair(), "transliterate"),
        (MockTranslationAdapter, translation_pair(), "translate"),
        (MockTextToSpeechAdapter, tts_pair(), "synthesize"),
    )

    for adapter_type, (request, expected), method_name in pairs:
        adapter = adapter_type({request.context.operation_id: expected})
        first = await getattr(adapter, method_name)(request)
        second = await getattr(adapter, method_name)(request)
        assert first == expected
        assert second == expected
        assert first is not expected
        assert first is not second

    assert isinstance(MockSpeechToTextAdapter({}), SpeechToTextPort)
    assert isinstance(MockLanguageDetectionAdapter({}), LanguageDetectionPort)
    assert isinstance(MockTransliterationAdapter({}), TransliterationPort)
    assert isinstance(MockTranslationAdapter({}), TranslationPort)
    assert isinstance(MockTextToSpeechAdapter({}), TextToSpeechPort)


@pytest.mark.asyncio
async def test_mock_unknown_request_and_injected_failure_are_content_free() -> None:
    request, _ = translation_pair()
    unknown = MockTranslationAdapter({})
    injected = MockTranslationAdapter(
        {request.context.operation_id: MockLanguageFailure(MockFailureCode.PROVIDER_UNAVAILABLE)}
    )

    with pytest.raises(MockLanguageFailure) as unknown_error:
        await unknown.translate(request)
    assert unknown_error.value.code is MockFailureCode.UNKNOWN_REQUEST
    assert str(unknown_error.value) == "UNKNOWN_REQUEST"

    with pytest.raises(MockLanguageFailure) as injected_error:
        await injected.translate(request)
    assert injected_error.value.code is MockFailureCode.PROVIDER_UNAVAILABLE
    assert "synthetic hello" not in str(injected_error.value)


@pytest.mark.asyncio
async def test_mock_rejects_wrong_result_type_and_stale_cross_request_result() -> None:
    request, result = stt_pair()
    _, translation_result = translation_pair()

    wrong_type = MockSpeechToTextAdapter({request.context.operation_id: translation_result})
    with pytest.raises(MockLanguageFailure, match="MALFORMED_RESULT"):
        await wrong_type.transcribe(request)

    stale = replace(result, source_audio=ref(generation=2))
    stale_adapter = MockSpeechToTextAdapter({request.context.operation_id: stale})
    with pytest.raises(MockLanguageFailure, match="MISMATCHED_RESULT"):
        await stale_adapter.transcribe(request)


@pytest.mark.asyncio
async def test_mock_snapshots_fixture_before_caller_mutation() -> None:
    request, result = stt_pair()
    adapter = MockSpeechToTextAdapter({request.context.operation_id: result})
    object.__setattr__(result, "operation_id", "op_mutated_000000")

    returned = await adapter.transcribe(request)

    assert returned.operation_id == request.context.operation_id


@pytest.mark.asyncio
async def test_mock_revalidates_mutated_request_before_fixture_lookup() -> None:
    request, result = stt_pair()
    adapter = MockSpeechToTextAdapter({request.context.operation_id: result})
    object.__setattr__(request.context, "operation_id", "invalid")

    with pytest.raises(MockLanguageFailure) as caught:
        await adapter.transcribe(request)

    assert caught.value.code is MockFailureCode.MALFORMED_REQUEST


@pytest.mark.asyncio
async def test_mock_performs_no_file_or_network_io(monkeypatch: pytest.MonkeyPatch) -> None:
    request, result = detection_pair()
    adapter = MockLanguageDetectionAdapter({request.context.operation_id: result})

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("I/O is forbidden in deterministic language mocks")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)

    assert await adapter.detect(request) == result
