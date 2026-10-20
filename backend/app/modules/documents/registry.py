"""Explicit immutable metadata registry for synthetic document routing receipts.

Descriptors in this module contain no callable, provider, import path, or runtime
activation. A successful lookup is still a ``NOOP_ABSTAIN`` receipt.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from app.modules.documents.classification import (
    PROCESSABLE_DOCUMENT_TYPES,
    ClassificationContractError,
    ClassificationDecision,
    ClassificationDisposition,
    DocumentType,
)
from app.modules.documents.contracts import (
    OCR_REQUEST_CONTRACT_VERSION,
    PARSER_REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    DocumentContractError,
    OCRMode,
    ParserMode,
)

PROCESSOR_REGISTRY_SCHEMA_VERSION: Final = "document-processor-registry.v1"
PROCESSOR_RECEIPT_SCHEMA_VERSION: Final = "document-processor-receipt.v1"
MAX_PROCESSOR_DESCRIPTORS: Final = 32

_PROCESSOR_ID = re.compile(r"^[A-Z][A-Za-z0-9]{0,47}Processor$")
_VERSION = re.compile(r"^v[1-9][0-9]{0,5}$")
_TYPE_ORDER: Final = {item: index for index, item in enumerate(DocumentType)}


class ProcessorAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class ProcessorDisposition(StrEnum):
    NOOP_ABSTAIN = "NOOP_ABSTAIN"


class RegistryResolutionStatus(StrEnum):
    PINNED_METADATA = "PINNED_METADATA"
    ABSTAINED = "ABSTAINED"
    UNAVAILABLE = "UNAVAILABLE"
    AMBIGUOUS = "AMBIGUOUS"


class RegistryReason(StrEnum):
    EXACT_PIN = "EXACT_PIN"
    CLASSIFICATION_NOT_SELECTED = "CLASSIFICATION_NOT_SELECTED"
    NO_PIN = "NO_PIN"
    MULTIPLE_UNPINNED_VERSIONS = "MULTIPLE_UNPINNED_VERSIONS"


class ProcessorRegistryCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_VERSION = "INVALID_VERSION"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    AMBIGUOUS_OWNERSHIP = "AMBIGUOUS_OWNERSHIP"
    UNKNOWN_PROCESSOR = "UNKNOWN_PROCESSOR"
    INCOMPATIBLE_DECLARATION = "INCOMPATIBLE_DECLARATION"
    INVALID_RECEIPT = "INVALID_RECEIPT"
    UNEXPECTED_FIELD = "UNEXPECTED_FIELD"


class ProcessorRegistryError(ValueError):
    """Content-free registry failure."""

    def __init__(self, code: ProcessorRegistryCode) -> None:
        self.code = code
        super().__init__(code.value)


def _fail(code: ProcessorRegistryCode) -> ProcessorRegistryError:
    return ProcessorRegistryError(code)


@dataclass(frozen=True, slots=True, kw_only=True, init=False)
class ProcessorDescriptor:
    processor_id: str
    processor_version: str
    accepted_types: tuple[DocumentType, ...]
    parser_modes: tuple[ParserMode, ...]
    ocr_modes: tuple[OCRMode, ...]
    input_schema_versions: tuple[str, ...]
    output_schema_version: str
    authority: ProcessorAuthority
    disposition: ProcessorDisposition

    def __init__(
        self,
        *,
        processor_id: str,
        processor_version: str,
        accepted_types: tuple[DocumentType, ...],
        parser_modes: tuple[ParserMode, ...],
        ocr_modes: tuple[OCRMode, ...],
        input_schema_versions: tuple[str, ...],
        output_schema_version: str,
        authority: ProcessorAuthority,
        disposition: ProcessorDisposition,
        **unexpected: object,
    ) -> None:
        if unexpected:
            raise _fail(ProcessorRegistryCode.UNEXPECTED_FIELD)
        object.__setattr__(self, "processor_id", processor_id)
        object.__setattr__(self, "processor_version", processor_version)
        object.__setattr__(self, "accepted_types", accepted_types)
        object.__setattr__(self, "parser_modes", parser_modes)
        object.__setattr__(self, "ocr_modes", ocr_modes)
        object.__setattr__(self, "input_schema_versions", input_schema_versions)
        object.__setattr__(self, "output_schema_version", output_schema_version)
        object.__setattr__(self, "authority", authority)
        object.__setattr__(self, "disposition", disposition)
        self.__post_init__()

    def __post_init__(self) -> None:
        if type(self.processor_id) is not str or _PROCESSOR_ID.fullmatch(self.processor_id) is None:
            raise _fail(ProcessorRegistryCode.INVALID_VALUE)
        if (
            type(self.processor_version) is not str
            or _VERSION.fullmatch(self.processor_version) is None
        ):
            raise _fail(ProcessorRegistryCode.INVALID_VERSION)
        if (
            type(self.accepted_types) is not tuple
            or not self.accepted_types
            or any(type(item) is not DocumentType for item in self.accepted_types)
        ):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        if any(item not in PROCESSABLE_DOCUMENT_TYPES for item in self.accepted_types):
            raise _fail(ProcessorRegistryCode.INCOMPATIBLE_DECLARATION)
        if self.accepted_types != tuple(
            sorted(set(self.accepted_types), key=lambda item: _TYPE_ORDER[item])
        ):
            raise _fail(ProcessorRegistryCode.DUPLICATE_IDENTITY)
        if type(self.parser_modes) is not tuple or any(
            type(item) is not ParserMode for item in self.parser_modes
        ):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        if type(self.ocr_modes) is not tuple or any(
            type(item) is not OCRMode for item in self.ocr_modes
        ):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        if not self.parser_modes and not self.ocr_modes:
            raise _fail(ProcessorRegistryCode.INCOMPATIBLE_DECLARATION)
        if self.parser_modes != tuple(sorted(set(self.parser_modes), key=lambda item: item.value)):
            raise _fail(ProcessorRegistryCode.DUPLICATE_IDENTITY)
        if self.ocr_modes != tuple(sorted(set(self.ocr_modes), key=lambda item: item.value)):
            raise _fail(ProcessorRegistryCode.DUPLICATE_IDENTITY)
        if (
            type(self.input_schema_versions) is not tuple
            or not self.input_schema_versions
            or any(type(item) is not str for item in self.input_schema_versions)
        ):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        expected_inputs = tuple(
            sorted(
                {
                    *((PARSER_REQUEST_CONTRACT_VERSION,) if self.parser_modes else ()),
                    *((OCR_REQUEST_CONTRACT_VERSION,) if self.ocr_modes else ()),
                }
            )
        )
        if self.input_schema_versions != expected_inputs:
            raise _fail(ProcessorRegistryCode.INVALID_VERSION)
        if self.output_schema_version != RESULT_CONTRACT_VERSION:
            raise _fail(ProcessorRegistryCode.INVALID_VERSION)
        if self.authority is not ProcessorAuthority.ENGINEERING_ONLY:
            raise _fail(ProcessorRegistryCode.INCOMPATIBLE_DECLARATION)
        if self.disposition is not ProcessorDisposition.NOOP_ABSTAIN:
            raise _fail(ProcessorRegistryCode.INCOMPATIBLE_DECLARATION)

    @property
    def identity(self) -> tuple[str, str]:
        return (self.processor_id, self.processor_version)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProcessorPin:
    document_type: DocumentType
    processor_id: str
    processor_version: str

    def __post_init__(self) -> None:
        if type(self.document_type) is not DocumentType:
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        if self.document_type not in PROCESSABLE_DOCUMENT_TYPES:
            raise _fail(ProcessorRegistryCode.INCOMPATIBLE_DECLARATION)
        if type(self.processor_id) is not str or _PROCESSOR_ID.fullmatch(self.processor_id) is None:
            raise _fail(ProcessorRegistryCode.INVALID_VALUE)
        if (
            type(self.processor_version) is not str
            or _VERSION.fullmatch(self.processor_version) is None
        ):
            raise _fail(ProcessorRegistryCode.INVALID_VERSION)


type _DescriptorSnapshot = tuple[
    str,
    str,
    tuple[DocumentType, ...],
    tuple[ParserMode, ...],
    tuple[OCRMode, ...],
    tuple[str, ...],
    str,
    ProcessorAuthority,
    ProcessorDisposition,
]


def _snapshot(descriptor: ProcessorDescriptor) -> _DescriptorSnapshot:
    validated = ProcessorDescriptor(
        processor_id=descriptor.processor_id,
        processor_version=descriptor.processor_version,
        accepted_types=descriptor.accepted_types,
        parser_modes=descriptor.parser_modes,
        ocr_modes=descriptor.ocr_modes,
        input_schema_versions=descriptor.input_schema_versions,
        output_schema_version=descriptor.output_schema_version,
        authority=descriptor.authority,
        disposition=descriptor.disposition,
    )
    return (
        validated.processor_id,
        validated.processor_version,
        validated.accepted_types,
        validated.parser_modes,
        validated.ocr_modes,
        validated.input_schema_versions,
        validated.output_schema_version,
        validated.authority,
        validated.disposition,
    )


def _restore(snapshot: _DescriptorSnapshot) -> ProcessorDescriptor:
    return ProcessorDescriptor(
        processor_id=snapshot[0],
        processor_version=snapshot[1],
        accepted_types=snapshot[2],
        parser_modes=snapshot[3],
        ocr_modes=snapshot[4],
        input_schema_versions=snapshot[5],
        output_schema_version=snapshot[6],
        authority=snapshot[7],
        disposition=snapshot[8],
    )


def _snapshot_pin(pin: ProcessorPin) -> ProcessorPin:
    """Detach and revalidate caller-owned pin fields before any hashing."""

    try:
        return ProcessorPin(
            document_type=pin.document_type,
            processor_id=pin.processor_id,
            processor_version=pin.processor_version,
        )
    except ProcessorRegistryError:
        raise
    except (AttributeError, TypeError):
        raise _fail(ProcessorRegistryCode.INVALID_TYPE) from None


def _snapshot_decision(decision: ClassificationDecision) -> ClassificationDecision:
    """Detach and revalidate a complete classification at the registry boundary."""

    try:
        return ClassificationDecision(
            request_id=decision.request_id,
            document_id=decision.document_id,
            processing_attempt_id=decision.processing_attempt_id,
            source=decision.source,
            candidates=decision.candidates,
            schema_version=decision.schema_version,
            config_version=decision.config_version,
            authority=decision.authority,
            disposition=decision.disposition,
            reason=decision.reason,
            selected_type=decision.selected_type,
        )
    except (ClassificationContractError, DocumentContractError, AttributeError, TypeError):
        raise _fail(ProcessorRegistryCode.INCOMPATIBLE_DECLARATION) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class ProcessorResolutionReceipt:
    registry_schema_version: str
    receipt_schema_version: str
    classification_schema_version: str
    document_type: DocumentType | None
    processor_id: str | None
    processor_version: str | None
    parser_modes: tuple[ParserMode, ...]
    ocr_modes: tuple[OCRMode, ...]
    input_schema_versions: tuple[str, ...]
    output_schema_version: str | None
    authority: ProcessorAuthority
    processor_disposition: ProcessorDisposition
    status: RegistryResolutionStatus
    reason: RegistryReason

    def __post_init__(self) -> None:
        if (
            self.registry_schema_version != PROCESSOR_REGISTRY_SCHEMA_VERSION
            or self.receipt_schema_version != PROCESSOR_RECEIPT_SCHEMA_VERSION
            or self.classification_schema_version != "synthetic-document-classification.v1"
        ):
            raise _fail(ProcessorRegistryCode.INVALID_VERSION)
        if self.authority is not ProcessorAuthority.ENGINEERING_ONLY or (
            self.processor_disposition is not ProcessorDisposition.NOOP_ABSTAIN
        ):
            raise _fail(ProcessorRegistryCode.INVALID_RECEIPT)
        if (
            type(self.status) is not RegistryResolutionStatus
            or type(self.reason) is not RegistryReason
        ):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        if type(self.parser_modes) is not tuple or any(
            type(item) is not ParserMode for item in self.parser_modes
        ):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        if type(self.ocr_modes) is not tuple or any(
            type(item) is not OCRMode for item in self.ocr_modes
        ):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        if type(self.input_schema_versions) is not tuple or any(
            type(item) is not str for item in self.input_schema_versions
        ):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        selected = self.status is RegistryResolutionStatus.PINNED_METADATA
        values_present = (
            type(self.document_type) is DocumentType
            and type(self.processor_id) is str
            and type(self.processor_version) is str
            and type(self.output_schema_version) is str
            and bool(self.parser_modes or self.ocr_modes)
            and bool(self.input_schema_versions)
        )
        if selected != values_present:
            raise _fail(ProcessorRegistryCode.INVALID_RECEIPT)
        if selected:
            if (
                self.document_type is None
                or self.processor_id is None
                or self.processor_version is None
            ):
                raise _fail(ProcessorRegistryCode.INVALID_RECEIPT)
            ProcessorPin(
                document_type=self.document_type,
                processor_id=self.processor_id,
                processor_version=self.processor_version,
            )
            if self.parser_modes != tuple(
                sorted(set(self.parser_modes), key=lambda item: item.value)
            ) or self.ocr_modes != tuple(sorted(set(self.ocr_modes), key=lambda item: item.value)):
                raise _fail(ProcessorRegistryCode.INVALID_RECEIPT)
            expected_inputs = tuple(
                sorted(
                    {
                        *((PARSER_REQUEST_CONTRACT_VERSION,) if self.parser_modes else ()),
                        *((OCR_REQUEST_CONTRACT_VERSION,) if self.ocr_modes else ()),
                    }
                )
            )
            if (
                self.input_schema_versions != expected_inputs
                or self.output_schema_version != RESULT_CONTRACT_VERSION
                or self.reason is not RegistryReason.EXACT_PIN
            ):
                raise _fail(ProcessorRegistryCode.INVALID_RECEIPT)
        else:
            invalid_empty = any(
                value is not None
                for value in (
                    self.document_type,
                    self.processor_id,
                    self.processor_version,
                    self.output_schema_version,
                )
            ) or bool(self.parser_modes or self.ocr_modes or self.input_schema_versions)
            invalid_reason = (
                (
                    self.status is RegistryResolutionStatus.ABSTAINED
                    and self.reason is not RegistryReason.CLASSIFICATION_NOT_SELECTED
                )
                or (
                    self.status is RegistryResolutionStatus.UNAVAILABLE
                    and self.reason is not RegistryReason.NO_PIN
                )
                or (
                    self.status is RegistryResolutionStatus.AMBIGUOUS
                    and self.reason is not RegistryReason.MULTIPLE_UNPINNED_VERSIONS
                )
            )
            if invalid_empty or invalid_reason:
                raise _fail(ProcessorRegistryCode.INVALID_RECEIPT)


@dataclass(frozen=True, slots=True, init=False)
class ProcessorRegistry:
    _descriptors: Mapping[tuple[str, str], _DescriptorSnapshot] = field(repr=False)
    _pins: Mapping[DocumentType, tuple[str, str]] = field(repr=False)
    _owners: Mapping[DocumentType, str] = field(repr=False)

    def __init__(
        self,
        *,
        descriptors: tuple[ProcessorDescriptor, ...],
        pins: tuple[ProcessorPin, ...] = (),
        **unexpected: object,
    ) -> None:
        if unexpected:
            raise _fail(ProcessorRegistryCode.UNEXPECTED_FIELD)
        if type(descriptors) is not tuple or any(
            type(item) is not ProcessorDescriptor for item in descriptors
        ):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        if len(descriptors) > MAX_PROCESSOR_DESCRIPTORS:
            raise _fail(ProcessorRegistryCode.LIMIT_EXCEEDED)
        if type(pins) is not tuple or any(type(item) is not ProcessorPin for item in pins):
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)

        registrations: dict[tuple[str, str], _DescriptorSnapshot] = {}
        owners: dict[DocumentType, str] = {}
        for descriptor in descriptors:
            snapshot = _snapshot(descriptor)
            identity = (snapshot[0], snapshot[1])
            if identity in registrations:
                raise _fail(ProcessorRegistryCode.DUPLICATE_IDENTITY)
            for document_type in snapshot[2]:
                owner = owners.get(document_type)
                if owner is not None and owner != snapshot[0]:
                    raise _fail(ProcessorRegistryCode.AMBIGUOUS_OWNERSHIP)
                owners[document_type] = snapshot[0]
            registrations[identity] = snapshot

        configured: dict[DocumentType, tuple[str, str]] = {}
        for supplied_pin in pins:
            validated_pin = _snapshot_pin(supplied_pin)
            if validated_pin.document_type in configured:
                raise _fail(ProcessorRegistryCode.AMBIGUOUS_OWNERSHIP)
            identity = (validated_pin.processor_id, validated_pin.processor_version)
            selected_snapshot = registrations.get(identity)
            if selected_snapshot is None:
                raise _fail(ProcessorRegistryCode.UNKNOWN_PROCESSOR)
            if validated_pin.document_type not in selected_snapshot[2]:
                raise _fail(ProcessorRegistryCode.INCOMPATIBLE_DECLARATION)
            configured[validated_pin.document_type] = identity

        object.__setattr__(self, "_descriptors", MappingProxyType(registrations.copy()))
        object.__setattr__(self, "_pins", MappingProxyType(configured.copy()))
        object.__setattr__(self, "_owners", MappingProxyType(owners.copy()))

    @property
    def descriptors(self) -> tuple[ProcessorDescriptor, ...]:
        return tuple(
            _restore(snapshot)
            for _, snapshot in sorted(self._descriptors.items(), key=lambda item: item[0])
        )

    def lookup(self, *, processor_id: object, processor_version: object) -> ProcessorDescriptor:
        if type(processor_id) is not str or type(processor_version) is not str:
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        snapshot = self._descriptors.get((processor_id, processor_version))
        if snapshot is None:
            raise _fail(ProcessorRegistryCode.UNKNOWN_PROCESSOR)
        return _restore(snapshot)

    def resolve(self, decision: ClassificationDecision) -> ProcessorResolutionReceipt:
        if type(decision) is not ClassificationDecision:
            raise _fail(ProcessorRegistryCode.INVALID_TYPE)
        validated_decision = _snapshot_decision(decision)
        if validated_decision.disposition is not ClassificationDisposition.SELECTED:
            return _empty_receipt(
                decision=validated_decision,
                status=RegistryResolutionStatus.ABSTAINED,
                reason=RegistryReason.CLASSIFICATION_NOT_SELECTED,
            )
        document_type = validated_decision.selected_type
        if document_type is None:
            raise _fail(ProcessorRegistryCode.INVALID_RECEIPT)
        selected_identity = self._pins.get(document_type)
        if selected_identity is None:
            versions = tuple(
                key for key, snapshot in self._descriptors.items() if document_type in snapshot[2]
            )
            return _empty_receipt(
                decision=validated_decision,
                status=(
                    RegistryResolutionStatus.AMBIGUOUS
                    if len(versions) > 1
                    else RegistryResolutionStatus.UNAVAILABLE
                ),
                reason=(
                    RegistryReason.MULTIPLE_UNPINNED_VERSIONS
                    if len(versions) > 1
                    else RegistryReason.NO_PIN
                ),
            )
        descriptor = self.lookup(
            processor_id=selected_identity[0], processor_version=selected_identity[1]
        )
        if document_type not in descriptor.accepted_types:
            raise _fail(ProcessorRegistryCode.INCOMPATIBLE_DECLARATION)
        return ProcessorResolutionReceipt(
            registry_schema_version=PROCESSOR_REGISTRY_SCHEMA_VERSION,
            receipt_schema_version=PROCESSOR_RECEIPT_SCHEMA_VERSION,
            classification_schema_version=validated_decision.schema_version,
            document_type=document_type,
            processor_id=descriptor.processor_id,
            processor_version=descriptor.processor_version,
            parser_modes=descriptor.parser_modes,
            ocr_modes=descriptor.ocr_modes,
            input_schema_versions=descriptor.input_schema_versions,
            output_schema_version=descriptor.output_schema_version,
            authority=ProcessorAuthority.ENGINEERING_ONLY,
            processor_disposition=ProcessorDisposition.NOOP_ABSTAIN,
            status=RegistryResolutionStatus.PINNED_METADATA,
            reason=RegistryReason.EXACT_PIN,
        )


def _empty_receipt(
    *,
    decision: ClassificationDecision,
    status: RegistryResolutionStatus,
    reason: RegistryReason,
) -> ProcessorResolutionReceipt:
    return ProcessorResolutionReceipt(
        registry_schema_version=PROCESSOR_REGISTRY_SCHEMA_VERSION,
        receipt_schema_version=PROCESSOR_RECEIPT_SCHEMA_VERSION,
        classification_schema_version=decision.schema_version,
        document_type=None,
        processor_id=None,
        processor_version=None,
        parser_modes=(),
        ocr_modes=(),
        input_schema_versions=(),
        output_schema_version=None,
        authority=ProcessorAuthority.ENGINEERING_ONLY,
        processor_disposition=ProcessorDisposition.NOOP_ABSTAIN,
        status=status,
        reason=reason,
    )


_CANONICAL_PROCESSORS: Final = (
    ("PrescriptionProcessor", DocumentType.PRESCRIPTION),
    ("LabReportProcessor", DocumentType.LAB_REPORT),
    ("DischargeSummaryProcessor", DocumentType.DISCHARGE_SUMMARY),
    ("DiagnosticReportProcessor", DocumentType.DIAGNOSTIC_REPORT),
    ("ImagingReportProcessor", DocumentType.IMAGING_REPORT),
    ("ReferralLetterProcessor", DocumentType.REFERRAL_LETTER),
)


def build_synthetic_processor_registry() -> ProcessorRegistry:
    """Build explicit inactive metadata; this factory performs no registration side effect."""

    descriptors = tuple(
        ProcessorDescriptor(
            processor_id=processor_id,
            processor_version="v1",
            accepted_types=(document_type,),
            parser_modes=(),
            ocr_modes=(OCRMode.TEXT,),
            input_schema_versions=(OCR_REQUEST_CONTRACT_VERSION,),
            output_schema_version=RESULT_CONTRACT_VERSION,
            authority=ProcessorAuthority.ENGINEERING_ONLY,
            disposition=ProcessorDisposition.NOOP_ABSTAIN,
        )
        for processor_id, document_type in _CANONICAL_PROCESSORS
    )
    pins = tuple(
        ProcessorPin(
            document_type=document_type,
            processor_id=processor_id,
            processor_version="v1",
        )
        for processor_id, document_type in _CANONICAL_PROCESSORS
    )
    return ProcessorRegistry(descriptors=descriptors, pins=pins)
