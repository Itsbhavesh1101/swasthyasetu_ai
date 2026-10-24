# Pre-P21 — Admin, Governance, Clinical Review: Existing-Spec Reconciliation and Accountable Decision Docket

> **DRAFT — NOT A NEW ADMIN SPECIFICATION; NOT AN OFFICIAL GATE COUNT; NO HUMAN APPROVAL; P21-A/B/C/D NOT STARTED; NO LIVE ADMIN OR CLINICAL AUTHORITY**

**Recorded:** 2026-10-25

**Verified baseline:** `main @ 06d51e5f29a486c9bc13b6d1d65d5ec82239f2ac`

**Existing design:** [`docs/25_ADMIN_PORTAL_SPEC.md`](../25_ADMIN_PORTAL_SPEC.md), created during Pre-P13 and still an unapproved draft

**Existing readiness inventory:** [`docs/implementation/PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md`](PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md)

**Review-owner roles:** product/institution, identity/security, privacy/legal/consent, source governance, provider/resource/referral operations, clinical safety, clinician workflow/provenance, model governance, data/audit/retention, accessibility/content/localization, platform/incident/release, and independent quality. Assignment and signatures remain pending.

This document is a dated review delta. It reconciles the existing Spec 25 with the current repository and upstream gates; it neither replaces that specification nor makes a clinical, legal, privacy, security, institutional, source, model, or release decision. Documentation and passing CI are not implementation or approval evidence.

## A. Existing artifacts versus present implementation — no duplicate

Spec 25 was created during Pre-P13. The older P13 readiness Gate 7 correctly recorded that it was absent at that earlier evidence date. The missing document now exists as an **unapproved draft**, but document existence is distinct from accountable gate review, owner approval, technical implementation, live validation, pilot eligibility, and release authorization. Historical records remain unchanged; P13 Gate 7 remains BLOCKED/not approved, and P21 remains **NOT STARTED**.

### Dated source hierarchy and evidence reconciliation

| Artifact or area                           | Current repository evidence                                                                                                                                                                                  | Unimplemented or blocked boundary                                                                                                                                                      | Owner / authority missing                                                                                                       |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Existing Spec 25                           | `docs/25_ADMIN_PORTAL_SPEC.md` is the unapproved canonical admin design draft created during Pre-P13.                                                                                                        | No route, API, data model, workflow, source, credential, approval, or live validation follows from the document.                                                                       | Accountable product/institution, identity/security, privacy, source, clinical, audit, accessibility and release review/signoff. |
| Pre-P13 admin readiness                    | `docs/implementation/PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md` records proposed OPEN/BLOCKED evidence areas and an unsigned template.                                                                        | It is not an official gate program and authorizes neither P13-E nor P21.                                                                                                               | Every named accountable role remains unassigned/unsigned.                                                                       |
| P13 provider/referral readiness and Gate 7 | `docs/implementation/P13_READINESS_GATE_REVIEW.md` historically says Spec 25 was missing; patient referrals remain unavailable and admin-web was a shell.                                                    | The missing-document artifact is addressed only by an unapproved draft. Roles, source warnings, copy, accessibility, privacy, identity, implementation and review remain unresolved.   | P13 source/referral and human review owners. Gate 7 remains BLOCKED/not approved.                                               |
| P20 specification/readiness                | P20 documentation defines future composition boundaries and eight unsigned review areas.                                                                                                                     | P20-A/B/C/D runtime is NOT STARTED and all live P20/product acceptance is unverified.                                                                                                  | Upstream module and release owners; P20 documentation grants no admin authority.                                                |
| `apps/admin-web`                           | `app/page.tsx` renders only an accessible “Foundation ready” empty state, with base loading/error/layout support and one page test.                                                                          | No navigation, BFF, identity flow, admin screen, live data, source moderation, clinical queue, audit viewer, or privileged action.                                                     | P21-B architecture, identity, security, privacy, accessibility/content, and product approval.                                   |
| P4 identity/authorization/MFA primitives   | Actors/roles persist; provider-neutral authentication/current-actor contracts and a deny-by-default `AuthorizationService` exist. Administrative role constants require trusted `ActorContext.mfa_verified`. | No configured production IdP, enrollment/proofing, actual MFA ceremony/recovery, trusted role or institution/source/object assignment, actor-management API, or credential governance. | Identity/security and institution owners. Role/MFA tests are not production proof.                                              |
| P3 outbox/audit foundations                | Versioned events and PostgreSQL transactional outbox primitives exist. `backend/app/modules/audit/` contains only `.gitkeep`.                                                                                | No admin/domain audit event contract, audit store/viewer, tamper evidence, retention/export policy, or audit-of-audit workflow.                                                        | Owning domains plus audit/data governance, privacy/security and records owners.                                                 |
| P10/P11 clinician/document boundaries      | P10 immutable synthetic summary contracts and P11 synthetic lifecycle/OCR/classification/evidence contracts exist.                                                                                           | P10 and P11 live use remain 0/9 approved; P11 has five OPEN/four BLOCKED. No trusted clinician assignment, source viewer, correction workflow or document processing.                  | Clinical governance, identity/institution, source/provenance, privacy/security and document owners.                             |
| P13 registries/referrals/source moderation | Provider, resource, referral and notification module directories are placeholders; `REFERRAL_SHARING` exists only as a consent purpose.                                                                      | No source registry, verified record, routing/referral service, recipient, send, status authority, moderation UI, or external adapter.                                                  | Source/provider/referral, consent/privacy, recipient and institutional owners.                                                  |
| P15 knowledge                              | Self-care module is a placeholder and P15 specification/readiness are unapproved drafts.                                                                                                                     | No approved corpus, eligibility policy, content workflow, RAG service or patient output.                                                                                               | Clinical self-care/content/source governance.                                                                                   |
| P18/P19 governance                         | Research specifications/readiness inventories exist; model module paths are placeholders.                                                                                                                    | P18 has no approved task/dataset/baseline/model; P19 therefore has no comparator. No promotion or patient inference.                                                                   | Research, clinical/biostatistical validation, data, model governance and release owners.                                        |
| P22 review                                 | Security/privacy controls exist incrementally; P22 remains NOT STARTED/NOT COMPLETE.                                                                                                                         | No platform-wide retention, threat, resilience, privileged identity, incident, bounded-pilot or release acceptance.                                                                    | Security, privacy/legal, records, operations, institutional and release owners.                                                 |

