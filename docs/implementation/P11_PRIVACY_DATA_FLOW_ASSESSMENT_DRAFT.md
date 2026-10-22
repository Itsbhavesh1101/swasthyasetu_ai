# P11 Privacy and Data-Flow Assessment

> **DRAFT — PRIVACY/DATA-FLOW ASSESSMENT; NOT LEGAL ADVICE, COMPLETED DPIA, INDIA DPDP COMPLIANCE ASSERTION, PRIVACY APPROVAL, OR RELEASE AUTHORIZATION.**

**Work unit:** `PRE-P11-A-SECURITY-PRIVACY-DRAFTS`

**Evidence baseline:** `main @ 2b2d9036c7fe9941bc90bb55d4130dabb6571263`

**Review state:** **DRAFT — HUMAN REVIEW REQUIRED**

**Live scope:** none; all data flows below are future unless explicitly labeled as-built

This assessment prepares questions and evidence for accountable privacy, legal, security, clinical,
data-governance, institutional, and product owners. It invents no lawful basis, purpose, population,
notice, consent, vendor, region, retention period, deletion promise, or approval.

## 1. Current repository truth and privacy boundary

P11-A/B/C/D are synthetic, nonmedical, in-memory engineering foundations. They do not read files or
patient data and are not registered in FastAPI. There are no P11 ORM tables, migration, API/BFF,
object-store binding, durable document worker, OCR provider, source viewer, or clinical review flow.
The patient `/documents` route remains unavailable and the clinician app remains a foundation.
Alembic head is `p7a_0007`.

The existing P4–P7 pseudonymous flow uses an exact opaque session bearer server-side and active
`SESSION` consent with purpose `GENERAL_PRODUCT_USE`, scope `clinical_intake`, and notice
`privacy-v1`. That consent authorizes the implemented deterministic intake boundary only. It is
**not transitive** to document upload, storage, scanning, OCR, external processing, clinician or
institution sharing, source preview, research, retention, or derived candidates. Authentication,
session creation, feature availability, or a prior consent never implies those uses.

## 2. Populations and actor-specific decisions

| Actor/population | As-built status | Future question requiring human decision | Default until decided |
| --- | --- | --- | --- |
| Anonymous/pseudonymous session | P7 exact-session deterministic intake only; no document purpose/scope | Whether documents may be associated with a pseudonymous session; ownership after expiry/recovery; uploader assurance; notice/consent; retention; later identity linking | No document processing or source access |
| Verified patient | Patient domain exists; authenticated continuity/document flow absent | Identity assurance, self-ownership, encounter association, permitted purposes, sharing, access/correction/deletion rights, age/guardian treatment | No document processing or source access |
| Caregiver | No caregiver/delegation capability | Identity, relationship/delegation evidence, scope/expiry/revocation, patient notice/consent, assisted-use privacy | Actor not approved; deny |
| Kiosk/assisted setting | P6 shell supports design considerations only | Institution/device authority, supervision, session cleanup, camera/files, shoulder-surfing, local residue, notice/accessibility, transfer to patient | Population not approved; deny |
| Clinician | No trusted production IdP, directory, assignment, or document view | Professional assurance, institution membership, exact current assignment, purpose, minimum fields, source permission, review authority and audit | Role label is insufficient; deny |
| Institution | Optional encounter institution field only | Controller/processor roles, sharing agreement, tenant boundary, assignment/transfer, data residency, retention and incident responsibility | No implied population-wide access |
| Administrator/support | Permissions do not imply clinical access | Narrow operational purpose, MFA, just-in-time access, separation of duties, audit, support-tool redaction | No document content/source access by default |
| Worker/system | Generic technical primitives only | Workload identity, minimum object/generation access, egress, telemetry, retention and incident behavior | No live document execution |

No actor class in this table is approved for P11 by this draft.

## 3. Future data-flow and lifecycle inventory

