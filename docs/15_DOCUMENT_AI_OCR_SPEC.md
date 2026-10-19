# SwasthyaSetu AI

## 15 — Document AI / OCR Specification

**Document ID:** `SSAI-SPEC-015`

**Status:** Canonical Pre-P11 prerequisite — **TECHNICAL SPECIFICATION — NOT CLINICAL/PRIVACY/PRODUCTION APPROVAL**

**Version:** `1.0.0`

**Scope:** P11 document ingestion, private-object handling, parsing/OCR, processing, candidate extraction, provenance, and future review design

---

# 1. Authority, purpose, and current truth

This specification refines `FR-DOC-001..023`, `FR-PROV-001..007`, and `AC-P11-001..011` without implementing them. It is subordinate to approved clinical/safety policy, the project master specification, architecture, privacy/consent rules, accepted ADRs, and R3 dependency policy.

The current repository has no document domain, persistence tables, migration, upload/status API, OCR adapter, parser registry, patient upload flow, or source viewer. `backend/app/modules/documents/` contains only `.gitkeep`; `apps/patient-web/app/documents/page.tsx` honestly reports the route unavailable. Existing `ObjectStoragePort`, process-local `JobDispatcher`, explicit worker, and PostgreSQL outbox are technical foundations only, not an untrusted medical-upload pipeline or durable document worker.

Completing this document does not authorize patient files, production OCR, a new dependency, a schema migration, external processing, medical extraction, canonical fact promotion, clinician access, or patient-facing clinical behavior.

# 2. Permanent trust and ownership boundaries

- `documents` owns document metadata, processing attempts, parser/OCR orchestration, and detached extraction candidates.
- `patients` owns canonical P5 clinical facts and their explicit correction/supersession rules. P11 never writes another module's ORM rows directly.
- `provenance` owns source metadata and permission-aware provenance visibility.
- `consent`, `sessions`, `identity`, and `encounters` remain authoritative for their own checks; an opaque object reference is never authority.
- OCR is evidence. Extraction is an unconfirmed proposal. Confidence is not clinical certainty. Human confirmation is a separate governed transaction.
- P8 candidates, P9 synthetic decisions, and P10 summary artifacts remain isolated. P11 is not a path around their live gates.

No document result may automatically diagnose, prescribe, alter medication, create an abnormal interpretation, select a safety route, create a signed summary, provide self-care, or overwrite a clinician-confirmed fact.

# 3. Canonical document aggregate

## 3.1 Document categories

The closed initial `DocumentType` set is:

```text
PRESCRIPTION
LAB_REPORT
DISCHARGE_SUMMARY
DIAGNOSTIC_REPORT
IMAGING_REPORT
REFERRAL_LETTER
OTHER
UNKNOWN
```

Untrusted input cannot introduce a new type. A new type requires an explicit versioned processor registration, schema, tests, governance classification, and documentation change. There is no runtime plugin discovery.

## 3.2 Bounded metadata contract

A future document record uses typed, versioned, access-controlled metadata, including only as applicable:

```text
document_id
metadata_schema_version
patient_id? / encounter_id? / session_subject_ref?
document_type
opaque_storage_ref
sanitized_display_filename?
detected_mime_type
declared_mime_type?
sha256_digest
size_bytes
page_count?
pixel_dimensions_by_page?
language_hints[] / detected_languages[]
acquisition_type?
captured_at? / uploaded_at / document_date?
uploader_class? / uploader_actor_ref? (only when authorized)
status / status_version / latest_attempt_id?
```

Exact lengths, collection bounds, allowed acquisition values, and population-specific required fields are deferred to P11-A contracts. Full file bytes, page images, unrestricted raw OCR text, and arbitrary provider payloads must not be stored in PostgreSQL metadata JSONB. `original_filename` is untrusted input; at most a sanitized bounded display value is retained if approved.

## 3.3 Lifecycle

Canonical states are:

