# P11-E source-access and UI readiness design

**Work unit:** Pre-P11-E documentation/readiness design only
**Evidence baseline:** `main @ f71662322b27ec79004745ec6217283887700ac8`
**Alembic head:** `p7a_0007` (unchanged)
**Decision status:** independent review pending; this document grants no runtime, file, clinical, or production authority

This design is subordinate to the project governance hierarchy, accepted ADRs, and the nine-gate
matrix in [`P11_READINESS_GATE_REVIEW.md`](P11_READINESS_GATE_REVIEW.md). It does not start P11-E,
approve a source viewer, select an upload or storage design, or change any live gate. P11 remains
**0 APPROVED / 5 OPEN / 4 BLOCKED**; P10 live clinician access remains **0/9 approved**.

## 1. As-built inventory versus conceptual future state

The Pre-P11 specification and readiness review are dated baseline snapshots. The merged synthetic
subsets below are newer repository truth, but they close no live gate and satisfy no live P11
acceptance criterion.

| Concrete path / symbol | As-built purpose | Current authorization | Remaining dependency before live use |
| --- | --- | --- | --- |
| `backend/app/modules/documents/domain.py` — `SyntheticDocumentDescriptor`, `SyntheticDocumentState` | Immutable synthetic metadata and lifecycle proofs | Direct offline engineering tests only; `ENGINEERING_ONLY` | Gate 1 ownership/consent, gate 2 byte security, gate 3 storage, gate 4 reviewed schema/persistence |
| `backend/app/modules/documents/ingestion.py` — `assess_synthetic_ingestion`, `compare_owner_scoped_idempotency` | Pure comparison of caller-supplied synthetic descriptors | No file, lookup, authorization, checksum computation, or upload | Authoritative server identity/ownership, streamed validation, same-owner persistence and nonenumerating API design |
| `backend/app/modules/documents/contracts.py`, `ports.py`, `processing.py` | Strict parser/OCR request-result and synthetic attempt/job-intent contracts | No provider, handler, queue binding, source read, or runtime registration | Gates 2, 3, 4, 5 and 9; durable processing and approved provider benchmark |
| `backend/tests/ocr_support/` — `MockOCRAdapter`, benchmark helpers | Deterministic test-only OCR evidence | Test package only; synthetic/nonmedical and zero-egress | Gate 5 benchmark outcome and explicit provider/privacy/operations approval |
| `backend/app/modules/documents/classification.py` — `classify_synthetic` | Exact caller-label normalization and abstention | Synthetic declarations only; not medical classification | Approved classifier evidence and gate 6 contract review |
| `backend/app/modules/documents/registry.py` — `ProcessorRegistry`, `build_synthetic_processor_registry` | Explicit version-pinned descriptor resolution | `ENGINEERING_ONLY` plus `NOOP_ABSTAIN`; no executable processors | Gate 6 review and later approved implementations; runtime plugin discovery stays prohibited |
| `backend/app/modules/documents/candidates.py`, `evidence.py` — `SyntheticDocumentCandidate`, `verify_structural_evidence` | Text-blind structural matching of detached synthetic metadata | `UNCONFIRMED`/`ABSTAINED`; positive result only `STRUCTURALLY_MATCHED_UNCONFIRMED` with `SourceAccessStatus.NOT_VERIFIED` | Gates 1, 3, 5, 7, 8 and 9; source authority and independent clinical validation |
| `backend/app/main.py` | Explicit application composition | Documents module is not registered; no document capability/router exists | Approved module/application design and every applicable live gate |
| `apps/patient-web/app/documents/page.tsx` | Honest unavailable placeholder | No upload, status, review, source access, or BFF route | Gates 1–4, 8 and 9 plus a real backend and approved copy |
| `apps/clinician-web/app/page.tsx` | Accessible foundation empty state | No login, queue, assignment, patient overview, document or source panel | P10 gates, especially trusted IdP and assignment, plus P11 gates 1, 3, 7–9 |
| `backend/app/modules/provenance/{domain,application,public}.py` and `backend/app/modules/patients/public.py` | P5 typed provenance, timeline, patient/fact read capabilities | Existing patient/session-owned API paths only; no document source opener | Fresh source-detail authorization, minimized read model, lifecycle and retention policy |
| `backend/app/modules/identity/authorization.py` | Role/permission primitives including assigned encounter read | No configured production IdP, clinician directory or assignment source | P10 gates for trusted identity, institution and exact assignment |
| `backend/app/modules/clinical_intake/` and patient `/intake/...` routes | Deterministic, non-diagnostic P7 manual intake | Existing exact session, consent and encounter ownership boundary | Remains the required text/touch fallback; never depends on OCR |
| Alembic `p7a_0007`, API composition and ORM tree | No document persistence or route | No document table, upload/status/source API, storage binding, worker, live provider, or extractor | Reviewed decisions and separately authorized future implementation |

