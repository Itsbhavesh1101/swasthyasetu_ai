# SwasthyaSetu AI

## 24 — Clinician Dashboard Specification

**Document ID:** `SSAI-SPEC-024`
**Status:** Canonical Pre-P10 Prerequisite — TECHNICAL SPECIFICATION, NOT CLINICAL APPROVAL
**Version:** `1.0.0`
**Scope:** Full P10 clinician queue, encounter overview, summary, and review design

---

# 1. Audience, authority, and current baseline

The audience is an authenticated, active clinician who is independently authorized for the exact
encounter and institution. Identity must come from a trusted provider-backed `ActorContext`, never a
pseudonymous patient session token, client role string, URL identifier, cookie invented by the UI,
or hidden navigation. `RoleCode.CLINICIAN` and `ENCOUNTER_READ_ASSIGNED` are necessary but do not
prove assignment. Every object read and mutation repeats permission, assignment, institution,
patient/encounter and purpose checks server-side. Role/assignment revocation takes effect on the next
request; no role receives implicit administrator access. MFA is required whenever the approved
institutional policy or privileged operation requires it.

Actual baseline:

- `apps/clinician-web/` is a buildable accessible empty-state foundation only;
- `identity` has provider-neutral contracts and role permissions, but no configured production IdP,
  clinician directory, organization membership or encounter assignment source;
- `encounters` has optional `institution_id`, but no clinician assignment relation;
- P5 patient/fact/provenance reads and P7 deterministic intake exist, while the clinician queue,
  overview, fact-review routes and summaries do not;
- `clinical_summaries` in `docs/05_DATABASE_SCHEMA.md` is conceptual; Alembic has no such table.

Therefore clinician IdP/directory selection, identity assurance, institution/tenant policy,
assignment/transfer source, lawful clinician access to pseudonymous P7 encounters, consent/purpose,
production hosting and UI data-sharing approval are **OPEN — IDENTITY/SECURITY/PRIVACY DECISION
REQUIRED**. General product consent is non-transitive. No fake/test clinician may be a production
default.

# 2. Screen and state inventory

## 2.1 Authorized encounter queue

The queue contains only encounters returned by a server-side authorization projection for the actor.
It supports bounded cursor pagination, allowlisted filters, stable sort, a freshness timestamp and
minimized row metadata. “Available” must be defined by an approved assignment policy; it cannot mean
all encounters or all patients. A row click repeats object authorization, so stale queue membership
does not grant access. An unrestricted patient listing is prohibited.

Required states: loading, authorized empty, results, stale/refreshing, forbidden, authentication
expired, dependency unavailable, and degraded read-only. Errors and counts must not reveal other
patients or institutions. No clinical data belongs in URLs, analytics or browser storage.

## 2.2 Encounter overview

An authorized overview may compose minimum-necessary public read capabilities for current encounter,
patient-scoped facts, P7 structured intake, chief complaint/HPI/history, and timeline. P7 content is
labeled **patient reported / structured intake / non-diagnostic**. Every fact shows a human-readable
source category, verification state and freshness without relying on color alone.

Medications and allergies are prominent, separate sections with explicit state semantics:

- `RECORDED`: at least one authorized record, each showing status and verification;
- `UNVERIFIED`: candidate/patient-reported entries exist but none are clinician-confirmed;
- `NOT_RECORDED`: the governed source has no recorded entry and no claim of clinical absence;
- `UNKNOWN`: completeness or authorized source coverage cannot be established;
- `UNAVAILABLE`: dependency/source/access failure prevents a trustworthy view.

The UI must never translate missing rows into “none,” “no known allergies,” or another reassuring
clinical assertion. Conflicts remain visible as conflicts; rejected/superseded history is available
only through an authorized provenance view.

## 2.3 Structured clinical summary

The summary sections follow `FR-SUM-002`: chief complaint; HPI; past medical/surgical history;
medications/allergies; family history; personal history; review of systems; and prior investigations.
The conceptual `ClinicalSummary` contains summary ID, encounter ID, version, status, sections,
`generated_from_fact_ids`, creator/time and optional confirmer/time. Canonical statuses are `DRAFT`,
`CLINICIAN_EDITED`, `CONFIRMED`, `REJECTED`, and `SUPERSEDED`.

P10-A begins with a deterministic, source-backed draft contract. It may organize only supplied
structured items and must abstain on missing data; it cannot create a diagnosis or fact. Optional AI
composition is separately gated by P8-C clinical/privacy/identity/egress approval and is not part of
the safe baseline. P8 candidates remain unconfirmed. P9 synthetic safety tokens are forbidden from
the dashboard. A draft is visibly labeled, source-linked and never presented as signed clinical
documentation.

