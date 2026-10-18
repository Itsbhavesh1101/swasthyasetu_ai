"""Strict, immutable P8-B engineering extraction contracts."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections.abc import Mapping
from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Final, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)

from app.modules.ai_orchestration.contracts import SourceReference

EXTRACTION_OPERATION_ID: Final = "clinical_intake.extract_literal"
EXTRACTION_SCHEMA_ID: Final = "clinical_intake.candidates"
EXTRACTION_SCHEMA_VERSION: Final = "engineering.1"
EXTRACTION_PROMPT_ID: Final = "clinical_intake.literal_extraction"
EXTRACTION_PROMPT_VERSION: Final = "engineering.1"
MAX_SOURCE_CHARACTERS: Final = 2_000
MAX_CANDIDATES: Final = 16
MAX_MISSING_CANDIDATES: Final = 16
MAX_CONTRADICTIONS: Final = 8
MAX_UNCERTAINTIES: Final = 16
MAX_LITERAL_CHARACTERS: Final = 500
MAX_TASK_OUTPUT_BYTES: Final = 16_384

_OPAQUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_REQUEST_ID = re.compile(r"^req_[A-Za-z0-9_-]{8,64}$")
_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_MACHINE_REASON = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=False,
        arbitrary_types_allowed=True,
    )


class CandidateFieldKey(StrEnum):
    """Closed non-inferential text fields compatible with future P7 reconciliation."""

    CHIEF_COMPLAINT_TEXT = "CHIEF_COMPLAINT_TEXT"
    HPI_DESCRIPTIVE_TEXT = "HPI_DESCRIPTIVE_TEXT"
    HISTORY_SECTION_TEXT = "HISTORY_SECTION_TEXT"


class VerificationState(StrEnum):
    AI_EXTRACTED_UNCONFIRMED = "AI_EXTRACTED_UNCONFIRMED"


class ExtractionDisposition(StrEnum):
    CANDIDATES = "CANDIDATES"
    ABSTAINED = "ABSTAINED"
    REFUSED = "REFUSED"


class MissingReason(StrEnum):
    NOT_STATED_IN_SOURCE = "NOT_STATED_IN_SOURCE"
    AMBIGUOUS_IN_SOURCE = "AMBIGUOUS_IN_SOURCE"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"


class UncertaintyCode(StrEnum):
    AMBIGUOUS_ATTRIBUTION = "AMBIGUOUS_ATTRIBUTION"
    NEGATION_UNRESOLVED = "NEGATION_UNRESOLVED"
    TEMPORALITY_UNRESOLVED = "TEMPORALITY_UNRESOLVED"
    SUBJECT_UNRESOLVED = "SUBJECT_UNRESOLVED"
    LITERAL_SUPPORT_INSUFFICIENT = "LITERAL_SUPPORT_INSUFFICIENT"


class SourceInput(_StrictModel):
    source_id: StrictStr = Field(min_length=1, max_length=128)
    source_version: StrictStr = Field(min_length=1, max_length=64)
    content_hash: StrictStr = Field(min_length=64, max_length=64)
    text: StrictStr = Field(min_length=1, max_length=MAX_SOURCE_CHARACTERS, repr=False)

    @model_validator(mode="after")
    def validate_source(self) -> Self:
        if not _OPAQUE_ID.fullmatch(self.source_id):
            raise ValueError("source_id is not a safe opaque identifier")
        if not _VERSION.fullmatch(self.source_version):
            raise ValueError("source_version is not machine readable")
        if not _SHA256.fullmatch(self.content_hash):
            raise ValueError("content_hash must be lowercase SHA-256")
        normalized = unicodedata.normalize("NFC", self.text.replace("\r\n", "\n"))
        if normalized != self.text or "\r" in self.text:
            raise ValueError("source text must already be NFC and LF normalized")
        if any(ord(character) < 32 and character not in {"\n", "\t"} for character in self.text):
            raise ValueError("source text contains an unsupported control character")
        if sha256(self.text.encode("utf-8")).hexdigest() != self.content_hash:
            raise ValueError("source content hash does not match normalized text")
        return self


class ClinicalExtractionTask(_StrictModel):
    request_id: StrictStr = Field(min_length=1, max_length=68)
    language_code: StrictStr
    source: SourceInput = Field(repr=False)

    @model_validator(mode="after")
    def validate_task(self) -> Self:
        if not _REQUEST_ID.fullmatch(self.request_id):
            raise ValueError("request_id is invalid")
        if self.language_code != "en":
            raise ValueError("language is not approved by the engineering prompt package")
        return self

    @property
    def source_reference(self) -> SourceReference:
        return SourceReference(
            source_id=self.source.source_id,
            source_version=self.source.source_version,
            content_hash=self.source.content_hash,
        )


class EvidenceSpan(_StrictModel):
    source_id: StrictStr = Field(min_length=1, max_length=128)
    source_version: StrictStr = Field(min_length=1, max_length=64)
    content_hash: StrictStr = Field(min_length=64, max_length=64)
    start: StrictInt
    end: StrictInt
    quote: StrictStr = Field(min_length=0, max_length=MAX_LITERAL_CHARACTERS, repr=False)


def derive_candidate_id(field_key: CandidateFieldKey, evidence: EvidenceSpan, value: str) -> str:
    """Derive a stable non-patient identifier from exact versioned evidence."""
    canonical = "\x1f".join(
        (
            EXTRACTION_SCHEMA_VERSION,
            evidence.source_id,
            evidence.source_version,
            evidence.content_hash,
            str(evidence.start),
            str(evidence.end),
            field_key.value,
            value,
        )
    )
    return f"cand_{sha256(canonical.encode('utf-8')).hexdigest()[:32]}"


def _evidence_identity(evidence: EvidenceSpan) -> str:
    return "\x1e".join(
        (
            evidence.source_id,
            evidence.source_version,
            evidence.content_hash,
            str(evidence.start),
            str(evidence.end),
            evidence.quote,
        )
    )


def derive_missing_candidate_id(
    field_key: CandidateFieldKey,
    reason: MissingReason,
    source_references: tuple[EvidenceSpan, ...],
) -> str:
    canonical = "\x1f".join(
        (
            EXTRACTION_SCHEMA_VERSION,
            field_key.value,
            reason.value,
            *(_evidence_identity(reference) for reference in source_references),
        )
    )
    return f"missing_{sha256(canonical.encode('utf-8')).hexdigest()[:32]}"


def derive_contradiction_candidate_id(
    field_key: CandidateFieldKey, left: EvidenceSpan, right: EvidenceSpan
) -> str:
    canonical = "\x1f".join(
        (
            EXTRACTION_SCHEMA_VERSION,
            field_key.value,
            _evidence_identity(left),
            _evidence_identity(right),
        )
    )
    return f"conflict_{sha256(canonical.encode('utf-8')).hexdigest()[:32]}"


class CandidateFact(_StrictModel):
    candidate_id: StrictStr = Field(min_length=6, max_length=64)
    field_key: CandidateFieldKey
    value: StrictStr = Field(min_length=1, max_length=MAX_LITERAL_CHARACTERS, repr=False)
    evidence: EvidenceSpan = Field(repr=False)
    verification_state: VerificationState
    confidence: StrictFloat | None = None

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float | None) -> float | None:
        if value is not None and (not math.isfinite(value) or not 0.0 <= value <= 1.0):
            raise ValueError("confidence must be finite and from zero to one")
        return value


class MissingInformationCandidate(_StrictModel):
    candidate_id: StrictStr = Field(min_length=6, max_length=64)
    field_key: CandidateFieldKey
    reason: MissingReason
    source_references: Annotated[tuple[EvidenceSpan, ...], Field(min_length=1, max_length=2)] = (
        Field(repr=False)
    )

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        expected = derive_missing_candidate_id(self.field_key, self.reason, self.source_references)
        if self.candidate_id != expected:
            raise ValueError("missing-information candidate identity is invalid")
        return self


class ContradictionCandidate(_StrictModel):
    candidate_id: StrictStr = Field(min_length=6, max_length=64)
    field_key: CandidateFieldKey
    left: EvidenceSpan = Field(repr=False)
    right: EvidenceSpan = Field(repr=False)

    @model_validator(mode="after")
    def require_distinct_evidence(self) -> Self:
        if self.left == self.right:
            raise ValueError("contradiction evidence must be distinguishable")
        expected = derive_contradiction_candidate_id(self.field_key, self.left, self.right)
        if self.candidate_id != expected:
            raise ValueError("contradiction candidate identity is invalid")
        return self


class TaskUncertainty(_StrictModel):
    code: UncertaintyCode


class ExtractionProvenance(_StrictModel):
    provider_id: StrictStr = Field(min_length=1, max_length=128)
    provider_model_id: StrictStr = Field(min_length=1, max_length=128)
    provider_model_version: StrictStr = Field(min_length=1, max_length=64)
    source_references: Annotated[tuple[SourceReference, ...], Field(min_length=1, max_length=1)] = (
        Field(repr=False)
    )

    @field_validator("source_references", mode="before")
    @classmethod
    def parse_source_references(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return tuple(
                SourceReference.from_dict(item) if isinstance(item, Mapping) else item
                for item in value
            )
        return value


class ExtractionEnvelope(_StrictModel):
    schema_id: StrictStr = EXTRACTION_SCHEMA_ID
    schema_version: StrictStr = EXTRACTION_SCHEMA_VERSION
    prompt_id: StrictStr = EXTRACTION_PROMPT_ID
    prompt_version: StrictStr = EXTRACTION_PROMPT_VERSION
    disposition: ExtractionDisposition
    candidate_facts: Annotated[tuple[CandidateFact, ...], Field(max_length=MAX_CANDIDATES)] = ()
    missing_information_candidates: Annotated[
        tuple[MissingInformationCandidate, ...], Field(max_length=MAX_MISSING_CANDIDATES)
    ] = ()
    contradiction_candidates: Annotated[
        tuple[ContradictionCandidate, ...], Field(max_length=MAX_CONTRADICTIONS)
    ] = ()
    uncertainty: Annotated[tuple[TaskUncertainty, ...], Field(max_length=MAX_UNCERTAINTIES)] = ()
    abstention_reason: StrictStr | None = Field(default=None, min_length=1, max_length=64)
    refusal_reason: StrictStr | None = Field(default=None, min_length=1, max_length=64)
    provenance: ExtractionProvenance = Field(repr=False)

    @model_validator(mode="after")
    def validate_envelope(self) -> Self:
        if (
            self.schema_id != EXTRACTION_SCHEMA_ID
            or self.schema_version != EXTRACTION_SCHEMA_VERSION
            or self.prompt_id != EXTRACTION_PROMPT_ID
            or self.prompt_version != EXTRACTION_PROMPT_VERSION
        ):
            raise ValueError("unsupported extraction schema or prompt identity")
        ids = [candidate.candidate_id for candidate in self.candidate_facts]
        ids.extend(candidate.candidate_id for candidate in self.missing_information_candidates)
        ids.extend(candidate.candidate_id for candidate in self.contradiction_candidates)
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate candidate identifiers are forbidden")
        field_keys = [candidate.field_key for candidate in self.candidate_facts]
        if len(field_keys) != len(set(field_keys)):
            raise ValueError("incompatible duplicate field claims are forbidden")
        if self.disposition is ExtractionDisposition.CANDIDATES:
            if not self.candidate_facts or self.abstention_reason or self.refusal_reason:
                raise ValueError("candidate disposition requires candidates only")
        elif self.disposition is ExtractionDisposition.ABSTAINED:
            if self.candidate_facts:
                raise ValueError("abstention requires no candidate facts")
            if not self.abstention_reason or self.refusal_reason:
                raise ValueError("abstention requires one safe machine reason")
        elif self.candidate_facts or self.abstention_reason or not self.refusal_reason:
            raise ValueError("refusal requires no candidates and one safe machine reason")
        for reason in (self.abstention_reason, self.refusal_reason):
            if reason is not None and not _MACHINE_REASON.fullmatch(reason):
                raise ValueError("reasons must be bounded machine codes")
        serialized = json.dumps(self.model_dump(mode="json"), separators=(",", ":"))
        if len(serialized.encode("utf-8")) > MAX_TASK_OUTPUT_BYTES:
            raise ValueError("extraction output exceeds the serialized byte limit")
        return self