`ENGINEERING_ONLY`, `NOOP_ABSTAIN`, `UNCONFIRMED`, `ABSTAINED`,
`STRUCTURALLY_MATCHED_UNCONFIRMED`, and `SourceAccessStatus.NOT_VERIFIED` confer no clinical,
ownership, existence, access, or source-view authority. A structural match neither proves that a
patient file exists or was scanned nor that it is viewable or medically meaningful. P11-E is not
started, implemented, or accepted.

## 2. Human decision and blocker register

Statuses and owners below mirror `P11_READINESS_GATE_REVIEW.md` §§1,3 as reviewed on 2026-10-20.
No row is a sign-off form and none may be changed to approved by filling this document.

| Gate | Status / accountable human owner | Dated controlling source | Missing approval and required decision artifact | Permitted evidence so far / dependencies | Negative evidence required; keep disabled |
| --- | --- | --- | --- | --- | --- |
| 1. Lawful ownership, upload/read/share, consent, identity and assignment | **BLOCKED** — privacy/legal; identity/security; clinical governance; product/institution owner | `docs/implementation/P11_READINESS_GATE_REVIEW.md` (2026-10-20) §3 gate 1; `docs/26_PRIVACY_CONSENT_SPEC.md` §§2–8 | `HUMAN DECISION REQUIRED`: populations, uploader classes, ownership/transfer, purpose, document-specific consent/sharing, pseudonymous-session treatment, clinician/institution assignment; signed policy and reviewed data flow | P4 session/consent, P5 self-read and P7 exact-session flow only; depends on P10-B/D | Wrong subject/institution/assignment, revoked role/consent, expired session and nonenumeration tests. Keep every upload/share/read/review path disabled. |
| 2. File signature, quarantine, malware and active content | **OPEN — HUMAN SECURITY REVIEW REQUIRED** — security engineering; platform operations; product | `docs/implementation/P11_READINESS_GATE_REVIEW.md` (2026-10-20) §3 gate 2; `docs/15_DOCUMENT_AI_OCR_SPEC.md` §4.3 | `NOT RECORDED`: formats and measured byte/page/pixel/runtime limits, signature parser, scanner/quarantine/sandbox and active-PDF policy; threat model and hostile-fixture report | Generic path guards and synthetic hostile-file benchmark plan only | Spoofed MIME, polyglot, bomb, malformed/corrupt input, active PDF, external reference, archive/executable and timeout tests. Keep untrusted byte acceptance disabled. |
| 3. Private storage, encryption, region, keys, retention and revocation | **BLOCKED** — privacy/legal; data governance; security; infrastructure/institution owner | `docs/implementation/P11_READINESS_GATE_REVIEW.md` (2026-10-20) §3 gate 3; `docs/15_DOCUMENT_AI_OCR_SPEC.md` §§4.4–4.5 | `HUMAN DECISION REQUIRED`: provider/profile, encryption/key custody, region/DPA, tenant isolation, backup/restore, retention/deletion/legal hold, signed-view policy and incident handling | `ObjectStoragePort` and noncompliant local adapter; ADR-009; depends on gate 1 and reviewed deployment | Cross-owner object, signed-URL replay, revoked/deleted/quarantined object, orphan and backup-deletion tests. Keep production objects and previews disabled. |
| 4. Metadata/processing schema, outbox and idempotency | **OPEN — SCHEMA REVIEW REQUIRED** — application/data architecture; privacy/data governance | `docs/implementation/P11_READINESS_GATE_REVIEW.md` (2026-10-20) §3 gate 4; `docs/15_DOCUMENT_AI_OCR_SPEC.md` §§3,6 | `NOT RECORDED`: reviewed migration/schema, lifecycle constraints, attempts/generations, owner-scoped idempotency, transaction/outbox, cancellation, cleanup and reconciliation | Synthetic lifecycle/attempt contracts plus generic PostgreSQL/outbox/jobs; no document table | Duplicate/race, stale result, rollback, partial DB/object/job failure and cleanup tests. Keep persistence, events and workers disabled. |
| 5. Measured OCR/provider/language/resource/egress | **OPEN — BENCHMARK/APPROVAL REQUIRED** — clinical validation; ML/document-AI; security/privacy; operations | `docs/implementation/P11_READINESS_GATE_REVIEW.md` (2026-10-20) §3 gate 5; `docs/15_DOCUMENT_AI_OCR_SPEC.md` §5.4 | `NOT RECORDED`: reproducible results, selected pinned model/artifact/hash, accuracy/abstention thresholds, license/DPA/egress, resource profile and rollback | Provider-neutral ports, test-only mock and offline harness; OCR benchmark plan; depends on gates 2, 3 and 9 | Hindi/mixed-language, handwriting/table, critical-token, silent omission, timeout/crash, egress and rollback evidence. Keep real OCR/model/provider disabled. |
| 6. Registry and source/version contracts | **OPEN — DESIGN REVIEW REQUIRED** — application architecture; document-AI engineering | `docs/implementation/P11_READINESS_GATE_REVIEW.md` (2026-10-20) §3 gate 6; `docs/15_DOCUMENT_AI_OCR_SPEC.md` §§5–8 | `NOT RECORDED`: accepted production registry/source/provenance/version contract and ownership review | Closed synthetic classification, version-pinned registry, `NOOP_ABSTAIN` receipts and structural evidence only | Duplicate/ambiguous/unknown/stale/mismatched version and runtime-plugin rejection. Keep executable processors and clinical routing disabled. |
| 7. Medical extraction and reviewer authority | **BLOCKED** — clinical governance; pharmacy/laboratory subject experts; data governance | `docs/implementation/P11_READINESS_GATE_REVIEW.md` (2026-10-20) §3 gate 7; `docs/15_DOCUMENT_AI_OCR_SPEC.md` §7 | `HUMAN DECISION REQUIRED`: field schemas, evidence sufficiency, validation set/thresholds, reviewer qualification, disposition/promotion and interaction source | Text-blind nonmedical candidate contracts only; depends on gate 5 and live P10-D | Missing unit/date/negation, incorrect dose/value alignment, low confidence, conflict, stale source and lower-trust overwrite tests. Keep medical extraction, fact promotion and clinical claims disabled. |
| 8. Preview/UI/accessibility and clinician assignment | **BLOCKED** — identity/security; privacy/legal; clinical content; accessibility/product | `docs/implementation/P11_READINESS_GATE_REVIEW.md` (2026-10-20) §3 gate 8; `docs/15_DOCUMENT_AI_OCR_SPEC.md` §9 | `HUMAN DECISION REQUIRED`: source-view permissions, assignment policy, sanitized preview approach, patient/clinician copy and manual accessibility review | Unavailable patient route, empty clinician shell and current P6 accessibility/privacy baseline only; depends on gates 1, 3, 7 and P10 | IDOR, source lifecycle, safe-copy, keyboard/screen-reader/reflow, cache/URL/log, SSRF/XSS/PDF and expiry tests. Keep all source/candidate/timeline screens disabled. |
| 9. Threat, incident, pilot, monitoring, rollback and release | **OPEN — RELEASE APPROVAL REQUIRED** — security; privacy/legal; clinical safety; model governance; operations; product/institution owner | `docs/implementation/P11_READINESS_GATE_REVIEW.md` (2026-10-20) §3 gate 9; `docs/15_DOCUMENT_AI_OCR_SPEC.md` §§12–14 | `NOT RECORDED`: approved threat/privacy reviews, incident runbook, pilot population, SLO/monitoring, kill switch, rollback drills and release decision | CI/security primitives and synthetic tests only; depends on evidence from every future P11 phase | Abuse, leakage, dependency outage, alerting, revoke/kill-switch, restoration and rollback exercises. Keep pilot/production activation disabled. |

