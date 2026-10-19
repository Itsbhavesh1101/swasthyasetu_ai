# SwasthyaSetu AI — Pre-P11 Document AI / OCR Specification and Readiness Pack

**Work unit:** `Pre-P11` — canonical documentation prerequisites ONLY, not P11-A/B/C/D/E implementation.
**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified baseline:** `main @ 7aad4dce8c68d008e98287d769d83d109c3cb46b`
**Merge evidence:** P10-A PR #30 MERGED with merge SHA above; reviewed feature head `400c8f19ccc6a3d1b1e91038665b0a30c3cda432`; merge tree has no change from reviewed head.
**Proposed branch:** `phase/pre-p11-document-ai-ocr-specification`
**Alembic:** `p7a_0007`; NO migrations in this work unit.
**Delivery rule:** Push branch; open PR to `main`; all six CI jobs must succeed at the final remote SHA; **DO NOT MERGE**.

## 0. Decision and scope

P10-A's **safe synthetic-only** domain subset is merged, but P10-B (live clinician queue/API), sensitive P10-C, and P10-D still lack the trusted clinician identity/assignment, lawful data-access, approved source/clinical wording, persistence and institutional authorizations recorded in `docs/implementation/P10_READINESS_GATE_REVIEW.md` (0/9 live gates approved). Do **not** invent such approval or begin P10-B/C/D while these blockers remain.

The next separately safe work unit is to complete the missing `docs/15_DOCUMENT_AI_OCR_SPEC.md`, identified as **NOT STARTED** under “Before P11” in `docs/implementation/38_PROGRESS_TRACKER.md`, and record a sober P11 readiness/gate assessment. **This is documentation only**: no patient file upload, image/OCR processing, active object access, retention policy, OCR provider activation, medical entity extraction, candidate promotion, clinician source viewer or production integration is authorized by completing the spec.

Existing P7 is a deterministic, non-diagnostic intake. P8-C real patient AI and P9-C real safety routing remain Stage 3 BLOCKED. P10 live clinician access remains blocked. Document AI results, confidence and source labels do not establish clinical truth. New document/OCR capabilities must never become a backdoor into P5 confirmed facts or an unapproved P8/P10/P9 workflow.

## 1. Preflight and required repository reconnaissance

1. Confirm clean worktree; local/remote `main` at exact baseline; PR #30 genuinely merged with same tree as reviewed head; Alembic head `p7a_0007`; no newer conflicting changes. **STOP** on drift and report, do not reset/discard user work.
2. Confirm `docs/15_DOCUMENT_AI_OCR_SPEC.md` is absent and `backend/app/modules/documents/` contains only `.gitkeep`; `apps/patient-web/app/documents` is currently an unavailable placeholder, not an upload workflow. If reality differs, reconcile and report; never describe a conceptual future contract as a live API.
3. Inspect established object-storage, jobs/worker and outbox abstractions by locating their **actual** filenames under `backend/app/shared/`, `backend/app/adapters/`, `backend/app/modules/`, and/or `backend/app/infrastructure/` (do not assume `shared/storage.py` or `shared/jobs.py` exists). Distinguish existing primitives from document-specific integration that is absent.
4. Follow `docs/codex/CODEX_INSTRUCTIONS.md`, `CODEX_WORKFLOW.md`, `CODEX_CONTEXT_RULES.md` and accepted R3 architectural/dependency precedence. If an authoritative design conflicts, record `SPECIFICATION DRIFT DETECTED`, stop for review rather than silently replacing it.

