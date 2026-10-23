# SwasthyaSetu AI

## 25 — Admin Portal Specification

> **DRAFT — PRE-P13/P21 GOVERNANCE DESIGN ONLY; NO LIVE ADMIN, CLINICAL, PRIVACY, SECURITY, OR PRODUCTION AUTHORIZATION.**

**Document ID:** `SSAI-ADMIN-025-DRAFT`
**Evidence baseline:** `main @ af32d98061b4605d405e954de5cde3d380974d8e`
**Evidence date:** `2026-10-23`
**Review state:** **UNAPPROVED DRAFT — ACCOUNTABLE OWNERS PENDING**
**Owners:** product/institution, identity/security, privacy/legal, source governance, clinical safety,
accessibility/content, operations, audit/data governance, and application owners — **assignment and
sign-off pending**

This document is a governance-readiness design. It is subordinate to approved clinical and privacy
policy, accepted ADRs, the [Product Requirements](01_PRODUCT_REQUIREMENTS.md),
[System Architecture](02_SYSTEM_ARCHITECTURE.md), [API Contracts](06_API_CONTRACTS.md),
[Provider Routing Policy](11_PROVIDER_ROUTING_POLICY.md),
[Clinical Provenance Specification](12_CLINICAL_PROVENANCE_SPEC.md),
[Privacy and Consent Specification](26_PRIVACY_CONSENT_SPEC.md), and accountable human decisions.
Green CI, a role constant, or a rendered panel is not an approval.

# 1. Scope, evidence labels, and phase ownership

## 1.1 Evidence labels

- **AS-BUILT TECHNICAL PRIMITIVE** means code exists at the evidence baseline, with no claim beyond
  its tested scope.
- **FUTURE / NOT IMPLEMENTED** means a proposed requirement requiring a separate phase prompt.
- **HUMAN DECISION PENDING** means engineering cannot choose the authority, policy, source, copy,
  retention, risk acceptance, or release decision.
- **LIVE NOT VERIFIED** means documentary design is not acceptance evidence.

## 1.2 As-built inventory

| Area | Repository evidence | Honest boundary |
| --- | --- | --- |
| Admin web | `apps/admin-web/app/page.tsx` renders an accessible “Foundation ready” empty state. | No navigation, identity flow, admin operation, moderation, viewer, or live data. |
| Identity | P4 persists actors/roles and exposes provider-neutral authentication/current-actor/authorization capabilities. | Production authentication provider is unconfigured; there is no actor-management API or verified role assignment. |
| Authorization | Server-side `AuthorizationService` denies unauthenticated actors, maps fixed P4 roles to a small permission set, and requires `mfa_verified` for administrative roles. | It does not prove a production identity, MFA ceremony, institutional employment, assignment, source authority, or human approval. |
| Consent | Central purpose-specific consent includes `REFERRAL_SHARING`. | No P13 referral-sharing flow exists; general product consent cannot authorize sharing. |
| Events/outbox | Versioned events and a PostgreSQL transactional outbox foundation exist. | No admin, provider, referral, notification, or audit event contract is implemented. |
| Feature flags | Safe-off configuration-backed flags exist. | No admin management API/table/workflow; flags never replace authorization or policy. |
| Provider/resource/referral/audit | Canonical documents contain future concepts and placeholder paths. | No registered module, record, API, persistence, verified source, referral side effect, audit viewer, or notification runtime. |
| Clinical review | P10 synthetic summary contracts exist and clinician web remains a future governed surface. | No live clinician access, assignment authority, confirmation workflow, or review queue. |

Alembic head is `p7a_0007`. The future tables and endpoints in canonical specifications are designs,
not present schema or API evidence.

## 1.3 Future ownership boundaries

