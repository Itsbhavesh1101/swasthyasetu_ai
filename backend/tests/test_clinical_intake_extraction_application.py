"""P8-B application orchestration and fail-closed boundary tests."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import cast

import pytest
from pydantic import ValidationError

from app.modules.ai_orchestration.contracts import (
    REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    FinishReason,
    JsonValue,
    ResultProvenance,
    StructuredLLMRequest,
    StructuredLLMResult,
)
from app.modules.ai_orchestration.providers import LLMFailureCategory, OrchestrationOutcome
from app.modules.clinical_intake.extraction.application import (
    ClinicalIntakeExtractor,
    ExtractionFailureCode,
)
from app.modules.clinical_intake.extraction.contracts import (
    EXTRACTION_OPERATION_ID,
    EXTRACTION_PROMPT_ID,
    EXTRACTION_PROMPT_VERSION,
    EXTRACTION_SCHEMA_ID,
    EXTRACTION_SCHEMA_VERSION,
    CandidateFieldKey,
    ClinicalExtractionTask,
    EvidenceSpan,
    SourceInput,
    derive_candidate_id,
)
from app.modules.clinical_intake.extraction.prompts import ENGINEERING_PROMPT_MANIFEST

NOW = datetime(2026, 10, 19, 8, tzinfo=UTC)
TEXT = "I report synthetic pain"


def task() -> ClinicalExtractionTask:
    return ClinicalExtractionTask(
        request_id="req_synthetic_0001",
        language_code="en",
        source=SourceInput(
            source_id="source_synthetic_001",
            source_version="1.0.0",
            content_hash=sha256(TEXT.encode()).hexdigest(),
            text=TEXT,
        ),
    )


def payload(input_task: ClinicalExtractionTask) -> dict[str, object]:
    span = EvidenceSpan(
        source_id=input_task.source.source_id,
        source_version=input_task.source.source_version,
        content_hash=input_task.source.content_hash,
        start=9,
        end=23,
        quote="synthetic pain",
    )
    return {
        "schema_id": EXTRACTION_SCHEMA_ID,
        "schema_version": EXTRACTION_SCHEMA_VERSION,
        "prompt_id": EXTRACTION_PROMPT_ID,
        "prompt_version": EXTRACTION_PROMPT_VERSION,
        "disposition": "CANDIDATES",
        "candidate_facts": [
            {
                "candidate_id": derive_candidate_id(
                    CandidateFieldKey.CHIEF_COMPLAINT_TEXT, span, "synthetic pain"
                ),
                "field_key": "CHIEF_COMPLAINT_TEXT",
                "value": "synthetic pain",
                "evidence": span.model_dump(),
                "verification_state": "AI_EXTRACTED_UNCONFIRMED",
                "confidence": None,
            }
        ],
        "missing_information_candidates": [],
        "contradiction_candidates": [],
        "uncertainty": [],
        "abstention_reason": None,
        "refusal_reason": None,
        "provenance": {
            "provider_id": "offline_fake",
            "provider_model_id": "fixture_model",
            "provider_model_version": "1.0.0",
            "source_references": [input_task.source_reference.to_dict()],
        },
    }


def successful_result(
    request: StructuredLLMRequest, value: dict[str, object]
) -> StructuredLLMResult:
    return StructuredLLMResult(
        result_contract_version=RESULT_CONTRACT_VERSION,
        request_id=request.request_id,
        operation_id=request.operation_id,
        request_contract_version=request.request_contract_version,
        schema_id=request.schema_id,
        schema_version=request.schema_version,
        prompt_id=request.prompt_id,
        prompt_version=request.prompt_version,
        provider_id="offline_fake",
        provider_model_id="fixture_model",
        provider_model_version="1.0.0",
        provider_request_id=None,
        validated_payload=cast(Mapping[str, JsonValue], value),
        finish_reason=FinishReason.STOP,
        usage=None,
        latency_ms=1.0,
        attempt_count=1,
        provenance=ResultProvenance(
            schema_id=request.schema_id,
            schema_version=request.schema_version,
            prompt_id=request.prompt_id,
            prompt_version=request.prompt_version,
            provider_id="offline_fake",
            provider_model_id="fixture_model",
            provider_model_version="1.0.0",
            source_references=request.provenance_context,
        ),
    )


class ScriptedCapability:
    def __init__(
        self,
        script: BaseException
        | OrchestrationOutcome
        | Callable[[StructuredLLMRequest], OrchestrationOutcome],
    ) -> None:
        self.script = script
        self.requests: list[StructuredLLMRequest] = []

    async def generate_structured(self, request: StructuredLLMRequest) -> OrchestrationOutcome:
        self.requests.append(request)
        if isinstance(self.script, BaseException):
            raise self.script
        if callable(self.script):
            return self.script(request)
        return self.script


async def test_extractor_builds_one_bounded_request_and_returns_only_unconfirmed_candidates() -> (
    None
):
    input_task = task()
    capability = ScriptedCapability(
        lambda request: OrchestrationOutcome.success(
            successful_result(request, payload(input_task))
        )
    )
    extractor = ClinicalIntakeExtractor(
        capability=capability, engineering_mode=True, clock=lambda: NOW
    )

    outcome = await extractor.extract(input_task)

    assert outcome.result is not None
    assert outcome.failure is None
    assert outcome.result.candidate_facts[0].verification_state.value == "AI_EXTRACTED_UNCONFIRMED"
    assert len(capability.requests) == 1
    request = capability.requests[0]
    assert request.operation_id == EXTRACTION_OPERATION_ID
    assert request.request_contract_version == REQUEST_CONTRACT_VERSION
    assert request.retry_budget == 0
    assert request.deadline_at == NOW + timedelta(seconds=10)
    assert request.input == {
        "source": {
            "source_id": input_task.source.source_id,
            "source_version": input_task.source.source_version,
            "content_hash": input_task.source.content_hash,
            "text": TEXT,
        }
    }
    assert "system_prompt" not in request.input
    assert ENGINEERING_PROMPT_MANIFEST.instruction_template not in repr(request.input)


async def test_engineering_package_is_default_off_and_never_calls_capability() -> None:
    capability = ScriptedCapability(RuntimeError("must not be called"))

    outcome = await ClinicalIntakeExtractor(capability=capability, clock=lambda: NOW).extract(
        task()
    )

    assert outcome.failure is not None
    assert outcome.failure.code is ExtractionFailureCode.PACKAGE_UNAVAILABLE
    assert capability.requests == []


@pytest.mark.parametrize("invalid_text", ["invalid-\ud800-source", "invalid-\udfff-source"])
async def test_invalid_unicode_is_rejected_before_provider_invocation(
    invalid_text: str,
) -> None:
    capability = ScriptedCapability(RuntimeError("must not be called"))

    with pytest.raises(ValidationError):
        invalid_task = ClinicalExtractionTask(
            request_id="req_synthetic_0001",
            language_code="en",
            source=SourceInput(
                source_id="source_synthetic_001",
                source_version="1.0.0",
                content_hash="0" * 64,
                text=invalid_text,
            ),
        )
        await ClinicalIntakeExtractor(
            capability=capability, engineering_mode=True, clock=lambda: NOW
        ).extract(invalid_task)

    assert capability.requests == []


@pytest.mark.parametrize("category", list(LLMFailureCategory))
async def test_every_p8a_failure_maps_to_safe_degraded_manual_fallback(
    category: LLMFailureCategory,
) -> None:
    capability = ScriptedCapability(
        OrchestrationOutcome.failure_outcome(
            category=category,
            operation_id=EXTRACTION_OPERATION_ID,
            request_id=task().request_id,
            attempt_count=1,
            retryable=False,
        )
    )

    outcome = await ClinicalIntakeExtractor(
        capability=capability, engineering_mode=True, clock=lambda: NOW
    ).extract(task())

    assert outcome.result is None
    assert outcome.failure is not None
    assert outcome.failure.code is ExtractionFailureCode.DEPENDENCY_UNAVAILABLE
    assert outcome.failure.fallback == "DETERMINISTIC_P7_INTAKE"
    assert len(capability.requests) == 1


@pytest.mark.parametrize(
    "mutate",
    [
        lambda result: replace(result, request_id="req_wrong_0001"),
        lambda result: replace(result, operation_id="wrong.operation"),
        lambda result: replace(result, schema_version="wrong"),
        lambda result: replace(result, prompt_version="wrong"),
        lambda result: replace(result, finish_reason=FinishReason.LENGTH),
        lambda result: replace(result, provider_id="spoofed_provider"),
        lambda result: replace(
            result,
            provenance=replace(result.provenance, provider_model_version="spoofed"),
        ),
    ],
)
async def test_result_correlation_provenance_and_completeness_mismatches_fail_closed(
    mutate: object,
) -> None:
    input_task = task()

    def script(request: StructuredLLMRequest) -> OrchestrationOutcome:
        result = successful_result(request, payload(input_task))
        return OrchestrationOutcome.success(mutate(result))  # type: ignore[operator]

    capability = ScriptedCapability(script)
    outcome = await ClinicalIntakeExtractor(
        capability=capability, engineering_mode=True, clock=lambda: NOW
    ).extract(input_task)

    assert outcome.result is None
    assert outcome.failure is not None
    assert outcome.failure.code in {
        ExtractionFailureCode.CORRELATION_INVALID,
        ExtractionFailureCode.INCOMPLETE_OUTPUT,
    }
    assert len(capability.requests) == 1


@pytest.mark.parametrize(
    "bad_payload",
    [
        {},
        {"candidate_facts": "wrong-root"},
        {**payload(task()), "diagnosis": "invented"},
        {
            **payload(task()),
            "candidate_facts": [
                {**payload(task())["candidate_facts"][0], "triage_route": "emergency"}  # type: ignore[index]
            ],
        },
    ],
)
async def test_malformed_or_authority_smuggling_payload_is_rejected_without_partial_acceptance(
    bad_payload: dict[str, object],
) -> None:
    capability = ScriptedCapability(
        lambda request: OrchestrationOutcome.success(successful_result(request, bad_payload))
    )

    outcome = await ClinicalIntakeExtractor(
        capability=capability, engineering_mode=True, clock=lambda: NOW
    ).extract(task())

    assert outcome.result is None
    assert outcome.failure is not None
    assert outcome.failure.code is ExtractionFailureCode.OUTPUT_SCHEMA_INVALID
    assert len(capability.requests) == 1


async def test_unexpected_capability_exception_is_safe_content_free_and_not_retried(
    caplog: pytest.LogCaptureFixture,
) -> None:
    marker = "synthetic-sensitive-patient-detail"
    capability = ScriptedCapability(RuntimeError(marker))

    outcome = await ClinicalIntakeExtractor(
        capability=capability, engineering_mode=True, clock=lambda: NOW
    ).extract(task())

    assert outcome.failure is not None
    assert outcome.failure.code is ExtractionFailureCode.DEPENDENCY_UNAVAILABLE
    assert marker not in repr(outcome)
    assert marker not in caplog.text
    assert len(capability.requests) == 1


async def test_cancellation_propagates() -> None:
    capability = ScriptedCapability(__import__("asyncio").CancelledError())
    with pytest.raises(__import__("asyncio").CancelledError):
        await ClinicalIntakeExtractor(
            capability=capability, engineering_mode=True, clock=lambda: NOW
        ).extract(task())