### Evidence classes

| Class                           | Present evidence                                                                                                                                                    | What it does not prove                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Implemented platform primitives | P4 actors/roles/authz contracts, purpose-specific consent, typed module capabilities, configuration flags, PostgreSQL/outbox, P5/P7 facts/provenance/manual intake. | Production admin identity, object/source authority, governance workflow, clinical approval or release. |
| Synthetic/detached evidence     | P8/P9/P10/P11 engineering contracts and tests.                                                                                                                      | Real-patient AI/safety/clinician/document authority.                                                   |
| Unapproved designs              | Specs/readiness packs for P12–P21, including Spec 25.                                                                                                               | Human decision, implementation or live acceptance.                                                     |
| Upstream blocked runtime        | P8-C/P9-C Stage 3; live P10/P11; P13–P21 modules as recorded.                                                                                                       | Eligibility for a P21 screen or privileged action.                                                     |
| Human decisions                 | None are signed by this phase.                                                                                                                                      | CI, PR review, constants and flags cannot substitute.                                                  |
| Future P21 engineering          | P21-A backend, P21-B web, P21-C clinical queues, P21-D audit/maker-checker.                                                                                         | No unit is authorized or started here.                                                                 |

## B. Scope and responsibility reconciliation — P13-E versus P21-A/B/C/D

| Future unit/domain | Conditional responsibility                                                                                                                                                                                | Authority it never acquires automatically                                                                                                        |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| P13 core and P13-E | P13 owns verified provider/resource truth, source provenance/freshness, specialty-first routing, referral lifecycle/external side effects, and any later bounded moderation/source-warning UI.            | P13-E cannot create source truth, clinical suitability, consent, referral delivery evidence, P21 governance, or generic admin authority.         |
| P21-A              | Separately authorized admin application/API contracts, thin routes, scoped services, and server-enforced actor/role/institution/object/source/purpose permissions.                                        | It cannot grant its own roles, approve source/clinical/content/model truth, bypass owning modules, or perform arbitrary cross-module ORM writes. |
| P21-B              | Admin web/BFF, minimum-data views, inaccessible/read-only/degraded states, confirmations and accessible interaction after backend authorization exists.                                                   | Frontend state, hidden routes, cookies, feature flags, opaque IDs or success copy never authorize an operation.                                  |
| P21-C              | Clinical review queues only after P10 identity/assignment, source/provenance, correction/supersession, concurrency and audit authority is independently approved.                                         | Ordinary admins cannot access patients, confirm/reject facts, resolve clinical disagreement or act as clinicians.                                |
| P21-D              | Authorized audit views and maker-checker mechanics after event/access/retention/integrity decisions; the source domain retains approval control.                                                          | Audit does not become the clinical record; mechanics do not appoint approvers or grant policy/model/source authority.                            |
| Owning domains     | P4 owns consent/identity foundations; P9/P14/P15 own clinical policy; P10 owns clinician decisions; P13 owns source validation/referral; P18/P19 own research/model evidence; P22 owns hardening/release. | These responsibilities do not transfer to a generic admin role or UI.                                                                            |

