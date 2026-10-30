"""Strict synthetic-only contracts for replaceable language and speech providers."""

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

SPEECH_TO_TEXT_REQUEST_VERSION: Final = "speech-to-text-request.v1"
SPEECH_TO_TEXT_RESULT_VERSION: Final = "speech-to-text-result.v1"
LANGUAGE_DETECTION_REQUEST_VERSION: Final = "language-detection-request.v1"
LANGUAGE_DETECTION_RESULT_VERSION: Final = "language-detection-result.v1"
TRANSLITERATION_REQUEST_VERSION: Final = "transliteration-request.v1"
TRANSLITERATION_RESULT_VERSION: Final = "transliteration-result.v1"
TRANSLATION_REQUEST_VERSION: Final = "translation-request.v1"
TRANSLATION_RESULT_VERSION: Final = "translation-result.v1"
TEXT_TO_SPEECH_REQUEST_VERSION: Final = "text-to-speech-request.v1"
TEXT_TO_SPEECH_RESULT_VERSION: Final = "text-to-speech-result.v1"

MAX_TEXT_LENGTH: Final = 4_096
MAX_COLLECTION_ITEMS: Final = 64
MAX_WARNING_ITEMS: Final = 16

_OPAQUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_OPERATION_ID = re.compile(r"^op_[A-Za-z0-9_-]{8,64}$")
_CORRELATION_ID = re.compile(r"^corr_[A-Za-z0-9_-]{8,64}$")
_IDEMPOTENCY_KEY = re.compile(r"^idem_[A-Za-z0-9_-]{8,64}$")
_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_MACHINE_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")
_LANGUAGE = re.compile(r"^(?:[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*|und)$")
_SCRIPT = re.compile(r"^[A-Z][a-z]{3}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_MEDIA_FORMAT = re.compile(r"^[a-z][a-z0-9.+-]{0,31}/[a-z0-9.+-]{1,63}$")
_MACHINE_CODE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


class LanguageContractError(ValueError):
    """Raised when synthetic language boundary data is malformed or unsafe."""


class OperationKind(StrEnum):
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"
    LANGUAGE_DETECTION = "LANGUAGE_DETECTION"
    TRANSLITERATION = "TRANSLITERATION"
    TRANSLATION = "TRANSLATION"
    TEXT_TO_SPEECH = "TEXT_TO_SPEECH"


class ProcessingStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    PARTIAL = "PARTIAL"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    ABSTAINED = "ABSTAINED"
    FAILED = "FAILED"


class ResultFinality(StrEnum):
    PARTIAL = "PARTIAL"
    FINAL = "FINAL"


class LanguageOutcome(StrEnum):
    KNOWN = "KNOWN"
    MIXED = "MIXED"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"


class QualityKind(StrEnum):
    UNKNOWN = "UNKNOWN"
    PROVIDER_CONFIDENCE = "PROVIDER_CONFIDENCE"
    PROVIDER_SCORE = "PROVIDER_SCORE"


class ProviderAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class VerificationState(StrEnum):
    UNVERIFIED = "UNVERIFIED"


def _error(message: str) -> LanguageContractError:
    return LanguageContractError(message)


def _string(value: object, *, name: str, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise _error(f"{name} has an invalid machine-readable value")
    return value


def _text(value: object, *, name: str, allow_empty: bool = False) -> str:
    if type(value) is not str or len(value) > MAX_TEXT_LENGTH:
        raise _error(f"{name} must be bounded text")
    if not allow_empty and (not value or value != value.strip()):
        raise _error(f"{name} must be non-empty and trimmed")
    return value


def _utc(value: object, *, name: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _warnings(value: object) -> tuple[str, ...]:
    if type(value) is not tuple or len(value) > MAX_WARNING_ITEMS:
        raise _error("warnings must be a bounded tuple")
    for warning in value:
        _string(warning, name="warning", pattern=_MACHINE_CODE)
    if len(set(value)) != len(value):
        raise _error("warnings must be unique")
    return value


def _enum(value: object, expected: type[StrEnum], *, name: str) -> None:
    if type(value) is not expected:
        raise _error(f"{name} has an invalid enum value")


@dataclass(frozen=True, slots=True)
class OperationContext:
    operation_id: str
    correlation_id: str
    operation: OperationKind
    created_at: datetime
    deadline_at: datetime
    idempotency_key: str
    cancelled: bool

    def __post_init__(self) -> None:
        _string(self.operation_id, name="operation_id", pattern=_OPERATION_ID)
        _string(self.correlation_id, name="correlation_id", pattern=_CORRELATION_ID)
        _enum(self.operation, OperationKind, name="operation")
        _string(self.idempotency_key, name="idempotency_key", pattern=_IDEMPOTENCY_KEY)
        if type(self.cancelled) is not bool:
            raise _error("cancelled must be a boolean")
        created = _utc(self.created_at, name="created_at")
        deadline = _utc(self.deadline_at, name="deadline_at")
        if deadline <= created:
            raise _error("deadline_at must be after created_at")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "deadline_at", deadline)


def _context(value: object, operation: OperationKind) -> OperationContext:
    if type(value) is not OperationContext:
        raise _error("context has an invalid type")
    snapshot = OperationContext(
        operation_id=value.operation_id,
        correlation_id=value.correlation_id,
        operation=value.operation,
        created_at=value.created_at,
        deadline_at=value.deadline_at,
        idempotency_key=value.idempotency_key,
        cancelled=value.cancelled,
    )
    if snapshot.operation is not operation:
        raise _error("context operation does not match the contract")
    return snapshot


@dataclass(frozen=True, slots=True)
class ArtifactReference:
    artifact_id: str
    artifact_version: str
    generation: int
    content_hash: str

    def __post_init__(self) -> None:
        _string(self.artifact_id, name="artifact_id", pattern=_OPAQUE_ID)
        if "://" in self.artifact_id:
            raise _error("artifact_id must not be a URL")
        _string(self.artifact_version, name="artifact_version", pattern=_VERSION)
        if type(self.generation) is not int or self.generation < 1:
            raise _error("generation must be a positive integer")
        _string(self.content_hash, name="content_hash", pattern=_SHA256)


def _artifact(value: object, *, name: str) -> ArtifactReference:
    if type(value) is not ArtifactReference:
        raise _error(f"{name} has an invalid type")
    return ArtifactReference(
        artifact_id=value.artifact_id,
        artifact_version=value.artifact_version,
        generation=value.generation,
        content_hash=value.content_hash,
    )


@dataclass(frozen=True, slots=True)
class TextArtifact:
    reference: ArtifactReference
    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference", _artifact(self.reference, name="text reference"))
        _text(self.text, name="text")


def _text_artifact(value: object) -> TextArtifact:
    if type(value) is not TextArtifact:
        raise _error("source_text has an invalid type")
    return TextArtifact(reference=value.reference, text=value.text)


@dataclass(frozen=True, slots=True)
class QualityEvidence:
    kind: QualityKind
    value: float | None

    def __post_init__(self) -> None:
        _enum(self.kind, QualityKind, name="quality kind")
        if self.kind is QualityKind.UNKNOWN:
            if self.value is not None:
                raise _error("unknown quality cannot contain a numeric value")
            return
        if (
            isinstance(self.value, bool)
            or not isinstance(self.value, (int, float))
            or not math.isfinite(self.value)
            or not 0 <= self.value <= 1
        ):
            raise _error("provider quality must be a finite value from zero to one")
        object.__setattr__(self, "value", float(self.value))


def _quality(value: object) -> QualityEvidence:
    if type(value) is not QualityEvidence:
        raise _error("quality has an invalid type")
    return QualityEvidence(kind=value.kind, value=value.value)


@dataclass(frozen=True, slots=True)
class LanguageCandidate:
    language: str
    script: str
    outcome: LanguageOutcome
    rank: int
    quality: QualityEvidence

    def __post_init__(self) -> None:
        _string(self.language, name="language", pattern=_LANGUAGE)
        _string(self.script, name="script", pattern=_SCRIPT)
        _enum(self.outcome, LanguageOutcome, name="language outcome")
        if type(self.rank) is not int or not 1 <= self.rank <= MAX_COLLECTION_ITEMS:
            raise _error("rank must be a bounded positive integer")
        object.__setattr__(self, "quality", _quality(self.quality))


def _candidate(value: object) -> LanguageCandidate:
    if type(value) is not LanguageCandidate:
        raise _error("language candidate has an invalid type")
    return LanguageCandidate(
        language=value.language,
        script=value.script,
        outcome=value.outcome,
        rank=value.rank,
        quality=value.quality,
    )


def _candidates(value: object) -> tuple[LanguageCandidate, ...]:
    if type(value) is not tuple or len(value) > MAX_COLLECTION_ITEMS:
        raise _error("language candidates must be a bounded tuple")
    snapshots = tuple(_candidate(item) for item in value)
    ranks = tuple(item.rank for item in snapshots)
    if len(set(ranks)) != len(ranks):
        raise _error("language candidate ranks must be unique")
    return snapshots


@dataclass(frozen=True, slots=True)
class ProtectedSpan:
    start: int
    end: int
    label: str

    def __post_init__(self) -> None:
        if (
            type(self.start) is not int
            or type(self.end) is not int
            or self.start < 0
            or self.end <= self.start
            or self.end > MAX_TEXT_LENGTH
        ):
            raise _error("protected span bounds are invalid")
        _string(self.label, name="protected span label", pattern=_MACHINE_CODE)


def _protected_spans(value: object, *, text: str) -> tuple[ProtectedSpan, ...]:
    if type(value) is not tuple or len(value) > MAX_COLLECTION_ITEMS:
        raise _error("protected spans must be a bounded tuple")
    snapshots = tuple(ProtectedSpan(item.start, item.end, item.label) for item in value)
    previous_end = 0
    for span in snapshots:
        if span.end > len(text) or span.start < previous_end:
            raise _error("protected spans must be ordered, non-overlapping, and within source text")
        previous_end = span.end
    return snapshots


@dataclass(frozen=True, slots=True)
class ProviderProvenance:
    operation: OperationKind
    provider_id: str
    adapter_version: str
    model_id: str
    model_revision: str
    model_artifact_hash: str
    created_at: datetime
    authority: ProviderAuthority = ProviderAuthority.ENGINEERING_ONLY
    verification: VerificationState = VerificationState.UNVERIFIED

    def __post_init__(self) -> None:
        _enum(self.operation, OperationKind, name="provenance operation")
        _string(self.provider_id, name="provider_id", pattern=_MACHINE_ID)
        _string(self.adapter_version, name="adapter_version", pattern=_VERSION)
        _string(self.model_id, name="model_id", pattern=_MACHINE_ID)
        _string(self.model_revision, name="model_revision", pattern=_VERSION)
        _string(self.model_artifact_hash, name="model_artifact_hash", pattern=_SHA256)
        _enum(self.authority, ProviderAuthority, name="provider authority")
        _enum(self.verification, VerificationState, name="verification")
        object.__setattr__(self, "created_at", _utc(self.created_at, name="created_at"))


def _provenance(value: object, operation: OperationKind) -> ProviderProvenance:
    if type(value) is not ProviderProvenance:
        raise _error("provenance has an invalid type")
    snapshot = ProviderProvenance(
        operation=value.operation,
        provider_id=value.provider_id,
        adapter_version=value.adapter_version,
        model_id=value.model_id,
        model_revision=value.model_revision,
        model_artifact_hash=value.model_artifact_hash,
        created_at=value.created_at,
        authority=value.authority,
        verification=value.verification,
    )
    if snapshot.operation is not operation:
        raise _error("provenance operation does not match the contract")
    return snapshot


@dataclass(frozen=True, slots=True)
class SpeechSegment:
    start_ms: int
    end_ms: int
    text: str
    candidates: tuple[LanguageCandidate, ...]
    quality: QualityEvidence

    def __post_init__(self) -> None:
        if (
            type(self.start_ms) is not int
            or type(self.end_ms) is not int
            or self.start_ms < 0
            or self.end_ms <= self.start_ms
        ):
            raise _error("speech segment timing is invalid")
        _text(self.text, name="segment text")
        object.__setattr__(self, "candidates", _candidates(self.candidates))
        object.__setattr__(self, "quality", _quality(self.quality))


def _segments(value: object) -> tuple[SpeechSegment, ...]:
    if type(value) is not tuple or len(value) > MAX_COLLECTION_ITEMS:
        raise _error("segments must be a bounded tuple")
    snapshots = tuple(
        SpeechSegment(item.start_ms, item.end_ms, item.text, item.candidates, item.quality)
        for item in value
    )
    previous_end = 0
    for segment in snapshots:
        if segment.start_ms < previous_end:
            raise _error("segments must be ordered and non-overlapping")
        previous_end = segment.end_ms
    return snapshots


def _request_header(
    contract_version: object,
    expected_version: str,
    context: object,
    operation: OperationKind,
) -> OperationContext:
    if contract_version != expected_version:
        raise _error("request contract version is invalid")
    return _context(context, operation)


def _result_header(
    contract_version: object,
    expected_version: str,
    operation_id: object,
    request_contract_version: object,
    expected_request_version: str,
) -> None:
    if contract_version != expected_version or request_contract_version != expected_request_version:
        raise _error("result contract version is invalid")
    _string(operation_id, name="operation_id", pattern=_OPERATION_ID)


def _status(value: object) -> ProcessingStatus:
    _enum(value, ProcessingStatus, name="processing status")
    return value  # type: ignore[return-value]


def _batch_status(value: object) -> ProcessingStatus:
    status = _status(value)
    if status is ProcessingStatus.PARTIAL:
        raise _error("partial status is reserved for speech recognition results")
    return status


def _audio_media_format(value: object) -> str:
    media_format = _string(value, name="declared_media_format", pattern=_MEDIA_FORMAT)
    if not media_format.startswith("audio/"):
        raise _error("declared_media_format must identify audio")
    return media_format


def _finality(value: object) -> ResultFinality:
    _enum(value, ResultFinality, name="result finality")
    return value  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class SpeechToTextRequest:
    contract_version: str
    context: OperationContext
    source_audio: ArtifactReference
    declared_media_format: str
    language_hints: tuple[LanguageCandidate, ...]
    request_word_alignment: bool

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "context",
            _request_header(
                self.contract_version,
                SPEECH_TO_TEXT_REQUEST_VERSION,
                self.context,
                OperationKind.SPEECH_TO_TEXT,
            ),
        )
        object.__setattr__(self, "source_audio", _artifact(self.source_audio, name="source_audio"))
        _audio_media_format(self.declared_media_format)
        object.__setattr__(self, "language_hints", _candidates(self.language_hints))
        if type(self.request_word_alignment) is not bool:
            raise _error("request_word_alignment must be a boolean")


@dataclass(frozen=True, slots=True)
class SpeechToTextResult:
    contract_version: str
    operation_id: str
    request_contract_version: str
    source_audio: ArtifactReference
    status: ProcessingStatus
    finality: ResultFinality
    original_transcript: str
    segments: tuple[SpeechSegment, ...]
    detected_languages: tuple[LanguageCandidate, ...]
    warnings: tuple[str, ...]
    provenance: ProviderProvenance
    quality: QualityEvidence

    def __post_init__(self) -> None:
        _result_header(
            self.contract_version,
            SPEECH_TO_TEXT_RESULT_VERSION,
            self.operation_id,
            self.request_contract_version,
            SPEECH_TO_TEXT_REQUEST_VERSION,
        )
        object.__setattr__(self, "source_audio", _artifact(self.source_audio, name="source_audio"))
        status = _status(self.status)
        finality = _finality(self.finality)
        _text(self.original_transcript, name="original_transcript", allow_empty=True)
        object.__setattr__(self, "segments", _segments(self.segments))
        object.__setattr__(self, "detected_languages", _candidates(self.detected_languages))
        object.__setattr__(self, "warnings", _warnings(self.warnings))
        object.__setattr__(
            self, "provenance", _provenance(self.provenance, OperationKind.SPEECH_TO_TEXT)
        )
        object.__setattr__(self, "quality", _quality(self.quality))
        if (status is ProcessingStatus.PARTIAL) != (finality is ResultFinality.PARTIAL):
            raise _error("only partial status may carry partial finality")
        has_content = bool(self.original_transcript and self.segments)
        if status in {
            ProcessingStatus.SUCCEEDED,
            ProcessingStatus.PARTIAL,
            ProcessingStatus.LOW_CONFIDENCE,
        }:
            if not has_content:
                raise _error("content-bearing status requires transcript and segments")
        elif self.original_transcript or self.segments or self.detected_languages:
            raise _error("abstained or failed result cannot contain derived speech content")

    def assert_matches(self, request: SpeechToTextRequest) -> None:
        validated = SpeechToTextRequest(
            request.contract_version,
            request.context,
            request.source_audio,
            request.declared_media_format,
            request.language_hints,
            request.request_word_alignment,
        )
        if (
            self.operation_id != validated.context.operation_id
            or self.source_audio != validated.source_audio
        ):
            raise _error("speech result does not match its request")


@dataclass(frozen=True, slots=True)
class LanguageDetectionRequest:
    contract_version: str
    context: OperationContext
    source_text: TextArtifact

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "context",
            _request_header(
                self.contract_version,
                LANGUAGE_DETECTION_REQUEST_VERSION,
                self.context,
                OperationKind.LANGUAGE_DETECTION,
            ),
        )
        object.__setattr__(self, "source_text", _text_artifact(self.source_text))