| Future unit | Conditional ownership | Explicit non-ownership |
| --- | --- | --- |
| P13-E | Patient source/freshness warnings and referral status; provider/resource moderation UI only after its source, identity, consent, copy, and accessibility decisions. | Does not establish provider truth, clinical routing policy, referral delivery truth, or P21 governance. |
| P21-A | Admin backend contracts, server authorization, scoped application services, and audited operation boundaries. | Does not grant roles, approve sources/content/models/policy, or own clinical facts. |
| P21-B | Admin web/BFF, accessible states, minimized views, and safe confirmations. | UI state and hidden controls are never authorization or success evidence. |
| P21-C | Governed clinical review queues after P10 authority, assignment, provenance, and correction approvals. | Ordinary administration cannot confirm clinical facts or summaries. |
| P21-D | Audit viewer and maker-checker mechanics after event, retention, access, and separation-of-duty decisions. | Audit display is not the clinical record and cannot rewrite history. |

P15 owns governed self-care content; P10 owns clinician summary/review authority; P18/P19 own model
evaluation and promotion evidence; P9/P14/P15 own their clinical policies; P13 owns providers,
resources, referrals, and notification integration. Feature management owns approved flags. Admin
visibility does not transfer ownership of patient, clinical, consent, source, policy, or model data.

# 2. Actors, trust, and proposed access matrix

Authentication proves only a trusted principal mapping. Authorization must additionally evaluate
active actor status, server-derived role/permission, MFA where required, institution, object, source,
assignment, purpose, consent, and governing-domain approval. Client headers, form fields, URLs, and
UI state cannot assert any of these.

The names below combine current P4 constants and future reviewer concepts. Only patient, clinician,
resource-admin, clinical-reviewer, system-admin, researcher, pseudonymous-user, and service-account
concepts have partial technical representation; every assignment and expanded permission remains
unapproved.

| Actor concept | Proposed permitted scope | Always forbidden without separate authority |
| --- | --- | --- |
| Patient | View own eligible public/provider/referral information and exercise applicable consent/correction rights. | Admin operations, another subject, source verification, or asserting external status. |
| Resource admin | Propose/correct source-backed provider/resource records within assigned institution/source after trusted MFA. | Clinical confirmation, policy/model promotion, patient record reads, self-approval, or referral impersonation. |
| System admin | Operational configuration and scoped audit access explicitly granted by policy after trusted MFA. | Blanket patient/clinical access, consent override, clinical/source truth, or break-glass by role alone. |
| Clinical reviewer | Review assigned clinical material under P10/P21-C policy after trusted MFA. | Unassigned subjects, source moderation by default, model/policy bypass, or silent overwrite. |
| Clinician | Assigned-patient/encounter work under P10 authority. | Directory verification, unrestricted search/export, or administrative promotion. |
| Source verifier/moderator | Verify/propose/suspend only assigned source fields with evidence. | Clinical suitability, referral outcome, or approval outside source scope. |
| Data-governance reviewer | Review privacy, retention, export, correction, and audit controls. | Direct clinical edits or policy activation. |
| Institutional owner | Decide institutional scope, delegated authority, and accountable release acceptance. | Cross-institution access or technical bypass. |
| Operations | View minimized health/state and execute approved runbooks. | Patient narrative, clinical documents, credentials, or approval decisions by default. |
| Service actor | Perform one narrowly scoped machine operation with rotated credentials and explicit audience. | Human-role impersonation, interactive export, or self-expansion of scope. |

## 2.1 Action rules

`view`, `propose`, `verify`, `approve`, `publish`, `suspend`, `revoke`, `correct`, `audit`, `restore`,
and `export` must be distinct server permissions where used. Each operation must bind object,
institution, source, purpose, and version as applicable. High-impact approve/publish/restore/export
operations require fresh authorization and, where approved, maker-checker separation. `revoke` and
`suspend` must fail safely and propagate without implying deletion. `restore` must never bypass
re-verification. Export is denied by default.

# 3. Source-backed provider and resource administration

All of this section is **FUTURE / NOT IMPLEMENTED** and must align with the unapproved taxonomies in
the [Provider Routing Policy](11_PROVIDER_ROUTING_POLICY.md).

1. Source/rights intake must record source identity, owner, permitted use, acquisition method,
   evidence reference, field coverage, jurisdiction, and review/expiry dates. No scraper/import
   vendor or licensing basis is selected here.