All rows are **FUTURE / NOT IMPLEMENTED**. `UNDECIDED` fields require accountable human decisions.
Synthetic P11 fixtures are excluded from these patient-data flows and may never be silently reused as
production records.

| Stage | Origin / actor | Sensitivity | Purpose | Exact authority, consent and allowed population | Recipient / region / provider | Minimization | Lifecycle | Retention | Deletion / backup | Human owner | Evidence/tests and pending decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Upload initiation and bytes | Patient/session/caregiver/kiosk/clinician — each **UNDECIDED** | File, metadata, identity and context: `HEALTH_SENSITIVE` / `IDENTITY_SENSITIVE` | **UNDECIDED** per permitted use | **UNDECIDED:** trusted actor/session; exact patient/encounter/institution; uploader class; document-specific purpose/scope/notice; delegation where applicable | Future BFF/API/quarantine; deployment/region/provider **UNDECIDED** | Pre-byte checks; generated object key; at most approved sanitized display name; no unrelated patient record | Intent/stream → quarantine or rejection; Pattern A/B **UNDECIDED** | **UNDECIDED** for incomplete/rejected upload | Cancel/expiry/orphan cleanup and backup exclusion **UNDECIDED** | Privacy/legal; identity/security; product/institution; security engineering | Wrong actor/subject/consent, oversize, spoof/polyglot, cancellation; decide population, pattern, limits and notice |
| Quarantine and scan | Future API/quarantine worker | Original bytes and scan result: `HEALTH_SENSITIVE`; malware/security metadata | Security validation only; exact secondary uses prohibited | Same exact object generation and still-valid upload authority; no downstream read | Scanner/sandbox/provider/region **UNDECIDED**; external egress prohibited until approved | Scanner gets only bytes and necessary closed metadata; no patient profile or bearer | Quarantined → released/rejected; no parse/preview before release | **UNDECIDED**, short as operationally justified | Cleanup for rejection/timeout; backup/legal-hold treatment **UNDECIDED** | Security; operations; privacy/legal | Malware/outage/escape/active-PDF/bomb/temp residue; decide scanner, DPA, network and SLA |
| Accepted original | Released quarantine object | Medical original: `HEALTH_SENSITIVE` | **UNDECIDED** clinical-record/intake purpose | Fresh ownership/purpose/consent and source lifecycle; allowed populations **UNDECIDED** | Private object store/provider/region **UNDECIDED** | Store exact accepted bytes once; no PostgreSQL blob; sanitized/minimal metadata only | Immutable object generation; private, no public list/read | Class and period **UNDECIDED** | Coordinated object/metadata/derived/backups/legal hold **UNDECIDED** | Data governance; privacy/legal; infrastructure/security | Cross-tenant/public/IAM/key/region tests; decide provider, encryption, key custody, lifecycle |
| Metadata and provenance | API/document service | Linkable IDs, hash, state, lineage: `SENSITIVE` / `HEALTH_SENSITIVE` by linkage | Manage exact document/attempt/source lifecycle; purpose **UNDECIDED** | Same subject/encounter/institution/purpose; minimum workers/readers only | PostgreSQL in deployment region **UNDECIDED** | No file bytes, page images, unrestricted OCR text, vendor payload, raw filename or bearer | Versioned document/attempt/generation/provenance; immutable history where required | **UNDECIDED** by record type | Tombstone/purge/legal-hold/backups and audit preservation **UNDECIDED** | Data architecture; data governance; privacy | Schema constraints, owner-scoped idempotency, IDOR, rollback, no-bytes-in-DB; migration not approved |
| Async job and outbox | Document service → future durable worker/event dispatcher | Closed IDs/status/version; potentially linkable `SENSITIVE` | Execute approved stage and recover safely | Fresh authority at enqueue, claim, object read and result write; exact generation/purpose | Future durable backend/worker; provider/region **UNDECIDED** | No raw bytes/OCR text/clinical candidate in job/event payload; opaque refs only where approved | Queued/claimed/retried/cancelled/terminal; at-least-once, not exactly-once | Attempt/event metadata duration **UNDECIDED** | Cancel/expire/purge/dead-letter and backup handling **UNDECIDED** | Application architecture; operations; privacy/security | Duplicate/crash/lease/revoke/delete/poison/quota tests; decide backend, identity, attempts, SLO |
| Derived parser/OCR output and candidates | Future sandbox/provider/worker | OCR text, layout, extracted proposal: `HEALTH_SENSITIVE` | Parsing/OCR and detached candidate generation; exact purpose **UNDECIDED** | Approved document authority plus provider/egress terms; no provider-selected clinical authority | Local/external provider, subprocessors and region **UNDECIDED** | Process only pages/fields required; raw output in memory by default; persist only approved bounded artifacts | Result bound to exact source/object/attempt/model/schema; `UNCONFIRMED`; stale results discarded | Raw/derived durations **UNDECIDED** | Purge with source/authority rules; provider deletion and backup **UNDECIDED** | Privacy/legal; clinical governance; document-AI; operations | Egress, provider retention/training, silent omission, forged provenance, low-confidence and no-promotion tests |
| Authorized source read / preview | Future patient or clinician UI via BFF/API | Original/derived content and access metadata: `HEALTH_SENSITIVE` | **UNDECIDED** self-access or assigned clinical review | Fresh trusted actor; exact patient/encounter/institution/assignment; source permission; purpose/consent/lawful basis; allowed population **UNDECIDED** | Browser/viewer/delivery service; provider/region **UNDECIDED** | Exact requested source/version only; no unrelated record; short-lived grant if approved | Per-request access; no-store; revoke/expiry; inaccessible/quarantined/deleted shown honestly | Browser persistence none; server retention **UNDECIDED** | No client cache; download/screenshot policy, audit and backup **UNDECIDED** | Identity/security; privacy/legal; clinical/content/accessibility | IDOR, assignment revoke, grant replay, cache/referrer/URL/log, active content, a11y; decide renderer/delivery/copy |
| Withdrawal / authority loss | Patient/authorized actor/governance source | Consent/authority metadata: `SENSITIVE` | Stop processing under withdrawn authority; exact effect **UNDECIDED** | Trusted actor and permitted withdrawal/delegation; legal exceptions **UNDECIDED** | Consent/document/job/storage/provider systems; recipients **UNDECIDED** | Closed reason and necessary linkage only | Block new operations; cancellation/late-result handling **UNDECIDED** | Consent/audit retention **UNDECIDED** | Withdrawal is not automatic universal deletion; in-flight/provider/backups **UNDECIDED** | Privacy/legal; data governance; architecture | Revoke at every stage; late result/source grant denial; decide user copy and retained-basis cases |
| Deletion request / purge | Authorized subject/records owner/system schedule | All originals, derived artifacts and metadata | Honor approved rights/lifecycle; purpose and exceptions **UNDECIDED** | Verified request, exact subject/scope, legal hold and records policy | DB/object/jobs/caches/providers/backups across regions **UNDECIDED** | Enumerated minimum deletion manifest without copying content | Requested/scheduled → pending/blocked/completed/failed, with honest evidence | Schedule and SLA **UNDECIDED** | Coordinated purge, backups, restored-data reconciliation and legal hold **UNDECIDED** | Privacy/legal; data governance; operations | Partial failure, idempotency, orphan, provider deletion, restore resurrection; decide policy/SLA |
| Backup / restore / legal hold | Infrastructure/data governance | Encrypted copies of health-sensitive data and metadata | Resilience/records obligation **UNDECIDED** | Restricted recovery personnel; approved purpose, region and hold authority | Backup provider/region/key custody **UNDECIDED** | Only governed stores; no ad hoc exports | Versioned backups; restore into isolated controlled workflow | Periods **UNDECIDED** | Backup deletion, hold release and tombstone reconciliation **UNDECIDED** | Infrastructure; data governance; privacy/legal; security | Unauthorized restore/read, wrong region/key, expired hold, deleted-data resurrection and recovery drill |