@dataclass(frozen=True, slots=True)
class LanguageDetectionResult:
    contract_version: str
    operation_id: str
    request_contract_version: str
    source_text: TextArtifact
    status: ProcessingStatus
    candidates: tuple[LanguageCandidate, ...]
    warnings: tuple[str, ...]
    provenance: ProviderProvenance

    def __post_init__(self) -> None:
        _result_header(
            self.contract_version,
            LANGUAGE_DETECTION_RESULT_VERSION,
            self.operation_id,
            self.request_contract_version,
            LANGUAGE_DETECTION_REQUEST_VERSION,
        )
        object.__setattr__(self, "source_text", _text_artifact(self.source_text))
        status = _batch_status(self.status)
        object.__setattr__(self, "candidates", _candidates(self.candidates))
        object.__setattr__(self, "warnings", _warnings(self.warnings))
        object.__setattr__(
            self, "provenance", _provenance(self.provenance, OperationKind.LANGUAGE_DETECTION)
        )
        if status is ProcessingStatus.SUCCEEDED and not self.candidates:
            raise _error("successful language detection requires candidates")
        if status in {ProcessingStatus.ABSTAINED, ProcessingStatus.FAILED} and self.candidates:
            raise _error("abstained or failed language detection cannot contain candidates")

    def assert_matches(self, request: LanguageDetectionRequest) -> None:
        validated = LanguageDetectionRequest(
            request.contract_version, request.context, request.source_text
        )
        if (
            self.operation_id != validated.context.operation_id
            or self.source_text != validated.source_text
        ):
            raise _error("language detection result does not match its request")