2. Field-level provenance must bind each displayed name, specialty/service, affiliation, location,
   hours, language, teleconsultation claim, URL, and contact to evidence and a verifier. Record-level
   “verified” must not hide unsupported fields.
3. Lifecycle must distinguish proposed, under review, verified, stale, expired, suspended, revoked,
   disputed, rejected, superseded, and corrected only after humans approve vocabulary/transitions.
   Unknown is never silently treated as verified.
4. Amendments preserve prior versions and reasons. Corrections and source revocations must
   invalidate public display/downstream references or show an approved warning until reconciled.
5. Critical contacts require independently approved dual control and re-verification. A source
   outage or expired evidence fails closed for verified display; it never falls back to generated
   contact data.
6. Synthetic records must be unmistakably labeled, isolated from protected environments, and never
   presented as verified real providers.

Malicious URLs, redirects, source impersonation, Unicode/control spoofing, source poisoning, and
stale/revoked evidence must be rejected or safely displayed as text. No provider, clinic, helpline,
specialty, verification proof, or contact is created by this draft.

# 4. Proposed governance surfaces and honest states

Every route and panel below is **FUTURE / NOT IMPLEMENTED**:

| Surface | Proposed information/actions | Mandatory unavailable/degraded behavior |
| --- | --- | --- |
| Providers/resources | Source fields, provenance, freshness, disputes, propose/verify/suspend/correct. | Read-only or unavailable when IdP, scope, source, evidence, or authority is absent; no verified badge from stale/unknown proof. |
| Referrals | Minimized status/evidence and reconciliation queue. | Never fabricate `SENT`, `ACKNOWLEDGED`, `SCHEDULED`, or `COMPLETED`; show unknown/failed honestly. |
| Policy versions | Identifier, version, owner, approval/activation metadata. | No ordinary-admin edit or activation; absent governing approval means read-only/unavailable. |
| Model versions | Evaluation/approval/release metadata owned by P18/P19. | Registry visibility is not approval; no promotion without owning workflow. |
| Self-care content | Version/source/review status owned by P15. | No publication or clinical copy without approved knowledge and reviewers. |
| Feature flags | Approved flag metadata, environment, owner, review date. | Safe-off; flags cannot bypass authorization, consent, provenance, policy, human approval, or release. |
| Audit | Authorized filtered event metadata. | No raw narrative/transcript/document/token/secret; no generic bulk export. |
| Operational status | Content-free dependency health and incidents. | No patient data or false healthy/success state. |
| Clinical review | Assigned queue and provenance under P10/P21-C. | Disabled/unavailable until real identity, assignment, authority, source access, and P10 gates exist. |

No button may claim success before the authoritative service commits and returns evidence. Stale
responses, timeouts, ambiguous external effects, and concurrent change must render an honest pending,
conflict, unavailable, or reconciliation state.

# 5. Review and maker-checker boundaries

A proposed versioned decision may use draft/proposed, under-review, approved, rejected, superseded,
suspended, and rolled-back concepts, but final vocabulary and authority are **HUMAN DECISIONS
PENDING**. Every decision record must preserve object/version, author, independent reviewer(s),
institution/source scope, permission/MFA evidence reference, reason code, evidence, UTC time,
effective period, supersession link, and re-review trigger.

The maker cannot check the same safety-critical change. Concurrent approval/revocation must use an
approved optimistic-lock or transaction design. Safety-critical content, crisis contacts, clinical
corrections, policy activation, and model promotion remain with their owning governance domains;
ordinary admins cannot perform them. Pull-request review and CI are technical evidence only.

# 6. Referral and notification operational views

Referral status is authoritative only from the owning service or validated external evidence. The
admin portal must not send a referral, impersonate a patient/recipient, substitute a provider, or
infer delivery. Any external sharing requires explicit, active, purpose-specific
`REFERRAL_SHARING` consent plus every additionally applicable legal/governance requirement. General
product consent cannot authorize sharing. Consent must be rechecked immediately before the side
effect and bound to recipient, purpose, and minimized field set under the approved future design.

Views expose only minimum authorized status and non-sensitive notification evidence. Raw transcript
search/export is off by default. URLs, notifications, logs, previews, and lock screens must exclude
patient narrative, clinical documents, contact secrets, tokens, and unnecessary health details.