### P4 identity trust gap

Server-side permission checks and a trusted `mfa_verified` boolean are valuable staged primitives. They do **not** establish a production IdP, identity proofing or enrollment, an actual MFA ceremony/recovery channel, current employment/relationship, actor provisioning/revocation, assigned institution, permitted patient/object/source, service-account governance, maker-checker independence, or credential lifecycle. Every privileged read and mutation must independently verify the active actor, institution, object, source, assignment, purpose and qualified reviewer authority at operation time.

No privilege may derive from frontend state, route hiding, feature flags, usernames, client headers, bearer/opaque IDs alone, staged tokens, CI results, PR approvals, or documentation. Backend authorization is authoritative and must fail closed without revealing object existence.

## C. Accountable decision docket — eight descriptive domains

These domains organize missing evidence. They are not a project-approved P21 gate count and must not be converted into approval arithmetic.

### 1. Production identity, MFA, role/object/source/institution authorization — BLOCKED

- **As-built proof:** P4 actor/role persistence, provider-neutral identity contracts, `ActorContext`, deny-by-default permissions, self-subject guard and administrative MFA-flag check.
- **Reason:** no trusted production provider, proofing/enrollment, MFA ceremony/recovery, current role/institution/source/object assignment, service-account lifecycle or credential policy exists.
- **Roles needing assignment:** identity/IAM, security, privacy, institution/employer, application owner, operations and independent security reviewer.
- **Missing accountable decision:** provider and assurance levels; provisioning/deprovisioning/revocation; role/permission/object/source/tenant matrix; MFA/recovery; service identities; session freshness; emergency access.
- **Required signed/source-backed evidence:** authoritative identity/assignment sources, threat/data-flow review, approved matrix, credential/runbook evidence and dated reviewer decisions.
- **Dependent units:** P21-A/B/C/D and P13-E.
- **Negative/adversarial tests:** forged role/header/MFA; disabled/revoked actor; stale assignment; wrong institution/object/source; IDOR/enumeration; privilege escalation; confused deputy; service-account impersonation.
- **Safe-off:** deny and show a nonenumerating inaccessible/unavailable state; P7 manual intake remains independent.
- **STOP:** any identity, MFA, relationship, assignment or scope is absent, stale, client-controlled or unverified.

### 2. Source-backed provider/resource verification and freshness — BLOCKED

- **As-built proof:** P13 policy/readiness drafts and ADR-015 define registry truth; provider/resource modules are placeholders and no real record exists.
- **Reason:** no approved source/right, field model, verifier, evidence format, freshness/expiry, dispute/correction, suspension/revocation or public-eligibility decision.
- **Roles needing assignment:** source governance, provider/resource steward, privacy/legal/licensing, clinical safety for critical resources, security, institution and operations.
- **Missing accountable decision:** sources/rights; field-level proof; verifier qualification; lifecycle/cadence; correction/appeal; critical-contact dual control; outage/recall and publication eligibility.
- **Required signed/source-backed evidence:** immutable source manifest, rights record, field/proof schema, verifier assignment, approved state model, freshness policy, review/incident evidence.
- **Dependent units:** P13-A/B/E and P21-A/B/D.
- **Negative/adversarial tests:** fabricated contact/source; malicious URL/redirect; Unicode/control spoof; future/expired/revoked proof; source poisoning; concurrent verify/suspend; synthetic record entering protected mode.
- **Safe-off:** record remains unverified/unavailable and no contact/link is generated or displayed as verified.
- **STOP:** no real provider/resource/contact or verified badge without current source-backed evidence and independent authority.

### 3. Governing-domain decisions, maker-checker and conflict of interest — BLOCKED

- **As-built proof:** immutable/versioned metadata exists in synthetic P9/P10/P11 contracts; no live governance state machine or approver registry exists.
- **Reason:** policy vocabulary does not appoint signatories or define independence, quorum, conflict, expiry, activation, suspension or rollback authority.
- **Roles needing assignment:** owning P9/P14 safety, P15 content, P18/P19 model, P10 clinical, P13 source, privacy/security, institution and audit governance.
- **Missing accountable decision:** distinct proposer/verifier/approver eligibility; separation and conflict rules; object/version binding; effective/expiry/review triggers; activation/rollback; emergency suspension.
- **Required signed/source-backed evidence:** domain-specific approval policies, qualified assignments, immutable decisions, validation evidence and rollback/incident records.
- **Dependent units:** P21-A/C/D, P13-E and every governing source domain.
- **Negative/adversarial tests:** self-check; ordinary-admin self-promotion; forged/stale approval; wrong version/environment; concurrent approval/revocation; audit bypass; rollback abuse; PR/CI treated as approval.
- **Safe-off:** read-only/unavailable; an unsigned or expired object cannot activate.
- **STOP:** generic admin must never become clinical, source, policy, content or model authority.

