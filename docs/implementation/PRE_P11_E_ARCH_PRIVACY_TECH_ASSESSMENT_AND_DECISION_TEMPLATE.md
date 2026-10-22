# SwasthyaSetu AI — P11-A Approval-Readiness Package

## Pre-P11-E Architecture and Privacy Technical Assessment and Decision Template

**Assessment date:** 2026-10-23 (Asia/Kolkata)

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`

**Evidence baseline:** `main @ fc662ff8c99ad9a314d53a084213d6542f4f9dde`

**Related Pre-P11-E PR:** #36, merged at the evidence baseline

**Reviewed Pre-P11-E head:** `a21184645b56b40d4ac8207c67e24df33288dd0c`

**Document status:** **TECHNICAL ASSESSMENT AND DECISION TEMPLATE — NO HUMAN APPROVAL GRANTED**

**P11 live gates:** **0 APPROVED / 5 OPEN / 4 BLOCKED**

**P10 live clinician gates:** **0/9 APPROVED**

**P8-C / P9-C Stage 3:** **BLOCKED**

> This package prepares accountable reviewers to decide whether and how a future live P11-A
> document-ingestion phase may proceed. It does not select an upload pattern, storage provider,
> scanner, retention period, lawful basis, population, schema, durable worker, OCR provider, or
> production environment. It is not privacy/legal, clinical, security, institutional, accessibility,
> data-governance, or production approval. Only named accountable humans may complete the decision
> records in §14.

---

## 1. Purpose and decision boundary

This document consolidates the evidence and unresolved decisions for future P11-A live document
ownership, consent, secure upload, private storage, persistence, processing, privacy, and security.
It also records the narrow Pre-P11-E synthetic-presentation assessment that triggered this package.

The package is documentation only. It does not authorize or implement:

- patient, caregiver, kiosk, clinician, administrator, or institutional document upload;
- document APIs, BFF handlers, patient or clinician UI, preview, download, or source access;
- file-byte ingestion, signature parsing, malware scanning, quarantine, or active-content handling;
- object-storage activation, encryption configuration, signed URLs, or retention/deletion jobs;
- SQLAlchemy models, Alembic migrations, document tables, events, durable jobs, or workers;
- OCR/parser providers, medical extraction, clinical review, fact promotion, or runtime activation;
- real-patient AI, patient-facing safety decisions, or live clinician workflows.

The controlling hierarchy remains the project master specification, system architecture, privacy
and security requirements, domain/database/API contracts, accepted ADRs, R3 dependency policy,
phase acceptance criteria, and current readiness reviews. This template cannot override them.

---

## 2. Evidence reviewed

### 2.1 Governing specifications and plans

- `00_PROJECT_MASTER_SPEC.md`: safety, privacy, failure isolation, extensibility, and new-feature
  decision requirements.
- `01_PRODUCT_REQUIREMENTS.md`: `FR-DOC-001..023`, `PRIV-001..004`, `NFR-RES-004..005`,
  `NFR-OBS-003`, and `NFR-TEST-011`.
- `02_SYSTEM_ARCHITECTURE.md`: documents ownership, ports/adapters, PostgreSQL truth, object storage,
  upload quarantine, background execution, degradation, retention, and deletion boundaries.
- `03_REPOSITORY_STRUCTURE.md`: current inert documents package and no-runtime-registration boundary.
- `04_DOMAIN_MODEL.md`: document ownership, provenance, candidate-only OCR output, and invariants
  `INV-002`, `INV-008`, and `INV-009`.
- `05_DATABASE_SCHEMA.md`: conceptual document tables and retention/encryption constraints.
- `06_API_CONTRACTS.md`: conceptual direct-multipart and presigned-intent alternatives; neither is
  approved or implemented.
- `12_CLINICAL_PROVENANCE_SPEC.md`: source linkage is not source-access authority; extracted is not
  clinician-confirmed.
- `15_DOCUMENT_AI_OCR_SPEC.md`: canonical P11 lifecycle, secure-ingestion, storage, processing,
  provenance, phase ownership, and gate requirements.
- `26_PRIVACY_CONSENT_SPEC.md`: purpose limitation, minimization, non-transitive consent, retention,
  withdrawal, telemetry, and external-processing gates.
- `29_ENGINEERING_STANDARDS.md`, `30_TESTING_STRATEGY.md`, and `33_ERROR_HANDLING_POLICY.md`.
- `34_MASTER_IMPLEMENTATION_PLAN.md`, `35_PHASE_ACCEPTANCE_CRITERIA.md`, and
  `36_DEPENDENCY_MAP.md`.

### 2.2 Decisions and readiness records

- Accepted ADRs 001–005 and `37_DECISION_LOG.md`, especially ADR-002, ADR-006 through ADR-010,
  ADR-019, ADR-020, ADR-027, ADR-036 through ADR-038, and ADR-040.
- `38_PROGRESS_TRACKER.md` through the merged P11-A/B/C/D synthetic subsets and Pre-P11-E design.
- `P11_READINESS_GATE_REVIEW.md` and
  `P11_E_SOURCE_ACCESS_AND_UI_READINESS_DESIGN.md`.
- `P10_READINESS_GATE_REVIEW.md`, `P8_C_INTEGRATION_GATE_REVIEW.md`, and
  `P9_C_SAFETY_PRESENTATION_GATE_REVIEW.md`.
- `R3_FINAL_TECHNOLOGY_STACK.md` and `R3_CODEX_DEPENDENCY_POLICY.md`.

`27_SECURITY_ARCHITECTURE.md` and `28_THREAT_MODEL.md` do not exist at this baseline. Their absence
is a material readiness gap, not permission to infer controls.

---

## 3. Verified repository truth

The merged repository provides engineering evidence only:

| Existing evidence | What it proves | What it does not prove |
| --- | --- | --- |
| `documents/domain.py` and `ingestion.py` | Strict synthetic metadata, lifecycle, explicit simulated validation, and owner-scoped comparison | Real upload, byte inspection, ownership, consent, scanner success, approved limits, or persistence |
| P11-B parser/OCR ports and test mock | Provider-neutral contracts and deterministic zero-egress tests | A selected or production-approved parser/OCR provider |
| P11-C classification/registry | Closed synthetic labels and version-pinned inert descriptors | Medical classification or executable runtime processors |
| P11-D candidates/evidence | Text-blind structural matching with unconfirmed status and unverified source access | Medical extraction, clinical correctness, source access, or fact promotion |
| `ObjectStoragePort` and local adapter | Replaceable storage boundary and controlled development primitive | Durable, encrypted, region-approved, compliant, or production storage |
| In-process jobs and PostgreSQL outbox | Generic process-local dispatch and transaction-scoped event foundation | Durable document processing, cross-process recovery, or exactly-once delivery |
| PostgreSQL/Alembic foundation | Transactional database and migration workflow | Document models, tables, migration, or retention policy |
| Patient `/documents` route | Honest unavailable state | Upload, status, preview, or review UI |
| Clinician web foundation | Empty accessible shell | Trusted clinician identity, assignment, source access, or review authority |

The documents package is absent from FastAPI/module composition. No document route, ORM model,
table, migration, object-store binding, production worker, provider, or patient/clinician workflow
exists. Alembic remains `p7a_0007`.

The synthetic P11-A constants of 50 MiB and 100 pages are engineering test-contract bounds only.
They are not approved patient upload limits. `ACCEPTED` in a synthetic lifecycle is not a malware,
authorization, authenticity, privacy, or clinical verdict.

---

## 4. Current gate classification

This package preserves the nine-gate P11 readiness decision:

| Gate | Status | Live P11-A relevance |
| --- | --- | --- |
| 1. Lawful ownership, purpose, consent, identity, assignment, and organizational access | **BLOCKED** | Must close before any real uploader or file association is accepted |
| 2. File validation, signature, quarantine, malware, and active-content controls | **OPEN — HUMAN SECURITY REVIEW REQUIRED** | Must close before any untrusted bytes are accepted |
| 3. Private storage, encryption, region, keys, retention, deletion, and backup | **BLOCKED** | Must close before real medical objects are stored |
| 4. Metadata schema, lifecycle, idempotency, outbox, cancellation, and cleanup | **OPEN — SCHEMA REVIEW REQUIRED** | Must close before migration or durable processing |
| 5. OCR/provider benchmark, language, egress, resource, and rollback | **OPEN — BENCHMARK/APPROVAL REQUIRED** | Not required for byte-ingestion design alone; required before real OCR activation |
| 6. Registry and source/version contracts | **OPEN — DESIGN REVIEW REQUIRED** | Synthetic evidence exists; production contracts remain unapproved |
| 7. Medical extraction and reviewer authority | **BLOCKED** | Out of P11-A; must remain disconnected |
| 8. Preview/UI/accessibility and clinician assignment | **BLOCKED** | Out of P11-A; no source viewer or clinician workflow |
| 9. Threat, privacy, incident, pilot, monitoring, rollback, and release | **OPEN — RELEASE APPROVAL REQUIRED** | Required before pilot or production activation |

No row is changed to approved by this document.

---

## 5. Document ownership and consent decision package

### 5.1 Decisions accountable humans must record

| Decision ID | Required decision | Accountable reviewers | Status |
| --- | --- | --- | --- |
| `P11A-OWN-001` | Allowed environments and populations, including age/guardian and assisted-use constraints | Privacy/legal, product, institutional governance | **PENDING** |
| `P11A-OWN-002` | Permitted uploader classes and the authoritative identity proof for each | Identity/security, privacy/legal, institution owner | **PENDING** |
| `P11A-OWN-003` | Document owner/controller, patient association, transfer, correction, and dispute rules | Privacy/legal, data governance, clinical operations | **PENDING** |
| `P11A-OWN-004` | Exact lawful/governance purpose, notice, consent scope, sharing scope, and withdrawal effect | Privacy/legal, consent owner, product | **PENDING** |
| `P11A-OWN-005` | Pseudonymous-session treatment and whether any session may upload or retain documents | Privacy/legal, identity/security, product | **PENDING** |
| `P11A-OWN-006` | Clinician/institution assignment, minimum source access, and nonenumerating denial policy | Identity/security, clinical governance, institution owner | **PENDING** |
| `P11A-OWN-007` | Caregiver, kiosk, administrator, and support access policy—or explicit prohibition | Privacy/legal, identity/security, clinical operations | **PENDING** |

Current `GENERAL_PRODUCT_USE` consent with `clinical_intake` scope is non-transitive. It does not
authorize document upload, storage, OCR, clinician sharing, external processing, or retention.
Authentication, possession of an opaque ID, role labels, browser state, checksums, object keys, and
prior access never establish current authority.

### 5.2 Required server-authoritative checks before accepting bytes

Any future design must re-evaluate, from trusted server state:

1. active bearer/session or trusted actor identity;
2. exact patient/encounter/subject ownership and institutional scope;
3. allowed uploader class and approved population;
4. exact purpose, notice, consent or other approved lawful basis;
5. document quota, encounter/session lifecycle, and expiry;
6. owner-scoped idempotency and replay state;
7. current revocation, deletion, legal-hold, and source-lifecycle constraints.

The browser cannot supply authoritative patient, role, assignment, consent, MIME, checksum,
filename, status, or source-access decisions.

### 5.3 Negative authorization evidence

Tests must deny wrong patient, encounter, institution, uploader class, assignment, purpose, consent,
session, disabled actor, expired actor, revoked role, transferred case, closed encounter, guessed ID,
cross-owner checksum, replayed intent, and stale authorization. Denials must not reveal whether
another subject's document, digest, intent, or object exists.

---

## 6. Secure upload and file-validation decision package

### 6.1 Upload architecture decision remains open

`06_API_CONTRACTS.md` permits two conceptual patterns. No pattern is selected here.

| Concern | Pattern A: direct streamed multipart | Pattern B: constrained intent/finalize |
| --- | --- | --- |
| Byte path | API receives and validates the stream | Client sends to a quarantine-only destination |
| Primary benefit | One authoritative streaming boundary and simpler finalization | Reduced API byte load |
| Primary risk | API resource exhaustion and backpressure failure | Orphans, replacement/finalize races, signed-destination leakage, and ambiguous ownership |
| Mandatory controls | Pre-body authorization where possible, hard streaming limits, cancellation, quarantine | Short expiry, one object/version, quarantine-only scope, checksum/finalize proof, cleanup, replay defense |
| Decision evidence | Load/resource tests plus hostile-file suite | Storage-policy tests, finalize races, orphan reconciliation, and signed-grant abuse tests |

Architecture, application security, infrastructure, privacy, and operations reviewers must select
one pattern, document rejected alternatives, and approve exact failure/recovery behavior before an
API or storage adapter is implemented.

### 6.2 File-control decisions

| Decision ID | Required decision | Accountable reviewers | Status |
| --- | --- | --- | --- |
| `P11A-FILE-001` | Exact allowed formats and authoritative signature parsers | Security engineering, document-AI engineering | **PENDING** |
| `P11A-FILE-002` | Byte, page, pixel, dimension, object, nesting, font, and runtime limits by environment | Security engineering, operations, product | **PENDING** |
| `P11A-FILE-003` | PDF active-content, form, attachment, macro, external-reference, and compound-file policy | Security engineering | **PENDING** |
| `P11A-FILE-004` | Malware/content scanner, quarantine boundary, update policy, outage behavior, and release rule | Security engineering, infrastructure, operations | **PENDING** |
| `P11A-FILE-005` | Temporary-file isolation, cleanup, crash recovery, and forensic handling | Security engineering, operations, privacy | **PENDING** |
| `P11A-FILE-006` | User-visible rejection taxonomy and nonenumerating content-free errors | Application security, privacy, content/accessibility | **PENDING** |

Validation must be streamed and fail closed. The server calculates SHA-256 over accepted bytes.
Declared MIME, extension, filename, and caller checksum are untrusted. Object keys are generated
independently of filenames. No preview, parsing, OCR, or downstream job may access quarantined or
unvalidated content.

### 6.3 Required hostile-file evidence

The approved suite must cover oversize streams, truncated streams, spoofed MIME/extensions,
polyglots, executables, archives, traversal names, symlinks, decompression bombs, huge dimensions,
page/object/nesting bombs, malformed/corrupt PDFs and images, JavaScript, launch actions, forms,
attachments, macros, external references, scanner detection, scanner timeout/unavailability,
quarantine escape, parser timeout/crash, temporary-file residue, and cancellation mid-stream.

---

## 7. Storage, encryption, retention, and deletion decision package

ADR-009 fixes the boundary: object storage owns binary medical files; PostgreSQL owns metadata,
references, hashes, state, and retention metadata. It does not select a production provider.
SeaweedFS is only an R3 candidate; the local filesystem adapter is not compliant storage.

| Decision ID | Required decision | Accountable reviewers | Status |
| --- | --- | --- | --- |
| `P11A-STOR-001` | Provider/profile, deployment region, tenant/institution isolation, and processor/DPA terms | Infrastructure, privacy/legal, institution owner | **PENDING** |
| `P11A-STOR-002` | TLS, at-rest encryption, key custody, rotation, recovery, and separation of duties | Security, infrastructure | **PENDING** |
| `P11A-STOR-003` | Least-privilege API/worker identities, bucket policy, public-access denial, and audit | Security, infrastructure | **PENDING** |
| `P11A-STOR-004` | Object lifecycle, retention classes, purge schedules, deletion SLA, and legal hold | Privacy/legal, data governance, clinical records owner | **PENDING** |
| `P11A-STOR-005` | Backup/restore, backup deletion, disaster recovery, and regional failover | Infrastructure, data governance, operations | **PENDING** |
| `P11A-STOR-006` | Preview/download delivery, expiry, audience/object/version binding, cache policy, and revocation | Security, privacy, application architecture | **PENDING** |
| `P11A-STOR-007` | DB/object compensation, orphan discovery, reconciliation, and incident handling | Application/data architecture, operations | **PENDING** |

No raw object key, signed URL, original filename, medical content, OCR text, bearer, patient ID, or
clinical identifier may appear in public URLs, logs, traces, metrics, analytics, or generic errors.
Deletion is a coordinated workflow across PostgreSQL, object storage, derived artifacts, jobs,
caches, and backups under the approved policy; deleting one row is not proof of deletion.

Required negative tests include public listing/access, wrong tenant/owner, guessed object key,
signed-grant replay, wrong audience/version, expired/revoked grant, deleted/quarantined object,
worker over-privilege, key rotation failure, DB commit after object failure, object write before DB
rollback, purge partial failure, orphan reconciliation, restore reintroducing deleted data, and
secret/identifier leakage.

---

## 8. PostgreSQL schema and processing architecture decision package

### 8.1 Conceptual schema is not migration approval

`05_DATABASE_SCHEMA.md` describes `clinical_documents`, `document_processing_runs`, and
`document_extractions`, but the canonical P11 specification identifies unresolved production needs.
Before a migration, the data/application architecture and privacy reviewers must approve at least:

- authoritative subject/owner representation for permitted populations;
- immutable object generation/version and opaque storage reference;
- declared versus detected MIME and minimized/sanitized filename policy;
- lifecycle/status version, rejection reason, latest generation/attempt, and optimistic concurrency;
- owner-scoped idempotency identity, request fingerprint, outcome, expiry, and uniqueness;
- attempt generation, processor/routing/config versions, lease/claim/heartbeat/recovery state;
- cancellation, revocation, late-result discard, and terminal-state rules;
- retention class, purge-after, legal hold, deletion/tombstone, and reconciliation state;
- transactionally consistent minimized outbox/audit metadata where approved;
- constraints, foreign keys, indexes, row-locking strategy, and nonenumerating lookup behavior;
- explicit prohibition on file bytes, page images, unrestricted OCR text, and vendor payloads in
  relational JSONB.

The existing conceptual schema must not be copied directly into a migration without this review.
No document table exists at the evidence baseline.

### 8.2 Transaction and idempotency boundaries

The future design must specify:

1. authorization and quota checks before accepting bytes;
2. quarantine object creation and owner-scoped upload intent/finalization;
3. atomic metadata plus outbox staging when an event is required;
4. compensation when object and database operations partially succeed;
5. same-owner identical retry behavior and conflicting-key behavior;
6. concurrency between finalize, reprocess, withdrawal, deletion, and retention jobs;
7. stale generation/attempt rejection and late-result discard after fresh authority checks;
8. recovery after ambiguous client responses by authoritative idempotency lookup, not blind replay.

Cross-patient or cross-institution digest deduplication and existence probing are prohibited by
default. Exactly-once delivery must not be claimed.

### 8.3 Processing architecture decisions

Long-running validation, parsing, and OCR must use the project job abstraction. The current
in-process queue is local/test-only and cannot support real durability. Before live processing,
reviewers must decide and evidence:

- durable job backend and why the R3 PostgreSQL-native candidate does or does not fit;
- claim/lease/heartbeat/recovery semantics and worker identity;
- bounded attempts, total deadline, backoff, poison-input handling, and dead-letter visibility;
- per-owner/system byte, page, CPU, memory, concurrency, and rate quotas;
- processing cancellation on consent/authority/object-generation changes;
- idempotent handler behavior under at-least-once delivery;
- outbox dispatch and recovery without raw document content in events;
- operational SLOs, safe metrics, alerting, incident response, kill switch, and rollback.

No durable backend, worker container, event type, or OCR provider is selected by this package.

---

## 9. Security and privacy requirements

### 9.1 Required missing governance artifacts

Before live implementation or approval, accountable owners must create or approve:

1. a P11-specific data-flow and data-inventory record;
2. a threat model covering untrusted bytes, object storage, workers, preview, IDOR, SSRF/XSS,
   decompression/resource exhaustion, malware, insider access, logs, backups, and deletion;
3. a security architecture covering trust zones, identities, secrets/keys, network paths, scanning,
   quarantine, storage, audit, incident response, and recovery;
4. a privacy assessment covering purpose, population, lawful/governance basis, consent/notice,
   minimization, access, sharing, processor terms, retention, deletion, subject rights, and breach;
5. an accessibility/content plan for any future user-visible status or rejection copy;
6. environment-specific pilot/production enablement and rollback decisions.

The missing canonical `27_SECURITY_ARCHITECTURE.md` and `28_THREAT_MODEL.md` are explicit blockers
for claiming a complete security/privacy review.

### 9.2 Minimum privacy invariants

- Collect only fields approved for the exact purpose and population.
- Consent and authentication are separate; consent is purpose-specific and non-transitive.
- Recheck authority at upload, finalize, enqueue, worker read, result write, status read, source read,
  reprocess, withdraw, delete, and preview boundaries as applicable.
- Keep health-sensitive bytes, OCR text, identifiers, tokens, and source references out of generic
  logs, traces, metrics, analytics, URLs, browser storage, and public errors.
- Use `Cache-Control: no-store` for every future sensitive success and error response.
- Preserve the P7 deterministic manual intake fallback during every document/OCR failure.
- Treat OCR and extracted content as evidence/candidates, never confirmed clinical truth.
- Do not let feature flags substitute for authorization, consent, policy, or approval.

---

## 10. Accountable reviewer matrix

Roles identify accountability; this document does not assign people or signatures.

| Reviewer role | Required review output | Blocking scope |
| --- | --- | --- |
| Privacy/legal and consent owner | Purpose/population, notice/consent, sharing, retention, deletion, processor/region, withdrawal | Any real file or metadata |
| Identity/security owner | Actor assurance, subject binding, assignment/institution, revocation, nonenumeration | Any upload/status/source access |
| Application/data architect | Upload pattern, aggregate/schema, idempotency, transactions, outbox, concurrency, reconciliation | API, migration, durable workflow |
| Security engineering | Threat model, formats/limits, parser/scanner/quarantine, active content, preview, secrets, testing | Any untrusted bytes or preview |
| Infrastructure/storage owner | Provider/profile, region, IAM, encryption/keys, backup/restore, lifecycle, DR | Production/pilot objects |
| Data governance/records owner | Retention classes, legal hold, deletion evidence, audit access, source stewardship | Persistence and lifecycle |
| Clinical governance | Permitted document purpose and separation from clinical truth; future reviewer authority | Medical extraction/review only; not P11-A mechanics alone |
| Document-AI engineering | Signature/parser feasibility, processing resource model, benchmark separation | Technical design; cannot grant privacy/clinical approval |
| Platform operations | Capacity, SLOs, monitoring, incident runbook, recovery, kill switch, rollback | Pilot/production activation |
| Product/institution owner | Population, user journeys, support model, operational ownership, release decision | Pilot/production activation |
| Accessibility/content owner | Future error/status copy, alternatives, announcements, reflow, assisted-use behavior | Any user-facing implementation |

Required approvals are additive. One reviewer cannot silently sign for another accountable function.
A GitHub approval or green CI run is code-review evidence, not legal, clinical, privacy, or production
authorization unless the repository's governed decision record explicitly establishes that role and
scope.

---

## 11. Acceptance-readiness and evidence matrix

This package does not pass an acceptance criterion. It defines evidence required before a future
implementation can claim it.

| Criterion / requirement | Required future evidence | Current status |
| --- | --- | --- |
| `FR-DOC-001`, `AC-P11-001` | Approved population/purpose; secure upload implementation; hostile-file and unauthorized-upload integration tests | **NOT VERIFIED** |
| `FR-DOC-003` | Approved formats/limits/scanner policy; streamed signature/security validation and adversarial fixtures | **NOT VERIFIED** |
| `FR-DOC-022`, `AC-P11-003` | Persistent lifecycle/attempt state; concurrency, partial failure, cancellation, stale/late result, and API evidence | **NOT VERIFIED** |
| `AC-P11-002` | Private object storage plus minimized PostgreSQL metadata; bytes absent from DB/API/logs; access and deletion tests | **NOT VERIFIED** |
| `AC-P11-010` | Owner-scoped idempotency, duplicate/race handling, ambiguous response recovery, and no existence leak | **NOT VERIFIED** |
| `FR-PROV-001..007` | Exact source/attempt/version lineage with separate permission checks and no confirmation promotion | **NOT VERIFIED** |
| `NFR-RES-004..005` | OCR/document outage preserves manual intake and reports honest degraded state | **NOT VERIFIED FOR LIVE P11** |
| `PRIV-001..004` | Approved minimization, purpose, retention, withdrawal/deletion policy and execution evidence | **APPROVAL REQUIRED** |

P11-B/C/D synthetic tests remain useful regression evidence, but they cannot substitute for real
PostgreSQL, object-store, HTTP, browser, security, privacy, or operations evidence.

---

## 12. Mandatory negative-test catalogue

### 12.1 Identity, ownership, consent, and enumeration

- anonymous, expired, closed, revoked, disabled, wrong-role, wrong-assignment, wrong-institution;
- wrong patient/encounter/session, caregiver without delegation, kiosk residue, administrator
  without source permission;
- missing/wrong/withdrawn consent or purpose, stale authorization between upload and finalize;
- guessed IDs/object keys, cross-owner digest, duplicate probing, timing/count/status differences;
- revocation or assignment transfer while queued, processing, previewing, or retrying.

### 12.2 Upload and content security

- size/page/pixel/object/nesting/runtime boundary values and streaming limit bypass;
- spoofed MIME/extension, polyglot, executable, archive, traversal, symlink, malformed and truncated;
- decompression bombs, active PDFs, JavaScript, launch actions, forms, attachments, macros, external
  references, embedded URLs, SSRF attempts, XSS payloads, and parser crashes;
- malware detected, scanner unavailable/timeout/stale signatures, quarantine bypass, TOCTOU object
  replacement, and cancellation during upload.

### 12.3 Storage, database, and processing failure

- object succeeds/DB fails; DB succeeds/object fails; event/outbox fails; enqueue fails;
- repeated finalize, reused idempotency key with different content, concurrent finalize/delete,
  concurrent reprocess, stale generation, duplicate delivery, worker crash, lease expiry;
- late result after withdrawal/deletion/revocation, retry after ambiguous response, poison input,
  orphan and derived-artifact cleanup, purge partial failure, backup restoration;
- no bytes or unrestricted OCR/vendor payload in PostgreSQL; no raw content or identifiers in
  events, logs, traces, metrics, errors, screenshots, test artifacts, or browser storage.

### 12.4 Clinical and cross-phase isolation

- failed/partial processing creates no accepted candidate or P5 fact;
- low-confidence/unconfirmed output never becomes `CLINICIAN_CONFIRMED`;
- lower-trust document output never overwrites clinician-confirmed data;
- missing unit/date/negation or ambiguous content is not invented;
- P11 output does not activate P8-C AI, P9-C safety, P10 summary/review, or self-care;
- OCR/provider outage leaves P7 text/touch manual intake and generic urgent-help access intact.

---

## 13. Pre-P11-E synthetic-presentation assessment

The proposed `PRE-P11-E-S` presentation-state module remains **DEFERRED / NOT AUTHORIZED** at this
baseline. Its narrow no-content/no-identifier/no-action design appears technically separable, but it
has no approved runtime consumer and closes none of the P11-A or P11-E gates. Creating another
status vocabulary before approved source-access semantics could increase later ambiguity.

If accountable architecture and privacy reviewers later find a concrete test-only need, they must
record an explicit scoped decision. That decision may authorize only inert synthetic contracts and
tests; it must not change the P11 gate matrix or authorize UI, source access, patient files, clinical
copy, or runtime bindings.

---

## 14. Human decision records — unsigned templates

> **STATE: PENDING.** Codex, an AI assistant, a green CI run, and a routine pull-request approval
> must not fill names, dates, decision status, or signatures on behalf of accountable owners.

### 14.1 P11-A architecture/privacy/security readiness decision

```text
Decision ID: [HUMAN GOVERNANCE OWNER TO ASSIGN]
Subject: Future live P11-A secure document ingestion and lifecycle
Evidence baseline: fc662ff8c99ad9a314d53a084213d6542f4f9dde
Decision: [PENDING / REJECT / DEFER / APPROVE A SPECIFIC FOLLOW-UP SCOPE]

