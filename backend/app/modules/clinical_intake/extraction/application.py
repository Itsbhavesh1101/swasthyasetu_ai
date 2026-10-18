"""Task-owned P8-B extraction service over the P8-A capability."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Final

from pydantic import ValidationError

from app.modules.ai_orchestration.contracts import (
    REQUEST_CONTRACT_VERSION,
    FinishReason,
    StructuredLLMRequest,
    StructuredLLMResult,
)
from app.modules.ai_orchestration.providers import (
    LLMFailureCategory,
    StructuredGenerationCapability,
)
from app.modules.clinical_intake.extraction.contracts import (
    EXTRACTION_OPERATION_ID,
    EXTRACTION_PROMPT_ID,
    EXTRACTION_PROMPT_VERSION,
    EXTRACTION_SCHEMA_ID,
    EXTRACTION_SCHEMA_VERSION,
    ClinicalExtractionTask,
    ExtractionEnvelope,
)
from app.modules.clinical_intake.extraction.prompts import (
    DEFAULT_PROMPT_REGISTRY,
    PromptApprovalState,
    PromptPackageError,
    PromptRegistry,
)
from app.modules.clinical_intake.extraction.validation import (
    ExtractionValidationError,
    validate_extraction,
)

EXTRACTION_DEADLINE_SECONDS: Final = 10
EXTRACTION_MAX_OUTPUT_TOKENS: Final = 2_048
EXTRACTION_RETRY_BUDGET: Final = 0
EXTRACTION_PROVIDER_POLICY_ID: Final = "clinical_intake.engineering_offline"
EXTRACTION_PROVIDER_POLICY_VERSION: Final = "engineering.1"


class ExtractionFailureCode(StrEnum):
    PACKAGE_UNAVAILABLE = "EXTRACTION_PACKAGE_UNAVAILABLE"
    DEPENDENCY_UNAVAILABLE = "EXTRACTION_DEPENDENCY_UNAVAILABLE"
    CORRELATION_INVALID = "EXTRACTION_CORRELATION_INVALID"
    INCOMPLETE_OUTPUT = "EXTRACTION_INCOMPLETE_OUTPUT"
    OUTPUT_SCHEMA_INVALID = "EXTRACTION_OUTPUT_SCHEMA_INVALID"
    EVIDENCE_INVALID = "EXTRACTION_EVIDENCE_INVALID"


@dataclass(frozen=True, slots=True)
class ExtractionFailure:
    code: ExtractionFailureCode
    fallback: str = "DETERMINISTIC_P7_INTAKE"
    upstream_category: LLMFailureCategory | None = None

    def __str__(self) -> str:
        return self.code.value


@dataclass(frozen=True, slots=True)
class ExtractionOutcome:
    result: ExtractionEnvelope | None = field(default=None, repr=False)
    failure: ExtractionFailure | None = None

    def __post_init__(self) -> None:
        if (self.result is None) == (self.failure is None):
            raise ValueError("extraction outcome must contain one result or failure")


class ClinicalIntakeExtractor:
    """Produces detached engineering candidates; it has no persistence or clinical authority."""

    def __init__(
        self,
        *,
        capability: StructuredGenerationCapability,
        engineering_mode: bool = False,
        prompt_registry: PromptRegistry = DEFAULT_PROMPT_REGISTRY,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._capability = capability
        self._engineering_mode = engineering_mode
        self._prompt_registry = prompt_registry
        self._clock = clock or (lambda: datetime.now(UTC))

    async def extract(self, task: ClinicalExtractionTask) -> ExtractionOutcome:
        try:
            manifest = self._prompt_registry.resolve(
                prompt_id=EXTRACTION_PROMPT_ID,
                prompt_version=EXTRACTION_PROMPT_VERSION,
                schema_id=EXTRACTION_SCHEMA_ID,
                schema_version=EXTRACTION_SCHEMA_VERSION,
                language_code=task.language_code,
            )
            if (
                not self._engineering_mode
                or manifest.approval_state is not PromptApprovalState.ENGINEERING_ONLY
            ):
                return self._failure(ExtractionFailureCode.PACKAGE_UNAVAILABLE)
            request = self._build_request(task)
        except (PromptPackageError, ValueError):
            return self._failure(ExtractionFailureCode.PACKAGE_UNAVAILABLE)

        try:
            orchestration = await self._capability.generate_structured(request)
        except asyncio.CancelledError:
            raise
        except Exception:
            return self._failure(ExtractionFailureCode.DEPENDENCY_UNAVAILABLE)
        if orchestration.failure is not None:
            return self._failure(
                ExtractionFailureCode.DEPENDENCY_UNAVAILABLE,
                upstream=orchestration.failure.category,
            )
        result = orchestration.result
        if result is None:
            return self._failure(ExtractionFailureCode.DEPENDENCY_UNAVAILABLE)
        if result.finish_reason is not FinishReason.STOP:
            return self._failure(ExtractionFailureCode.INCOMPLETE_OUTPUT)
        if not self._correlates(request, result):
            return self._failure(ExtractionFailureCode.CORRELATION_INVALID)
        try:
            payload = dict(result.validated_payload)
            required = frozenset(ExtractionEnvelope.model_fields)
            if frozenset(payload) != required:
                raise ValueError("wrong root fields")
            envelope = ExtractionEnvelope.model_validate(payload)
        except (ValidationError, ValueError, TypeError):
            return self._failure(ExtractionFailureCode.OUTPUT_SCHEMA_INVALID)
        if (
            envelope.provenance.provider_id != result.provider_id
            or envelope.provenance.provider_model_id != result.provider_model_id
            or envelope.provenance.provider_model_version != result.provider_model_version
            or envelope.provenance.source_references != result.provenance.source_references
        ):
            return self._failure(ExtractionFailureCode.CORRELATION_INVALID)
        try:
            validated = validate_extraction(task, envelope)
        except ExtractionValidationError:
            return self._failure(ExtractionFailureCode.EVIDENCE_INVALID)
        return ExtractionOutcome(result=validated)

    def _build_request(self, task: ClinicalExtractionTask) -> StructuredLLMRequest:
        now = self._clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("clock must be timezone aware")
        source = task.source
        return StructuredLLMRequest(
            operation_id=EXTRACTION_OPERATION_ID,
            language_code=task.language_code,
            request_id=task.request_id,
            request_contract_version=REQUEST_CONTRACT_VERSION,
            schema_id=EXTRACTION_SCHEMA_ID,
            schema_version=EXTRACTION_SCHEMA_VERSION,
            prompt_id=EXTRACTION_PROMPT_ID,
            prompt_version=EXTRACTION_PROMPT_VERSION,
            input={
                "source": {
                    "source_id": source.source_id,
                    "source_version": source.source_version,
                    "content_hash": source.content_hash,
                    "text": source.text,
                }
            },
            max_output_tokens=EXTRACTION_MAX_OUTPUT_TOKENS,
            deadline_at=now.astimezone(UTC) + timedelta(seconds=EXTRACTION_DEADLINE_SECONDS),
            retry_budget=EXTRACTION_RETRY_BUDGET,
            attempt=1,
            provider_policy_id=EXTRACTION_PROVIDER_POLICY_ID,
            provider_policy_version=EXTRACTION_PROVIDER_POLICY_VERSION,
            provenance_context=(task.source_reference,),
        )

    @staticmethod
    def _correlates(request: StructuredLLMRequest, result: StructuredLLMResult) -> bool:
        provenance = result.provenance
        return (
            result.request_id == request.request_id
            and result.operation_id == request.operation_id
            and result.request_contract_version == request.request_contract_version
            and result.schema_id == request.schema_id
            and result.schema_version == request.schema_version
            and result.prompt_id == request.prompt_id
            and result.prompt_version == request.prompt_version
            and result.attempt_count == 1
            and provenance.schema_id == result.schema_id
            and provenance.schema_version == result.schema_version
            and provenance.prompt_id == result.prompt_id
            and provenance.prompt_version == result.prompt_version
            and provenance.provider_id == result.provider_id
            and provenance.provider_model_id == result.provider_model_id
            and provenance.provider_model_version == result.provider_model_version
            and provenance.source_references == request.provenance_context
            and result.raw_retained is False
        )

    @staticmethod
    def _failure(
        code: ExtractionFailureCode,
        *,
        upstream: LLMFailureCategory | None = None,
    ) -> ExtractionOutcome:
        return ExtractionOutcome(failure=ExtractionFailure(code, upstream_category=upstream))