# 7. Audit, privacy, observability, and retention

Future audit coverage must include source/resource changes, consent, privileged admin actions,
policy/model promotion, clinician review/correction, referral status, failed authentication,
authorization denial, bulk/export attempt, and source suspension/revocation. Proposed event fields
are closed identifiers and codes: event ID/type/version, actor/service ID, target type/opaque ID,
institution/source scope, action/outcome/reason, request/correlation ID, object version, and UTC time.

Audit history is separate from the clinical record and operational telemetry. Generic logs,
analytics, traces, errors, and audit events must not contain raw patient narrative/transcripts,
documents, credentials, bearer tokens, consent bodies, signed URLs, or personal data. Access to audit
events is itself scoped and auditable; tamper evidence and append-only behavior need an approved
architecture.

Retention periods, deletion/subject-right workflows, legal holds, backup propagation, export rights,
break-glass authority, reviewer-identity visibility, cross-institution isolation, and incident
response are **HUMAN DECISIONS PENDING**. This draft selects no values and makes no legal claim.

# 8. Security, privacy, accessibility, and negative evidence

Future BFF/API responses must use strict `no-store`, bounded requests, safe error mapping, CSRF/XSS
protections appropriate to the selected session design, and backend-owned object authorization. No
clinical content is persisted in browser storage. The UI must support keyboard use, visible focus,
screen-reader names/status, 320/390px reflow, non-color-only meaning, safe confirmation/dialog focus,
and human-reviewed locale/source-warning copy. P7 manual text/touch intake and generic urgent-help
navigation remain independent of admin, providers, and optional AI.

Required future negative/adversarial tests include:

- unauthenticated, non-MFA, disabled, stale, unknown-role, forged-role/header, and wrong-permission;
- guessed IDs, wrong subject/institution/object/source/assignment, enumeration and timing leakage;
- privilege escalation, confused deputy, service-account misuse, maker-checker self-approval;
- forged/missing/future/expired/revoked verification, source poisoning and stale version approval;
- malicious URL/redirect, XSS, Unicode/control spoof, CSV formula, filter/SQL injection and SSRF;
- concurrent propose/approve/suspend/revoke/restore, replay, duplicate action and rollback failure;
- unauthorized search/bulk export, raw narrative/document/token leakage and audit tamper;
- feature-flag, client-state, UI hiding, CI-status and PR-approval bypass attempts;
- IdP/source outage, dependency timeout, ambiguous external effect and rollback/reconciliation;
- keyboard/focus/screen-reader, forced-colors, 320/390px reflow, missing locale and unsafe copy;
- absent source/approval must render disabled/read-only/unavailable without false success.

# 9. Requirement and acceptance traceability

Every status is **LIVE NOT VERIFIED**. “Evidence” below is documentary or adjacent technical context,
not implementation acceptance.

## 9.1 `FR-ADMIN-001..010`

