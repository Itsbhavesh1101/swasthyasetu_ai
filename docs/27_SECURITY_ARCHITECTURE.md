# SwasthyaSetu AI

## 27 — Security Architecture

> **DRAFT — P11-FOCUSED SECURITY DESIGN ONLY; NOT COMPLETE PLATFORM-WIDE SECURITY ARCHITECTURE; NO POLICY/PRODUCTION APPROVAL.**

**Document ID:** `SSAI-SEC-027-P11-DRAFT`

**Evidence baseline:** `main @ 2b2d9036c7fe9941bc90bb55d4130dabb6571263`

**Review state:** **DRAFT — HUMAN REVIEW REQUIRED**

**Scope:** P11 document ingestion, storage, processing, provenance, and future source presentation only

This draft supplies review material for P11 gates 1–4 and 9. It does not approve a population,
purpose, consent scope, vendor, region, encryption/key design, retention period, file format, quota,
scanner, worker, OCR provider, clinical use, pilot, or release. All non-P11 platform security domains
remain outside this draft and pending separate platform-wide review.

## 1. Authority and evidence labels

This document is subordinate to approved clinical/safety policy, the Project Master Specification,
System Architecture, Product Requirements, privacy/consent specifications, and accepted ADRs. It
uses four explicit evidence states:

- **AS-BUILT TECHNICAL CONTROL** — present in the baseline repository, with no claim beyond its
  implemented scope.
- **PROPOSED CONTROL — UNAPPROVED** — a design requirement for accountable human review.
- **HUMAN DECISION PENDING** — values, policy, or authorization cannot be selected by engineering.
- **NOT IMPLEMENTED** — no live repository capability exists.

Green tests or CI are engineering evidence only. They are not security, privacy, legal, clinical,
institutional, vendor, pilot, or production approval.

## 2. Baseline: as-built versus future

### 2.1 As-built technical primitives

- P4 supplies opaque pseudonymous sessions, centralized consent checks, provider-neutral identity
  contracts, server-side permission policy, and synthetic authorization tests. A production IdP,
  clinician directory, caregiver delegation, kiosk identity, and encounter assignment source are
  absent.
- P5 supplies patient/encounter persistence, typed provenance, permission-aware patient-owned reads,
  and guarded fact supersession. It does not supply document-source access or live clinician review.
- P6/P7 supply a same-origin patient BFF, transient `HttpOnly`, `SameSite=Strict`, `Path=/` cookies,
  production/non-loopback `Secure`, server-only bearer forwarding, `Cache-Control: no-store`, and a
  deterministic manual intake path. `/documents` is an honest unavailable route.
- `ObjectStoragePort` and `LocalFilesystemObjectStorage` exist. The local adapter is development/test
  only and explicitly provides no production durability, encryption, malware, or compliance
  guarantee.
- `OutboxRepository` is transaction-scoped PostgreSQL infrastructure with at-least-once-aware status;
  it does not provide exactly-once delivery. `JobDispatcher`, `InProcessJobBackend`, and
  `InProcessWorker` are volatile, process-local, and explicitly invoked.
- P11-A/B/C/D code is immutable, bounded, synthetic, nonmedical, and engineering-only. It has no
  application registration, route, ORM model, migration, source read, executable medical processor,
  real OCR model, or persistence. Structural evidence remains unconfirmed and source access remains
  unverified.
- The clinician application is an empty-state foundation. No trusted clinician login, assignment,
  document panel, or source viewer exists.

### 2.2 Future elements in this design

Every element named below is **FUTURE / NOT IMPLEMENTED** unless the text explicitly says as-built:
document API/BFF handlers; upload/quarantine/scan services; private production object storage;
document PostgreSQL tables; durable document jobs/workers; document outbox events; parser/OCR
adapters; candidate persistence; source viewer; signed viewing grants; audit persistence; purge and
reconciliation services; kill switches and P11 incident runbooks.

## 3. Security goals and data classification

P11 must preserve confidentiality, integrity, availability, provenance, authorization freshness,
purpose limitation, and recoverability without elevating document or model output to clinical truth.

| Asset or datum | Classification | Security objective |
| --- | --- | --- |
| Session bearer, provider credential, signing/encryption key | `SECURITY_SECRET` | Never enter browser JavaScript, URLs, logs, events, metrics, or documents; tightly scoped and revocable. |
| Original medical file, page image, OCR text, extracted candidate | `HEALTH_SENSITIVE` | Private, minimum-necessary, purpose-bound, lifecycle-controlled, and excluded from generic telemetry/caches. |
| Patient/actor identity and assignment | `IDENTITY_SENSITIVE` | Trusted-source resolution and exact object/institution binding; no client assertion. |
| Document/object/source identifiers, checksums, signed grants | `SENSITIVE` when linkable | Nonenumerating access and no cross-owner existence/digest disclosure. |
| Processing status, versions, closed error code | `INTERNAL` or `SENSITIVE` by context | Bounded, content-free, and disclosed only after exact authorization. |
| Synthetic engineering fixture | `INTERNAL` | Must remain visibly synthetic, nonmedical, non-dereferenceable, and isolated from runtime. |