```text
UPLOADED -> VALIDATING -> ACCEPTED -> QUEUED -> PROCESSING
VALIDATING -> REJECTED
ACCEPTED -> REJECTED
QUEUED -> FAILED | REJECTED
PROCESSING -> NEEDS_REVIEW | SUCCEEDED | FAILED | REJECTED
FAILED -> QUEUED                 (authorized new attempt)
NEEDS_REVIEW -> QUEUED           (authorized reprocess, new attempt)
SUCCEEDED -> QUEUED              (authorized reprocess, new attempt)
```

`REJECTED` is terminal for that uploaded object. A retry creates or addresses an explicit processing attempt; it does not erase history. Reprocessing never mutates the identity/version of a completed result in place. A concurrent request with the same document and idempotency key returns the existing attempt; a different key is rejected or serialized according to the future approved concurrency contract.

The states mean different things:

- `ACCEPTED`: validation/quarantine policy passed; it says nothing about OCR quality.
- `SUCCEEDED`: the selected processing attempt completed its technical contract; it says nothing about clinical truth.
- `NEEDS_REVIEW`: output is incomplete, ambiguous, low-confidence, or requires human review.
- confirmed P5 fact: a separate, authorized P5/P10-D outcome and never a document state.

Deletion, consent withdrawal, loss of authorization, or expiry must prevent new processing/view access and cancel stale queued work where policy permits. Retention/legal-hold semantics remain human decisions; this spec does not invent a deletion promise.

# 4. Secure ingestion boundary

## 4.1 Upload contract decision

`docs/06_API_CONTRACTS.md` allows direct multipart (Pattern A) or presigned intent/finalize (Pattern B). **Decision status: OPEN — HUMAN ARCHITECTURE/SECURITY APPROVAL REQUIRED.**

- Pattern A simplifies authoritative streaming validation and ambiguous-finalization handling, but routes all bytes through the API and requires strict backpressure and request-size controls.
- Pattern B reduces API byte load, but requires narrowly scoped short-lived upload destinations, quarantine-only placement, checksum/finalize proof, expiry, orphan cleanup, and race-safe reconciliation. Upload possession cannot establish document ownership.

Both patterns must yield the same lifecycle and authorization semantics. No production endpoint is selected or activated here.

## 4.2 Preconditions

Before accepting bytes, a future server boundary must validate, from authoritative server state:

- bearer/session or trusted actor identity;
- exact patient/encounter ownership, clinician assignment, and institution boundary where applicable;
- allowed uploader class and population;
- approved lawful purpose and consent/scope when required;
- session/encounter/document state and expiry;
- request idempotency and quota.

Browser-provided patient, role, consent, encounter ownership, filename, MIME, checksum, or status is never authoritative. General product consent is not automatically document upload, external OCR, clinician sharing, or retention consent.

## 4.3 File controls

Validation must be streamed and fail closed. It must include:

- hard content-length and actual streamed-byte caps;
- an allowlist of recognized content signatures, reconciled with extension and declared MIME;
- generated opaque object keys and sanitized bounded display filenames;
- rejection of executables, archives unless explicitly supported, polyglots, symlinks, path traversal, embedded external fetches, and unsupported compound formats;
- PDF/image decompression-bomb defenses, bounded page count, decoded pixels, dimensions, nesting, objects, fonts, and runtime;
- PDF JavaScript, launch actions, attachments, macros, forms, and other active/external content treatment;
- malware/content scanning and quarantine before OCR, parsing, download, or preview;
- SHA-256 calculated server-side over the accepted bytes, with expected-checksum mismatch rejection;
- explicit `REJECTED` reason codes that reveal no parser internals or other user's object existence.

Exact byte, page, pixel, runtime, quota, and scanner limits are **OPEN — proposed values require security, operations, and product approval plus hostile-fixture testing**. No scanner vendor is selected.

## 4.4 Private object handling

Binary originals and large derived artifacts belong in private object storage behind `ObjectStoragePort`; PostgreSQL stores opaque references and minimized metadata. Required design properties are:

- encryption in transit and at rest under an approved deployment design;
- deny-public access and least-privilege worker/API identities;
- tenant/patient/session/institution isolation enforced outside object-key obscurity;
- short-lived, single-purpose authorized preview/download or server-streaming only after a fresh access check;
- no raw object key, signed URL, filename, file content, OCR text, bearer, or clinical identifier in logs, traces, metrics, analytics, or public URLs;
- scan-before-use, bounded temporary directories, cleanup, and orphan reconciliation;
- coordinated database/object compensation for partial writes and deletes.

