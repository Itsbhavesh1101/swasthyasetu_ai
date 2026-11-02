"""Deterministic, content-free P11 engineering demonstration."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.modules.documents.candidates import (
    CANDIDATE_SCHEMA_VERSION,
    EVIDENCE_SCHEMA_VERSION,
    CandidateAuthority,
    CandidateDisposition,
    CandidateReason,
    EvidenceKind,
    StructuralEvidenceRef,
    SyntheticCandidateRef,
    SyntheticDocumentCandidate,
)
from app.modules.documents.classification import (
    CLASSIFICATION_CONFIG_VERSION,
    CLASSIFICATION_SCHEMA_VERSION,
    ClassificationRequest,
    DocumentType,
    SyntheticClassificationCandidate,
    SyntheticClassificationRef,
    classify_synthetic,
)
from app.modules.documents.contracts import (
    OCR_REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    BlockKind,
    Confidence,
    ConfidenceKind,
    DocumentProcessingResult,
    NormalizedBox,
    PageResult,
    PageSelection,
    PageStatus,
    ProviderProvenance,
    ResourceUsage,
    ResultStatus,
    SyntheticSourceRef,
    TextBlock,
)
from app.modules.documents.domain import (
    DocumentStatus,
    SyntheticDocumentDescriptor,
    SyntheticIdempotencyKey,
    SyntheticOwnerScope,
    SyntheticRepresentation,
    SyntheticSha256,
    SyntheticValidationDecision,
    SyntheticValidationDisposition,
    create_synthetic_document_state,
)
from app.modules.documents.evidence import verify_structural_evidence
from app.modules.documents.ingestion import assess_synthetic_ingestion
from app.modules.documents.processing import (
    AttemptStage,
    AttemptStatus,
    ProcessingAttempt,
    RetryClassification,
)
from app.modules.documents.registry import build_synthetic_processor_registry
from app.shared.types import OpaqueId


def _id(value: int) -> OpaqueId:
    return OpaqueId(UUID(int=value))


@dataclass(frozen=True, slots=True)
class EngineeringDocumentResult:
    status: str
    classification: str
    ingestion_disposition: str
    lifecycle: tuple[str, ...]
    processing_status: str
    processed_pages: int
    provider: str
    external_egress: bool
    document_type: str
    classification_disposition: str
    classification_reason: str
    processor_id: str
    processor_version: str
    processor_disposition: str
    candidate_disposition: str
    evidence_references: int
    structural_match: str
    source_access: str
    confidence: str
    notice: str


class EngineeringDocumentDemoService:
    """Compose immutable P11 contracts without I/O, persistence, or source access."""

    def project(self, *, clock: datetime | None = None) -> EngineeringDocumentResult:
        now = clock or datetime.now(UTC)
        request_id = _id(1)
        document_id = _id(2)
        attempt_id = _id(3)
        source = SyntheticSourceRef("SYNTHETIC_SOURCE_COLLEGE_DEMO")
        owner = SyntheticOwnerScope("SYNTHETIC_OWNER_COLLEGE_DEMO")

        descriptor = SyntheticDocumentDescriptor(
            document_id=document_id,
            source=source,
            owner_scope=owner,
            idempotency_key=SyntheticIdempotencyKey("SYNTHETIC_IDEMPOTENCY_COLLEGE_DEMO"),
            sha256_claim=SyntheticSha256("a" * 64),
            document_type=DocumentType.LAB_REPORT,
            representation=SyntheticRepresentation.SYNTHETIC_PDF,
            byte_count_claim=1024,
            page_count_claim=1,
            metadata_version=1,
            generation=1,
            declared_at=now,
        )
        ingestion = assess_synthetic_ingestion(
            descriptor,
            expected_owner_scope=owner,
            expected_source=source,
            expected_representation=SyntheticRepresentation.SYNTHETIC_PDF,
        )
        lifecycle = create_synthetic_document_state(descriptor)
        lifecycle_tokens = [lifecycle.status.value]

        def move(target: DocumentStatus, **extra: object) -> None:
            nonlocal lifecycle
            lifecycle = lifecycle.transition(
                target,
                at=now,
                expected_document_id=document_id,
                expected_state_version=lifecycle.state_version,
                expected_metadata_version=descriptor.metadata_version,
                expected_generation=lifecycle.generation,
                **extra,  # type: ignore[arg-type]
            )
            lifecycle_tokens.append(lifecycle.status.value)

        move(DocumentStatus.VALIDATING)
        move(
            DocumentStatus.ACCEPTED,
            decision=SyntheticValidationDecision(
                document_id=document_id,
                source=source,
                owner_scope=owner,
                metadata_version=1,
                disposition=SyntheticValidationDisposition.SYNTHETIC_COMPATIBLE,
                decided_at=now,
            ),
        )
        move(DocumentStatus.QUEUED, new_attempt_id=attempt_id)
        move(DocumentStatus.PROCESSING)

        attempt = ProcessingAttempt(
            attempt_id=attempt_id,
            document_id=document_id,
            request_id=request_id,
            generation=1,
            source_version="synthetic.v1",
            routing_version="routing.v1",
            idempotency_ref="synthetic.college.demo",
            stage=AttemptStage.QUEUED,
            status=AttemptStatus.QUEUED,
            created_at=now,
            deadline_at=now + timedelta(seconds=5),
            started_at=None,
            completed_at=None,
            failure_code=None,
            retry_classification=RetryClassification.NONE,
            retry_budget=0,
        ).start(at=now, generation=1)

        box = NormalizedBox(0.1, 0.2, 0.9, 0.4)
        processed = DocumentProcessingResult(
            result_contract_version=RESULT_CONTRACT_VERSION,
            request_contract_version=OCR_REQUEST_CONTRACT_VERSION,
            request_id=request_id,
            document_id=document_id,
            processing_attempt_id=attempt_id,
            source=source,
            requested_pages=PageSelection((1,)),
            status=ResultStatus.SUCCEEDED,
            pages=(
                PageResult(
                    page_number=1,
                    status=PageStatus.SUCCEEDED,
                    width=100,
                    height=100,
                    rotation_degrees=0,
                    languages=(),
                    blocks=(
                        TextBlock(
                            block_id="block.synthetic",
                            kind=BlockKind.TEXT,
                            text="SYNTHETIC_DOCUMENT_TOKEN",
                            reading_order=0,
                            box=box,
                            confidence=Confidence(ConfidenceKind.UNKNOWN, None),
                        ),
                    ),
                    tables=(),
                ),
            ),
            provenance=ProviderProvenance(
                provider_id="engineering.fixture",
                adapter_id="engineering.offline",
                adapter_version="v1",
                engine_id="synthetic.contract",
                engine_version="v1",
                routing_version="routing.v1",
                runtime_backend="in.memory",
            ),
            warnings=(),
            error_code=None,
            resource_usage=ResourceUsage(elapsed_ms=0.0, processed_pages=1, peak_memory_bytes=0),
        )
        attempt = attempt.succeed(at=now, generation=1)

        label = SyntheticClassificationCandidate(
            candidate_ref=SyntheticClassificationRef("SYNTHETIC_CLASSIFICATION_COLLEGE_DEMO"),
            request_id=request_id,
            document_id=document_id,
            processing_attempt_id=attempt_id,
            source=source,
            document_type=DocumentType.LAB_REPORT,
            schema_version=CLASSIFICATION_SCHEMA_VERSION,
            config_version=CLASSIFICATION_CONFIG_VERSION,
        )
        classification = classify_synthetic(
            ClassificationRequest(
                request_id=request_id,
                document_id=document_id,
                processing_attempt_id=attempt_id,
                source=source,
                candidates=(label,),
                schema_version=CLASSIFICATION_SCHEMA_VERSION,
                config_version=CLASSIFICATION_CONFIG_VERSION,
            )
        )
        receipt = build_synthetic_processor_registry().resolve(classification)
        evidence = StructuralEvidenceRef(
            evidence_schema_version=EVIDENCE_SCHEMA_VERSION,
            request_id=request_id,
            document_id=document_id,
            processing_attempt_id=attempt_id,
            source=source,
            routing_version="routing.v1",
            page_number=1,
            kind=EvidenceKind.BLOCK,
            block_id="block.synthetic",
            box=box,
        )
        candidate = SyntheticDocumentCandidate(
            candidate_ref=SyntheticCandidateRef("SYNTHETIC_CANDIDATE_COLLEGE_DEMO"),
            request_id=request_id,
            document_id=document_id,
            processing_attempt_id=attempt_id,
            source=source,
            document_type=DocumentType.LAB_REPORT,
            processor_id="LabReportProcessor",
            processor_version="v1",
            candidate_schema_version=CANDIDATE_SCHEMA_VERSION,
            routing_version="routing.v1",
            disposition=CandidateDisposition.UNCONFIRMED,
            authority=CandidateAuthority.ENGINEERING_ONLY,
            evidence=(evidence,),
            confidence=Confidence(ConfidenceKind.UNKNOWN, None),
            reason=CandidateReason.STRUCTURAL_REFERENCE_ONLY,
            created_at=now,
        )
        match = verify_structural_evidence(
            candidate=candidate,
            result=processed,
            classification=classification,
            receipt=receipt,
        )
        move(DocumentStatus.NEEDS_REVIEW)

        return EngineeringDocumentResult(
            status=lifecycle.status.value,
            classification="ENGINEERING_ONLY",
            ingestion_disposition=ingestion.disposition.value,
            lifecycle=tuple(lifecycle_tokens),
            processing_status=attempt.status.value,
            processed_pages=processed.resource_usage.processed_pages,
            provider=processed.provenance.provider_id,
            external_egress=False,
            document_type=(
                classification.selected_type.value if classification.selected_type else ""
            ),
            classification_disposition=classification.disposition.value,
            classification_reason=classification.reason.value,
            processor_id=receipt.processor_id or "",
            processor_version=receipt.processor_version or "",
            processor_disposition=receipt.processor_disposition.value,
            candidate_disposition=candidate.disposition.value,
            evidence_references=match.matched_references,
            structural_match=match.status.value,
            source_access=match.source_access.value,
            confidence=candidate.confidence.kind.value,
            notice=(
                "Synthetic engineering metadata only. No file was uploaded, no medical value was "
                "extracted, and no clinical decision was made."
            ),
        )
