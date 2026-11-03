"""Provider-neutral contracts for bounded, source-backed wellness guidance."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol
from urllib.parse import urlsplit

MAX_QUESTION_LENGTH = 1_000
MAX_ANSWER_LENGTH = 6_000
MAX_CITATIONS = 8
MAX_ANNOTATIONS = 32


class GuidanceOutcome(StrEnum):
    ANSWERED = "ANSWERED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    CONSENT_REQUIRED = "CONSENT_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    REJECTED = "REJECTED"


class GuidanceProviderFailureCode(StrEnum):
    UNAVAILABLE = "UNAVAILABLE"
    INVALID_RESPONSE = "INVALID_RESPONSE"


class GuidanceProviderError(RuntimeError):
    """Content-free provider failure safe to map at an application boundary."""

    def __init__(self, code: GuidanceProviderFailureCode) -> None:
        self.code = code
        super().__init__(code.value)


def _text(name: str, value: object, *, maximum: int) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    normalized = value.strip()
    if not normalized or len(normalized) > maximum or any(ord(char) < 32 for char in normalized):
        raise ValueError(f"{name} must be bounded printable text")
    return normalized


def _utc(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidanceQuestion:
    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", _text("question", self.text, maximum=MAX_QUESTION_LENGTH))


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidanceProviderRequest:
    """Deliberately contains only the disclosed question, never patient context."""

    question: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "question", _text("provider question", self.question, maximum=MAX_QUESTION_LENGTH)
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidanceCitation:
    title: str
    url: str

    def __post_init__(self) -> None:
        title = _text("citation title", self.title, maximum=200)
        if type(self.url) is not str or len(self.url) > 2_048:
            raise ValueError("citation URL must be bounded HTTPS")
        parsed = urlsplit(self.url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port is not None
            or parsed.fragment
        ):
            raise ValueError("citation URL must be clean HTTPS")
        object.__setattr__(self, "title", title)


@dataclass(frozen=True, slots=True, kw_only=True, order=True)
class SourceAnnotation:
    start: int
    end: int
    citation_index: int

    def __post_init__(self) -> None:
        if any(type(value) is not int for value in (self.start, self.end, self.citation_index)):
            raise TypeError("annotation positions must be integers")
        if self.start < 0 or self.end <= self.start or self.citation_index < 0:
            raise ValueError("annotation positions are invalid")


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidanceProviderResult:
    answer: str
    citations: tuple[GuidanceCitation, ...]
    annotations: tuple[SourceAnnotation, ...]
    retrieved_at: datetime

    def __post_init__(self) -> None:
        answer = _text("guidance answer", self.answer, maximum=MAX_ANSWER_LENGTH)
        if (
            type(self.citations) is not tuple
            or not self.citations
            or len(self.citations) > MAX_CITATIONS
        ):
            raise ValueError("guidance citations must be a bounded tuple")
        if any(type(citation) is not GuidanceCitation for citation in self.citations):
            raise TypeError("guidance citations must use GuidanceCitation")
        urls = tuple(citation.url for citation in self.citations)
        if len(set(urls)) != len(urls) or urls != tuple(sorted(urls)):
            raise ValueError("guidance citations must be unique and stably ordered")
        if (
            type(self.annotations) is not tuple
            or not self.annotations
            or len(self.annotations) > MAX_ANNOTATIONS
            or any(type(annotation) is not SourceAnnotation for annotation in self.annotations)
        ):
            raise ValueError("source annotations must be a bounded tuple")
        if self.annotations != tuple(sorted(self.annotations)) or len(set(self.annotations)) != len(
            self.annotations
        ):
            raise ValueError("source annotations must be unique and stably ordered")
        previous_end = -1
        for annotation in self.annotations:
            if (
                annotation.start < previous_end
                or annotation.end > len(answer)
                or annotation.citation_index >= len(self.citations)
            ):
                raise ValueError("source annotations overlap or reference invalid content")
            previous_end = annotation.end
        object.__setattr__(self, "answer", answer)
        object.__setattr__(self, "retrieved_at", _utc("retrieved_at", self.retrieved_at))


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidanceAnswer:
    outcome: GuidanceOutcome
    answer: str | None
    citations: tuple[GuidanceCitation, ...]
    retrieved_at: datetime | None

    def __post_init__(self) -> None:
        if type(self.outcome) is not GuidanceOutcome:
            raise TypeError("guidance outcome must be closed")
        if self.outcome is GuidanceOutcome.ANSWERED:
            if self.answer is None or not self.citations or self.retrieved_at is None:
                raise ValueError("answered guidance requires validated content and citations")
            if (
                type(self.citations) is not tuple
                or len(self.citations) > MAX_CITATIONS
                or any(type(citation) is not GuidanceCitation for citation in self.citations)
            ):
                raise TypeError("answered guidance requires bounded citations")
            object.__setattr__(
                self, "answer", _text("guidance answer", self.answer, maximum=MAX_ANSWER_LENGTH)
            )
            object.__setattr__(self, "retrieved_at", _utc("retrieved_at", self.retrieved_at))
        elif self.answer is not None or self.citations or self.retrieved_at is not None:
            raise ValueError("non-answered guidance cannot carry provider content")


class GuidanceProvider(Protocol):
    async def generate(self, request: GuidanceProviderRequest) -> GuidanceProviderResult: ...


__all__ = [
    "GuidanceAnswer",
    "GuidanceCitation",
    "GuidanceOutcome",
    "GuidanceProvider",
    "GuidanceProviderError",
    "GuidanceProviderFailureCode",
    "GuidanceProviderRequest",
    "GuidanceProviderResult",
    "GuidanceQuestion",
    "SourceAnnotation",
]