## 4. Actor and authority inventory

| Actor class | Current reality | Future minimum authority; **unapproved** | Default now |
| --- | --- | --- | --- |
| Patient | Patient-owned P5 reads exist; authenticated continuity is not activated for documents. | Trusted patient binding, exact subject/encounter ownership, purpose, and document-specific consent. | Deny document operations. |
| Pseudonymous session | Exact session + `GENERAL_PRODUCT_USE` / `clinical_intake` consent supports P7 only. | Approved document purpose/scope and ownership semantics for an exact active session. | Existing consent is non-transitive; deny. |
| Caregiver | No delegation domain or API. | Trusted caregiver identity, explicit delegation scope/expiry, patient relationship, and consent. | Deny. |
| Kiosk | No approved kiosk actor/session policy. | Approved supervised purpose, session isolation, cleanup, device controls, and no residual data. | Deny. |
| Clinician | Permission constants exist; no production IdP, directory, institution membership, or assignment source. | Trusted active actor plus exact permission, institution, assignment, patient/encounter purpose, source permission, and MFA where policy requires. | Role alone is insufficient; deny. |
| Administrator | Administrative permissions do not imply clinical content access. | Explicit least-privilege operational action, purpose, MFA gate, audit, and separation of duties. | No document/source access by default. |
| Institution | Optional encounter `institution_id` exists; no tenant/assignment authority is configured. | Authoritative membership, assignment/transfer, data-sharing, isolation, and incident ownership. | No implied access. |
| Worker | Process-local generic worker exists; no durable document identity. | Dedicated least-privilege service identity bound to exact object/generation/stage with network and resource restrictions. | No live document work. |
| System | Compile-time modules and technical services exist. | Narrow service capability, key/secret boundary, safe audit, reconciliation, and revocation. | No ambient or global document authority. |

Authentication, role, assignment, institution, ownership, purpose, consent, and clinical review are
separate proofs. Identity is not consent; role is not assignment; possession of an opaque ID,
checksum, object key, upload intent, registry receipt, or prior response is not authorization.

## 5. Conceptual trust zones and future data flow

```text
[Patient browser — FUTURE document UI]
       | same-origin; no clinical browser persistence
       v
[Patient BFF — FUTURE document handlers]
       | server-only bearer; bounded/no-store responses
       v
[FastAPI document API — FUTURE]
       | fresh session/actor + patient/encounter/institution + purpose/consent checks
       +--------------------+
       |                    |
       v                    v
[Quarantine/scan — FUTURE]  [PostgreSQL metadata/outbox — FUTURE P11 schema]
       | released only after approved validation          |
       v                                                  v
[Private object storage — FUTURE provider]       [Durable jobs — FUTURE backend]
       ^                                                  |
       | exact object generation; least privilege         v
       +---------------------------------------- [Sandboxed parser/OCR — FUTURE]
                                                          |
                                                          v
                                      [Unconfirmed candidates/provenance — FUTURE]
                                                          |
                                               fresh source authorization
                                                          v
                                   [Patient/clinician source viewer — FUTURE]
```

Trust boundaries are browser→BFF, BFF→API, API→quarantine/scanner, API/worker→object storage,
API/worker→PostgreSQL/outbox/jobs, worker→parser/OCR, and API/BFF→future source viewer. External
provider egress is an additional boundary and remains prohibited without operation-specific review.
Research/benchmark infrastructure is isolated from production patient data.

## 6. Upload design alternatives — decision deliberately open

### Pattern A — streamed multipart through the API

Potential benefit: one authoritative stream can enforce pre-byte authorization, backpressure,
actual-byte limits, hashing, signature validation, quarantine, cancellation, and a single completion
decision. Risks include API resource exhaustion, temporary-file handling, reverse-proxy/body-limit
drift, and long request ambiguity.

### Pattern B — quarantine-only intent/finalize

Potential benefit: file bytes avoid the primary API process. Required safeguards include a narrowly
scoped, short-lived, single-object quarantine destination; owner/audience/object/version binding;
server-calculated or independently verified hash/size; replacement/TOCTOU protection; intent expiry;
one authoritative finalize result; orphan cleanup; and replay-safe reconciliation. Possession of an
intent or object never proves ownership.