@dataclass(frozen=True, slots=True)
class TransliterationRequest:
    contract_version: str
    context: OperationContext
    source_text: TextArtifact
    source_script: str
    target_script: str
    protected_spans: tuple[ProtectedSpan, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "context",
            _request_header(
                self.contract_version,
                TRANSLITERATION_REQUEST_VERSION,
                self.context,
                OperationKind.TRANSLITERATION,
            ),
        )
        source = _text_artifact(self.source_text)
        object.__setattr__(self, "source_text", source)
        _string(self.source_script, name="source_script", pattern=_SCRIPT)
        _string(self.target_script, name="target_script", pattern=_SCRIPT)
        if self.source_script == self.target_script:
            raise _error("transliteration scripts must differ")
        object.__setattr__(
            self, "protected_spans", _protected_spans(self.protected_spans, text=source.text)
        )


@dataclass(frozen=True, slots=True)
class TransliterationResult:
    contract_version: str
    operation_id: str
    request_contract_version: str
    source_text: TextArtifact
    output_text: str
    source_script: str
    target_script: str
    protected_spans: tuple[ProtectedSpan, ...]
    status: ProcessingStatus
    warnings: tuple[str, ...]
    provenance: ProviderProvenance
    quality: QualityEvidence

    def __post_init__(self) -> None:
        _result_header(
            self.contract_version,
            TRANSLITERATION_RESULT_VERSION,
            self.operation_id,
            self.request_contract_version,
            TRANSLITERATION_REQUEST_VERSION,
        )
        source = _text_artifact(self.source_text)
        object.__setattr__(self, "source_text", source)
        status = _batch_status(self.status)
        _text(self.output_text, name="output_text", allow_empty=True)
        _string(self.source_script, name="source_script", pattern=_SCRIPT)
        _string(self.target_script, name="target_script", pattern=_SCRIPT)
        if self.source_script == self.target_script:
            raise _error("transliteration scripts must differ")
        object.__setattr__(
            self, "protected_spans", _protected_spans(self.protected_spans, text=source.text)
        )
        object.__setattr__(self, "warnings", _warnings(self.warnings))
        object.__setattr__(
            self, "provenance", _provenance(self.provenance, OperationKind.TRANSLITERATION)
        )
        object.__setattr__(self, "quality", _quality(self.quality))
        if status in {ProcessingStatus.SUCCEEDED, ProcessingStatus.LOW_CONFIDENCE}:
            if not self.output_text:
                raise _error("successful transliteration requires output")
        elif self.output_text:
            raise _error("non-successful transliteration cannot contain output")

    def assert_matches(self, request: TransliterationRequest) -> None:
        validated = TransliterationRequest(
            request.contract_version,
            request.context,
            request.source_text,
            request.source_script,
            request.target_script,
            request.protected_spans,
        )
        if (
            self.operation_id != validated.context.operation_id
            or self.source_text != validated.source_text
            or self.source_script != validated.source_script
            or self.target_script != validated.target_script
            or self.protected_spans != validated.protected_spans
        ):
            raise _error("transliteration result does not match its request")