| Requirement (exact canonical wording) | Draft mapping / as-built evidence | Human decision required | Status |
| --- | --- | --- | --- |
| `FR-ADMIN-001` — Administrative capabilities SHALL be protected by role-based authorization. | §§2,8; P4 deny-by-default permission/MFA primitive only. | Real IdP, assignment, scopes, roles, MFA/recovery. | LIVE NOT VERIFIED |
| `FR-ADMIN-002` — Authorized users SHALL manage provider/resource records. | §§2–4; no records or service. | Ownership, sources, fields, permissions, workflow. | LIVE NOT VERIFIED |
| `FR-ADMIN-003` — The admin workflow SHALL support resource verification timestamps/owners. | §§3,5; design only. | Verifier authority, evidence and cadence. | LIVE NOT VERIFIED |
| `FR-ADMIN-004` — Admins SHALL be able to mark stale/expired resources inactive. | §§3–5; design only. | State vocabulary, authority, propagation and rollback. | LIVE NOT VERIFIED |
| `FR-ADMIN-005` — Authorized reviewers SHALL be able to manage self-care knowledge approval state. | §§1,4–5; owned by P15. | Clinical/content authority and approved knowledge. | LIVE NOT VERIFIED |
| `FR-ADMIN-006` — Admins/reviewers SHALL be able to identify active policy versions. | §§4–5; P9 metadata is not activation approval. | Policy owner, activation and rollback evidence. | LIVE NOT VERIFIED |
| `FR-ADMIN-007` — Authorized users SHALL be able to identify active predictive model versions. | §§4–5; future P18/P19 ownership. | Model governance, evaluation, promotion and release. | LIVE NOT VERIFIED |
| `FR-ADMIN-008` — Authorized users SHALL have access to relevant audit events. | §§4,7; no audit viewer/module. | Audit schema, scopes, retention and tamper controls. | LIVE NOT VERIFIED |
| `FR-ADMIN-009` — Authorized users MAY manage approved feature flags. | §4; safe-off configuration primitive only. | Flag ownership, allowed mutations, review and rollback. | LIVE NOT VERIFIED |
| `FR-ADMIN-010` — Safety-critical production policy changes SHOULD require an approval workflow rather than unrestricted direct edits. | §5 mandates future separation. | Maker-checker authority and governing-domain workflows. | LIVE NOT VERIFIED |

## 9.2 `FR-AUDIT-001..007`

| Requirement (exact canonical wording) | Draft mapping / missing evidence | Human decision required | Status |
| --- | --- | --- | --- |
| `FR-AUDIT-001` — Safety/policy changes SHALL be auditable. | §§5,7; admin audit absent. | Event contract, access, integrity, retention. | LIVE NOT VERIFIED |
| `FR-AUDIT-002` — Provider/resource changes SHALL be auditable. | §§3,7; P13 not started. | Source/version/change event design. | LIVE NOT VERIFIED |
| `FR-AUDIT-003` — Consent changes SHALL be auditable. | §§6–7; central consent events exist, P13 evidence absent. | Referral correlation, access and retention. | LIVE NOT VERIFIED FOR P13/P21 |
| `FR-AUDIT-004` — Sensitive administrative actions SHALL be auditable. | §7; no live actions or audit viewer. | Sensitive-action inventory and event policy. | LIVE NOT VERIFIED |
| `FR-AUDIT-005` — Clinician corrections to AI-extracted clinical information SHOULD be auditable. | §§1,5,7; P10 live workflow blocked. | Clinical authority, correction and provenance policy. | LIVE NOT VERIFIED |
| `FR-AUDIT-006` — Model promotion/release SHALL be auditable. | §§4–5,7; future P18/P19. | Model governance and release evidence. | LIVE NOT VERIFIED |
| `FR-AUDIT-007` — Auditability MUST NOT require indiscriminate storage of raw sensitive conversations. | §§6–8 prohibit raw content. | Approved minimized schema and leakage tests. | LIVE NOT VERIFIED |

## 9.3 `AC-P21-001..008`

| Criterion | Required future evidence | Status |
| --- | --- | --- |
| `AC-P21-001` — Admin access is role-restricted. | Real IdP/MFA/assignment plus server/object/institution authorization tests. | LIVE NOT VERIFIED |
| `AC-P21-002` — Provider/resource verification workflow exists. | Approved source workflow, persistence, APIs, UI and adversarial evidence. | LIVE NOT VERIFIED |
| `AC-P21-003` — Self-care content approval/version state can be governed. | P15 approval authority and P21 workflow evidence. | LIVE NOT VERIFIED |
| `AC-P21-004` — Active policy/model versions are visible to authorized users. | Owning registries plus scoped read/API/UI evidence. | LIVE NOT VERIFIED |
| `AC-P21-005` — Audit viewer exists for authorized users. | Audit service/viewer, isolation, minimization and access logging. | LIVE NOT VERIFIED |
| `AC-P21-006` — Clinical review queue exists where required. | P10/P21-C authority, assignment and correction workflow. | LIVE NOT VERIFIED |
| `AC-P21-007` — Ordinary admins cannot bypass clinical-policy governance. | Server denial, separation-of-duty and bypass regression tests. | LIVE NOT VERIFIED |
| `AC-P21-008` — Raw transcript search is not enabled by default. | Search/index/export negative evidence and telemetry scans. | LIVE NOT VERIFIED |