## 4. Purpose, consent, lawful basis, and India review

No P11 purpose or allowed population is approved. Human reviewers must decide separately whether
each operation is necessary for care intake, record continuity, institution workflow, source review,
or another documented purpose. Secondary analytics, model improvement, provider training, research,
and unrelated institutional use are prohibited unless separately governed.

Counsel and institutional privacy owners must determine applicable India Digital Personal Data
Protection Act and healthcare obligations using current deployment facts. This draft does not claim
DPDP compliance, select consent or another lawful basis, define Data Fiduciary/Processor roles,
approve a notice, set a child/guardian age or verification rule, determine cross-border legality, or
resolve health-record retention. Required questions include:

- exact purpose, necessity, permitted population, controller/processor roles, and user notice;
- whether affirmative document-specific consent is required for upload, OCR, external processing,
  clinician/institution access, retention, and sharing;
- verified-patient, pseudonymous, caregiver/guardian, assisted/kiosk, and withdrawal handling;
- access, correction, erasure, grievance, nomination/authorized representative and breach duties;
- legal/clinical record holds, institutional obligations and conflict with deletion requests;
- deployment region, international transfer, subprocessors, contracts, audit and evidence retention.

## 5. External processors and model egress

No scanner, storage, OCR, parser, LLM, support, analytics, or backup provider is approved. Before any
patient content leaves a controlled first-party boundary, privacy/legal, security, architecture and
institution owners must approve the named operation, minimum fields/pages, endpoint, region,
transfer basis, DPA/procurement, subprocessors, retention/deletion, training/model-improvement use,
abuse monitoring, human review, credentials, network allowlist, incident duties, support access and
fallback. Provider marketing or a zero-retention toggle is not sufficient evidence.