Encryption product, key custody, malware scanner, storage region, object lifetime, backup policy, legal hold, deletion SLA, and DPA are **not approved by this specification**. The current local filesystem adapter explicitly lacks durability, encryption, malware, and compliance guarantees and is only a development/test primitive.

## 4.5 Idempotency and duplicates

A SHA-256 digest detects byte identity; it grants neither access nor clinical equivalence. Cross-patient deduplication or existence probing is prohibited by default. Same-authority retries may reuse an existing upload only through an approved owner-scoped idempotency record and identical validated metadata, returning indistinguishable errors to unauthorized callers.

Pattern B finalize must safely handle missing/expired intents, checksum mismatch, object replacement, repeated finalize, DB commit failure, and an object written without metadata. A reconciliation job may quarantine/delete orphans only under an approved retention rule. Ambiguous mutation responses are not automatically retried by the browser.

# 5. Parser and OCR ports

## 5.1 Separation

`DocumentParserPort` handles born-digital/structured content; `OCRPort` recognizes raster/scanned pages. Neither classifies clinical truth or extracts medication/diagnosis semantics.

Conceptual versioned requests contain:

```text
request_id / document_id / processing_attempt_id
opaque authorized object ref
detected mime signature
page range
language/script hints
mode (native, text, layout, table-aware)
contract version / routing-policy version
deadline and resource profile
safe correlation ID
```

Requests are immutable and bounded. Adapters do not receive patient authorization objects, session bearers, arbitrary URLs, or provider credentials from callers.

## 5.2 Result contract

A parser/OCR result is strict and versioned:

```text
request/document/attempt identity
status: SUCCEEDED | PARTIAL | FAILED | NEEDS_FALLBACK
pages[]: page number, dimensions, rotation, language/script confidence
blocks[]: bounded text, block ID/type, reading order, bbox/polygon, confidence + kind
tables[]: table/row/column/cell identities, spans, text, bbox, confidence + kind
provider, adapter, engine/model names and exact versions/checksums where applicable
routing/configuration version and runtime backend
warnings[] and closed error codes
elapsed/resource metadata within approved bounds
source document/page/block/table-cell linkage
```

Missing confidence is represented as unavailable, not fabricated. A failed page cannot be silently omitted: the overall result is `PARTIAL` or `FAILED` and the document normally enters `NEEDS_REVIEW`, retry, or safe failure. Raw vendor objects do not escape adapters.

## 5.3 Deterministic mock

P11-B may define `MockOCRAdapter` for direct tests only. It uses exact versioned mappings, nonmedical `SYNTHETIC_*` text, caller-supplied stable IDs/UTC clock, deterministic ordering, no filesystem/network egress, and configurable success, partial-page failure, timeout, refusal, unavailable engine, and malformed-result cases. It cannot be selected in protected environments and never establishes clinical accuracy.

## 5.4 Provider status and benchmark

R3 authorizes ports and evaluation, not a production winner:

- PaddleOCR 3.x PP-OCRv5/PPStructureV3: preferred baseline candidate, benchmark-gated;
- PaddleOCR-VL: difficult-page/handwriting candidate, benchmark-gated and distinct confidence semantics;
- Docling: native parsing/normalization candidate behind `DocumentParserPort`;
- Surya, docTR, Tesseract, and RapidOCR: challengers/baseline candidates.

Selection requires the repository OCR benchmark plan: printed/handwritten prescriptions, labs, discharge and diagnostic pages; English, Hindi/Devanagari, mixed language; tables/layout; critical numeric, unit, dose/frequency, date, and negation preservation; transparent failure; license/security/privacy; CPU/GPU latency and cost; offline/network behavior; rollback. Benchmark datasets require manifest, license/provenance, and no real patient data committed. No OCR/parser dependency is added in Pre-P11.

# 6. Processing pipeline, jobs, and events

## 6.1 Stages