**HUMAN DECISION PENDING:** architecture/security must select the pattern. This draft selects neither
one and sets no supported format, byte/page/pixel/object/runtime quota, scanner, or vendor.

Both patterns must enforce before any accepted byte operation:

1. fresh trusted identity/session and exact patient/encounter/institution authority;
2. approved uploader population, purpose, notice, and scope-specific consent;
3. closed request/idempotency identity and approved quota;
4. actual streamed-byte ceilings independent of `Content-Length`;
5. server-side signature detection and declared MIME/extension mismatch rejection;
6. executable/archive/polyglot/symlink/traversal rejection unless explicitly governed;
7. active PDF treatment covering JavaScript, launch actions, forms, attachments, macros, external
   references, embedded URLs, and SSRF;
8. decompression, page, image, dimension, nesting, object, font, memory, CPU, and wall-clock bounds;
9. malware/content scan with fail-closed scanner outage and quarantine before parse/read/preview;
10. cancellation and bounded temporary-file cleanup; no downstream read before an immutable release
    decision tied to the exact object generation.

## 7. Storage, encryption, retention, and source delivery

ADR-009 is binding: object storage owns original files and large derived binary artifacts;
PostgreSQL owns minimized metadata, opaque references, hashes, states, provenance, and retention
metadata. The conceptual schema is not migration approval.

**PROPOSED CONTROL — UNAPPROVED:** production storage must deny public access; isolate tenant,
institution, subject, and environment outside key obscurity; use least-privilege API/worker/service
identities; encrypt transport and stored data; separate key custody and rotation duties; and record
access without duplicating content. Provider, region, DPA, encryption scheme, key service/custodian,
rotation, recovery, and actual IAM topology are **HUMAN DECISION PENDING**.

Retention class, purge time, deletion SLA, legal hold, backup scope, restoration controls, derived
artifact lifecycle, and provider deletion are also **HUMAN DECISION PENDING**. Withdrawal blocks new
processing under the withdrawn authority but is not an invented promise of immediate deletion.
Deletion must coordinate metadata, original/derived objects, queued/running work, caches, audit,
outbox, and backups, and must detect restoration of logically deleted data.

Future source delivery requires fresh server-side authorization for the exact object version. A
short-lived viewing grant, if approved, must be audience/object/version/purpose bound, revocable,
noncacheable, and non-replayable outside its scope. A server-streamed alternative remains open.
Preview must use an isolated origin or equivalent reviewed boundary, restrictive CSP, safe content
type and disposition, no sniffing, no active content/external fetch, and no permissive frame/embed
policy. No source reference itself grants access.

## 8. Object authorization and nonenumeration

Every upload, finalize, status read, enqueue, worker read, result write, reprocess, source read,
preview, withdraw, and delete operation must re-resolve authoritative server state. The check is
patient/encounter/institution/source specific and includes current actor/session, permission,
assignment, purpose/consent or approved lawful basis, source lifecycle, generation, and retention.

Guessed IDs, another owner's digest, checksum reuse, timing, counts, status differences, and error
messages must not reveal whether a document/object exists. Cross-owner/cross-institution deduplication
or checksum probing is prohibited by default. Same-authority idempotency may return an existing
logical outcome only after equivalent request and ownership checks. Authorization failures follow a
reviewed common, content-free response policy.

## 9. Transaction, idempotency, and race design

**PROPOSED CONTROL — UNAPPROVED:** future design must provide:

- owner-scoped, bounded idempotency records with request fingerprints and conflict behavior;
- immutable object generation, document state version, processing attempt, and processor/config
  versions;
- PostgreSQL constraints plus locking/optimistic version checks for finalize/reprocess/delete races;
- atomic document metadata + minimized outbox staging where an event is required;
- compensation/reconciliation for object succeeds/DB fails, DB succeeds/object fails, event or
  enqueue failure, and orphaned quarantine objects;
- at-least-once idempotent handlers, durable claim/lease/heartbeat recovery, bounded attempts and
  total deadlines before live asynchronous processing;
- fresh authority/generation checks before worker read and result commit; stale or late results are
  discarded, never attached to the newest generation;
- withdrawal, deletion, assignment transfer, retention, reprocess, and restore race rules;
- poison-input isolation and safe operational visibility without raw file/OCR/candidate content.

Exactly-once delivery or processing is not claimed. The current volatile queue cannot provide
cross-process delivery or crash recovery, and no worker auto-starts from FastAPI.

## 10. Browser, BFF, telemetry, secrets, and operations