Approved environment(s): [PENDING]
Approved population(s): [PENDING]
Approved uploader classes and identity assurance: [PENDING]
Approved purpose, notice, consent/lawful basis, and sharing: [PENDING]
Approved upload pattern and exact limits: [PENDING]
Approved scanner/quarantine/active-content design: [PENDING]
Approved storage/provider/region/encryption/key design: [PENDING]
Approved retention/deletion/legal-hold/backup design: [PENDING]
Approved schema/idempotency/transaction/outbox design: [PENDING]
Approved durable processing/recovery/rollback design: [PENDING]
Approved threat/privacy/security evidence: [PENDING]
Explicitly excluded capabilities: [PENDING]

Application/data architecture reviewer: [NAME / ROLE / DATE / REFERENCE]
Security reviewer: [NAME / ROLE / DATE / REFERENCE]
Privacy/legal reviewer: [NAME / ROLE / DATE / REFERENCE]
Identity/institution reviewer: [NAME / ROLE / DATE / REFERENCE]
Data-governance/records reviewer: [NAME / ROLE / DATE / REFERENCE]
Infrastructure/operations reviewer: [NAME / ROLE / DATE / REFERENCE]
Product/institution owner: [NAME / ROLE / DATE / REFERENCE]
Clinical reviewer, if scope requires: [NAME / ROLE / DATE / REFERENCE]
Accessibility/content reviewer, if user-facing scope requires: [NAME / ROLE / DATE / REFERENCE]