### 4. P10 clinical review queue and P11 document-source authority — BLOCKED

- **As-built proof:** P5 provenance/correction foundations, synthetic P10 summary contracts, and detached synthetic P11 contracts; no live clinician queue or source viewer.
- **Reason:** P10 and P11 live approval remain 0/9; P11 remains five OPEN/four BLOCKED. Trusted clinician assignment, source access, correction authority and document lifecycle are absent.
- **Roles needing assignment:** clinical governance, clinician operations/institution, identity/security, provenance/data governance, document security/privacy, accessibility and records.
- **Missing accountable decision:** assignment/relationship; source/patient/encounter access; review/confirm/reject/correct semantics; supersession; optimistic concurrency; document ownership/consent; audit/retention.
- **Required signed/source-backed evidence:** P10/P11 gate decisions, clinical validation, assignment/source-access policy, correction transaction design, threat/privacy review and tested audit trail.
- **Dependent units:** P21-C/D; P10-B/C/D; P11-E.
- **Negative/adversarial tests:** role without assignment; wrong patient/institution/source; broken provenance; low-confidence/failed evidence promotion; lower-trust overwrite; stale concurrent correction; unavailable source shown as valid.
- **Safe-off:** no queue/source access or clinical mutation; honest unavailable state and existing P7 workflow.
- **STOP:** no live clinician access, document processing or fact confirmation while applicable P10/P11 decisions remain unsigned.

### 5. P13 referral/notification visibility, purpose-specific consent and external side effects — BLOCKED

- **As-built proof:** central consent supports the `REFERRAL_SHARING` purpose; no referral/notification service, recipient, adapter or admin view exists.
- **Reason:** consent-purpose vocabulary is not a grant, and admin visibility does not authorize send/delivery or establish recipient/status truth.
- **Roles needing assignment:** referral/notification owners, consent/privacy/legal, identity/institution, recipient/integration security, patient experience and operations.
- **Missing accountable decision:** exact purpose/notice/scope; recipient evidence; minimized fields; withdrawal/in-flight behavior; adapter/channel; idempotency/retry/reconciliation; status authority and correction.
- **Required signed/source-backed evidence:** explicit active purpose-specific `REFERRAL_SHARING` grant plus all additionally applicable lawful/governance requirements, recipient agreement, payload allowlist, adapter/security review and incident runbook.
- **Dependent units:** P13-C/D/E and P21-A/B/D.
- **Negative/adversarial tests:** general-consent substitution; revoked/expired consent; recipient substitution; overbroad/raw transcript payload; duplicate send; spoofed callback; false `SENT`/`ACKNOWLEDGED`/`SCHEDULED`/`COMPLETED`; lock-screen leakage.
- **Safe-off:** no transmission; display only an authorized honest unknown/failed/unavailable state.
- **STOP:** general product consent can never authorize sharing; missing consent or additional applicable authority blocks the side effect.

### 6. Audit/event integrity, privacy, retention, export and threat model — BLOCKED

- **As-built proof:** typed events/outbox and privacy-safe logging conventions exist; audit module is only a placeholder with no store/viewer.
- **Reason:** no approved closed event schema, audience, integrity model, audit-of-audit, retention/deletion/hold, export, incident or cross-institution policy exists.
- **Roles needing assignment:** audit/data governance, privacy/legal, security, records/retention, domain event owners, institution, operations/incident and independent threat reviewer.
- **Missing accountable decision:** minimum event metadata; append-only/tamper evidence; actor/object access; search/index/export; retention/deletion/backup/legal hold; reviewer visibility; monitoring and breach response.
- **Required signed/source-backed evidence:** event catalog, data classification, threat/privacy assessment, access matrix, retention/rights decision, integrity/recovery tests and incident exercise.
- **Dependent units:** P21-A/D and every audited owning domain.
- **Negative/adversarial tests:** event omission/tamper; wrong-tenant audit read; audit-of-audit bypass; raw transcript/document/prompt/secret/token leakage; unrestricted search/export; CSV formula/injection; deletion/hold/restore conflict.
- **Safe-off:** no audit viewer or bulk export; retain only approved minimal metadata. This draft assumes no retention duration and makes no DPDP compliance claim.
- **STOP:** auditability cannot require indiscriminate sensitive content or bypass source-domain/object authorization.

### 7. Admin API/BFF/UI, accessibility and fail-closed operational states — OPEN

