"""P8-A provider-neutral contract and serialization tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from math import inf

import pytest

from app.modules.ai_orchestration.contracts import (
    REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    ContractValidationError,
    FinishReason,
    ResultProvenance,
    SourceReference,
    StructuredLLMRequest,
    StructuredLLMResult,
    TokenUsage,
)


def request_payload() -> dict[str, object]:
    return {
        "operation_id": "synthetic.extract",
        "language_code": "en",
        "request_id": "req_synthetic_0001",
        "request_contract_version": REQUEST_CONTRACT_VERSION,
        "schema_id": "synthetic_candidate",
        "schema_version": "1.0.0",
        "prompt_id": "synthetic_prompt",
        "prompt_version": "1.0.0",
        "input": {"items": [{"label": "alpha", "value": 7}]},
        "max_output_tokens": 256,
        "deadline_at": (datetime.now(UTC) + timedelta(seconds=10)).isoformat(),
        "retry_budget": 1,
        "attempt": 1,
        "provider_policy_id": "offline_only",
        "provider_policy_version": "1.0.0",
        "provenance_context": [
            {
                "source_id": "source_synthetic_0001",
                "source_version": "1",
                "content_hash": "a" * 64,
            }
        ],
    }


def result_payload(request: StructuredLLMRequest) -> dict[str, object]:
    return {
        "result_contract_version": RESULT_CONTRACT_VERSION,
        "request_id": request.request_id,
        "operation_id": request.operation_id,
        "request_contract_version": request.request_contract_version,
        "schema_id": request.schema_id,
        "schema_version": request.schema_version,
        "prompt_id": request.prompt_id,
        "prompt_version": request.prompt_version,
        "provider_id": "offline_fake",
        "provider_model_id": "fixture_model",
        "provider_model_version": "1.0.0",
        "provider_request_id": "provider_synthetic_0001",
        "validated_payload": {"candidate": "synthetic-only"},
        "finish_reason": "STOP",
        "usage": {"input_tokens": 12, "output_tokens": 4, "total_tokens": 16},
        "latency_ms": 2.5,
        "attempt_count": 1,
        "provenance": {
            "schema_id": request.schema_id,
            "schema_version": request.schema_version,
            "prompt_id": request.prompt_id,
            "prompt_version": request.prompt_version,
            "provider_id": "offline_fake",
            "provider_model_id": "fixture_model",
            "provider_model_version": "1.0.0",
            "source_references": [reference.to_dict() for reference in request.provenance_context],
        },
        "raw_retained": False,
    }


def test_request_is_immutable_strict_and_round_trips() -> None:
    request = StructuredLLMRequest.from_dict(request_payload())

    assert StructuredLLMRequest.from_dict(request.to_dict()) == request
    with pytest.raises(FrozenInstanceError):
        request.attempt = 2  # type: ignore[misc]
    with pytest.raises(TypeError):
        request.input["extra"] = "mutation"  # type: ignore[index]

    unknown = request_payload() | {"unknown": True}
    with pytest.raises(ContractValidationError, match="unknown fields"):
        StructuredLLMRequest.from_dict(unknown)


def test_direct_construction_freezes_source_references_and_rejects_bad_types() -> None:
    request = StructuredLLMRequest.from_dict(request_payload())
    mutable_refs = list(request.provenance_context)
    reconstructed = StructuredLLMRequest(
        operation_id=request.operation_id,
        language_code=request.language_code,
        request_id=request.request_id,
        request_contract_version=request.request_contract_version,
        schema_id=request.schema_id,
        schema_version=request.schema_version,
        prompt_id=request.prompt_id,
        prompt_version=request.prompt_version,
        input=request.input,
        max_output_tokens=request.max_output_tokens,
        deadline_at=request.deadline_at,
        retry_budget=request.retry_budget,
        attempt=request.attempt,
        provider_policy_id=request.provider_policy_id,
        provider_policy_version=request.provider_policy_version,
        provenance_context=mutable_refs,  # type: ignore[arg-type]
    )
    mutable_refs.clear()

    assert len(reconstructed.provenance_context) == 1
    with pytest.raises(ContractValidationError, match="datetime"):
        StructuredLLMRequest(
            operation_id=request.operation_id,
            language_code=request.language_code,
            request_id=request.request_id,
            request_contract_version=request.request_contract_version,
            schema_id=request.schema_id,
            schema_version=request.schema_version,
            prompt_id=request.prompt_id,
            prompt_version=request.prompt_version,
            input=request.input,
            max_output_tokens=request.max_output_tokens,
            deadline_at="not-a-datetime",  # type: ignore[arg-type]
            retry_budget=request.retry_budget,
            attempt=request.attempt,
            provider_policy_id=request.provider_policy_id,
            provider_policy_version=request.provider_policy_version,
            provenance_context=request.provenance_context,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("request_contract_version", "structured-llm-request.v999"),
        ("request_id", "patient-12345678"),
        ("operation_id", "patient supplied free text"),
        ("language_code", "not_a_language"),
        ("max_output_tokens", 0),
        ("retry_budget", 99),
        ("attempt", 0),
        ("deadline_at", "2026-01-01T00:00:00"),
    ],
)
def test_request_rejects_invalid_versions_identifiers_and_limits(field: str, value: object) -> None:
    payload = request_payload()
    payload[field] = value

    with pytest.raises(ContractValidationError):
        StructuredLLMRequest.from_dict(payload)


@pytest.mark.parametrize(
    "invalid_input",
    [
        {"headers": {"Authorization": "synthetic-secret"}},
        {"nested": {"credentials": "synthetic-secret"}},
        {"patient_endpoint": "https://example.invalid"},
        {"base-url": "https://example.invalid"},
        {"api_key": "synthetic-secret"},
        {"tools": ["call_external_system"]},
        {"policy_overrides": {"route": "urgent"}},
        {"chain_of_thought": True},
        {"non_finite": inf},
        {"too_deep": {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {}}}}}}}}}},
        {"too_many": list(range(65))},
        {"too_long": "x" * 4097},
    ],
)
def test_request_rejects_forbidden_or_unbounded_structured_input(
    invalid_input: dict[str, object],
) -> None:
    payload = request_payload()
    payload["input"] = invalid_input

    with pytest.raises(ContractValidationError):
        StructuredLLMRequest.from_dict(payload)


def test_request_rejects_oversize_serialized_input_and_invalid_source_reference() -> None:
    payload = request_payload()
    payload["input"] = {f"k{index}": "x" * 300 for index in range(64)}
    with pytest.raises(ContractValidationError, match="serialized byte limit"):
        StructuredLLMRequest.from_dict(payload)

    payload = request_payload()
    payload["provenance_context"] = [{"source_id": "raw patient sentence"}]
    with pytest.raises(ContractValidationError):
        StructuredLLMRequest.from_dict(payload)


def test_result_is_immutable_bounded_strict_and_round_trips() -> None:
    request = StructuredLLMRequest.from_dict(request_payload())
    result = StructuredLLMResult.from_dict(result_payload(request))

    assert StructuredLLMResult.from_dict(result.to_dict()) == result
    assert result.finish_reason is FinishReason.STOP
    assert result.usage == TokenUsage(input_tokens=12, output_tokens=4, total_tokens=16)
    assert result.provenance == ResultProvenance(
        schema_id=request.schema_id,
        schema_version=request.schema_version,
        prompt_id=request.prompt_id,
        prompt_version=request.prompt_version,
        provider_id="offline_fake",
        provider_model_id="fixture_model",
        provider_model_version="1.0.0",
        source_references=(
            SourceReference(
                source_id="source_synthetic_0001",
                source_version="1",
                content_hash="a" * 64,
            ),
        ),
    )
    with pytest.raises(TypeError):
        result.validated_payload["extra"] = True  # type: ignore[index]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("result_contract_version", "structured-llm-result.v999"),
        ("finish_reason", "provider-custom"),
        ("latency_ms", inf),
        ("attempt_count", 0),
        ("raw_retained", True),
    ],
)
def test_result_rejects_invalid_or_unsafe_values(field: str, value: object) -> None:
    request = StructuredLLMRequest.from_dict(request_payload())
    payload = result_payload(request)
    payload[field] = value

    with pytest.raises(ContractValidationError):
        StructuredLLMResult.from_dict(payload)


def test_result_rejects_unknown_fields_bad_usage_and_oversize_payload() -> None:
    request = StructuredLLMRequest.from_dict(request_payload())
    unknown = result_payload(request) | {"provider_raw_response": "synthetic-sensitive"}
    with pytest.raises(ContractValidationError, match="unknown fields"):
        StructuredLLMResult.from_dict(unknown)

    bad_usage = result_payload(request)
    bad_usage["usage"] = {"input_tokens": 12, "output_tokens": 4, "total_tokens": 99}
    with pytest.raises(ContractValidationError, match="sum"):
        StructuredLLMResult.from_dict(bad_usage)

    oversize = result_payload(request)
    oversize["validated_payload"] = {f"k{index}": "x" * 300 for index in range(64)}
    with pytest.raises(ContractValidationError, match="serialized byte limit"):
        StructuredLLMResult.from_dict(oversize)