PaddleOCR, PaddleOCR-VL, Docling, Surya, docTR, RapidOCR and Tesseract are research/benchmark
candidates, not selected production processors. The current deterministic mock and offline harness
use synthetic engineering inputs only and establish no clinical/privacy suitability.

## 6. Minimization, browser/BFF, telemetry, and purpose leakage

The future API must accept and return only the fields required for the approved operation. File
bytes belong in object storage, not PostgreSQL blobs; unrestricted OCR text/vendor payloads do not
belong in metadata JSONB. Original filenames are untrusted and may be retained only as an approved,
bounded sanitized display value. Checksums detect byte identity and must not enable cross-owner
deduplication or existence probing.

The existing same-origin BFF model remains the reference: transient server-only credentials,
bounded upstream calls, strict response parsing, and `Cache-Control: no-store`. Original/derived
content, candidate values, source/object references, patient/encounter IDs, signed grants, tokens,
or consent bodies must not enter localStorage, sessionStorage, IndexedDB, Cache Storage,
service-worker caches, background sync, URLs/query strings, analytics/session replay, support/error
tools, logs, traces, metrics, screenshots or CI artifacts.

Operational records may contain only approved safe correlation, operation, stage, version, bounded
count/duration and closed outcome/error data. Access-controlled audit may link an actor/resource only
after purpose, retention and access decisions; it is not a raw document/OCR archive.

## 7. Withdrawal, deletion, legal hold, backup, and in-flight work

Consent withdrawal, deletion, expiration, assignment revocation, source unavailability and legal
hold are distinct events. Human policy must state which stops new processing, cancels queued/running
work, discards late results, removes viewing grants, deletes originals/derived artifacts/metadata,
retains audit evidence, delays purge, triggers provider deletion, and propagates to backups.

The product must not promise immediate deletion where legal hold, backups, already-dispatched
processing or recovery constraints apply. It must not treat withdrawal as consent to retain data for
another purpose. Restore must reconcile tombstones/retention before content becomes accessible.
Every state needs honest, approved user copy and incident escalation for partial failure.