- **As-built proof:** admin-web is a static foundation shell. Server API conventions require typed responses, backend authorization and nonenumerating/no-store behavior for sensitive workflows.
- **Reason:** journeys, routes, contracts, copy, locales, browser-security design and backend authority are undecided; a bounded design review is possible but no runtime is authorized.
- **Roles needing assignment:** admin app/product, API/architecture, identity/security, privacy, accessibility, content/localization, source/clinical domain owners and QA.
- **Missing accountable decision:** navigation and view minimization; BFF/session/CSRF design; API contracts; source/freshness/uncertainty copy; confirmations; error/degraded states; browser storage/cache; accessibility acceptance.
- **Required signed/source-backed evidence:** reviewed journey/API/BFF design, content/locales, privacy/security assessment, accessibility plan and backend authorization dependency.
- **Dependent units:** P21-A/B/C/D and P13-E.
- **Negative/adversarial tests:** XSS/malicious links; CSRF; IDOR; stale state; false success/badge; client/flag authorization; sensitive cache/storage; missing locale; keyboard/focus/screen-reader/forced-colors; 320/390px reflow.
- **Safe-off:** disabled/read-only/inaccessible/unavailable with no misleading success; admin outage must not break P7 manual intake or generic urgent help.
- **STOP:** no screen or BFF may expose data or action until its authoritative backend, copy, identity and scope are separately approved.

### 8. Environment, credential/feature controls, incident/rollback and P22/P24 release governance — BLOCKED

- **As-built proof:** configuration-backed safe-off flags and content-free health checks exist; P22 and P24 are not complete.
- **Reason:** there is no protected-environment identity/credential topology, preview-to-production control, monitoring/SLO, recovery test, kill-switch ownership, pilot boundary or signed release decision.
- **Roles needing assignment:** platform/SRE, security, privacy, clinical safety, credential/secret owner, incident response, product/institution, release/pilot and independent quality.
- **Missing accountable decision:** environment separation; credential issuance/rotation; audited configuration; flag ownership; backup/restore/DR; incident containment; rollback; bounded pilot population/environment; residual risk and expiry.
- **Required signed/source-backed evidence:** environment/credential design, monitored runbooks, recovery/rollback and kill-switch exercises, P22 evidence, P24 pilot protocol and explicit release record.
- **Dependent units:** all P21 units, P13-E, P22 and P24.
- **Negative/adversarial tests:** preview elevation; flag bypass; stolen/stale credential; unapproved artifact/config; IdP/source outage; partial deploy; false healthy state; rollback/restore failure; admin dependency disabling P7.
- **Safe-off:** no activation; preserve unrelated P7 manual intake and generic urgent-help navigation.
- **STOP:** CI, PR review or a feature flag never constitutes production, clinical, privacy or institutional approval.

## D. Exact normative traceability and STOP crosswalk

### `FR-ADMIN-001..010` — exact canonical wording

| ID and exact wording                                                                                                                  | Existing Spec 25 | Current implementation proof                               | Missing evidence / future artifact                                                         | Responsible domain                     | Status            |
| ------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------- | ----------------- |
| `FR-ADMIN-001` — Administrative capabilities SHALL be protected by role-based authorization.                                          | §§2, 8, 9.1      | P4 deny-by-default permissions and MFA flag; no admin API. | Trusted IdP/assignment matrix and object/institution tests.                                | Identity/security; P21-A               | LIVE NOT VERIFIED |
| `FR-ADMIN-002` — Authorized users SHALL manage provider/resource records.                                                             | §§2–4, 9.1       | Provider/resource placeholders only.                       | Approved source workflow, persistence, API/UI and authorization.                           | P13; P21-A/B                           | LIVE NOT VERIFIED |
| `FR-ADMIN-003` — The admin workflow SHALL support resource verification timestamps/owners.                                            | §§3, 5, 9.1      | No resource records or verifier workflow.                  | Source/proof schema, qualified verifier and lifecycle evidence.                            | P13 source governance; P21-D mechanics | LIVE NOT VERIFIED |
| `FR-ADMIN-004` — Admins SHALL be able to mark stale/expired resources inactive.                                                       | §§3–5, 9.1       | No lifecycle state or mutation.                            | Approved states, authority, freshness clock, propagation and rollback.                     | P13; P21-A/B/D                         | LIVE NOT VERIFIED |
| `FR-ADMIN-005` — Authorized reviewers SHALL be able to manage self-care knowledge approval state.                                     | §§1, 4–5, 9.1    | Self-care placeholder; P15 unapproved.                     | Approved corpus/policy and governing reviewer workflow.                                    | P15; P21-D mechanics                   | LIVE NOT VERIFIED |
| `FR-ADMIN-006` — Admins/reviewers SHALL be able to identify active policy versions.                                                   | §§4–5, 9.1       | Synthetic P9 metadata is not real activation.              | Owning policy registries, effective proof and scoped read view.                            | P9/P14/P15; P21-B                      | LIVE NOT VERIFIED |
| `FR-ADMIN-007` — Authorized users SHALL be able to identify active predictive model versions.                                         | §§4–5, 9.1       | No approved P18 model or P19 comparator.                   | Approved registry/lifecycle evidence and scoped view.                                      | P18/P19 model governance; P21-B        | LIVE NOT VERIFIED |
| `FR-ADMIN-008` — Authorized users SHALL have access to relevant audit events.                                                         | §§4, 7, 9.1      | Outbox exists; audit module/viewer absent.                 | Approved audit schema/store/access/integrity/retention and UI.                             | Audit/data governance; P21-D           | LIVE NOT VERIFIED |
| `FR-ADMIN-009` — Authorized users MAY manage approved feature flags.                                                                  | §4, 9.1          | Configuration provider only; no management API.            | Optional approved flag-management policy, audit and rollback. `MAY` remains optional.      | Feature owner; P21-A/B/D               | LIVE NOT VERIFIED |
| `FR-ADMIN-010` — Safety-critical production policy changes SHOULD require an approval workflow rather than unrestricted direct edits. | §5, 9.1          | No live policy editor or approval workflow.                | Governing-domain maker-checker policy and denial tests. `SHOULD` is not silently upgraded. | Clinical/model/content owners; P21-D   | LIVE NOT VERIFIED |