Conditions and required negative tests: [PENDING]
Related ADR/decision-log changes: [PENDING]
Expiry/review date and rollback trigger: [PENDING]
Final governed decision record/signatures: [PENDING]
```

### 14.2 Optional PRE-P11-E-S offline-contract decision

```text
Decision ID: [HUMAN GOVERNANCE OWNER TO ASSIGN]
Subject: Optional inert synthetic presentation-state contracts
Decision: [PENDING / REJECT / DEFER / APPROVE NARROW OFFLINE SCOPE]
Concrete engineering need: [PENDING]
Architecture reviewer: [NAME / ROLE / DATE / REFERENCE]
Privacy reviewer: [NAME / ROLE / DATE / REFERENCE]

If approved, maximum scope:
  - one pure, identifier-free, content-free, engineering-only contract module;
  - focused synthetic/adversarial tests;
  - no runtime mapper, UI, API, source access, permissions, actions, or clinical copy.

P11 0/9, P10 0/9, and P8-C/P9-C restrictions remain unchanged: [ACKNOWLEDGED]
Conditions and negative tests: [PENDING]
Decision record/signatures: [PENDING]
```

---

## 15. Approval sequencing and next recommended action

1. Accountable owners review §§5–12 and assign governed decision IDs.
2. Create the missing P11-specific threat model, security architecture, privacy/data-flow assessment,
   and retention schedule proposal without implementing runtime behavior.
3. Decide the allowed population, uploader authority, purpose/consent, and institutional boundary.
4. Select and document the upload pattern, exact hostile-file limits, and quarantine/scanner design.
5. Select and document the storage/encryption/key/region/retention/deletion/backup design.
6. Review the revised relational schema, idempotency, transaction/outbox, durable worker,
   cancellation, reconciliation, and rollback proposal.
7. Record approvals or rejections with names, roles, dates, scope, evidence, and expiry.
8. Only then issue a new, tightly bounded implementation prompt from the approved baseline.

**Next recommended action:** conduct the human-owned P11-A gate 1–4 and gate 9 decision review and
create the missing threat/security/privacy artifacts. Do not implement live P11-A or P11-E until
the applicable decisions are recorded. OCR provider activation, medical extraction, clinician
review, and source UI remain separate later gates.

---

## 16. Preserved restrictions and final status

- P11 remains **0/9 approved: 5 OPEN, 4 BLOCKED**.
- P10 live clinician access remains **0/9 approved**.
- P8-C Stage 3 real-patient AI remains blocked.
- P9-C Stage 3 patient-facing safety decisions remain blocked.
- `AC-P11-001..011` remain unverified for live use.
- Alembic remains `p7a_0007`; no dependency, schema, API, runtime, storage, worker, provider, or UI
  change is authorized by this package.
- P7 deterministic manual intake remains the supported fallback.

**Package conclusion:** approval-readiness documentation is prepared; human decisions are still
outstanding. No approval has been invented or granted.