Count remains **0 APPROVED / 5 OPEN / 4 BLOCKED**. Per Spec 15 §11 and the readiness review §5,
all live `AC-P11-001..011` remain **NOT VERIFIED**.

## 3. Threat and authorization boundary matrix — design only

Every future request must re-resolve trusted active identity, exact permission, exact
patient/encounter/institution assignment, approved lawful purpose and scope-specific consent,
source lifecycle/retention/withdrawal, owner-scoped idempotency, and object version/freshness on the
server. A URL, opaque ID, browser state, role label, registry receipt, candidate, digest, object key
or prior successful request is never authority. Denials use one reviewed content-free policy so an
unauthorized caller cannot distinguish missing from forbidden; this design deliberately does not
promise HTTP 403 versus 404 before policy review.

| Actor class | Future authority that must be independently proven | Default while unresolved |
| --- | --- | --- |
| Patient | Trusted authenticated patient binding, exact patient/encounter ownership and document purpose/consent | No document access; current pseudonymous session is not patient identity |
| Caregiver | Separate caregiver identity, delegation scope, expiry, patient relationship and consent | Actor/flow does not exist; deny |
| Pseudonymous session | Exact active session, encounter ownership and an approved document-specific purpose/scope | General `clinical_intake` consent is non-transitive; deny document operations |
| Kiosk | Approved kiosk threat model, session isolation, cleanup, supervised purpose and no residual data | Actor/flow does not exist; deny |
| Clinician | Trusted active IdP actor, permission plus exact institution and current encounter/patient assignment | Role constant alone is insufficient; deny |
| Administrator | Explicit operational permission and purpose; no implicit clinical/source access | Admin role never grants document content or clinical review by default |

