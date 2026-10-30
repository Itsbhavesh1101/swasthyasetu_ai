from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

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
    LanguageContractError,
    LanguageDetectionRequest,
    LanguageDetectionResult,
    LanguageOutcome,
    OperationContext,
    OperationKind,
    ProcessingStatus,
    ProtectedSpan,
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

NOW = datetime(2026, 10, 30, 10, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64


def context(kind: OperationKind, *, operation_id: str = "op_synthetic_0001") -> OperationContext:
    return OperationContext(
        operation_id=operation_id,
        correlation_id="corr_synthetic_0001",
        operation=kind,
        created_at=NOW,
        deadline_at=NOW + timedelta(seconds=5),
        idempotency_key="idem_aaaaaaaa",
        cancelled=False,
    )


def artifact(*, generation: int = 1, digest: str = HASH_A) -> ArtifactReference:
    return ArtifactReference(
        artifact_id="artifact_synthetic_0001",
        artifact_version="v1",
        generation=generation,
        content_hash=digest,
    )


def text_artifact(text: str = "synthetic hello") -> TextArtifact:
    return TextArtifact(reference=artifact(), text=text)


def provenance(kind: OperationKind) -> ProviderProvenance:
    return ProviderProvenance(
        operation=kind,
        provider_id="synthetic.provider",
        adapter_version="v1",
        model_id="synthetic.model",
        model_revision="rev-1",
        model_artifact_hash=HASH_B,
        created_at=NOW,
    )


def unknown_quality() -> QualityEvidence:
    return QualityEvidence(kind=QualityKind.UNKNOWN, value=None)


def candidate() -> LanguageCandidate:
    return LanguageCandidate(
        language="en",
        script="Latn",
        outcome=LanguageOutcome.KNOWN,
        rank=1,
        quality=unknown_quality(),
    )


def stt_request() -> SpeechToTextRequest:
    return SpeechToTextRequest(
        contract_version=SPEECH_TO_TEXT_REQUEST_VERSION,
        context=context(OperationKind.SPEECH_TO_TEXT),
        source_audio=artifact(),
        declared_media_format="audio/synthetic",
        language_hints=(candidate(),),
        request_word_alignment=False,
    )


def stt_result(request: SpeechToTextRequest | None = None) -> SpeechToTextResult:
    request = request or stt_request()
    return SpeechToTextResult(
        contract_version=SPEECH_TO_TEXT_RESULT_VERSION,
        operation_id=request.context.operation_id,
        request_contract_version=request.contract_version,
        source_audio=request.source_audio,
        status=ProcessingStatus.SUCCEEDED,
        finality=ResultFinality.FINAL,
        original_transcript="synthetic hello",
        segments=(
            SpeechSegment(
                start_ms=0,
                end_ms=500,
                text="synthetic hello",
                candidates=(candidate(),),
                quality=unknown_quality(),
            ),
        ),
        detected_languages=(candidate(),),
        warnings=(),
        provenance=provenance(OperationKind.SPEECH_TO_TEXT),
        quality=unknown_quality(),
    )


def test_operation_context_normalizes_aware_time_to_utc_and_is_immutable() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    value = OperationContext(
        operation_id="op_synthetic_0001",
        correlation_id="corr_synthetic_0001",
        operation=OperationKind.TRANSLATION,
        created_at=NOW.astimezone(offset),
        deadline_at=(NOW + timedelta(seconds=5)).astimezone(offset),
        idempotency_key="idem_aaaaaaaa",
        cancelled=False,
    )

    assert value.created_at == NOW
    assert value.created_at.tzinfo is UTC
    assert value.deadline_at.tzinfo is UTC
    with pytest.raises(FrozenInstanceError):
        value.cancelled = True  # type: ignore[misc]


@pytest.mark.parametrize(
    ("created_at", "deadline_at"),
    [
        (datetime(2026, 10, 30, 10, 0), NOW + timedelta(seconds=5)),
        (NOW, datetime(2026, 10, 30, 10, 0, 5)),
        (NOW, NOW),
        (NOW, NOW - timedelta(microseconds=1)),
    ],
)
def test_operation_context_rejects_naive_or_nonpositive_deadlines(
    created_at: datetime, deadline_at: datetime
) -> None:
    with pytest.raises(LanguageContractError):
        OperationContext(
            operation_id="op_synthetic_0001",
            correlation_id="corr_synthetic_0001",
            operation=OperationKind.TRANSLATION,
            created_at=created_at,
            deadline_at=deadline_at,
            idempotency_key="idem_aaaaaaaa",
            cancelled=False,
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"artifact_id": "https://example.invalid/audio"},
        {"artifact_version": ""},
        {"generation": 0},
        {"generation": True},
        {"content_hash": "not-a-hash"},
    ],
)
def test_artifact_reference_rejects_authority_bearing_or_malformed_values(
    changes: dict[str, Any],
) -> None:
    values: dict[str, Any] = {
        "artifact_id": "artifact_synthetic_0001",
        "artifact_version": "v1",
        "generation": 1,
        "content_hash": HASH_A,
    }
    values.update(changes)
    with pytest.raises(LanguageContractError):
        ArtifactReference(**values)