### `FR-AUDIT-001..007` — exact canonical wording

| ID and exact wording                                                                                  | Existing Spec 25 | Current implementation proof                                                     | Missing evidence / future artifact                                                        | Responsible domain                      | Status            |
| ----------------------------------------------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | --------------------------------------- | ----------------- |
| `FR-AUDIT-001` — Safety/policy changes SHALL be auditable.                                            | §§5, 7, 9.2      | No real policy mutation or audit record.                                         | Approved domain event/audit contract and integrity tests.                                 | P9/P14/P15; P21-D                       | LIVE NOT VERIFIED |
| `FR-AUDIT-002` — Provider/resource changes SHALL be auditable.                                        | §§3, 7, 9.2      | No provider/resource mutation.                                                   | Source-version event and audit lifecycle.                                                 | P13; P21-D                              | LIVE NOT VERIFIED |
| `FR-AUDIT-003` — Consent changes SHALL be auditable.                                                  | §§6–7, 9.2       | P4 consent outbox events exist; no P13/P21 audit viewer or referral correlation. | Approved minimized access/retention/view contract.                                        | Consent; P13; P21-D                     | LIVE NOT VERIFIED |
| `FR-AUDIT-004` — Sensitive administrative actions SHALL be auditable.                                 | §7, 9.2          | No live administrative action.                                                   | Sensitive-action inventory, event contract and audit-of-audit.                            | P21-A/D; owning domains                 | LIVE NOT VERIFIED |
| `FR-AUDIT-005` — Clinician corrections to AI-extracted clinical information SHOULD be auditable.      | §§1, 5, 7, 9.2   | P5 supersession guard; no live P10 correction.                                   | Approved correction authority/transaction/provenance event. `SHOULD` remains conditional. | P10/P5; P21-C/D                         | LIVE NOT VERIFIED |
| `FR-AUDIT-006` — Model promotion/release SHALL be auditable.                                          | §§4–5, 7, 9.2    | No approved model or promotion workflow.                                         | P18/P19 lifecycle, trusted artifact and release event evidence.                           | Model governance; P21-D                 | LIVE NOT VERIFIED |
| `FR-AUDIT-007` — Auditability MUST NOT require indiscriminate storage of raw sensitive conversations. | §§6–8, 9.2       | Privacy-safe logging baseline; audit store absent.                               | Minimized closed schema and leakage/export tests.                                         | Privacy/security; audit/data governance | LIVE NOT VERIFIED |

### `AC-P21-001..008` — exact canonical wording