| Deny-by-default threat | Future negative proof | Human decision owner |
| --- | --- | --- |
| Guessed source ID or another patient's ID | Indistinguishable content-free denial; no timing/count/existence leak | Identity/security + privacy |
| Another institution | Exact institution and assignment mismatch denial on every request | Institution owner + identity/security |
| Clinician role without assignment; revoked/disabled role | Deny after fresh actor and assignment resolution, including stale open UI | Identity/security + clinical governance |
| Revoked/missing consent or expired session | Block new read/process/mutation; define in-flight handling without false deletion promises | Privacy/legal + product |
| Stale queue/read-model reference | Recheck source generation, assignment and actor; deny or return reviewed unavailable state | Application architecture + identity |
| Deleted, quarantined, rejected, expired or superseded object | No bytes or signed URL; lifecycle-safe nonenumerating response | Security + data governance |
| Source/candidate/attempt/version mismatch | Fail closed before display or disposition; no partial clinical mutation | Document-AI + clinical governance |
| Bearer/token/key leakage | No secrets in client JS, URL, analytics, logs or errors; rotate/revoke and incident test | Security + operations |
| Browser cache, service worker or logs | Automated absence scans plus browser evidence; `no-store` for sensitive responses | Frontend/security + privacy |
| SSRF, unsafe preview or active PDF | No caller URL fetch; sanitized/origin-isolated viewer; active content disabled; hostile fixtures | Security engineering |
| Signed URL replay | Short-lived single-purpose grant, audience/object/version binding and revocation behavior | Security + storage owner |
| BFF error disclosure | Reject malformed upstream data and map to bounded error; never relay raw body | Application security |
| Repeated ambiguous upload/finalize mutation | Owner-scoped idempotency and authoritative lookup; no blind client retry | Application/data architecture |