```text
authorize upload
 -> stream validation and quarantine
 -> malware/content decision
 -> ACCEPTED + enqueue intent
 -> preprocess
 -> native parse or OCR
 -> document classification
 -> registered type-specific extraction
 -> strict validation and provenance binding
 -> detached candidate output
 -> SUCCEEDED / NEEDS_REVIEW / FAILED / REJECTED
```

Upload validation, strict schema mechanics, deterministic mocks, and registry behavior can be engineering-only work. Real patient association, scan policy, external OCR, medical extraction, interpretation, promotion, source viewing, and clinical wording require their corresponding gates.

## 6.2 Actual primitive integration

The repository currently provides:

- `app.shared.storage.ObjectStoragePort` with async byte put/get/exists/delete and safe `ObjectKey`/`ObjectMetadata`;
- `app.adapters.storage.local.LocalFilesystemObjectStorage`, development/test only;
- `app.jobs.JobDispatcher`, `JobRequest`, volatile `InProcessJobBackend`, and explicitly invoked `InProcessWorker`; there is no durable job table or daemon;
- `app.events.OutboxRepository` and `outbox_events` for transaction-scoped versioned events with retry status.

Future document integration must extend or compose these contracts explicitly. The volatile queue cannot claim crash recovery or cross-process delivery. Outbox reliability does not provide exactly-once processing. No worker auto-starts inside FastAPI.

## 6.3 Attempt and failure semantics

Every run has an immutable attempt ID, document ID, processor/routing/config version, idempotency key, timestamps, status, bounded error code, and source/result versions. Required behavior includes:

- atomic metadata plus outbox staging where an event is required;
- at-least-once-aware idempotent handlers and deterministic duplicate recognition;
- durable claim/lease/heartbeat/recovery design before real asynchronous processing;
- stale attempt cancellation when authority, consent, document version, or reprocess generation changes;
- bounded exponential backoff with jitter policy, total deadline, attempt cap, and non-retryable classes;
- serialized/optimistic concurrent reprocess and a single authoritative latest generation;
- poison-input quarantine/dead-letter visibility without raw content in diagnostics;
- per-owner and system page/byte/CPU/memory/concurrency quotas;
- compensation/reconciliation for DB/object/job mismatch;
- read-your-write or documented eventual status consistency;
- telemetry limited to safe IDs, stages, versions, counts, duration, and closed error codes.

Revocation or deletion requests stop future reads/processing when policy allows and cause late results to be discarded after rechecking authority. Legal/retention obligations and already-dispatched external data require an approved human policy.

## 6.4 Compile-time processor registry

P11-C owns explicit registrations for:

```text
PrescriptionProcessor
LabReportProcessor
DischargeSummaryProcessor
DiagnosticReportProcessor
ImagingReportProcessor
ReferralLetterProcessor
```

Each declaration includes processor ID/version, accepted document types, MIME/page/language modes, input/output schema versions, required parser/OCR capability, bounded failure/abstention states, and mock/no-op fallback. Duplicate registrations, unsupported versions, and ambiguous `UNKNOWN`/`OTHER` documents fail closed. An ambiguous classifier never silently selects a medical processor.

# 7. Detached extraction candidates

P11-D candidate envelopes are immutable, strict, versioned, and explicitly `UNCONFIRMED`. Each field proposal includes:

```text
candidate/field ID and schema version
document ID + processing attempt ID
document type + processor/extractor/provider/model/prompt versions as applicable
page + block/region/span/table-cell evidence
recognized source text only where retention/access is separately approved
proposed normalized value plus original representation
confidence kind/value or unavailable
uncertainty/abstention/warning reason codes
review status
created-at UTC
```

Potential schemas may propose medication name, dose, unit, route, frequency and duration; lab analyte, value, unit, reference range and date; discharge/diagnosis/problem terms; procedure/report type and dates. They must never infer missing units, dose, negation, abnormality, date, identity, or medical conclusion. A medication-interaction flag requires an independently validated source and a separately approved clinical capability; OCR/model memory is insufficient.

Validation rejects unsupported categories, unknown fields, oversize values, nonfinite confidence, invalid evidence locations, stale/mismatched source versions, invented content, and provider-selected verification. Invalid results do not partially persist authoritative facts. Low confidence cannot become confirmation.