### Mandatory canonical reading

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md        # FR-DOC-001..023; FR-PROV-001..007
docs/02_SYSTEM_ARCHITECTURE.md        # module ownership, trust boundaries and ports
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md              # §§33–36 ClinicalDocument, types, OCR and extraction results
docs/05_DATABASE_SCHEMA.md           # §15 conceptual document tables — NOT migration approval
docs/06_API_CONTRACTS.md             # §§17–18 upload/status/reprocessing conceptual APIs
docs/07_CLINICAL_INTAKE_SPEC.md
docs/08_SAFETY_AND_TRIAGE_POLICY.md  # DRAFT, no clinical safety activation
docs/12_CLINICAL_PROVENANCE_SPEC.md
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/22_UX_AND_USER_FLOWS.md
docs/23_PATIENT_APP_SPEC.md           # /documents unavailable, PWA/BFF privacy baseline
docs/24_CLINICIAN_DASHBOARD_SPEC.md
docs/26_PRIVACY_CONSENT_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md # §19 P11-A..E and exit criteria
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md # AC-P11-001..011
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md
docs/implementation/P9_C_SAFETY_PRESENTATION_GATE_REVIEW.md
docs/implementation/P10_READINESS_GATE_REVIEW.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
docs/research/ocr/OCR_TECHNOLOGY_EVALUATION.md
docs/research/ocr/OCR_BENCHMARK_PLAN.md
docs/research/ocr/OCR_ADAPTER_CONTRACT_DRAFT.md
```

Research documents are informative beneath current canonical specifications and accepted R3 rules; do not blindly promote a research recommendation into a production decision. Inspect real code/CI and the currently unavailable patient document page as evidence, not as a basis for changing runtime behavior.

## 2. Primary deliverable: `docs/15_DOCUMENT_AI_OCR_SPEC.md`

Create the canonical full P11 design with project-appropriate document ID, version and **`TECHNICAL SPECIFICATION — NOT CLINICAL/PRIVACY/PRODUCTION APPROVAL`** header, exact source references, ownership, deferred decisions and phased implementation boundaries. Make it implementable without falsely resolving human decisions.

### A. Purpose, identity and lifecycle

- Describe document categories exactly aligned with canonical `ClinicalDocument` types: `PRESCRIPTION`, `LAB_REPORT`, `DISCHARGE_SUMMARY`, `DIAGNOSTIC_REPORT`, `IMAGING_REPORT`, `REFERRAL_LETTER`, `OTHER`, `UNKNOWN`; new types through a registered processor design, not arbitrary untrusted plugins.
- Lifecycle from domain model: `UPLOADED`, `VALIDATING`, `ACCEPTED`, `QUEUED`, `PROCESSING`, `NEEDS_REVIEW`, `SUCCEEDED`, `FAILED`, `REJECTED`. Design explicit valid transitions, terminal/retry semantics and idempotent processing attempts. Distinguish upload acceptance, OCR success, entity candidate quality, human review and confirmed clinical fact — **not** the same thing.
- Preserve document owner `documents`; P5 `patients` owns canonical facts and explicit supersession; `provenance` owns source metadata/visibility; P11 does not directly write into other modules' ORM tables. P8 candidates and P10 summary domain remain isolated/unapproved for live content.
- Define bounded, typed, versioned document metadata and provenance (patient/encounter/source identity, mime signature, language, SHA-256 digest, byte/page count, object ref, acquisition date, captured/uploaded/document dates as appropriate, status, uploader class where authorized); use minimal access-controlled metadata. Never store full file contents inside PostgreSQL metadata JSONB.
- Human decisions required: allowed populations, source accuracy, patient/session/clinician upload authority, ownership and transfer, lawful purpose/consent, source access permissions, retention/deletion, incident response, and production rollout.

### B. Secure ingestion and controlled object storage

- Distinguish multipart upload (contract Pattern A) from presigned intent/finalize (Pattern B) in `docs/06_API_CONTRACTS.md`. Select a future pattern **only** if established canonical/R3 decisions permit, otherwise record the decision as OPEN and outline trade-offs and consistent transition semantics.
- Describe exact server-side requirements for bearer/actor, session & encounter ownership, approved consent/lawful basis, scope, expiration, content-length/streamed hard cap, allowlisted mime signatures vs extensions, filename sanitization, executable/polyglot/symlink/path-traversal rejection, decompression bombs (PDF/image), image dimensions/page limits, PDF script/active-content handling, malicious file scanning/quarantine, checksum, duplicate detection and safer `REJECTED` behavior. Limits not previously approved should be explicit **proposed values/OPEN**, never quietly asserted as active policy.
- Explain secure object metadata vs opaque storage ref vs underlying private file bytes, encryption and access controls, tenant/session isolation, short-lived authorized download/preview, no raw storage keys or file contents in URLs/logs/traces/analytics, no public bucket or arbitrary presigned URL, object cleanup and orphan recovery, scan-before-any-OCR or viewer access.
- Duplicate SHA-256 alone is not sufficient for cross-patient deduplication or access; design safe same-owner duplicate/idempotency behavior without exposing another user's document existence. Handle ambiguous finalize, racing uploads, retries, checksum mismatch, revoked access and storage/DB transaction mismatch.
- Do not invent an approved encryption, malware-scanning vendor, storage region, object lifetime or DPA. Separate design options from recorded decisions.

### C. Adapter-first parsing and OCR contracts

- Specify project-owned `DocumentParserPort` (native PDFs/structured formats) separately from `OCRPort` (raster/scanned pages), in line with R2-A adapter draft and R3 OCR preference. Define request/result shape, bounded text blocks/coordinates/table structures/page numbers, language confidence, provider+version, status/warnings/error codes, bounded elapsed time/resources and source document/page linkage.
- Define `MockOCRAdapter`/deterministic fixture semantics for P11-B tests, no egress, nonmedical fake text, stable clock/IDs, configurable timeout/refusal/malformed output. Provider-neutral and no provider SDK in domain modules.
- R3: PaddleOCR 3.x PP-OCRv5/PPStructureV3 is **benchmark-gated candidate**, PaddleOCR-VL a difficult-page candidate, Docling a native parser candidate, Surya/docTR/Tesseract/RapidOCR challengers. **NO production winner yet.** Cite research bench plan; record language/prescription/handwriting/table evaluation, license/privacy/processing cost, latency, CPU/GPU and rollback approval. Do not import PaddleOCR/Docling dependencies in this doc phase.
- OCR result is evidence only; recognition errors, low confidence and lost units/tables cannot be auto-converted into authoritative diagnosis, medication changes or abnormal clinical flags.

### D. Jobs, processing-state and parser registry

- Define a bounded and retry-aware pipeline consistent with plan §19: upload -> validate/quarantine -> queue -> preprocess -> parse/OCR -> document classification -> type-specific extraction -> validation -> detached candidate output -> `NEEDS_REVIEW`/failure states. Make it explicit which stages require prior data governance or clinician approval and which are safe pure mechanics.
- Integrate conceptually with existing real worker/job/outbox abstractions only after investigating actual interfaces. Specify crash recovery, idempotency/dedup keys, per-document processing attempt identity, stale work cancellation, backoff, timeout, concurrent reprocess, revocation/withdrawal, poison input, quota/resource limits, bounded telemetry, failure compensation, and status read consistency.
- Define compile-time processor registry for the six plan processors: `PrescriptionProcessor`, `LabReportProcessor`, `DischargeSummaryProcessor`, `DiagnosticReportProcessor`, `ImagingReportProcessor`, `ReferralLetterProcessor`. Each parser/extractor declares version, accepted document/type/language, schema, failure/abstention, and a clear mock/no-op fallback. Unknown/ambiguous type never silently chooses a medical parser.

### E. Typed extraction, traceability and clinical separation

- Define versioned strict candidate schemas as **not accepted/confirmed facts**, with source document ID and page/region/span/table-cell evidence, original recognized text only where separately authorized, extraction/parser/provider version, confidence/uncertainty, normalized field proposals and review status. Do not claim bounded confidence equals clinical certainty.
- Cover prescription medication names and dose/frequency, lab analyte/value/unit/reference range/date, discharge/diagnosis/problem terms, procedures and report dates; never invent units, dose, negation, abnormal interpretation, date, or medical conclusion from missing/ambiguous OCR. No medication-interaction check without an independently validated source. Keep extraction clinical model selection and actual healthcare acceptance OPEN.
- Require explicit controlled human review; no automatic `CLINICIAN_CONFIRMED`, P5 fact overwrite, patient-facing advice, P9 safety decision, P10 signed summary or P15 self-care. Source provenance and privacy/consent still apply to any future promotion. Confirmation/correction belongs to separately approved P10-D/P5 governed transactions and cannot be smuggled into P11.
- Note source viewer restrictions: a source ref/opaque ID is not access permission; clinician identity/assignment and privacy gates are unresolved (0/9 for P10); P11-E must not expose medical images/PDFs without authorized source access and approved preview security.

### F. Patient/clinician UI and privacy design (future only)

- Document future upload/camera, progress, supported formats, review and status UX for patient web, and source/candidate review/timeline for clinician web. All are **design-only** pending authorization. `apps/patient-web/app/documents` remains an honest unavailable route in this work unit.
- Preserve P6/P7 same-origin BFF, transient `HttpOnly`, `SameSite=Strict` session cookies, server-only bearer, no-store responses, no clinical data in local/session/IndexedDB/Cache Storage, service-worker cache or analytics, and no auto retry of ambiguous mutation; temporary camera/file input must not become offline clinical persistence.
- Require accessible input/camera alternatives, progress/failure/retry, screen reader labels, keyboard operation, 320/390 reflow, warning/verification text not solely color, explicit source not available and consent/expired-session states. Do not author clinically sensitive advice without approved content review.

## 3. Required gate review: `docs/implementation/P11_READINESS_GATE_REVIEW.md`

Write an independently auditable matrix. Per gate: precise controlling spec/ADR, actual current code evidence vs missing pieces, accountable human owner, decision ID/date or **NONE RECORDED**, authorized env/population/purpose, `OPEN/BLOCKED` classification, and prerequisite subphase. Suggested distinct gates:

1. lawful upload/share/use of health documents; session/encounter/clinician identity, consent/assignment and organizational access;
2. file-type/size/content scanning and quarantine, PDF/image attack-defense limits and review;
3. private object storage encryption, access, region, retention/deletion/backup and leak prevention;
4. database schemas, provenance, idempotency/outbox, status, revocation and transactional cleanup;
5. OCR benchmark/model selection, language/handwriting accuracy, external processing/processor/legal terms, resource policy;
6. parser registry and explicit source/verification/version contracts;
7. medical term/medication/dose/lab interpretation and human review with independent clinical validation;
8. source preview/clinician assignment permissions, patient/clinician copy and accessibility;
9. security/privacy/threat/incident, model governance, pilot/prod enablement/monitoring and rollback.

**No blanket clinical/patient-data deployment approval exists.** Be precise about technical primitives which already exist; do not assign an arbitrary approval number merely to mirror P10's 0/9. The number of P11 approved/open/blocked gates comes from actual recorded evidence. Clearly distinguish:

- **Future P11-A** secure upload/storage implementation (real patient flow gated; a synthetic/offline engineering-only subset might be separately proposed after review);
- **P11-B** OCR port/mock/job contracts (engineering-only deterministic tests potentially safe; real provider/models gated by benchmark and privacy);
- **P11-C** classification/parser registry (synthetic-only mechanics potentially safe);
- **P11-D** medical entity extraction (clinical/retention/human review gated; any synthetic-only subset needs a new approved prompt);
- **P11-E** UI/review/timeline (patient/clinician authz, data-sharing and P10-D approvals required).

Do **not** implement these phases as part of Pre-P11.

## 4. Traceability, conflicts and acceptance truthfulness

- Map **every** `FR-DOC-001..023` and `AC-P11-001..011` to section/owner, source of evidence, planned phase, negative-case test, and status `NOT YET IMPLEMENTED/NOT VERIFIED`; record `FR-PROV-001..007` as applicable and document source permission and P5 guard compatibility.
- Explicitly distinguish future conceptual `clinical_documents`, `document_processing_runs`, `document_extractions` from existing P3 object-storage/jobs primitives; do not pretend schema exists or introduce an Alembic migration.
- Check R2 OCR adapter draft vs R3 baseline vs canonical plan: record any real discrepancy. No silent provider winner, no broad dependency installation, no unbounded raw-document text embedding, no fabricated clinical facts.
- Do not modify P10/P8/P9 clinical governance; P10 stays **IN PROGRESS/PARTIAL**, P8/P9 remain **PARTIAL**, and no P11 AC has passed because documentation exists.
- If a canonical requirement demands a decision no owner has approved, mark `OPEN — HUMAN APPROVAL REQUIRED` or `DEFERRED TO P11-<x>`; do not fill with general knowledge or an inferred consent/retention default.

## 5. Allowed files — documentation only

```text
docs/15_DOCUMENT_AI_OCR_SPEC.md
docs/implementation/P11_READINESS_GATE_REVIEW.md
docs/implementation/38_PROGRESS_TRACKER.md
  # note P10-A PR #30 merged at 7aad4dce... with engineering-only qualification;
  # P11 prerequisites written subject to review; P11 remains NOT STARTED