## 8. Incident, breach, and subject-rights readiness

Before live use, owners must define detection, severity, on-call/escalation, containment, document
processing/source-view kill switches, secret/key rotation, affected-data assessment, processor and
institution coordination, counsel-led notification obligations, evidence preservation, recovery,
post-incident review, and rollback. Support tooling must not gain broad content access during an
incident by default.

Subject-rights workflows must authenticate the requester without leaking another subject, scope the
request across metadata/originals/derived content/providers/backups, distinguish correction from
clinical fact review, report unavailable/legal-hold states honestly, and preserve minimum required
audit evidence. Exact rights and response periods are **HUMAN LEGAL DECISIONS PENDING**.

## 9. Research and synthetic-data separation

Nonmedical `SYNTHETIC_*` fixture references, deterministic mock results and hostile synthetic files
remain in test/research contexts. They cannot be linked to a patient, presented as medical evidence,
or used to justify live acceptance. Real or linkable patient documents cannot silently become OCR
benchmarks, prompt examples, regression fixtures, analytics, or research datasets. Any approved
research dataset requires its own manifest, provenance/license, de-identification/governance,
access, environment, retention and ethics/privacy decisions.

## 10. Requirements, acceptance, and gate traceability

| Requirement / gate | Draft treatment | Current status |
| --- | --- | --- |
| `PRIV-001` minimization | §§3, 6 require minimum fields/pages/recipients and prohibit unrestricted payload copies. | PROPOSED; live P11 not implemented |
| `PRIV-002` purpose limitation | §§2, 4 separate every actor/operation/purpose and prohibit transitive consent. | HUMAN DECISION PENDING |
| `PRIV-003` retention | §§3, 7 require explicit per-artifact schedules; no duration chosen. | HUMAN DECISION PENDING |
| `PRIV-004` deletion/withdrawal | §§3, 7 distinguish withdrawal, purge, legal hold, provider and backup effects. | HUMAN DECISION PENDING |
| `PRIV-005` minimal referral payload | P11 does not implement referral sharing; document-to-referral transfer is prohibited. | DEFERRED TO P13 |
| `PRIV-006` pseudonymous minimization | §2 prohibits implied identity collection/linkage and requires a separate P11 decision. | HUMAN DECISION PENDING |
| `PRIV-007` sensitive logs | §6 prohibits content, identifiers and credentials in telemetry/support/error channels. | AS-BUILT P4–P7 BASELINE; P11 TESTS PENDING |
| `PRIV-008` research separation | §9 prohibits silent reuse of production documents. | PROPOSED CONTROL — UNAPPROVED |
| `PRIV-009` analytics | §6 excludes identifiable document/source content from analytics/session replay. | PROPOSED CONTROL — UNAPPROVED |
| `FR-DOC-001..003` | Upload/camera and validation require gates 1–3, approved population/purpose and hostile-file evidence. | NOT IMPLEMENTED / NOT VERIFIED |
| `FR-DOC-004..010` | OCR/classification require approved source, benchmark/provider, language/resource and privacy terms. | Synthetic mechanics only; live NOT VERIFIED |
| `FR-DOC-011..020` | Medical extraction/low confidence remain detached, unconfirmed and clinical-review blocked. | Gates 5–7 BLOCKED/OPEN; live NOT VERIFIED |
| `FR-DOC-021..023` | Source linkage, lifecycle and registry require permission, persistence and version evidence. | Synthetic evidence only; live NOT VERIFIED |
| `FR-PROV-001..007` | Exact source/attempt/provider/model/schema/confidence/verification lineage with separate source access. | P5 baseline + synthetic P11 evidence; live NOT VERIFIED |
| `AC-P11-001..011` | Future evidence is mapped in the readiness pack and threat/security drafts. | All remain NOT VERIFIED for live P11 |
| Gates 1–4 and 9 | Population/consent, file security, storage/retention, schema/processing, threat/privacy/release. | 0 approved; decisions pending |
| Gates 5–8 | Provider benchmark, registry contract, clinical extraction, source UI/assignment. | OPEN/BLOCKED; no activation |
| P10 live gates | Needed for clinician identity, assignment, review and source access. | 0/9 approved |
| P8-C/P9-C Stage 3 | Must not receive document content or be activated through P11. | BLOCKED |

