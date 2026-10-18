"""Strict, immutable, provider-neutral structured-generation contracts."""

import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Final, cast

REQUEST_CONTRACT_VERSION: Final = "structured-llm-request.v1"
RESULT_CONTRACT_VERSION: Final = "structured-llm-result.v1"
MAX_SERIALIZED_BYTES: Final = 16_384
MAX_COLLECTION_ITEMS: Final = 64
MAX_JSON_DEPTH: Final = 8
MAX_STRING_LENGTH: Final = 4_096
MAX_OUTPUT_TOKENS: Final = 4_096
MAX_RETRY_BUDGET: Final = 3
MAX_TOKEN_COUNT: Final = 1_000_000
MAX_LATENCY_MS: Final = 300_000.0

_MACHINE_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")
_OPAQUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_REQUEST_ID = re.compile(r"^req_[A-Za-z0-9_-]{8,64}$")
_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_LANGUAGE = re.compile(r"^[a-z]{2,3}(?:-[A-Z]{2})?$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_FORBIDDEN_INPUT_KEYS = frozenset(
    {
        "authorization",
        "api_key",
        "authorization_header",
        "base_url",
        "bearer",
        "chain_of_thought",
        "credentials",
        "endpoint",
        "headers",
        "patient_endpoint",
        "provider_endpoint",
        "provider_policy",
        "policy_overrides",
        "proxy",
        "system_prompt",
        "tool_permissions",
        "tools",
    }
)


class ContractValidationError(ValueError):
    """Raised when a project-owned AI contract is malformed or unbounded."""


class FinishReason(StrEnum):
    """Closed provider-neutral completion reasons."""

    STOP = "STOP"
    LENGTH = "LENGTH"
    OTHER = "OTHER"


JsonValue = None | bool | int | float | str | tuple["JsonValue", ...] | Mapping[str, "JsonValue"]


def _strict_fields(value: Mapping[str, object], expected: frozenset[str], name: str) -> None:
    supplied = frozenset(value)
    unknown = supplied - expected
    missing = expected - supplied
    if unknown:
        raise ContractValidationError(f"{name} contains unknown fields: {sorted(unknown)}")
    if missing:
        raise ContractValidationError(f"{name} is missing fields: {sorted(missing)}")