Promotion/correction requires future authorized P10-D/P5 transactions with fresh source permission, reviewer authority, concurrency, provenance, audit/outbox, and supersession guards. It never automatically sets `CLINICIAN_CONFIRMED` or overwrites a higher-trust fact.

# 8. Provenance and source permission

`FR-PROV-001..007` apply. A future provenance record links the exact source type (`OCR` or `DOCUMENT_AI`), opaque source document and attempt, page/evidence coordinates, adapter/provider/model/schema versions, confidence semantics, reviewer disposition, and timestamps. Imported/external data additionally records source system and import context.

Provenance visibility is permissioned. A source reference proves linkage, not permission, file existence disclosure, download authority, or review authority. Missing, deleted, quarantined, expired, revoked, superseded, or inaccessible sources are represented honestly. P10's clinician identity/assignment/source-access gates remain 0/9 approved; P11-E cannot expose source files until they close.

# 9. Future UI design only

## 9.1 Patient web

Future P11-A/E may offer file selection/camera capture alternatives, supported-format guidance, explicit upload/scan/process status, safe retry, withdrawal/delete request state, and candidate review. It must retain same-origin BFF architecture, transient `HttpOnly`, `SameSite=Strict` session cookies, production `Secure`, server-only bearers, and `Cache-Control: no-store`.

No clinical file, preview, OCR text, candidate, object URL, or identifier may enter localStorage, sessionStorage, IndexedDB, Cache Storage, service-worker caches, analytics, URLs, or error reporting. Temporary camera/file objects are released promptly and never become offline clinical persistence. Ambiguous upload/finalize mutations are not auto-retried.

## 9.2 Clinician web

Future review requires trusted clinician identity, current assignment/institution/purpose, source-detail permission, safe preview, and fresh object authorization. Source/candidate/timeline panels must distinguish patient-provided, OCR evidence, unconfirmed candidate, clinician-confirmed, rejected, superseded, missing, and unavailable states.

## 9.3 Accessibility and copy

Both UIs require keyboard operation, named controls, screen-reader labels and status announcements, accessible camera alternatives, visible focus, 320/390 reflow, non-color-only warnings/verification, bounded progress, and explicit unsupported, quarantined, failed, expired-session, withdrawn-consent, and source-unavailable states. Clinical advice or reassuring absence wording requires approved content review.

The current `/documents` unavailable route remains unchanged in Pre-P11.

# 10. P11 phase ownership

| Phase | Owner and intended scope                                                                                       | Authorization boundary                                                                                                                                                                             |
| ----- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P11-A | `documents`: aggregate, persistence design/migration, controlled upload/private storage, validation and status | Real patient flow is gated. A separately approved synthetic/offline validation/storage contract subset may be possible after this pack is reviewed.                                                |
| P11-B | Parser/OCR ports, deterministic mock, job/attempt contracts, benchmark harness                                 | Safest candidate next subset: engineering-only deterministic contracts/tests with synthetic bytes and no egress. Real models/providers require benchmark, privacy, security and resource approval. |
| P11-C | Classification and compile-time processor registry                                                             | Synthetic mechanics may be separately approved; medical classifier content and production routing remain gated.                                                                                    |
| P11-D | Type-specific medical candidate schemas/extraction                                                             | Blocked on clinical validation, retention, human-review semantics, source authority, and approved extraction providers/prompts. Requires a new explicit prompt.                                    |
| P11-E | Patient upload/status/review and clinician source/candidate/timeline UI                                        | Blocked on upload, trusted identity/assignment, lawful sharing, retention, preview security, P10-D review authority, accessibility/content approval.                                               |

No phase is implemented or accepted by this document.

# 11. Requirement traceability

All rows are **NOT YET IMPLEMENTED / NOT VERIFIED**.