## 11. Accountable reviewers, unsigned decision checklist, and acceptance evidence

Roles establish accountability only; names/signatures/dates must be supplied by authorized humans.

- [ ] **Privacy/legal and consent owner:** purpose, population, notice, consent/lawful basis, DPDP and
  guardian treatment, rights, processor/region, sharing, withdrawal, retention and deletion.
- [ ] **Identity/security owner:** actor assurance, patient/session binding, caregiver delegation,
  institution/assignment, source authorization, nonenumeration and revocation.
- [ ] **Application/data architect:** upload pattern, minimum schema, idempotency, lifecycle,
  transactions/outbox, concurrency, cancellation and reconciliation.
- [ ] **Security engineering:** threat review, formats/limits, signature detection, scanner,
  quarantine/sandbox, active content, preview, secrets and adversarial evidence.
- [ ] **Infrastructure/storage/operations:** provider/profile, region, IAM, encryption/keys,
  durable jobs, capacity/SLO, backup/restore, incident response, kill switch and rollback.
- [ ] **Data governance/records owner:** retention classes, legal hold, purge evidence, source/audit
  stewardship and restored-data handling.
- [ ] **Clinical governance and subject experts:** permitted medical purpose, candidate boundaries,
  evidence sufficiency, reviewer qualification and separation from clinical truth.
- [ ] **Accessibility/content and product/institution owners:** approved population/journey,
  meaningful notice/status/error/source copy, assisted use, accessibility and release decision.

Acceptance evidence must include approved decision records with scope/environment/population and
expiry; reviewed data-flow and threat/security architecture; real implementation evidence only in a
later authorized phase; PostgreSQL/object/job/API/browser tests; privacy leakage scans; hostile-file
and failure/race tests; accessibility review; incident/restore/rollback exercises; and all six CI
jobs on the applicable implementation SHA. Documentation and CI alone cannot approve P11.

## 12. STOP conditions and open decision register

Stop affected implementation, data collection, processing, sharing, or release if any applicable
item is unknown:

1. permitted purpose, population, uploader and ownership model;
2. notice, consent/lawful basis, guardian/delegation and institutional sharing;
3. exact upload pattern, supported formats/limits, scanner/quarantine/sandbox;
4. provider, recipient, region, DPA, subprocessors, retention/training/human review and egress;
5. object storage, IAM, encryption/key custody, retention, deletion, legal hold and backups;
6. schema, idempotency, transaction/outbox, durable worker, cancellation and reconciliation;
7. source-read/preview permissions, clinician assignment, renderer, copy and accessibility;
8. clinical extraction fields, validation, provenance and reviewer authority;
9. incident/breach, monitoring, kill switch, rollback, pilot and production approval.

Open decision IDs for human governance to assign: population/purpose; P11 consent/notice; upload
pattern and limits; scanner/quarantine; storage/provider/region/IAM; encryption/key custody;
retention/deletion/legal hold/backup; metadata and durable-processing architecture; provider/egress;
source delivery; clinician assignment/reviewer authority; incident/pilot/release. No decision ID,
owner name, signature, date, or disposition is fabricated here.

## 13. Conclusion

This is a draft privacy/data-flow assessment, not a completed DPIA or compliance determination.
P11 remains **0 APPROVED / 5 OPEN / 4 BLOCKED**; P10 remains **0/9 approved**; P8-C/P9-C Stage 3
remain blocked; `/documents` remains unavailable; P11-E remains unimplemented; and P7 deterministic
manual intake remains the supported fallback.
