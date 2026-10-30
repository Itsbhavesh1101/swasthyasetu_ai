"""Exact-mapping, no-I/O mocks for the five independent P12-A ports."""

from collections.abc import Callable, Mapping
from dataclasses import replace
from enum import StrEnum
from types import MappingProxyType

from app.modules.language.contracts import (
    LanguageContractError,
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


class MockFailureCode(StrEnum):
    UNKNOWN_REQUEST = "UNKNOWN_REQUEST"
    CANCELLED = "CANCELLED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    REFUSED = "REFUSED"
    MALFORMED_REQUEST = "MALFORMED_REQUEST"
    MALFORMED_RESULT = "MALFORMED_RESULT"
    MISMATCHED_RESULT = "MISMATCHED_RESULT"


class MockLanguageFailure(RuntimeError):
    """Content-free deterministic test failure."""

    def __init__(self, code: MockFailureCode) -> None:
        self.code = code
        super().__init__(code.value)


type MockOutcome[ResultT] = ResultT | MockLanguageFailure | object


class _FixtureStore[RequestT, ResultT]:
    def __init__(
        self,
        fixtures: Mapping[str, MockOutcome[ResultT]],
        *,
        request_type: type[RequestT],
        result_type: type[ResultT],
        clone_request: Callable[[RequestT], RequestT],
        clone: Callable[[ResultT], ResultT],
        operation_id: Callable[[RequestT], str],
        cancelled: Callable[[RequestT], bool],
        assert_matches: Callable[[ResultT, RequestT], None],
    ) -> None:
        detached: dict[str, MockOutcome[ResultT]] = {}
        for key, outcome in fixtures.items():
            if type(key) is not str:
                raise TypeError("fixture identity must be a string")
            if type(outcome) is result_type:
                detached[key] = clone(outcome)
            elif isinstance(outcome, MockLanguageFailure):
                detached[key] = MockLanguageFailure(outcome.code)
            else:
                detached[key] = outcome
        self._fixtures = MappingProxyType(detached)
        self._request_type = request_type
        self._result_type = result_type
        self._clone_request = clone_request
        self._clone = clone
        self._operation_id = operation_id
        self._cancelled = cancelled
        self._assert_matches = assert_matches

    def resolve(self, request: RequestT) -> ResultT:
        if type(request) is not self._request_type:
            raise MockLanguageFailure(MockFailureCode.MALFORMED_REQUEST)
        try:
            validated_request = self._clone_request(request)
        except (LanguageContractError, TypeError):
            raise MockLanguageFailure(MockFailureCode.MALFORMED_REQUEST) from None
        if self._cancelled(validated_request):
            raise MockLanguageFailure(MockFailureCode.CANCELLED)
        outcome = self._fixtures.get(self._operation_id(validated_request))
        if outcome is None:
            raise MockLanguageFailure(MockFailureCode.UNKNOWN_REQUEST)
        if isinstance(outcome, MockLanguageFailure):
            raise MockLanguageFailure(outcome.code) from None
        if type(outcome) is not self._result_type:
            raise MockLanguageFailure(MockFailureCode.MALFORMED_RESULT)
        try:
            result = self._clone(outcome)
            self._assert_matches(result, validated_request)
        except LanguageContractError:
            raise MockLanguageFailure(MockFailureCode.MISMATCHED_RESULT) from None
        return result


def _speech_store(
    fixtures: Mapping[str, MockOutcome[SpeechToTextResult]],
) -> _FixtureStore[SpeechToTextRequest, SpeechToTextResult]:
    return _FixtureStore(
        fixtures,
        request_type=SpeechToTextRequest,
        result_type=SpeechToTextResult,
        clone_request=lambda value: replace(value),
        clone=lambda value: replace(value),
        operation_id=lambda value: value.context.operation_id,
        cancelled=lambda value: value.context.cancelled,
        assert_matches=lambda result, request: result.assert_matches(request),
    )


def _detection_store(
    fixtures: Mapping[str, MockOutcome[LanguageDetectionResult]],
) -> _FixtureStore[LanguageDetectionRequest, LanguageDetectionResult]:
    return _FixtureStore(
        fixtures,
        request_type=LanguageDetectionRequest,
        result_type=LanguageDetectionResult,
        clone_request=lambda value: replace(value),
        clone=lambda value: replace(value),
        operation_id=lambda value: value.context.operation_id,
        cancelled=lambda value: value.context.cancelled,
        assert_matches=lambda result, request: result.assert_matches(request),
    )


def _transliteration_store(
    fixtures: Mapping[str, MockOutcome[TransliterationResult]],
) -> _FixtureStore[TransliterationRequest, TransliterationResult]:
    return _FixtureStore(
        fixtures,
        request_type=TransliterationRequest,
        result_type=TransliterationResult,
        clone_request=lambda value: replace(value),
        clone=lambda value: replace(value),
        operation_id=lambda value: value.context.operation_id,
        cancelled=lambda value: value.context.cancelled,
        assert_matches=lambda result, request: result.assert_matches(request),
    )


def _translation_store(
    fixtures: Mapping[str, MockOutcome[TranslationResult]],
) -> _FixtureStore[TranslationRequest, TranslationResult]:
    return _FixtureStore(
        fixtures,
        request_type=TranslationRequest,
        result_type=TranslationResult,
        clone_request=lambda value: replace(value),
        clone=lambda value: replace(value),
        operation_id=lambda value: value.context.operation_id,
        cancelled=lambda value: value.context.cancelled,
        assert_matches=lambda result, request: result.assert_matches(request),
    )


def _text_to_speech_store(
    fixtures: Mapping[str, MockOutcome[TextToSpeechResult]],
) -> _FixtureStore[TextToSpeechRequest, TextToSpeechResult]:
    return _FixtureStore(
        fixtures,
        request_type=TextToSpeechRequest,
        result_type=TextToSpeechResult,
        clone_request=lambda value: replace(value),
        clone=lambda value: replace(value),
        operation_id=lambda value: value.context.operation_id,
        cancelled=lambda value: value.context.cancelled,
        assert_matches=lambda result, request: result.assert_matches(request),
    )


class MockSpeechToTextAdapter:
    def __init__(self, fixtures: Mapping[str, MockOutcome[SpeechToTextResult]]) -> None:
        self._store = _speech_store(fixtures)

    async def transcribe(self, request: SpeechToTextRequest) -> SpeechToTextResult:
        return self._store.resolve(request)


class MockLanguageDetectionAdapter:
    def __init__(self, fixtures: Mapping[str, MockOutcome[LanguageDetectionResult]]) -> None:
        self._store = _detection_store(fixtures)

    async def detect(self, request: LanguageDetectionRequest) -> LanguageDetectionResult:
        return self._store.resolve(request)


class MockTransliterationAdapter:
    def __init__(self, fixtures: Mapping[str, MockOutcome[TransliterationResult]]) -> None:
        self._store = _transliteration_store(fixtures)

    async def transliterate(self, request: TransliterationRequest) -> TransliterationResult:
        return self._store.resolve(request)


class MockTranslationAdapter:
    def __init__(self, fixtures: Mapping[str, MockOutcome[TranslationResult]]) -> None:
        self._store = _translation_store(fixtures)

    async def translate(self, request: TranslationRequest) -> TranslationResult:
        return self._store.resolve(request)


class MockTextToSpeechAdapter:
    def __init__(self, fixtures: Mapping[str, MockOutcome[TextToSpeechResult]]) -> None:
        self._store = _text_to_speech_store(fixtures)

    async def synthesize(self, request: TextToSpeechRequest) -> TextToSpeechResult:
        return self._store.resolve(request)