## 4. Conceptual presentation inventory and safe-copy rules

This is a non-executable state specification. Every example label is **DRAFT — CONTENT/A11Y REVIEW
REQUIRED** and is generic, nonclinical placeholder copy.

| State | Conceptual patient/clinician presentation rule |
| --- | --- |
| Unavailable/disabled | “Document feature unavailable.” Do not show upload, preview or clinical action. |
| Loading | Bounded progress/status with cancellation/navigation safety; never imply completion. |
| Unknown / no record | Distinguish “no record returned” from “state unknown”; never say a condition or medication is absent. |
| Unsupported | Name only approved generic format guidance; preserve manual intake. |
| Simulated lifecycle | Must say “engineering simulation”; never visually resemble a real patient record. |
| Processing/error/stale | State that processing is incomplete, unavailable or stale; do not reuse prior results as current. |
| Consent/assignment denied | Generic nonenumerating access message; do not reveal source existence or another subject. |
| Revoked | Access and new processing stop according to approved policy; do not claim universal deletion. |
| Quarantined | No preview/download; generic security state without parser/scanner details. |
| Source inaccessible/deleted | “Source unavailable” rather than reconstructed/fabricated evidence. |
| Unconfirmed candidate | Explicitly unconfirmed and source-dependent; no diagnosis, treatment, medication instruction or reassuring absence wording. |

“No record,” “cannot verify,” “not authorized,” “unknown,” and “no clinically confirmed assertion”
are distinct states. The UI must never convert any of them into “none,” “normal,” “safe,” “no known
allergies,” “not taking medication,” or another clinical conclusion.

Future browser privacy rules are absolute: original bytes, page images, OCR text, medical candidates,
bearers, signed URLs, source references and patient identifiers must not enter `localStorage`,
`sessionStorage`, IndexedDB, Cache Storage, service-worker caches, analytics/session replay, URLs,
query strings, or client error payloads. Current same-origin BFF rules remain the reference:
transient `HttpOnly`, `SameSite=Strict`, `Path=/` cookies, production/non-loopback `Secure`,
server-only bearer forwarding, bounded upstream responses and `Cache-Control: no-store`. These are
design requirements, not P11-E implementation.

P7 text/touch manual intake stays available when documents, camera or OCR are unavailable. Neither
`STRUCTURALLY_MATCHED_UNCONFIRMED` nor a `NOOP_ABSTAIN` receipt grants permission or supports a
clinical display.

## 5. Review/preview and accessibility security plan

Before a source viewer can exist, accountable owners must approve a sanitizer/renderer boundary and
delivery design. Each preview request must renew identity, permission, assignment, purpose/consent,
source lifecycle, retention/withdrawal and exact object-version checks. Delivery must be time-limited,
object-isolated and noncacheable; revocation must prevent subsequent access. The design must address
content sniffing and safe `Content-Disposition`, origin isolation, restrictive CSP, PDF JavaScript,
forms/attachments/external references, XSS/SSRF, signed-URL replay, screenshots/download/source-copy
policy, and cleanup. This pack selects no library, provider or streaming pattern and authorizes no
current clinical preview.

| Area | Automated engineering evidence | Manual approval evidence |
| --- | --- | --- |
| Keyboard/focus | Complete keyboard path, visible focus, logical order, contained/restored dialog focus | Accessibility review with representative assistive workflows |
| Screen reader/status | Named controls/landmarks, associated errors, polite/assertive async announcements as reviewed | Screen-reader and content review of every sensitive state |
| Reflow/zoom | 320px and 390px reflow, zoom, touch targets, no hidden action | Product/accessibility sign-off |
| Camera/file alternative | Permission-denial test; text/touch fallback remains reachable | Device/population usability review |
| State semantics | Visible text for unknown, unconfirmed, stale, revoked, unavailable and quarantined; not color-only | Clinical/content/privacy approval of exact wording |
| Session/network/CSRF | Expiry, CSRF, offline, timeout, partial-response and retry tests with no false success | Security threat-model and incident review |
| Preview isolation | CSP/header, active-content, cross-origin, cache and hostile-fixture tests | Security approval of renderer/delivery architecture |