Future document responses, including errors, must be bounded and `Cache-Control: no-store`. Medical
bytes, previews, OCR text, candidates, bearers, signed grants, patient/source identifiers, or object
keys must not enter localStorage, sessionStorage, IndexedDB, Cache Storage, service-worker caches,
background sync, URLs/query strings, analytics/session replay, screenshots/test artifacts, or client
error payloads. The BFF never relays raw upstream bodies and never accepts browser-asserted role,
ownership, consent, or state.

Logs, traces, metrics, audit events, outbox payloads, and support tooling retain only necessary safe
operation, stage, version, duration, count, outcome, and closed error metadata. Audit linkage, if
approved, is access-controlled and purpose-bound. Raw filenames, file content, OCR text, clinical
candidates, credentials, tokens, signed URLs, and unrestricted IDs are prohibited.

Secrets must use an approved secret store and workload identity; no credential is committed or
placed in job/event payloads. Future P11 operations require redacted alerting, dependency health,
capacity/SLO decisions, incident classification, containment and breach workflow, key/credential
rotation, quarantine/source-access kill switches, rollback to disabled state, restoration checks,
and rehearsal evidence. Owners and deployment values remain pending.

P7 text/touch intake and generic urgent-help access remain independent when upload, storage,
scanner, worker, OCR, or source view fails. P11 cannot activate or bypass P8-C real-patient AI,
P9-C patient-facing safety decisions, P10 clinician authority, or P5 fact supersession protections.

## 11. Security control register

| ID | Threat / asset | Current reality | Proposed control | Status | Human owner | Negative test | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `P11-SC-001` | Wrong subject/encounter ownership | P4–P7 exact-session checks; no document route | Fresh object-level patient/encounter/source authorization at every boundary | UNDECIDED — PROPOSED CONTROL UNAPPROVED | Identity/security; application architecture | Guessed/cross-owner IDs produce indistinguishable denial | 1, 9 |
| `P11-SC-002` | Clinician role without assignment/institution | Permission constants only; no trusted IdP/assignment | Trusted active actor + exact assignment/institution + source purpose | UNDECIDED — HUMAN DECISION PENDING | Identity/security; institution; clinical governance | Wrong/revoked/disabled/stale assignment denied | 1, 8 |
| `P11-SC-003` | Consent or purpose overreach | `clinical_intake` consent only | Separate document purpose/scope/notice and per-operation recheck | UNDECIDED — HUMAN DECISION PENDING | Privacy/legal; product/institution | Missing/wrong/withdrawn consent and in-flight race | 1, 9 |
| `P11-SC-004` | Oversize/spoof/polyglot/bomb | No upload boundary | Stream caps, signature allowlist, mismatch and resource-bomb rejection | UNDECIDED — PROPOSED CONTROL UNAPPROVED | Security engineering; operations | Boundary, truncation, mismatch, bomb, cancellation cases | 2 |
| `P11-SC-005` | Malware/active PDF/SSRF | No scanner/quarantine | Fail-closed quarantine, scan and sandbox; no external fetch/active content | UNDECIDED — HUMAN DECISION PENDING | Security engineering; operations | Detection, outage, stale signature, escape, JS/link/SSRF cases | 2, 9 |
| `P11-SC-006` | Public/cross-tenant object exposure | Local adapter only; non-production | Private deny-public storage, explicit IAM and tenant/institution isolation | UNDECIDED — HUMAN DECISION PENDING | Infrastructure; security; institution | Public list/read, wrong identity and worker over-privilege | 3 |
| `P11-SC-007` | Key compromise/wrong region | No production provider or key design | Approved encryption, key custody/rotation, region and processor terms | UNDECIDED — HUMAN DECISION PENDING | Security; infrastructure; privacy/legal | Wrong key/region, rotation/recovery and secret leakage | 3, 9 |
| `P11-SC-008` | Retention/deletion/restore failure | No P11 data; no schedule | Coordinated lifecycle, legal hold, backup deletion and tombstone/reconciliation | UNDECIDED — HUMAN DECISION PENDING | Data governance; privacy/legal; operations | Partial purge, legal hold, restore resurrection, derived residue | 3, 9 |
| `P11-SC-009` | Intent theft/replay/object replacement | Pattern not selected | Short-lived quarantine-only binding, exact generation/hash and finalize reconciliation | UNDECIDED — HUMAN DECISION PENDING | Architecture; security | Replay, expiry, wrong audience, replacement/TOCTOU, ambiguous finalize | 2–4 |
| `P11-SC-010` | DB/object/outbox partial failure | Generic outbox exists; no document integration | Transactional metadata/outbox plus compensation and orphan reconciliation | UNDECIDED — PROPOSED CONTROL UNAPPROVED | Data/application architecture; operations | Each failure ordering rolls back or reconciles without false success | 4, 9 |
| `P11-SC-011` | Duplicate/stale/late processing | Synthetic attempts only; volatile queue | Versioned attempts/generations, durable lease, idempotency and late-result discard | UNDECIDED — PROPOSED CONTROL UNAPPROVED | Application architecture; operations | Duplicate job, crash, lease expiry, stale generation, revoke/delete race | 4, 9 |
| `P11-SC-012` | Source/signed-preview replay | No viewer exists | Fresh source permission, isolated renderer, CSP, no-store, expiring scoped grant | UNDECIDED — HUMAN DECISION PENDING | Security; privacy; application architecture | IDOR, expired/revoked grant, active content, cache and referrer leak | 3, 8, 9 |
| `P11-SC-013` | OCR prompt injection or forged provenance | Synthetic text-blind evidence only | Treat text as data, strict schema, exact source/attempt/version linkage, unconfirmed state | UNDECIDED — PROPOSED CONTROL UNAPPROVED | Document-AI; clinical governance; security | Instruction-like text, mismatched evidence/version, unsupported claim | 5–7, 9 |
| `P11-SC-014` | Candidate becomes clinical truth | P5 supersession guard; P11 candidates unconfirmed | Separate authorized review transaction; no direct P5 write or lower-trust overwrite | DEFERRED | Clinical governance; data architecture | Low confidence/failed source cannot confirm or overwrite | 7, 8 |
| `P11-SC-015` | Browser/BFF/log/telemetry leakage | P6/P7 privacy baseline exists | No-store, no clinical browser persistence, bounded BFF, redaction and absence tests | UNDECIDED — PROPOSED CONTROL UNAPPROVED | Frontend/application security; privacy | Cache/storage/URL/log/trace/analytics/upstream-error leakage scans | 8, 9 |
| `P11-SC-016` | Dependency/supply-chain compromise | CI scans exist; no OCR/scanner dependency | Pin narrow profile, SBOM/review, trusted artifacts, sandbox and rollback | DEFERRED | Security; document-AI; operations | Tampered artifact/config, vulnerable dependency and rollback exercise | 5, 9 |
| `P11-SC-017` | Insider/service-account abuse | No P11 production identities/audit | Least privilege, separation of duties, approved audit access and incident response | UNDECIDED — HUMAN DECISION PENDING | Security; institution; data governance | Unauthorized admin/support read, worker scope escalation, audit misuse | 3, 8, 9 |
| `P11-SC-018` | Optional failure disables core intake | P7 manual path is independent | Kill switch and honest degraded state; preserve manual intake | AS-BUILT (P7 fallback) / UNDECIDED (P11 controls) | Operations; product | Scanner/store/OCR outage leaves text/touch intake available | 9 |