| ID         | Specification owner/section          | Current evidence                   | Planned phase        | Required negative-case evidence                                                            |
| ---------- | ------------------------------------ | ---------------------------------- | -------------------- | ------------------------------------------------------------------------------------------ |
| FR-DOC-001 | documents / §4                       | Conceptual API only                | P11-A/E              | unauthorized, wrong subject, expired consent/session, oversize and hostile upload rejected |
| FR-DOC-002 | patient UI / §9                      | unavailable route                  | P11-E                | camera denied/unavailable; no browser persistence                                          |
| FR-DOC-003 | documents / §4.3                     | engineering standard only          | P11-A                | spoofed MIME, polyglot, bomb, active PDF, malware, traversal rejected                      |
| FR-DOC-004 | OCR + prescription processor / §§5,6 | research candidates only           | P11-B/D              | timeout/partial/incorrect critical token never becomes fact                                |
| FR-DOC-005 | OCR + lab processor / §§5–7          | research candidates only           | P11-B/D              | analyte/value/unit misalignment needs review                                               |
| FR-DOC-006 | OCR + discharge processor / §§5–7    | research candidates only           | P11-B/D              | missing pages/negation fail closed                                                         |
| FR-DOC-007 | OCR / §5                             | benchmark plan only                | P11-B                | printed fixture failure is explicit                                                        |
| FR-DOC-008 | OCR / §5.4                           | benchmark-gated                    | P11-B/D              | handwriting ambiguity abstains/reviews                                                     |
| FR-DOC-009 | OCR / §5.4                           | benchmark-gated                    | P11-B                | unsupported/mixed language is explicit                                                     |
| FR-DOC-010 | classifier / §6.4                    | no registry                        | P11-C                | unknown/ambiguous type selects no medical parser                                           |
| FR-DOC-011 | extraction / §7                      | no extractor                       | P11-D                | diagnosis term is unconfirmed and source-bound                                             |
| FR-DOC-012 | extraction / §7                      | no extractor                       | P11-D                | medication name is never prescription authority                                            |
| FR-DOC-013 | extraction / §7                      | no extractor                       | P11-D                | missing/ambiguous dose/unit not invented                                                   |
| FR-DOC-014 | extraction / §7                      | no extractor                       | P11-D                | investigation candidate cannot imply interpretation                                        |
| FR-DOC-015 | extraction / §7                      | no extractor                       | P11-D                | unsupported procedure text abstains                                                        |
| FR-DOC-016 | extraction / §7                      | no extractor                       | P11-D                | absent/ambiguous date stays unknown                                                        |
| FR-DOC-017 | documents/timeline / §§3,8           | no projection                      | P11-E                | missing date does not fabricate ordering                                                   |
| FR-DOC-018 | clinical validation / §7             | no approved rule/source            | P11-D                | OCR/model cannot invent abnormal flag                                                      |
| FR-DOC-019 | separate clinical source / §7        | no approved interaction capability | Later governed phase | no OCR/model-memory interaction flag                                                       |
| FR-DOC-020 | review / §§7–9                       | no review flow                     | P11-D/E              | low confidence never auto-confirms                                                         |
| FR-DOC-021 | provenance / §8                      | P5 provenance primitive only       | P11-D/E              | inaccessible/deleted source does not leak or falsely resolve                               |
| FR-DOC-022 | lifecycle / §§3,6                    | generic jobs only                  | P11-A/B              | every partial/failure/stale state is explicit                                              |
| FR-DOC-023 | registry / §6.4                      | no document registry               | P11-C                | duplicate/unregistered/runtime plugin rejected                                             |

## 11.1 Provenance applicability

| ID          | P11 application                                   | Compatibility/negative proof                         | Status                             |
| ----------- | ------------------------------------------------- | ---------------------------------------------------- | ---------------------------------- |
| FR-PROV-001 | record OCR/document-AI source type                | unknown source type rejected                         | NOT YET IMPLEMENTED / NOT VERIFIED |
| FR-PROV-002 | exact document/attempt/page evidence              | opaque ref alone grants no access                    | NOT YET IMPLEMENTED / NOT VERIFIED |
| FR-PROV-003 | optional confidence plus confidence kind          | missing/nonfinite/misrepresented confidence rejected | NOT YET IMPLEMENTED / NOT VERIFIED |
| FR-PROV-004 | candidate stays unconfirmed until governed review | provider cannot select verification state            | NOT YET IMPLEMENTED / NOT VERIFIED |
| FR-PROV-005 | adapter/model/parser/extractor versions           | mismatched/unknown version rejected                  | NOT YET IMPLEMENTED / NOT VERIFIED |
| FR-PROV-006 | any downstream policy identity stays separate     | OCR cannot create P9 policy provenance               | NOT YET IMPLEMENTED / NOT VERIFIED |
| FR-PROV-007 | external source/import metadata where applicable  | external provenance never grants trust/access        | NOT YET IMPLEMENTED / NOT VERIFIED |