## 9.4 Applicable `AC-P13-001..011` and readiness Gate 7

| Criterion | Draft mapping / required evidence | Status |
| --- | --- | --- |
| `AC-P13-001` — Provider registry stores source and verification metadata. | §3; source/provenance registry persistence and tests required. | LIVE NOT VERIFIED |
| `AC-P13-002` — Resource registry stores source and verification metadata. | §3; resource source/provenance persistence and tests required. | LIVE NOT VERIFIED |
| `AC-P13-003` — Stale/expired resources are identifiable. | §§3–4; UTC freshness/revocation query and UI tests required. | LIVE NOT VERIFIED |
| `AC-P13-004` — Specialty/service-type routing occurs before individual-provider selection. | P13 owns specialty-first routing; this admin draft grants no taxonomy. | LIVE NOT VERIFIED |
| `AC-P13-005` — LLM-generated provider contact details are impossible through normal registry flow. | §§3,8; registry/import boundary must make generated contacts impossible. | LIVE NOT VERIFIED |
| `AC-P13-006` — Referral requires appropriate explicit consent before external sharing. | §6; explicit active purpose-specific consent and server recheck required. | LIVE NOT VERIFIED |
| `AC-P13-007` — Full raw transcript is not included by default. | §§6–7; minimized payload/capture tests required. | LIVE NOT VERIFIED |
| `AC-P13-008` — Referral state machine supports required states. | §6; owning referral aggregate and approved state evidence required. | LIVE NOT VERIFIED |
| `AC-P13-009` — Duplicate referral side effects are idempotently controlled. | §§5–6; transaction/outbox/idempotency/race tests required. | LIVE NOT VERIFIED |
| `AC-P13-010` — External referral adapter failures produce visible status/fallback. | §§4,6,8; visible failure/ambiguity/fallback tests required. | LIVE NOT VERIFIED |
| `AC-P13-011` — Synthetic provider records are clearly marked if real verified data is unavailable. | §§3–4; synthetic isolation and unmistakable labeling required. | LIVE NOT VERIFIED |
| Pre-P13 Gate 7 | This draft closes only the missing-document artifact. Roles, copy, accessibility, source-warning, privacy, identity, implementation and review decisions remain blocked. | BLOCKED / NOT APPROVED |

# 10. Conditional future plan, decisions, and STOP triggers

Separately scoped work may later produce documentation or nonmedical, synthetic UI-state contracts,
but only after the owning prompt and review. It must not register runtime modules, create signed
decisions, add migrations/APIs, or imply live acceptance.

Accountable human roles must record decisions for:

1. production identity provider, actor lifecycle, role/permission assignment, MFA/recovery,
   institutional/object/source/assignment scopes, service identities and separation of duties;
2. provider/resource source rights, verification evidence, field model, freshness/expiry,
   corrections/disputes, suspension/revocation, critical-contact dual control and public eligibility;
3. clinical/safety/content/model/policy owners and maker-checker authority;
4. referral visibility, recipient/status evidence, explicit `REFERRAL_SHARING` consent,
   minimization, external processors, notification channels, reconciliation and incidents;
5. audit schema/integrity/access, privacy, retention/deletion/legal hold, export, break-glass,
   cross-institution isolation, monitoring and incident response;
6. admin API/BFF/UI architecture, approved copy/locales, accessibility evidence, source warnings,
   browser privacy, degraded behavior and false-success prevention; and
7. operations, safe-off flags, rollback, manual fallback, pilot scope, residual risk, re-review and
   production release.

**STOP** if trusted production identity or MFA is absent; authorization scope is ambiguous; a source,
rights, verification, approval, consent, retention, incident, clinical, privacy, security,
accessibility, pilot, or release decision is missing; an operation could cross subjects/institutions;
an ordinary admin could create clinical/source authority; status truth is unavailable; or a UI could
claim success without authoritative evidence. P13 and P21 remain not started until separately
authorized. This specification does not activate any admin operation.