No negative test in this table is claimed executed for a live P11 system. It is a required future
evidence catalogue.

## 12. Human decisions and STOP conditions

Accountable roles are privacy/legal and consent owner; identity/security owner; application/data
architect; security engineering; infrastructure/storage owner; data governance/records owner;
clinical governance and applicable pharmacy/laboratory experts; document-AI engineering; platform
operations; product/institution owner; and accessibility/content owner. Roles identify
accountability, not named approvals.

Stop live implementation or activation when any applicable population/purpose/consent, ownership,
identity/assignment, upload pattern/limits, scanner/quarantine, storage/IAM/encryption/key/region,
retention/deletion/legal hold, schema/idempotency, durable processing, provider/benchmark, source
viewer, clinical-review, incident, or rollback decision is missing. Do not infer approval from this
draft, a pull request, synthetic tests, or CI.

## 13. Traceability and current conclusion

This draft applies `FR-DOC-001..023`, `FR-PROV-001..007`, `PRIV-001..009`,
`NFR-RES-004..007`, and `AC-P11-001..011`; follows ADR-002, ADR-006, ADR-007, ADR-008,
ADR-009, ADR-010, ADR-019, ADR-020, ADR-022, ADR-027, ADR-036, ADR-037, ADR-038, and
ADR-040; and must be read with Specifications 12, 15, 23, 24, 26, 29, 30, and 33 plus the P11
readiness-gate review.

Current conclusion: this document is a P11-focused draft, not the complete platform security
architecture. P11 remains **0 APPROVED / 5 OPEN / 4 BLOCKED**; P10 remains **0/9 approved**;
P8-C/P9-C Stage 3 remain blocked; `/documents` remains unavailable; P11-E remains unimplemented;
and P7 manual intake remains the supported path.