Clinician edits create a new version. Text that asserts a new clinical fact must enter the governed
fact/provenance workflow rather than silently becoming truth. Source drift marks affected content
stale and requires review again as specified in `12_CLINICAL_PROVENANCE_SPEC.md`.

## 2.4 Review controls and safe unavailable behavior

Confirm, correct, reject, summary edit/confirm/revise are future P10-D operations. Each requires
fresh actor/assignment/purpose checks, expected version, actor-scoped idempotency, atomic persistence,
safe conflict recovery, provenance and approved audit/outbox handling. If trusted identity,
assignment, consent/lawful basis, transaction support or source authority is missing, controls are
absent or explicitly `READ_ONLY`; the client never shows a fake success.

## 2.5 Compile-time extension slots

The layout reserves typed read-only slots for `PatientHeader`, `CriticalAlerts`,
`MedicationAllergyPanel`, `Timeline`, `EncounterSummary`, `DecisionSupport`, `Documents`, `Referrals`
and `FeaturePanels`. The owning module supplies a permissioned minimized projection through an
explicit compile-time registration. No runtime plugin discovery or untrusted code loading is allowed.
Unavailable/unimplemented owners remain hidden or honestly disabled: P9 synthetic fixtures cannot
create alerts, future models cannot create risk panels, P11 cannot create document viewers, and P13
cannot create referrals before their governed phases.

# 3. API/BFF architecture — design only

Future contracts align with `docs/06_API_CONTRACTS.md` §§15, 16 and 26:

- `GET /api/v1/clinician/encounters` — actor-authorized queue;
- `GET /api/v1/clinician/patients/{patient_id}/overview` — composite authorized read model;
- fact confirm/reject/correct — P10-D mutations owned through patient/provenance capabilities;
- encounter summary create/latest and summary confirm/revise — summaries-owned lifecycle.

These conceptual examples are not active routes or consent. Backend application services compose
public capability protocols; API/BFF/UI code must not import another module's ORM record or mutate
patient facts. Requests and responses are strict, versioned and bounded. Lists use opaque cursor and
maximum limit. Responses minimize fields and set `Cache-Control: no-store`; CSP/referrer policy and
same-origin BFF rules protect credentials. Bearers/IdP credentials remain server-only and are never
placed in JavaScript-readable storage, URLs, logs, traces or analytics.

Every read/write declares authentication, permission, institution/assignment rule, object ownership,
purpose/consent or lawful basis, allowed encounter states and source-detail scope. Cross-object IDOR
tests must return the safe common error envelope without existence leakage. Live API/BFF activation
requires the applicable readiness gates in `implementation/P10_READINESS_GATE_REVIEW.md` to close.

# 4. Persistence lifecycle — design only

The conceptual `clinical_summaries` fields in `docs/05_DATABASE_SCHEMA.md` are a starting design, not
migration authority. Before implementation, data governance must approve section schema/version,
source-reference representation, creator/editor/confirmer attribution, optimistic version field,
status transitions, retention/deletion/legal-hold behavior, audit/outbox payload minimization and
rollback. Summary version, source snapshot and authorized review evidence commit atomically. No
retention duration is invented here.

# 5. Accessibility and safe UX

The clinician UI requires one `h1`, named landmarks, semantic table headers/captions, keyboard-only
operation and visible focus. Verification and freshness use text/icon labels as well as color.
Controls have accessible names and error association; modal focus is contained/restored. Layouts
reflow at 320/390 CSS pixels, applicable targets are at least 44×44 CSS pixels, forced-colors and
reduced-motion are honored, and zoom does not hide actions. Loading, offline, forbidden, expired,
withdrawn/unavailable and draft states are explicit. Accessibility does not weaken privacy: screen
reader text also remains minimum-necessary. The existing foundation remains until an authorized
backend flow exists.

# 6. P10 phase ownership

| Phase | Owner/scope                                                                              | Prerequisites and safe boundary                                                                                                                                                                                                |
| ----- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| P10-A | `summaries`: domain/backend foundation, deterministic source-backed draft contract/tests | Safe next subset after independent spec review: pure types, transition rules, deterministic projection and synthetic/non-PHI unit tests. No route, clinician runtime, migration or AI activation unless separately authorized. |
| P10-B | Clinician application/read model/API composition                                         | **Blocked** until trusted role binding, actor lifecycle, assignment/institution source and privacy/consent/lawful-sharing decisions are implemented and approved.                                                              |
| P10-C | `clinician-web` wired to P10-B                                                           | **Blocked for live sensitive data** until P10-B and UI/security/privacy review pass. Shell work only when separately scoped.                                                                                                   |
| P10-D | Patient/provenance/summaries integration for confirm/correct/reject                      | **Blocked** until authorized reviewers, lifecycle/concurrency, persistence, audit/outbox and retention decisions have real PostgreSQL/API evidence.                                                                            |