@dataclass(frozen=True, slots=True)
class TranslationRequest:
    contract_version: str
    context: OperationContext
    source_text: TextArtifact
    source_language: str
    target_language: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "context",
            _request_header(
                self.contract_version,
                TRANSLATION_REQUEST_VERSION,
                self.context,
                OperationKind.TRANSLATION,
            ),
        )
        object.__setattr__(self, "source_text", _text_artifact(self.source_text))
        _string(self.source_language, name="source_language", pattern=_LANGUAGE)
        _string(self.target_language, name="target_language", pattern=_LANGUAGE)
        if self.source_language == self.target_language:
            raise _error("translation languages must differ")


@dataclass(frozen=True, slots=True)
class TranslationResult:
    contract_version: str
    operation_id: str
    request_contract_version: str
    source_text: TextArtifact
    translated_text: str
    source_language: str
    target_language: str
    status: ProcessingStatus
    warnings: tuple[str, ...]
    provenance: ProviderProvenance
    quality: QualityEvidence

    def __post_init__(self) -> None:
        _result_header(
            self.contract_version,
            TRANSLATION_RESULT_VERSION,
            self.operation_id,
            self.request_contract_version,
            TRANSLATION_REQUEST_VERSION,
        )
        object.__setattr__(self, "source_text", _text_artifact(self.source_text))
        status = _batch_status(self.status)
        _text(self.translated_text, name="translated_text", allow_empty=True)
        _string(self.source_language, name="source_language", pattern=_LANGUAGE)
        _string(self.target_language, name="target_language", pattern=_LANGUAGE)
        if self.source_language == self.target_language:
            raise _error("translation languages must differ")
        object.__setattr__(self, "warnings", _warnings(self.warnings))
        object.__setattr__(
            self, "provenance", _provenance(self.provenance, OperationKind.TRANSLATION)
        )
        object.__setattr__(self, "quality", _quality(self.quality))
        if status in {ProcessingStatus.SUCCEEDED, ProcessingStatus.LOW_CONFIDENCE}:
            if not self.translated_text:
                raise _error("successful translation requires output")
        elif self.translated_text:
            raise _error("non-successful translation cannot contain output")

    def assert_matches(self, request: TranslationRequest) -> None:
        validated = TranslationRequest(
            request.contract_version,
            request.context,
            request.source_text,
            request.source_language,
            request.target_language,
        )
        if (
            self.operation_id != validated.context.operation_id
            or self.source_text != validated.source_text
            or self.source_language != validated.source_language
            or self.target_language != validated.target_language
        ):
            raise _error("translation result does not match its request")