## 6. Requirements traceability and conditional sequencing

Planning evidence is not acceptance evidence.

| Requirement | Existing evidence | Live acceptance still missing / negative obligation |
| --- | --- | --- |
| `FR-DOC-002` | Patient route exists only as unavailable placeholder; P6 camera-independent shell baseline | Approved file/camera flow; permission denial, fallback and no-browser-persistence evidence |
| `FR-DOC-017` | P5 timeline service and synthetic document date contracts are separate | Authorized projection; missing date must not fabricate ordering; stale/deleted source handling |
| `FR-DOC-020` | P11-D candidates are only `UNCONFIRMED`/`ABSTAINED` | Governed reviewer authority; low confidence must never auto-confirm |
| `FR-DOC-021` | Structural evidence retains exact synthetic coordinates and `NOT_VERIFIED` access | Permissioned source linkage; inaccessible/deleted/cross-object source must not leak or falsely resolve |
| `FR-DOC-022` | Synthetic lifecycle and attempt/status contracts | Persistent/API lifecycle and honest partial, stale, revoked and failed states |
| `FR-PROV-001..007` | P5 provenance types plus strict synthetic P11 source/version evidence | Live OCR/document source, exact attempt/page, confidence semantics, unconfirmed state, version lineage, policy separation, external origin and access tests |
| `AC-P11-007` | Text-blind structural linkage only | Medical fact provenance and inaccessible-source integration; **NOT VERIFIED** |
| `AC-P11-008` | Candidate contract forbids clinician-confirmed state | Authorized clinical review integration and low-confidence tests; **NOT VERIFIED** |
| `AC-P11-009` | P7 manual intake exists independently; mock failures are isolated | End-to-end live OCR outage with manual path preserved; **NOT VERIFIED** |
| `AC-P11-011` | No source viewer or trusted clinician assignment | Real assigned-clinician source review plus IDOR/revocation tests; **NOT VERIFIED** |
| Cross-cutting security/privacy/a11y | P4–P7 BFF/privacy/accessibility baseline, generic CI/security scans | P11-specific threat model, retention, hostile upload/preview, accessibility and release evidence |

Conditional future work packages, none authorized by this document:

1. Live P11-A upload/storage/security/schema and P11-B real OCR/provider may begin only after the
   accountable decisions for gates 1–5 and 9 that apply to the chosen ordering are recorded. The
   order may change with the approved upload/storage/provider architecture.
2. Live P10-B/D identity, assignment and source-review authority requires independent closure of
   the applicable P10 gates before any clinician document access.
3. Live P11-D medical extraction/candidate review requires independent clinical field-schema and
   evidence validation plus privacy, retention, source-authority and reviewer approvals.
4. P11-E UI, service read models, preview and review require real approved backends; applicable P11
   and P10 gates; security, clinical, content and accessibility approvals; and independent PR review.
5. A later, separately reviewed synthetic-only P11-E presentation-contract subset could test inert
   types in isolation, but may not change patient/clinician routes, introduce a fake clinician, or
   imply uploads work.

Objective blockers by package: package 1 is blocked by ownership/consent, file-security, storage,
schema and provider/release decisions; package 2 by trusted IdP/directory, institution and assignment,
lawful access and review authority; package 3 by approved medical schemas, validation thresholds,
source retention and reviewer qualifications; package 4 by all preceding applicable decisions plus
preview/copy/a11y approval; package 5 requires a new explicit synthetic-only prompt and independent
architecture/privacy review.

**STOP condition:** if consent/purpose, source ownership/access, retention/deletion, trusted IdP,
assignment/institution, or clinical claim/reviewer requirements are unknown, stop the affected work.
Any future provider, upload pattern or schema decision must first be recorded in the decision log or
appropriate ADR; implementation must not silently choose it.