| ID and exact wording                                                         | Existing Spec 25 | Current proof or absence                          | Missing human evidence / future artifact                                          | Responsible domain         | Status            |
| ---------------------------------------------------------------------------- | ---------------- | ------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------- | ----------------- |
| `AC-P21-001` — Admin access is role-restricted.                              | §§2, 8, 9.3      | P4 primitive only; no admin access path.          | Production identity/MFA/assignment and object authorization E2E.                  | Identity/security; P21-A/B | LIVE NOT VERIFIED |
| `AC-P21-002` — Provider/resource verification workflow exists.               | §§3–5, 9.3       | Absent.                                           | Approved source registry, workflow, persistence, API/UI and adversarial evidence. | P13; P21-A/B/D             | LIVE NOT VERIFIED |
| `AC-P21-003` — Self-care content approval/version state can be governed.     | §§4–5, 9.3       | Absent; P15 unapproved.                           | Approved content/policy and governing workflow evidence.                          | P15; P21-D                 | LIVE NOT VERIFIED |
| `AC-P21-004` — Active policy/model versions are visible to authorized users. | §§4–5, 9.3       | No live approved policy/model registries or view. | Source-owned effective versions and scoped read/UI evidence.                      | Policy/model owners; P21-B | LIVE NOT VERIFIED |
| `AC-P21-005` — Audit viewer exists for authorized users.                     | §§4, 7, 9.3      | Absent.                                           | Audit service/store/viewer, isolation, minimization and audit-of-audit.           | P21-D                      | LIVE NOT VERIFIED |
| `AC-P21-006` — Clinical review queue exists where required.                  | §§1, 4–5, 9.3    | Absent; P10 live gates blocked.                   | Trusted assignment/source/correction workflow and clinical validation.            | P10; P21-C                 | LIVE NOT VERIFIED |
| `AC-P21-007` — Ordinary admins cannot bypass clinical-policy governance.     | §§1–2, 5, 8–9    | Design prohibition only; no live action.          | Server denial, separation-of-duty and bypass regression evidence.                 | Owning governance; P21-A/D | LIVE NOT VERIFIED |
| `AC-P21-008` — Raw transcript search is not enabled by default.              | §§6–9            | No audit/admin search exists.                     | Search/index/export design and negative leakage evidence.                         | Privacy/security; P21-D    | LIVE NOT VERIFIED |

### P13 acceptance and historical Gate 7 — separate related scope

| P13 criterion                                                                                      | Current relationship to P21                                                                                                                                                                                                         | Status                 |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `AC-P13-001` — Provider registry stores source and verification metadata.                          | P13 owns registry truth; admin may later expose only authorized moderation.                                                                                                                                                         | LIVE NOT VERIFIED      |
| `AC-P13-002` — Resource registry stores source and verification metadata.                          | Same source-authority boundary.                                                                                                                                                                                                     | LIVE NOT VERIFIED      |
| `AC-P13-003` — Stale/expired resources are identifiable.                                           | P13 owns freshness; P21 cannot invent it.                                                                                                                                                                                           | LIVE NOT VERIFIED      |
| `AC-P13-004` — Specialty/service-type routing occurs before individual-provider selection.         | Routing remains P13 clinical/product scope, not admin policy.                                                                                                                                                                       | LIVE NOT VERIFIED      |
| `AC-P13-005` — LLM-generated provider contact details are impossible through normal registry flow. | Admin must never admit generated contacts as verified truth.                                                                                                                                                                        | LIVE NOT VERIFIED      |
| `AC-P13-006` — Referral requires appropriate explicit consent before external sharing.             | Explicit active `REFERRAL_SHARING` plus all other applicable requirements; admin visibility is not send authority.                                                                                                                  | LIVE NOT VERIFIED      |
| `AC-P13-007` — Full raw transcript is not included by default.                                     | Admin/audit/referral views require minimization.                                                                                                                                                                                    | LIVE NOT VERIFIED      |
| `AC-P13-008` — Referral state machine supports required states.                                    | P13 owns state truth; no admin inference.                                                                                                                                                                                           | LIVE NOT VERIFIED      |
| `AC-P13-009` — Duplicate referral side effects are idempotently controlled.                        | P13 owns transaction/outbox/idempotency; admin cannot retry blindly.                                                                                                                                                                | LIVE NOT VERIFIED      |
| `AC-P13-010` — External referral adapter failures produce visible status/fallback.                 | Future admin UI may show only authoritative honest status.                                                                                                                                                                          | LIVE NOT VERIFIED      |
| `AC-P13-011` — Synthetic provider records are clearly marked if real verified data is unavailable. | Synthetic records remain isolated and never production truth.                                                                                                                                                                       | LIVE NOT VERIFIED      |
| Historical P13 Gate 7                                                                              | Its missing-Spec-25 artifact has been addressed by an unapproved draft. The gate itself remains BLOCKED/not approved; roles, copy, accessibility, source warnings, privacy, identity, implementation and validation remain missing. | BLOCKED / NOT APPROVED |

### Integrated and product acceptance remains upstream/unverified

| Range              | Relevance only                                                                                                                                                                                                | Status                     |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| `AC-P20-001..010`  | A future coherent journey depends on independently governed module outputs, verified registry truth, fail-safe optional dependencies and approved RAG. This P21 delta supplies none of that live evidence.    | LIVE NOT VERIFIED          |
| `AC-PROD-001..014` | Eventual patient, document, safety, mental-health, self-care, provider/referral, clinician, FHIR, research and extensibility outcomes remain owned across the product. P21 documentation cannot satisfy them. | PRODUCT-LEVEL NOT VERIFIED |