P5 compatibility requires source-authorized candidate promotion through the existing explicit supersession guard. A lower-trust OCR/document candidate cannot silently replace a clinician-confirmed fact.

## 11.2 Acceptance criteria

| ID         | Design section / owner            | Planned phase | Required evidence and negative case                                    | Status                             |
| ---------- | --------------------------------- | ------------- | ---------------------------------------------------------------------- | ---------------------------------- |
| AC-P11-001 | §4 / documents                    | P11-A         | secure upload integration; hostile and unauthorized files rejected     | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-002 | §§3–4 / documents                 | P11-A         | DB contains metadata/ref only; bytes private and absent from JSON/logs | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-003 | §§3,6 / documents                 | P11-A/B       | state/attempt/API tests including partial, stale and failed            | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-004 | §5 / documents adapters           | P11-B         | shared port contract tests; provider types do not leak                 | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-005 | §5.3 / documents adapters         | P11-B         | deterministic zero-egress success/failure fixtures                     | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-006 | §6.4 / documents                  | P11-C         | compile-time registration, duplicate/unknown/abstention tests          | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-007 | §§7–8 / documents + provenance    | P11-D         | exact evidence chain and inaccessible-source tests                     | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-008 | §7 / review                       | P11-D/E       | low confidence cannot set clinician-confirmed                          | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-009 | §§5–6,9 / intake + documents      | P11-B/E       | OCR failure leaves deterministic manual P7 intake usable               | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-010 | §4.5 / documents                  | P11-A         | owner-scoped idempotency/race/no-existence-leak tests                  | NOT YET IMPLEMENTED / NOT VERIFIED |
| AC-P11-011 | §§8–9 / provenance + clinician UI | P11-E         | trusted clinician assignment and cross-object/expired-source denial    | NOT YET IMPLEMENTED / NOT VERIFIED |

# 12. Decisions and approvals still required

Human owners must record decisions for allowed populations; patient/session/clinician/kiosk upload authority; document ownership/transfer; lawful purpose, consent and sharing; source accuracy responsibility; supported types and limits; scanner/quarantine; encryption/key custody; storage region; retention/deletion/backup/legal hold; external processing/DPA; OCR benchmark thresholds; clinical candidate schemas; reviewer qualifications; source preview; incident response; pilot monitoring; rollback; and production enablement.

Until recorded, the relevant item is **OPEN — HUMAN APPROVAL REQUIRED** or blocked as classified in `implementation/P11_READINESS_GATE_REVIEW.md`.

# 13. Reconciliation and deferred conceptual schema

The R2 adapter draft and R3 are consistent: two provider-neutral ports, PaddleOCR as a benchmark-gated baseline, Docling as a parser candidate, and no production winner. The older research draft's example routing is informative, not an activated production policy. The canonical plan's phrase “PaddleOCRAdapter or selected first adapter” is satisfied only after benchmark and approval.

`clinical_documents`, `document_processing_runs`, and `document_extractions` in `05_DATABASE_SCHEMA.md` are conceptual future designs, not current tables or migration approval. Their eventual schema must be reviewed against this specification's attempts, idempotency, authorization, retention, and provenance rules. Alembic remains `p7a_0007`.

# 14. Governance preservation

- P8-C real patient AI remains blocked; no document content may be sent to an unapproved LLM/provider.
- P9-C patient safety routing remains blocked; document output cannot trigger safety/self-care behavior.
- P10 remains partial; live clinician queue, source access, confirmation, and correction remain blocked.
- P7 deterministic manual intake remains available and authoritative for its approved scope.
- No P11 acceptance criterion passes merely because this specification exists.