## 7. Manual gate-review checklist and evidence ledger

The evidence categories align with Spec 15 §12. Existing paths are evidence sources, not approvals.

| Evidence ID | Accountable owner | Expected artifact and current source | Test plan | Approval state / blocker |
| --- | --- | --- | --- | --- |
| `E-P11-01` | Privacy/legal + product/institution | Lawful purpose, populations, ownership/share/consent/assignment decision; current `docs/26_PRIVACY_CONSENT_SPEC.md` §§2–9 | Wrong-subject, revoked/missing consent, pseudonymous and delegation cases | `HUMAN OWNER TO COMPLETE`; gate 1 BLOCKED |
| `E-P11-02` | Security + platform operations | Upload threat model, signature/scan/quarantine/active-PDF policy; Spec 15 §4.3 | Hostile files, limits, timeout, isolation and no-leak checks | `HUMAN OWNER TO COMPLETE`; gate 2 OPEN |
| `E-P11-03` | Data governance + security + infrastructure | Storage/encryption/key/region/DPA/retention/deletion/backup/preview decision; ADR-009 and Spec 15 §§4.4–4.5 | Isolation, replay, revoke, orphan, restore and purge evidence | `HUMAN OWNER TO COMPLETE`; gate 3 BLOCKED |
| `E-P11-04` | Application/data architecture | Reviewed schema/migration/lifecycle/outbox/idempotency design; Spec 15 §§3,6 | PostgreSQL atomicity, concurrency, stale generation and reconciliation | `HUMAN OWNER TO COMPLETE`; gate 4 OPEN |
| `E-P11-05` | Clinical validation + document-AI + privacy/ops | Reproducible benchmark, pinned model/license, language/resource/egress/rollback record; `docs/research/ocr/OCR_BENCHMARK_PLAN.md` | Critical token, handwriting, Hindi/mixed, table, failure transparency and zero-unapproved-egress | `HUMAN OWNER TO COMPLETE`; gate 5 OPEN |
| `E-P11-06` | Application architecture + document-AI | Production registry/source/version review; synthetic evidence in `backend/app/modules/documents/{classification,registry,evidence}.py` | Duplicate, ambiguity, version mismatch and no runtime plugin | Engineering criteria assessable now; live approval `NOT RECORDED`, gate 6 OPEN |
| `E-P11-07` | Clinical governance + pharmacy/lab SMEs | Approved field schemas, validation set, evidence/abstention and reviewer policy; Spec 15 §7 | Critical ambiguity, conflict, no inference and no lower-trust overwrite | `HUMAN OWNER TO COMPLETE`; gate 7 BLOCKED |
| `E-P11-08` | Identity/security + content + accessibility | IdP/assignment/source-access policy, preview review and approved copy; `docs/24_CLINICIAN_DASHBOARD_SPEC.md` §§1–5 | IDOR/revocation, safe states, keyboard, screen reader, 320/390 reflow and preview attacks | `HUMAN OWNER TO COMPLETE`; gate 8 BLOCKED |
| `E-P11-09` | Security/privacy/clinical/model governance/ops/product | Integrated threat/privacy review, pen-test/hostile fixtures, incident runbook, pilot decision, monitoring and rollback | Kill switch, alert, outage, incident and rollback drills | `HUMAN OWNER TO COMPLETE`; gate 9 OPEN |
| `E-P11-10` | Engineering owner | Exact-head CI, scope and prohibited-activation audit; this design and `38_PROGRESS_TRACKER.md` | Six CI jobs; links; changed-path/runtime/schema/dependency checks | Assessable for this docs-only PR; cannot approve any live gate |

## 8. Readiness conclusion

This pack is ready only for independent architecture, security, privacy, clinical, accessibility and
data-governance review. No sign-off, vendor, quota, pilot population, date or approval has been
invented. P8-C real-patient AI, P9-C patient-facing safety, P10 live clinician authority and all live
P11 capabilities remain restricted. Stop after review; do not begin P11-E or P12 from this document.