def _bounded_string(value: object, *, name: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ContractValidationError(f"{name} has an invalid machine-readable value")
    return value


def _bounded_int(value: object, *, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ContractValidationError(f"{name} must be an integer from {minimum} to {maximum}")
    return value


def _freeze_json(value: object, *, depth: int = 0, path: str = "input") -> JsonValue:
    if depth > MAX_JSON_DEPTH:
        raise ContractValidationError(f"{path} exceeds the maximum nesting depth")
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, str):
        if len(value) > MAX_STRING_LENGTH:
            raise ContractValidationError(f"{path} contains an oversize string")
        return value
    if isinstance(value, Mapping):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ContractValidationError(f"{path} contains too many fields")
        frozen: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key or len(key) > 128:
                raise ContractValidationError(f"{path} contains an invalid field name")
            normalized_key = key.strip().casefold().replace("-", "_")
            if normalized_key in _FORBIDDEN_INPUT_KEYS:
                raise ContractValidationError(f"{path} contains prohibited provider authority")
            frozen[key] = _freeze_json(item, depth=depth + 1, path=f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ContractValidationError(f"{path} contains too many items")
        return tuple(
            _freeze_json(item, depth=depth + 1, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        )
    raise ContractValidationError(f"{path} contains a non-JSON value")


def _thaw_json(value: JsonValue) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _validate_serialized_size(value: JsonValue, *, name: str) -> None:
    serialized = json.dumps(_thaw_json(value), ensure_ascii=False, separators=(",", ":"))
    if len(serialized.encode("utf-8")) > MAX_SERIALIZED_BYTES:
        raise ContractValidationError(f"{name} exceeds the serialized byte limit")


@dataclass(frozen=True, slots=True)
class SourceReference:
    """Opaque source identity without source content."""

    source_id: str
    source_version: str
    content_hash: str

    def __post_init__(self) -> None:
        _bounded_string(self.source_id, name="source_id", pattern=_OPAQUE_ID)
        _bounded_string(self.source_version, name="source_version", pattern=_VERSION)
        _bounded_string(self.content_hash, name="content_hash", pattern=_SHA256)

    @classmethod
    def from_dict(cls, value: object) -> "SourceReference":
        if not isinstance(value, Mapping):
            raise ContractValidationError("source reference must be an object")
        _strict_fields(
            cast(Mapping[str, object], value),
            frozenset({"source_id", "source_version", "content_hash"}),
            "source reference",
        )
        return cls(
            source_id=cast(str, value["source_id"]),
            source_version=cast(str, value["source_version"]),
            content_hash=cast(str, value["content_hash"]),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "source_version": self.source_version,
            "content_hash": self.content_hash,
        }


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """Bounded content-free provider token counters."""

    input_tokens: int
    output_tokens: int
    total_tokens: int

    def __post_init__(self) -> None:
        _bounded_int(self.input_tokens, name="input_tokens", minimum=0, maximum=MAX_TOKEN_COUNT)
        _bounded_int(self.output_tokens, name="output_tokens", minimum=0, maximum=MAX_TOKEN_COUNT)
        _bounded_int(self.total_tokens, name="total_tokens", minimum=0, maximum=MAX_TOKEN_COUNT)
        if self.total_tokens != self.input_tokens + self.output_tokens:
            raise ContractValidationError("total_tokens must equal the input/output token sum")

    @classmethod
    def from_dict(cls, value: object) -> "TokenUsage":
        if not isinstance(value, Mapping):
            raise ContractValidationError("usage must be an object")
        _strict_fields(
            cast(Mapping[str, object], value),
            frozenset({"input_tokens", "output_tokens", "total_tokens"}),
            "usage",
        )
        return cls(
            input_tokens=cast(int, value["input_tokens"]),
            output_tokens=cast(int, value["output_tokens"]),
            total_tokens=cast(int, value["total_tokens"]),
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass(frozen=True, slots=True)
class ResultProvenance:
    """Version and source-reference linkage for a candidate result."""

    schema_id: str
    schema_version: str
    prompt_id: str
    prompt_version: str
    provider_id: str
    provider_model_id: str
    provider_model_version: str
    source_references: tuple[SourceReference, ...]

    def __post_init__(self) -> None:
        for name in ("schema_id", "prompt_id", "provider_id", "provider_model_id"):
            _bounded_string(getattr(self, name), name=name, pattern=_MACHINE_ID)
        for name in ("schema_version", "prompt_version", "provider_model_version"):
            _bounded_string(getattr(self, name), name=name, pattern=_VERSION)
        if not isinstance(self.source_references, Sequence) or isinstance(
            self.source_references, (str, bytes, bytearray)
        ):
            raise ContractValidationError("provenance source references must be a sequence")
        references = tuple(self.source_references)
        if any(not isinstance(reference, SourceReference) for reference in references):
            raise ContractValidationError("provenance source references are invalid")
        object.__setattr__(self, "source_references", references)
        if len(references) > MAX_COLLECTION_ITEMS:
            raise ContractValidationError("provenance has too many source references")

    @classmethod
    def from_dict(cls, value: object) -> "ResultProvenance":
        if not isinstance(value, Mapping):
            raise ContractValidationError("provenance must be an object")
        fields = frozenset(
            {
                "schema_id",
                "schema_version",
                "prompt_id",
                "prompt_version",
                "provider_id",
                "provider_model_id",
                "provider_model_version",
                "source_references",
            }
        )
        _strict_fields(cast(Mapping[str, object], value), fields, "provenance")
        refs = value["source_references"]
        if not isinstance(refs, Sequence) or isinstance(refs, (str, bytes, bytearray)):
            raise ContractValidationError("source_references must be an array")
        return cls(
            schema_id=cast(str, value["schema_id"]),
            schema_version=cast(str, value["schema_version"]),
            prompt_id=cast(str, value["prompt_id"]),
            prompt_version=cast(str, value["prompt_version"]),
            provider_id=cast(str, value["provider_id"]),
            provider_model_id=cast(str, value["provider_model_id"]),
            provider_model_version=cast(str, value["provider_model_version"]),
            source_references=tuple(SourceReference.from_dict(item) for item in refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "provider_id": self.provider_id,
            "provider_model_id": self.provider_model_id,
            "provider_model_version": self.provider_model_version,
            "source_references": [reference.to_dict() for reference in self.source_references],
        }


@dataclass(frozen=True, slots=True)
class StructuredLLMRequest:
    """Bounded generic request carrying task-supplied data, never provider authority."""

    operation_id: str
    language_code: str
    request_id: str
    request_contract_version: str
    schema_id: str
    schema_version: str
    prompt_id: str
    prompt_version: str
    input: Mapping[str, JsonValue] = field(repr=False)
    max_output_tokens: int
    deadline_at: datetime
    retry_budget: int
    attempt: int
    provider_policy_id: str
    provider_policy_version: str
    provenance_context: tuple[SourceReference, ...] = field(repr=False)

    def __post_init__(self) -> None:
        for name in ("operation_id", "schema_id", "prompt_id", "provider_policy_id"):
            _bounded_string(getattr(self, name), name=name, pattern=_MACHINE_ID)
        _bounded_string(self.language_code, name="language_code", pattern=_LANGUAGE)
        _bounded_string(self.request_id, name="request_id", pattern=_REQUEST_ID)
        for name in ("schema_version", "prompt_version", "provider_policy_version"):
            _bounded_string(getattr(self, name), name=name, pattern=_VERSION)
        if self.request_contract_version != REQUEST_CONTRACT_VERSION:
            raise ContractValidationError("unsupported request contract version")
        frozen = _freeze_json(self.input)
        if not isinstance(frozen, Mapping):
            raise ContractValidationError("input must be an object")
        _validate_serialized_size(frozen, name="input")
        object.__setattr__(self, "input", frozen)
        _bounded_int(
            self.max_output_tokens,
            name="max_output_tokens",
            minimum=1,
            maximum=MAX_OUTPUT_TOKENS,
        )
        if not isinstance(self.deadline_at, datetime):
            raise ContractValidationError("deadline_at must be a datetime")
        if self.deadline_at.tzinfo is None or self.deadline_at.utcoffset() is None:
            raise ContractValidationError("deadline_at must be timezone-aware")
        object.__setattr__(self, "deadline_at", self.deadline_at.astimezone(UTC))
        _bounded_int(
            self.retry_budget,
            name="retry_budget",
            minimum=0,
            maximum=MAX_RETRY_BUDGET,
        )
        _bounded_int(
            self.attempt,
            name="attempt",
            minimum=1,
            maximum=self.retry_budget + 1,
        )
        if not isinstance(self.provenance_context, Sequence) or isinstance(
            self.provenance_context, (str, bytes, bytearray)
        ):
            raise ContractValidationError("provenance_context must be a sequence")
        references = tuple(self.provenance_context)
        if any(not isinstance(reference, SourceReference) for reference in references):
            raise ContractValidationError("provenance_context contains invalid references")
        object.__setattr__(self, "provenance_context", references)
        if len(references) > MAX_COLLECTION_ITEMS:
            raise ContractValidationError("provenance_context has too many references")

    @classmethod
    def from_dict(cls, value: object) -> "StructuredLLMRequest":
        if not isinstance(value, Mapping):
            raise ContractValidationError("request must be an object")
        fields = frozenset(cls.__dataclass_fields__)
        _strict_fields(cast(Mapping[str, object], value), fields, "request")
        raw_deadline = value["deadline_at"]
        if not isinstance(raw_deadline, str):
            raise ContractValidationError("deadline_at must be an ISO-8601 string")
        try:
            deadline = datetime.fromisoformat(raw_deadline)
        except ValueError as error:
            raise ContractValidationError("deadline_at must be an ISO-8601 datetime") from error
        raw_refs = value["provenance_context"]
        if not isinstance(raw_refs, Sequence) or isinstance(raw_refs, (str, bytes, bytearray)):
            raise ContractValidationError("provenance_context must be an array")
        raw_input = value["input"]
        if not isinstance(raw_input, Mapping):
            raise ContractValidationError("input must be an object")
        return cls(
            operation_id=cast(str, value["operation_id"]),
            language_code=cast(str, value["language_code"]),
            request_id=cast(str, value["request_id"]),
            request_contract_version=cast(str, value["request_contract_version"]),
            schema_id=cast(str, value["schema_id"]),
            schema_version=cast(str, value["schema_version"]),
            prompt_id=cast(str, value["prompt_id"]),
            prompt_version=cast(str, value["prompt_version"]),
            input=cast(Mapping[str, JsonValue], raw_input),
            max_output_tokens=cast(int, value["max_output_tokens"]),
            deadline_at=deadline,
            retry_budget=cast(int, value["retry_budget"]),
            attempt=cast(int, value["attempt"]),
            provider_policy_id=cast(str, value["provider_policy_id"]),
            provider_policy_version=cast(str, value["provider_policy_version"]),
            provenance_context=tuple(SourceReference.from_dict(item) for item in raw_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "operation_id": self.operation_id,
            "language_code": self.language_code,
            "request_id": self.request_id,
            "request_contract_version": self.request_contract_version,
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "input": _thaw_json(cast(JsonValue, self.input)),
            "max_output_tokens": self.max_output_tokens,
            "deadline_at": self.deadline_at.isoformat(),
            "retry_budget": self.retry_budget,
            "attempt": self.attempt,
            "provider_policy_id": self.provider_policy_id,
            "provider_policy_version": self.provider_policy_version,
            "provenance_context": [reference.to_dict() for reference in self.provenance_context],
        }


@dataclass(frozen=True, slots=True)
class StructuredLLMResult:
    """Bounded provider candidate result; never a trusted domain fact."""

    result_contract_version: str
    request_id: str
    operation_id: str
    request_contract_version: str
    schema_id: str
    schema_version: str
    prompt_id: str
    prompt_version: str
    provider_id: str
    provider_model_id: str
    provider_model_version: str
    provider_request_id: str | None
    validated_payload: Mapping[str, JsonValue] = field(repr=False)
    finish_reason: FinishReason
    usage: TokenUsage | None
    latency_ms: float
    attempt_count: int
    provenance: ResultProvenance = field(repr=False)
    raw_retained: bool = False

    def __post_init__(self) -> None:
        if self.result_contract_version != RESULT_CONTRACT_VERSION:
            raise ContractValidationError("unsupported result contract version")
        if self.request_contract_version != REQUEST_CONTRACT_VERSION:
            raise ContractValidationError("unsupported request contract version")
        for name in (
            "operation_id",
            "schema_id",
            "prompt_id",
            "provider_id",
            "provider_model_id",
        ):
            _bounded_string(getattr(self, name), name=name, pattern=_MACHINE_ID)
        _bounded_string(self.request_id, name="request_id", pattern=_REQUEST_ID)
        for name in ("schema_version", "prompt_version", "provider_model_version"):
            _bounded_string(getattr(self, name), name=name, pattern=_VERSION)
        if self.provider_request_id is not None:
            _bounded_string(
                self.provider_request_id, name="provider_request_id", pattern=_OPAQUE_ID
            )
        frozen = _freeze_json(self.validated_payload, path="validated_payload")
        if not isinstance(frozen, Mapping):
            raise ContractValidationError("validated_payload must be an object")
        _validate_serialized_size(frozen, name="validated_payload")
        object.__setattr__(self, "validated_payload", frozen)
        if self.usage is not None and not isinstance(self.usage, TokenUsage):
            raise ContractValidationError("usage must be TokenUsage or null")
        if not isinstance(self.provenance, ResultProvenance):
            raise ContractValidationError("provenance must be ResultProvenance")
        if not isinstance(self.finish_reason, FinishReason):
            try:
                object.__setattr__(self, "finish_reason", FinishReason(self.finish_reason))
            except ValueError as error:
                raise ContractValidationError("finish_reason is unsupported") from error
        if isinstance(self.latency_ms, bool) or not isinstance(self.latency_ms, (int, float)):
            raise ContractValidationError("latency_ms must be numeric")
        if not math.isfinite(self.latency_ms) or not 0 <= self.latency_ms <= MAX_LATENCY_MS:
            raise ContractValidationError("latency_ms must be finite and bounded")
        _bounded_int(
            self.attempt_count,
            name="attempt_count",
            minimum=1,
            maximum=MAX_RETRY_BUDGET + 1,
        )
        if self.raw_retained is not False:
            raise ContractValidationError("raw provider responses cannot be retained")

    @classmethod
    def from_dict(cls, value: object) -> "StructuredLLMResult":
        if not isinstance(value, Mapping):
            raise ContractValidationError("result must be an object")
        fields = frozenset(cls.__dataclass_fields__)
        _strict_fields(cast(Mapping[str, object], value), fields, "result")
        payload = value["validated_payload"]
        if not isinstance(payload, Mapping):
            raise ContractValidationError("validated_payload must be an object")
        provider_request_id = value["provider_request_id"]
        if provider_request_id is not None and not isinstance(provider_request_id, str):
            raise ContractValidationError("provider_request_id must be a string or null")
        raw_usage = value["usage"]
        return cls(
            result_contract_version=cast(str, value["result_contract_version"]),
            request_id=cast(str, value["request_id"]),
            operation_id=cast(str, value["operation_id"]),
            request_contract_version=cast(str, value["request_contract_version"]),
            schema_id=cast(str, value["schema_id"]),
            schema_version=cast(str, value["schema_version"]),
            prompt_id=cast(str, value["prompt_id"]),
            prompt_version=cast(str, value["prompt_version"]),
            provider_id=cast(str, value["provider_id"]),
            provider_model_id=cast(str, value["provider_model_id"]),
            provider_model_version=cast(str, value["provider_model_version"]),
            provider_request_id=provider_request_id,
            validated_payload=cast(Mapping[str, JsonValue], payload),
            finish_reason=cast(FinishReason, value["finish_reason"]),
            usage=None if raw_usage is None else TokenUsage.from_dict(raw_usage),
            latency_ms=cast(float, value["latency_ms"]),
            attempt_count=cast(int, value["attempt_count"]),
            provenance=ResultProvenance.from_dict(value["provenance"]),
            raw_retained=cast(bool, value["raw_retained"]),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "result_contract_version": self.result_contract_version,
            "request_id": self.request_id,
            "operation_id": self.operation_id,
            "request_contract_version": self.request_contract_version,
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "provider_id": self.provider_id,
            "provider_model_id": self.provider_model_id,
            "provider_model_version": self.provider_model_version,
            "provider_request_id": self.provider_request_id,
            "validated_payload": _thaw_json(cast(JsonValue, self.validated_payload)),
            "finish_reason": self.finish_reason.value,
            "usage": None if self.usage is None else self.usage.to_dict(),
            "latency_ms": self.latency_ms,
            "attempt_count": self.attempt_count,
            "provenance": self.provenance.to_dict(),
            "raw_retained": self.raw_retained,
        }