def test_quality_requires_explicit_semantics_and_never_fabricates_confidence() -> None:
    assert unknown_quality().value is None
    assert QualityEvidence(kind=QualityKind.PROVIDER_CONFIDENCE, value=0.75).value == 0.75

    with pytest.raises(LanguageContractError):
        QualityEvidence(kind=QualityKind.UNKNOWN, value=0.5)
    with pytest.raises(LanguageContractError):
        QualityEvidence(kind=QualityKind.PROVIDER_CONFIDENCE, value=None)
    with pytest.raises(LanguageContractError):
        QualityEvidence(kind=QualityKind.PROVIDER_CONFIDENCE, value=float("nan"))
    with pytest.raises(LanguageContractError):
        QualityEvidence(kind=QualityKind.PROVIDER_CONFIDENCE, value=1.01)


def test_language_candidate_keeps_language_script_and_uncertainty_distinct() -> None:
    mixed = LanguageCandidate(
        language="und",
        script="Zyyy",
        outcome=LanguageOutcome.MIXED,
        rank=1,
        quality=unknown_quality(),
    )

    assert mixed.language == "und"
    assert mixed.script == "Zyyy"
    assert mixed.outcome is LanguageOutcome.MIXED

    with pytest.raises(LanguageContractError):
        replace(mixed, language="English")
    with pytest.raises(LanguageContractError):
        replace(mixed, script="Latin")
    with pytest.raises(LanguageContractError):
        replace(mixed, rank=0)


def test_speech_to_text_contract_preserves_original_segments_and_lineage() -> None:
    request = stt_request()
    result = stt_result(request)

    result.assert_matches(request)
    assert result.original_transcript == "synthetic hello"
    assert result.segments[0].text == "synthetic hello"
    assert result.source_audio == request.source_audio
    assert result.provenance.operation is OperationKind.SPEECH_TO_TEXT

    with pytest.raises(LanguageContractError):
        replace(request, declared_media_format="application/json")


@pytest.mark.parametrize(
    "changes",
    [
        {"status": ProcessingStatus.PARTIAL, "finality": ResultFinality.FINAL},
        {"status": ProcessingStatus.SUCCEEDED, "finality": ResultFinality.PARTIAL},
        {
            "status": ProcessingStatus.ABSTAINED,
            "original_transcript": "invented",
            "segments": (),
        },
        {"status": ProcessingStatus.SUCCEEDED, "original_transcript": "", "segments": ()},
    ],
)
def test_speech_to_text_result_enforces_status_finality_and_content(
    changes: dict[str, Any],
) -> None:
    values = (
        stt_result().__dict__
        if hasattr(stt_result(), "__dict__")
        else {field: getattr(stt_result(), field) for field in stt_result().__dataclass_fields__}
    )
    values.update(changes)
    with pytest.raises(LanguageContractError):
        SpeechToTextResult(**values)


def test_speech_to_text_result_rejects_stale_generation_and_request_version() -> None:
    request = stt_request()

    with pytest.raises(LanguageContractError):
        replace(stt_result(request), source_audio=artifact(generation=2)).assert_matches(request)
    with pytest.raises(LanguageContractError):
        replace(stt_result(request), request_contract_version="speech-to-text-request.v0")


def test_language_detection_preserves_source_and_can_abstain() -> None:
    request = LanguageDetectionRequest(
        contract_version=LANGUAGE_DETECTION_REQUEST_VERSION,
        context=context(OperationKind.LANGUAGE_DETECTION),
        source_text=text_artifact("123"),
    )
    result = LanguageDetectionResult(
        contract_version=LANGUAGE_DETECTION_RESULT_VERSION,
        operation_id=request.context.operation_id,
        request_contract_version=request.contract_version,
        source_text=request.source_text,
        status=ProcessingStatus.ABSTAINED,
        candidates=(),
        warnings=("INSUFFICIENT_SIGNAL",),
        provenance=provenance(OperationKind.LANGUAGE_DETECTION),
    )

    result.assert_matches(request)
    assert result.source_text.text == "123"
    with pytest.raises(LanguageContractError):
        replace(result, status=ProcessingStatus.PARTIAL)