@dataclass(frozen=True, slots=True)
class TextToSpeechRequest:
    contract_version: str
    context: OperationContext
    source_text: TextArtifact
    language: str
    voice_profile_id: str
    voice_profile_version: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "context",
            _request_header(
                self.contract_version,
                TEXT_TO_SPEECH_REQUEST_VERSION,
                self.context,
                OperationKind.TEXT_TO_SPEECH,
            ),
        )
        object.__setattr__(self, "source_text", _text_artifact(self.source_text))
        _string(self.language, name="language", pattern=_LANGUAGE)
        _string(self.voice_profile_id, name="voice_profile_id", pattern=_MACHINE_ID)
        _string(self.voice_profile_version, name="voice_profile_version", pattern=_VERSION)


@dataclass(frozen=True, slots=True)
class TextToSpeechResult:
    contract_version: str
    operation_id: str
    request_contract_version: str
    source_text: ArtifactReference
    generated_audio: ArtifactReference | None
    language: str
    voice_profile_id: str
    voice_profile_version: str
    declared_media_format: str
    status: ProcessingStatus
    warnings: tuple[str, ...]
    provenance: ProviderProvenance

    def __post_init__(self) -> None:
        _result_header(
            self.contract_version,
            TEXT_TO_SPEECH_RESULT_VERSION,
            self.operation_id,
            self.request_contract_version,
            TEXT_TO_SPEECH_REQUEST_VERSION,
        )
        object.__setattr__(self, "source_text", _artifact(self.source_text, name="source_text"))
        status = _batch_status(self.status)
        if self.generated_audio is not None:
            object.__setattr__(
                self, "generated_audio", _artifact(self.generated_audio, name="generated_audio")
            )
        _string(self.language, name="language", pattern=_LANGUAGE)
        _string(self.voice_profile_id, name="voice_profile_id", pattern=_MACHINE_ID)
        _string(self.voice_profile_version, name="voice_profile_version", pattern=_VERSION)
        _audio_media_format(self.declared_media_format)
        object.__setattr__(self, "warnings", _warnings(self.warnings))
        object.__setattr__(
            self, "provenance", _provenance(self.provenance, OperationKind.TEXT_TO_SPEECH)
        )
        if status is ProcessingStatus.SUCCEEDED:
            if self.generated_audio is None or self.generated_audio == self.source_text:
                raise _error("successful speech synthesis requires a distinct output artifact")
        elif self.generated_audio is not None:
            raise _error("non-successful speech synthesis cannot contain generated audio")

    def assert_matches(self, request: TextToSpeechRequest) -> None:
        validated = TextToSpeechRequest(
            request.contract_version,
            request.context,
            request.source_text,
            request.language,
            request.voice_profile_id,
            request.voice_profile_version,
        )
        if (
            self.operation_id != validated.context.operation_id
            or self.source_text != validated.source_text.reference
            or self.language != validated.language
            or self.voice_profile_id != validated.voice_profile_id
            or self.voice_profile_version != validated.voice_profile_version
        ):
            raise _error("speech synthesis result does not match its request")