### Preserved phase and governance truth

- P4 authorization and consent remain bounded primitives; identity is not consent and general product consent is non-transitive.
- P5 provenance/corrections remain source-controlled; P7 deterministic manual text/touch intake is functional and independent.
- P8-C/P9-C patient-facing Stage 3 remain **BLOCKED**.
- P10/P11 live use remain `0/9` approved; P11 remains five OPEN/four BLOCKED.
- P12–P21 runtime remains **NOT STARTED** where applicable. P15 clinical/source STOP conditions remain.
- P16/P17 exchange remains unauthorized; P18 has no approved baseline and P19 has no comparator.
- P20 runtime remains NOT STARTED and its live acceptance remains unverified. P22 remains NOT COMPLETE.

Any fresh contradiction with these source records is a STOP requiring accountable reconciliation, not permission to alter the roadmap here.

## E. Review-ready decision template, owner/risk register and explicit next action

### Unsigned bounded decision record

No field below is approved by this phase. A future record is valid only through an authenticated, authorized, auditable process accepted by accountable owners.

| Field                                                              | Pending record |
| ------------------------------------------------------------------ | -------------- |
| Decision ID                                                        | **PENDING**    |
| Affected phase/unit and governing domain                           | **PENDING**    |
| Exact use/action/object and excluded operations                    | **PENDING**    |
| Institution, population, recipient, purpose and environment        | **PENDING**    |
| Official/source version, immutable evidence/hash and provenance    | **PENDING**    |
| Data classification and exact consent/lawful/governance authority  | **PENDING**    |
| Reviewer assignment, qualification, independence and segregation   | **PENDING**    |
| Approved resource/clinical/content/model evidence, when applicable | **PENDING**    |
| Trusted identity/MFA/institution/object/source proof               | **PENDING**    |
| Positive, negative, adversarial, accessibility and recovery tests  | **PENDING**    |
| Risk acceptance and residual risk owner                            | **PENDING**    |
| Effective/expiry dates and reevaluation/recall triggers            | **PENDING**    |
| Rollback, incident, withdrawal and reconciliation actions          | **PENDING**    |
| Named reviewer identities, signatures and dates                    | **PENDING**    |

### Role and risk register

| Decision area                           | Accountable roles                                                    | Status and principal risk                                              |
| --------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Identity/MFA/scope                      | Identity/security; institution; privacy; operations                  | BLOCKED — privilege or cross-institution/object access.                |
| Provider/resource source truth          | Source/provider/resource governance; privacy/legal; clinical safety  | BLOCKED — false, stale, malicious or harmful resource.                 |
| Clinical/policy/content/model authority | Owning clinical/content/model governance; institution                | BLOCKED — ordinary admin creates clinical authority or self-approves.  |
| Clinician/document review               | Clinical operations; provenance; identity; document/privacy/security | BLOCKED — unauthorized review or fact promotion.                       |
| Referral/notification/consent           | Referral/notification; consent/privacy/legal; recipient/integration  | BLOCKED — unauthorized disclosure or fabricated delivery state.        |
| Audit/retention/export                  | Audit/data governance; privacy/legal; security; records; incident    | BLOCKED — sensitive leakage, tamper, over-retention or rights failure. |
| UI/API/accessibility                    | App/API; security/privacy; accessibility/content; domain owners      | OPEN — misleading/inaccessible control without authoritative backend.  |
| Environment/release                     | SRE/security; clinical safety; institution; P22/P24 release          | BLOCKED — unsafe activation, credential misuse or failed rollback.     |

### Human action checklist

1. Assign named, qualified decision-makers outside Codex for each applicable domain.
2. Verify current official clinical, source, privacy/legal, security, institutional and model evidence.
3. Review and sign narrowly bounded decisions with scope, version, effective/expiry dates, negative tests, incident and rollback evidence.
4. Record unresolved conflicts and keep affected operations safe-off.
5. Request a **new**, separately bounded prompt only after prerequisite evidence is current and independently reviewed.

A possible future **nonclinical synthetic P21-A authorization-contract preflight** is a proposal only. It requires explicit owner-reviewed scope and another prompt; it cannot create runtime routes, persistence, real credentials/role grants, live patient/source access, or acceptance evidence. P21-B/C/D, P13-E, pilot and release remain STOP.

> **FINAL STOP:** this documentation delta does not replace Spec 25 and grants no actor, administrator, clinician, source, policy, model, patient-data, referral, audit, pilot, production or system authority. P21-A/B/C/D are NOT STARTED; accountable humans must make and sign all real decisions before any new specifically approved engineering phase.