def test_transliteration_preserves_source_and_protected_spans() -> None:
    protected = ProtectedSpan(start=0, end=3, label="NUMBER")
    request = TransliterationRequest(
        contract_version=TRANSLITERATION_REQUEST_VERSION,
        context=context(OperationKind.TRANSLITERATION),
        source_text=text_artifact("123 namaste"),
        source_script="Latn",
        target_script="Deva",
        protected_spans=(protected,),
    )
    result = TransliterationResult(
        contract_version=TRANSLITERATION_RESULT_VERSION,
        operation_id=request.context.operation_id,
        request_contract_version=request.contract_version,
        source_text=request.source_text,
        output_text="123 नमस्ते",
        source_script=request.source_script,
        target_script=request.target_script,
        protected_spans=request.protected_spans,
        status=ProcessingStatus.SUCCEEDED,
        warnings=(),
        provenance=provenance(OperationKind.TRANSLITERATION),
        quality=unknown_quality(),
    )

    result.assert_matches(request)
    assert result.output_text.startswith("123")
    with pytest.raises(LanguageContractError):
        replace(result, protected_spans=()).assert_matches(request)
    with pytest.raises(LanguageContractError):
        replace(result, target_script=result.source_script)
    with pytest.raises(LanguageContractError):
        replace(result, status=ProcessingStatus.PARTIAL, output_text="")


def test_translation_preserves_source_and_exact_language_pair() -> None:
    request = TranslationRequest(
        contract_version=TRANSLATION_REQUEST_VERSION,
        context=context(OperationKind.TRANSLATION),
        source_text=text_artifact(),
        source_language="en",
        target_language="hi",
    )
    result = TranslationResult(
        contract_version=TRANSLATION_RESULT_VERSION,
        operation_id=request.context.operation_id,
        request_contract_version=request.contract_version,
        source_text=request.source_text,
        translated_text="सिंथेटिक नमस्ते",
        source_language="en",
        target_language="hi",
        status=ProcessingStatus.SUCCEEDED,
        warnings=(),
        provenance=provenance(OperationKind.TRANSLATION),
        quality=unknown_quality(),
    )

    result.assert_matches(request)
    with pytest.raises(LanguageContractError):
        replace(result, target_language="en").assert_matches(request)
    with pytest.raises(LanguageContractError):
        replace(result, target_language=result.source_language)
    with pytest.raises(LanguageContractError):
        replace(result, status=ProcessingStatus.PARTIAL, translated_text="")


def test_text_to_speech_uses_versioned_text_and_voice_identity_without_reference_audio() -> None:
    request = TextToSpeechRequest(
        contract_version=TEXT_TO_SPEECH_REQUEST_VERSION,
        context=context(OperationKind.TEXT_TO_SPEECH),
        source_text=text_artifact(),
        language="en",
        voice_profile_id="synthetic.voice",
        voice_profile_version="v1",
    )
    result = TextToSpeechResult(
        contract_version=TEXT_TO_SPEECH_RESULT_VERSION,
        operation_id=request.context.operation_id,
        request_contract_version=request.contract_version,
        source_text=request.source_text.reference,
        generated_audio=artifact(generation=2, digest=HASH_B),
        language="en",
        voice_profile_id="synthetic.voice",
        voice_profile_version="v1",
        declared_media_format="audio/synthetic",
        status=ProcessingStatus.SUCCEEDED,
        warnings=(),
        provenance=provenance(OperationKind.TEXT_TO_SPEECH),
    )

    result.assert_matches(request)
    assert result.generated_audio != request.source_text.reference
    with pytest.raises(LanguageContractError):
        replace(result, declared_media_format="application/octet-stream")
    with pytest.raises(LanguageContractError):
        replace(result, status=ProcessingStatus.PARTIAL, generated_audio=None)
    with pytest.raises(TypeError):
        cast(Any, TextToSpeechRequest)(
            contract_version=TEXT_TO_SPEECH_REQUEST_VERSION,
            context=context(OperationKind.TEXT_TO_SPEECH),
            source_text=text_artifact(),
            language="en",
            voice_profile_id="synthetic.voice",
            voice_profile_version="v1",
            reference_audio=artifact(),
        )


@pytest.mark.parametrize(
    "builder",
    [
        lambda: TextArtifact(reference=artifact(), text="x" * 4097),
        lambda: SpeechSegment(
            start_ms=10,
            end_ms=5,
            text="synthetic",
            candidates=(candidate(),),
            quality=unknown_quality(),
        ),
        lambda: ProtectedSpan(start=0, end=5000, label="NUMBER"),
        lambda: ProviderProvenance(
            operation=OperationKind.TRANSLATION,
            provider_id="https://provider.invalid",
            adapter_version="v1",
            model_id="synthetic.model",
            model_revision="rev-1",
            model_artifact_hash=HASH_B,
            created_at=NOW,
        ),
    ],
)
def test_contracts_reject_unbounded_or_authority_bearing_values(builder: Any) -> None:
    with pytest.raises(LanguageContractError):
        builder()