docs/codex/CODEX_PHASE_PROMPTS/PRE_P11_DOCUMENT_AI_OCR_SPECIFICATION_AND_READINESS_PACK.md
docs/README.md                     # optional canonical index link only
docs/implementation/README.md    # optional index link only
```

No edits in `backend/**`, `apps/**`, `packages/**`, migrations, actual schemas, dependencies, lockfiles, CI, Docker, infrastructure, feature flags, real policy, OCR model artifacts or research datasets. Additional docs require reasoned scope justification and should be flagged for review.

## 6. Verification and final PR handoff

- Run exact base/merge verification, link/heading/document existence checks, unique requirement/AC IDs, code-vs-contract truth audit, research precedence comparison, gate cross-consistency, scope allowlist and `git diff --check`.
- Run required full CI checks despite docs-only change: Ruff/strict mypy/backend, real PostgreSQL, frontend unit/builds, Playwright, Docker/PG, source/image security scans. Note skipped tests/retries truthfully. Alembic must stay `p7a_0007`.
- All **six mandatory GitHub Actions jobs** must succeed at the **exact final remote SHA**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`.
- Push branch `phase/pre-p11-document-ai-ocr-specification`; open PR against `main`; **DO NOT MERGE**. Never start P11-A/B/C/D/E automatically.

Return a concise report using:

```text
STATUS: COMPLETE / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA: 7aad4dce8c68d008e98287d769d83d109c3cb46b
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
SPEC 15 STATUS / CANONICAL OCR AND DOCUMENT CONTRACT:
P11 READINESS GATE MATRIX / APPROVED VS OPEN VS BLOCKED:
OCR ADAPTER / BENCHMARK-GATED PROVIDER STATUS:
UPLOAD, STORAGE, CONSENT, DATA RETENTION AND SECURITY DECISIONS:
P11-A/B/C/D/E OWNERSHIP / SAFEST CANDIDATE NEXT SUBSET:
FR-DOC-001..023 / AC-P11-001..011 TRACEABILITY:
P8-C / P9-C / P10 LIVE GATES PRESERVED:
DOCUMENT-ONLY DIFF / FORBIDDEN FILE CHECK:
LOCAL QUALITY COUNTS / SIX CI JOB CONCLUSIONS:
CI RUN ID:
ALEMBIC HEAD / DEPENDENCY CHANGES:
MERGED: NO
```

**STOP after submitting this report.** The next implementation prompt requires independent review of this Pre-P11 pack and explicit, separate scope approval.