# 7. Requirements and acceptance mapping

All statuses are `NOT YET IMPLEMENTED`; documentation is not acceptance evidence.

| ID                          | Owner / design                                  | Prerequisite                                          | Required evidence                                                      |
| --------------------------- | ----------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------- |
| `FR-CLIN-001`, `AC-P10-001` | P10-B authorized queue                          | Trusted actor + assignment/institution policy         | Authn/authz, IDOR, pagination, stale assignment, PostgreSQL/API tests. |
| `FR-CLIN-002`, `AC-P10-002` | P10-B overview/intake projection                | Exact encounter authority; P7 labels                  | Contract, minimization, terminal/degraded tests.                       |
| `FR-CLIN-003`               | P10-B provenance timeline projection            | Patient scope + lawful access                         | Permission/filter/pagination/source tests.                             |
| `FR-CLIN-004`, `AC-P10-003` | P10-B/C medication/allergy panels               | Completeness semantics + content review               | Unknown/not-recorded/unverified and a11y tests.                        |
| `FR-CLIN-005`               | Future approved safety panel                    | P9 Stage 3 clinical approval                          | Separation/no-synthetic-token tests.                                   |
| `FR-CLIN-006`               | Future approved risk panel                      | Future model governance                               | Prediction/confirmed-data distinction tests.                           |
| `FR-CLIN-007`, `AC-P10-007` | P10-B/D provenance inspection                   | Source-owner permission                               | Missing/expired/cross-object source tests.                             |
| `FR-CLIN-008`, `AC-P10-005` | P10-D correction                                | Review authority + atomic lifecycle                   | Supersession, concurrency, rollback, idempotency and history tests.    |
| `FR-CLIN-009`               | P10-D confirmation                              | Review authority + exact current state                | Permission, duplicate, stale-state and atomic confirmation tests.      |
| `FR-CLIN-010`, `AC-P10-006` | P10-D rejection and preserved history           | Review authority + exact current state                | Permission, concurrency, rollback and immutable provenance tests.      |
| `FR-CLIN-011`               | Future P11 document source viewer               | P11 plus source permission/retention                  | Malware/access/expired-source tests.                                   |
| `FR-CLIN-012`               | Future P13 referral action                      | P13 authorization/consent                             | Referral state/idempotency tests.                                      |
| `FR-CLIN-013`, `AC-P10-009` | P10-C compile-time feature panels               | Typed registration and permissions                    | Owner isolation, unavailable-panel, a11y tests.                        |
| `FR-SUM-001`, `AC-P10-004`  | P10-A physician-ready source-backed draft       | Authorized bounded source projection                  | Golden, abstention and no-new-fact tests.                              |
| `FR-SUM-002`                | P10-A standard sections                         | Approved section schema                               | Completeness, ordering and unknown-state tests.                        |
| `FR-SUM-003`                | P10-A multi-source synthesis                    | Authorized typed inputs with source identity          | Source separation, contradiction and minimization tests.               |
| `FR-SUM-004`                | P10-A/C persistent visible draft status         | Version/status contract                               | State serialization and UI label tests.                                |
| `FR-SUM-005`                | P10-D clinician edit/revision                   | Authorized review + persistence                       | Optimistic concurrency, rollback and attribution tests.                |
| `FR-SUM-006`                | P10-D accept/amend/reject                       | Authorized review + exact source snapshot             | State, idempotency, rollback and provenance tests.                     |
| `FR-SUM-007`                | Optional patient confirmation, not P10 baseline | Separate patient UX/consent decision                  | No implementation planned by this spec.                                |
| `FR-SUM-008`                | P10-A/D source mapping and drift                | Spec 12 contract                                      | Source trace, changed-source, permission tests.                        |
| `AC-P10-008`                | Backend authorization boundary                  | Trusted clinician provider and deny-by-default policy | Patient-token and wrong-role route denial tests.                       |

# 8. Hard blockers

Before live clinician data access: approve/configure trusted clinician authentication and assurance;
authoritative clinician directory/status; assignment/transfer and institution isolation; privacy/legal
purpose and sharing/consent treatment for pseudonymous P7 encounters; least-privilege field set;
medication/allergy copy; source permissions; audit/retention; threat/privacy/accessibility/security
review; hosting/production enablement and rollback. Before P10-D, also approve fact/summary transaction,
concurrency, audit/outbox and migration design. P8-C and P9-C Stage 3 remain blocked and cannot be
used as shortcuts.
