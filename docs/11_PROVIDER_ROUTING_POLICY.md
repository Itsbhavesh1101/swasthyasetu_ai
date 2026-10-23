# SwasthyaSetu AI

## 11 — Provider Routing Policy

> **DRAFT — PRE-P13 POLICY DESIGN, UNAPPROVED; NO CLINICAL/PRIVACY/SECURITY/PRODUCTION AUTHORIZATION**

**Document ID:** `SSAI-SPEC-011-PRE-P13-DRAFT`

**Evidence baseline:** `main @ 568ad42047d6671971a9de3834c47b9de0687641`

**Review date:** 2026-10-23

**Review state:** DRAFT — ACCOUNTABLE HUMAN REVIEW REQUIRED

**Alembic head:** `p7a_0007` (unchanged)

This document proposes boundaries for later P13 review. It is not a clinical routing algorithm, a
verified directory, a consent notice, an external referral or notification service, or a pilot or
production release. It selects no provider source, contact, specialty taxonomy, clinical rule,
ranking weight, jurisdiction, integration, channel, retention period, or release population.

---

# 1. Authority, scope, and repository evidence

## 1.1 Governing authority

Approved clinical and safety policy, the Project Master Specification, System Architecture,
Product Requirements, privacy and consent specification, accepted ADRs, and R3 policy outrank this
draft. Binding boundaries include:

- ADR-002 and ADR-007: external integrations use project-owned ports and explicit compile-time
  registration, not vendor leakage or runtime plugin discovery;
- ADR-003: clinical/safety routing remains deterministic, versioned, and outside directory authority;
- ADR-006 and ADR-008: reliable events use a transactional outbox and PostgreSQL remains the
  authoritative transactional store;
- ADR-015: provider/resource contact truth comes only from a verified registry or validated source;
- ADR-016: governed care category and specialty/service type precede individual-provider selection;
- ADR-019 and ADR-037: future long-running delivery/retry uses a job abstraction, with PostgreSQL-
  native infrastructure evaluated before adding a broker;
- ADR-020: risky features remain safe-off and a flag never grants authorization;
- ADR-022 and ADR-023: engineering cannot invent clinical policy or represent synthetic providers
  as verified production truth;
- ADR-027: manual intake and urgent-help navigation remain independent of optional AI/providers; and
- ADR-038 and ADR-040: dependency profiles and phase activation prevent premature infrastructure.

No accepted ADR is changed here. No incompatibility requiring a new ADR was found in this audit.

## 1.2 In scope

- terminology and module ownership;
- proposed provider/resource source lifecycle and specialty-first routing contract;
- proposed referral, consent, side-effect, notification, failure, security, and privacy boundaries;
- exact requirement and acceptance traceability; and
- conditional P13-A/B/C/D/E review sequencing and human decisions.

## 1.3 Out of scope

Application or test code, fixtures, real records or contacts, scraping, provider evaluation, APIs,
OpenAPI, BFF/UI, schemas, ORM, migrations, feature flags, jobs, queues, storage, dependencies,
Docker/CI changes, clinical mappings, referral/notification delivery, approved copy, consent-policy
changes, patient data, credentials, signatures, and runtime activation are out of scope.

## 1.4 Exact as-built inventory

| Area | Baseline evidence | Honest conclusion |
| --- | --- | --- |
| P13 module paths | `backend/app/modules/providers/`, `resources/`, and `referrals/` contain only `.gitkeep`. | Domain, application, persistence, public registration, and tests are **NOT IMPLEMENTED**. |
| Routing policy path | `clinical/policies/provider_routing/` is a placeholder only. | No taxonomy, rule, threshold, or policy version is implemented or approved. |
| Composition | `backend/app/main.py` explicitly registers P2–P8 foundations, but no P13 module. | No P13 capability or API is active. |
| LLM provider file | `backend/app/modules/ai_orchestration/providers.py` defines LLM adapter contracts. | It is not a clinician/provider directory and supplies no contact truth. |
| Consent | P4 implements centralized purposes including `REFERRAL_SHARING`; the connected patient flow uses `GENERAL_PRODUCT_USE` with `clinical_intake`. | Existing intake consent is non-transitive and does not authorize referral disclosure. |
| Patient/encounter/intake | P5/P7 provide governed patient, encounter, provenance, and deterministic intake foundations. | P7 is non-diagnostic and cannot silently choose specialty, urgency, provider, or suitability. |
| AI/safety/summary | P8-C and P9-C patient Stage 3 are blocked; P10 live clinician access is 0/9 approved. | No AI, safety preview, or summary may authorize P13 routing. |
| Patient UI | `/referrals` states verified providers/referral pathways are unavailable; `/urgent-help` states verified contacts are not configured. | Honest unavailable/generic navigation exists; no directory or referral journey exists. |
| Admin UI | `apps/admin-web/app/page.tsx` is a foundation-only empty state. | No source verification, moderation, or governance workflow exists. |
| Data/API | Conceptual provider/resource/referral tables and endpoints exist only in canonical design docs. | No table, migration, repository, route, webhook, or external send exists. Alembic is `p7a_0007`. |
| Dependencies/infrastructure | Existing outbox and process-local job ports are generic foundations. | No durable referral worker, notification adapter, broker, provider SDK, or new infrastructure is authorized. |
| Required specifications | This file and `docs/25_ADMIN_PORTAL_SPEC.md` were absent at the baseline. | This draft fills only Spec 11; Spec 25 remains a separate missing P13-E prerequisite. |

P13 remains **NOT STARTED**. P12 is a draft specification only and supplies no runtime or language
authorization. P7 manual text/touch intake remains the supported fallback.

---

# 2. Ownership, trust, and terminology

## 2.1 Distinct concepts

| Concept | Meaning and trust boundary |
| --- | --- |
| Verified provider registry | Versioned records for individual clinicians/services whose identity, fields, sources, and contacts have passed an approved verification workflow. It is not model output. |
| Resource registry | Separately owned crisis, hospital, counselling, public-support, NGO, or institution resource records with jurisdiction, source, freshness, and approval evidence. |
| Care category | A governed category produced by an approved upstream policy. The final taxonomy is undecided. |
| Specialty/service type | A normalized directory query category governed separately from a named provider. |
| Facility | An organization/location record with its own identity, source, status, and contacts; affiliation must not imply current provider availability. |
| Contact method | A source-backed, purpose-specific value whose format, ownership, and current validity were verified. A nonempty value is not proof. |
| Scheduling link | A separately verified booking destination/integration; a general provider website is not automatically a booking link. |
| Referral | A governed aggregate recording an offer, consent, external-delivery state, and later externally evidenced outcomes. It is not merely a link click. |
| Notification | A privacy-minimized intent delivered through a replaceable adapter; it is not proof that a referral was received or completed. |
| Clinical/safety triage | An independently approved deterministic authority. Directory availability cannot create, downgrade, or infer a P9 decision. |
| Source provenance | The versioned origin, rights, publisher/institution, verifier evidence, timestamps, and correction lineage supporting a record and each externally useful field. |

Speculative specialty suggestions, LLM-generated names, and reverse-mapped model text are not
verified directory truth. A directory query result is not a diagnosis, endorsement, availability
guarantee, appointment, clinical suitability decision, or emergency response.

## 2.2 Module ownership and boundaries

| Module | Future authoritative ownership | Prohibited coupling |
| --- | --- | --- |
| `providers` | Provider, facility, contact, source, verification, and directory-query contracts. | No LLM contact generation; no direct writes to consent/referral tables. |
| `resources` | Care-resource records, jurisdiction, eligibility, verification, expiry, and governed fallback metadata. | No module-local consent or inferred crisis policy. |
| `referrals` | Referral aggregate, exact consent linkage, minimized payload intent, destination adapter port, delivery attempts, status history, and correction. | No unrestricted patient read or direct notification/provider internals. |
| `notifications` | Notification intent, approved template/version, preference, adapter, attempt, and delivery status. | No referral-state authority or sensitive copy invented by an adapter. |

Future modules expose typed capabilities/ports and are composed explicitly. They consume centralized
`consent.check`, authorization, patient/encounter projections, outbox, and job ports through public
contracts. They must not create shadow consent, directly mutate another module's tables, or treat a
cache/search index as authoritative. The conceptual domain, schema, and API documents are design
evidence only; they do not approve migrations or routes.

---

# 3. Provider and resource source-of-truth lifecycle — proposed and unapproved

## 3.1 Proposed source record

A future versioned source record should carry a stable source/version identifier, source type,
publisher/author and institution, license or permission evidence, permitted fields/uses,
jurisdiction/coverage, obtained/issued time, last verification time, verifier role and proof,
supersedes/superseded-by lineage, correction/appeal state, and audit reference. Exact fields,
evidence format, access rules, and retention are human decisions.

The following proposed lifecycle vocabulary is **UNAPPROVED**:

```text
UNKNOWN | UNVERIFIED | VERIFIED | STALE | EXPIRED | SUSPENDED | REVOKED
```

Canonical documents currently use overlapping values such as `ACTIVE`, `STALE`, `EXPIRED`,
`INACTIVE`, `UNVERIFIED`, and resource `approval_status`. `ACTIVE` must never be silently equated
with current verified truth. P13-A must reconcile the final closed vocabulary and transitions under
human architecture, operations, privacy, and source-governance review.

## 3.2 Freshness, time, correction, and revocation

- `verified_at`, `expires_at`, and all lifecycle times must be timezone-aware UTC;
- recheck cadence and expiry calculations are **UNDECIDED** and source/jurisdiction dependent;
- an expired, revoked, suspended, unknown, or unverified source cannot silently produce a current
  verified result;
- stale disclosure, if ever permitted, needs approved warning, ordering, fallback, and safety rules;
- supersession preserves prior source and verifier lineage rather than overwriting history;
- revocation must invalidate affected derived contacts/results under an approved propagation SLA;
- clock rollback, future-dated proof, missing expiry, conflicting versions, and concurrent
  correction must fail closed or enter accountable review; and
- correction and appeal require non-destructive audit evidence and appropriate separation of duties.

## 3.3 Provider, facility, resource, and contact fields

The canonical design supports provider display name, type, normalized specialty/service type,
optional qualifications/registration metadata, optional facility, optional geography, languages,
verified contact methods, optional booking integration, optional teleconsultation, optional hours,
source, verification time, optional expiry, and status. Resource design adds resource type, display
label, optional eligibility and institution, approval state, locale/language, and version.

Every optional field must remain explicitly unknown when evidence is absent. Language listing does
not prove availability or clinical-language competency. Teleconsultation, hours, accessibility,
eligibility, facility affiliation, and geography need their own source and freshness semantics. A
valid-looking phone number or URL is not verified. URLs require scheme/host policy, allowlisted
destinations where appropriate, redirect review, and protection from malicious links and SSRF.

No real provider, crisis contact, phone number, email address, booking URL, or institution record is
created by this draft. Import adapters, source-vendor choice, moderation, dual control for sensitive
resource changes, refresh jobs, and audit implementation remain conceptual.

## 3.4 Synthetic versus verified production data

Future synthetic fixtures must use unmistakably nonreal identifiers and reserved/example domains,
carry an `ENGINEERING_SYNTHETIC` classification, be impossible to select in protected environments,
and never claim verification, availability, registration, or clinical suitability. Synthetic data
must not resemble real PII or use scraped contacts. Production records require approved sources,
rights, verifier evidence, freshness, and release authorization. Environment flags or CI success do
not convert synthetic data into verified truth.

---

# 4. Specialty-first routing — no invented clinical policy

## 4.1 Conceptual sequence

The only proposed sequence is:

```text
approved upstream care-category signal/policy
  -> normalized specialty or service type
  -> verified and eligible directory query
  -> transparent user-controlled filters
  -> options with source freshness and limitations
```

This sequence is **UNAPPROVED FOR LIVE USE**. No taxonomy, symptom-to-specialty mapping, urgency
threshold, triage cutoff, eligibility rule, or ranking weight is defined here. Opaque LLM ranking,
fabricated provider details, paid-ranking influence on clinical relevance, and reverse mapping an
LLM suggestion into a registry contact are prohibited.

## 4.2 Proposed decision metadata

A future immutable typed result may contain:

```text
decision_id
subject/encounter reference (authorized, minimized)
care_category | UNKNOWN
specialty_or_service_type | UNKNOWN
reason_codes[]
policy_id + policy_version
upstream_source references + versions
created_at (aware UTC)
outcome = MATCH | ABSTAIN | UNKNOWN
```

This is design only. It contains no provider contact and grants no P9 safety authority. Missing or
unapproved upstream authority, policy, source, eligibility, geography, or required context results
in abstention/unknown while preserving approved manual options. It must never fabricate contact,
claim that help is available, or interpret lack of a directory result as low clinical risk.

## 4.3 Stewardship and uncertainty

Accountable humans must decide the specialty taxonomy, mapping stewardship, clinical review,
authorized geography/service coverage, age/guardian/institution eligibility, disabled clinician or
facility handling, language and availability semantics, conflict resolution, freshness, transparent
filters, accessibility attributes, ranking, monitoring, and release criteria. Precise location is
optional; manual city/area/institution filters must remain possible. Provider selection remains
user-controlled within approved policy and verified eligibility.

---

# 5. Referral aggregate and consent boundary — design only

## 5.1 State meanings

The canonical closed state set is:

```text
OFFERED, CONSENTED, SENT, ACKNOWLEDGED, SCHEDULED, COMPLETED,
DECLINED, UNREACHABLE, EXPIRED, FAILED, CANCELLED
```

`OFFERED` records an available intent and never authorizes disclosure. `CONSENTED` means the exact
governed sharing authorization was validated and linked; it is not proof of dispatch. A delivery
attempt is separate operational evidence. `SENT` must require adapter evidence under the approved
contract and must not be inferred from enqueueing. `ACKNOWLEDGED`, `SCHEDULED`, and `COMPLETED`
require authenticated/validated external or authorized human evidence and cannot be fabricated from
timeouts, page visits, or notifications.

## 5.2 Proposed transition matrix for human/application-owner review

| From | Proposed allowed next state(s) | Required evidence | Status |
| --- | --- | --- | --- |
| New intent | `OFFERED` | Authorized route/destination offer; no sharing side effect. | UNAPPROVED |
| `OFFERED` | `CONSENTED`, `DECLINED`, `EXPIRED`, `CANCELLED` | Exact decision/consent or governed timeout/cancel evidence. | UNAPPROVED |
| `CONSENTED` | `SENT`, `FAILED`, `EXPIRED`, `CANCELLED` | Consent revalidation plus idempotent adapter outcome or governed race result. | UNAPPROVED |
| `SENT` | `ACKNOWLEDGED`, `UNREACHABLE`, `FAILED`, `EXPIRED`, `CANCELLED` | Validated destination event or accountable correction. | UNAPPROVED |
| `ACKNOWLEDGED` | `SCHEDULED`, `UNREACHABLE`, `EXPIRED`, `CANCELLED` | Authenticated external/authorized workflow evidence. | UNAPPROVED |
| `SCHEDULED` | `COMPLETED`, `FAILED`, `CANCELLED` | Validated appointment outcome; never client inference. | UNAPPROVED |
| Any terminal state | none except an explicit audited correction workflow | Separate correction authority; preserve original history. | UNAPPROVED |

The table reconciles possible meanings but does not approve transitions. Human owners must decide
terminal states, late acknowledgements, reopening/correction, expiry clocks, unreachable semantics,
cancellation after send, withdrawal after disclosure, and precedence during concurrent events.
Invalid transitions, stale versions, duplicate events, and cross-referral updates must reject.

## 5.3 Consent and minimization

External referral sharing requires explicit, active, purpose-specific `REFERRAL_SHARING` consent.
Any additionally applicable lawful or governance requirements must also be satisfied; they cannot
replace that mandatory consent. Existing `GENERAL_PRODUCT_USE` / `clinical_intake` consent,
authentication, an offered referral, or provider selection cannot authorize external sharing.

The approved design must bind subject, authorized patient/guardian/institution actor, recipient and
destination identity, purpose, exact field allowlist, notice/version, scope, grant, expiry, and
withdrawal state. These are human decisions pending. The sender revalidates authorization,
destination, consent, source freshness, and current referral version immediately before an external
side effect. No raw transcript by default; no bearer/cookie, unrestricted history, unnecessary
contact, clinical text in logs, or fields beyond the approved minimum. A future optional narrative
requires separate explicit consent and governed template.

## 5.4 Idempotency, outbox, retry, and ambiguous effects

Future creation and external delivery need separate opaque idempotency identities, transactional
state/outbox recording, bounded retries through a job abstraction, and immutable attempt evidence.
The system must not hold a transaction open during an external call or claim exactly-once delivery.
After timeout or connection loss, delivery is ambiguous: do not blindly resend; reconcile using an
adapter idempotency key/status query or send to human review. Duplicate callbacks and sends must not
advance state twice.

Signed webhooks require exact adapter routing, signature and timestamp validation, replay defense,
schema/version checks, destination/referral binding, nonenumerating errors, and state-transition
validation. Consent withdrawal, cancellation, expiry, and late callback races need an approved
ordering policy and audit trail. Status correction must never erase the original external event.
There are no real sends, webhooks, emails, SMS, jobs, or contact sharing in this phase.

---

# 6. Resources, urgent-help failure isolation, and notifications

Verified emergency/crisis resources and any bundled fallback need an accountable source,
jurisdiction, approval, validity window, maintenance owner, incident path, and tested withdrawal.
This draft contains no helpline numbers, clinical crisis scripts, unsupported urgent routing, or
translations. Missing registry/provider/LLM state must not promise help availability, infer safety,
or remove the existing generic `/urgent-help` navigation and P7 manual intake.

Provider lookup failure must preserve care-category information only when that upstream category is
itself approved, show an honest unavailable/unknown result, and use cached/static resources only if
their current verification and disclosure policy permits it. Stale/expired resources never become
fresh because the live source is down.

Future notifications require user authorization and configurable preferences where applicable,
approved versioned templates, minimum safe variables, privacy-safe generic lock-screen copy,
replaceable adapters, bounded/idempotent attempts, and visible failure/correction. Channel,
provider, recipient, content, timing, retry, retention, and escalation are undecided. A notification
delivery receipt cannot establish referral acknowledgement or clinical completion.

---

# 7. Security, privacy, operational, and accessibility threats

| Threat/failure | Required future control and negative evidence | Accountable reviewer roles |
| --- | --- | --- |
| IDOR/cross-subject access | Server-owned actor/session/patient/institution binding; nonenumerating read/update tests across every registry/referral object. | Identity/security; application owner |
| Fake contact/source impersonation | Signed/allowlisted imports where applicable, field-level provenance, independent verification, dual control for sensitive resources; reject unverifiable proof. | Source governance; security; operations |
| Malicious URL, redirect, SSRF | Strict parsing and scheme/host policy, no patient-controlled server fetch, redirect/destination checks, safe link rendering; adversarial URL tests. | Security; frontend; integration owner |
| Stale/expired/crisis misinformation | UTC expiry, revocation propagation, fail-closed query, visible approved warnings, incident removal/rollback drills. | Clinical safety; resource owner; operations |
| SQL/filter/injection and imported data | Typed bounded filters, parameterized queries, strict schema/size/Unicode handling, content rendering as text, quarantine/review for imports. | Security; data/application owner |
| Admin/moderator abuse and source poisoning | Least privilege, MFA gate, separation of duties, immutable audit, approval workflow, anomaly/rollback evidence. | Security; admin governance; audit owner |
| Recipient substitution/cross-institution disclosure | Destination binding at consent and send, exact institution scope, reauthorization, adapter allowlist; substitution tests. | Privacy; identity; referral owner |
| Consent withdrawal/cancellation race | Recheck before side effect, version/lock policy, ordered outbox/jobs, late-event handling; injected-race tests. | Privacy; application/data architect |
| Webhook spoof/replay/duplicate send | Signature/timestamp/schema/idempotency validation and state guard; replay, wrong-key, stale-event, duplicate tests. | Security; integration owner |
| Provider outage/ambiguous send | Bounded deadline/retry, no false success, reconciliation/human review, visible failure, rollback runbook. | Operations; referral owner |
| Log/analytics/notification leakage | No raw history/transcript/contact/bearer in telemetry, reports, URLs, previews, or lock screens; seeded-canary scans. | Privacy; security; observability owner |
| Accessibility/localized-copy failure | Keyboard, screen reader, focus, 320/390px reflow, non-color warnings, safe text rendering; only approved source warnings/locales. | Accessibility; content/localization |

Privacy decisions remain open for purpose, mandatory explicit `REFERRAL_SHARING` consent and notice,
any additionally applicable lawful or governance requirements, patient/guardian/caregiver authority,
source/contact rights and licensing, collection, access, institution isolation, retention/deletion,
corrections, external processors, notifications, incident handling, and subject rights. Additional
requirements cannot replace explicit referral consent. This document makes no legal or compliance
claim.

---

# 8. Requirement traceability

All statuses below are live **NOT VERIFIED**. Existing conceptual documentation or adjacent platform
primitives are not P13 acceptance evidence.

## 8.1 `FR-DIR-001..017`

| ID and exact requirement | Draft section / present evidence / missing implementation | Human owner | Live status |
| --- | --- | --- | --- |
| `FR-DIR-001` — The system SHOULD map patient context to a care category/specialty before selecting individual providers. | §4 proposes ordering; no approved mapping/policy exists. | Clinical governance; routing owner | NOT VERIFIED |
| `FR-DIR-002` — Named provider/resource data SHALL come from a verified registry or validated integration. | §§2–3 define trust; registries/integrations absent. | Source governance; architecture | NOT VERIFIED |
| `FR-DIR-003` — Provider records SHALL support a display name. | §3 records conceptual field only. | Providers owner | NOT VERIFIED |
| `FR-DIR-004` — Provider records SHALL include normalized specialty/service type. | §§3–4; taxonomy and model absent. | Clinical taxonomy; providers owner | NOT VERIFIED |
| `FR-DIR-005` — Provider records SHOULD include facility affiliation. | §3 treats affiliation as optional/source-backed; absent. | Providers/facilities owner | NOT VERIFIED |
| `FR-DIR-006` — Provider records SHALL support one or more verified contact methods. | §3 requires field-level proof; no contacts or workflow exist. | Source governance; providers owner | NOT VERIFIED |
| `FR-DIR-007` — Provider records MAY include a booking URL/integration. | §3 distinguishes site from verified booking; absent. | Integration/security owner | NOT VERIFIED |
| `FR-DIR-008` — Provider records SHOULD support location. | §§3–4 require bounded optional geography; absent. | Providers/privacy owner | NOT VERIFIED |
| `FR-DIR-009` — Provider records SHOULD support languages served. | §3 requires qualified/uncertain semantics; absent. | Providers/language owner | NOT VERIFIED |
| `FR-DIR-010` — Provider records SHOULD represent teleconsultation availability. | §3 requires separately sourced status; absent. | Providers owner | NOT VERIFIED |
| `FR-DIR-011` — Provider/resource records SHOULD represent known operating hours. | §3 requires source/freshness; absent. | Providers/resources owner | NOT VERIFIED |
| `FR-DIR-012` — Every external provider/resource record SHALL have a verification timestamp where managed by the platform. | §3 requires UTC verification; no records exist. | Source governance | NOT VERIFIED |
| `FR-DIR-013` — Managed provider/resource records SHOULD have verification expiry. | §3; cadence/expiry policy undecided. | Source governance; operations | NOT VERIFIED |
| `FR-DIR-014` — Stale resources SHALL be identifiable. | §3 proposes lifecycle; no schema/query/UI exists. | Resources owner | NOT VERIFIED |
| `FR-DIR-015` — User-facing provider filters/ranking factors SHOULD be transparent. | §4 requires user-controlled transparent filters; weights undecided. | Product; clinical governance | NOT VERIFIED |
| `FR-DIR-016` — The application MUST NOT display provider data invented by generative AI. | §§2–4 prohibit fabrication; no registry flow exists to prove it. | Architecture; security | NOT VERIFIED |
| `FR-DIR-017` — Additional provider-directory data sources SHALL be addable through adapters. | §§2–3 require ports/adapters; none implemented. | Architecture/integration owner | NOT VERIFIED |

## 8.2 `FR-REF-001..013`

| ID and exact requirement | Draft section / present evidence / missing implementation | Human owner | Live status |
| --- | --- | --- | --- |
| `FR-REF-001` — The system SHALL be able to offer a referral when the route permits it. | §5 distinguishes offer from send; no approved route/referral exists. | Clinical/product; referrals owner | NOT VERIFIED |
| `FR-REF-002` — A referral that shares information externally SHALL require explicit consent. | §5 requires exact sharing consent; no live sharing flow. | Privacy/consent owner | NOT VERIFIED |
| `FR-REF-003` — Referral payloads SHALL contain only necessary information. | §5 requires approved allowlist; payload undecided. | Privacy; referrals owner | NOT VERIFIED |
| `FR-REF-004` — Full chat transcripts MUST NOT be transmitted by default. | §5 prohibits raw transcript by default; no adapter exists. | Privacy/security | NOT VERIFIED |
| `FR-REF-005` — Referral lifecycle SHALL support `OFFERED`. | §5 design only; aggregate absent. | Referrals owner | NOT VERIFIED |
| `FR-REF-006` — Referral lifecycle SHALL support `CONSENTED`. | §5 design only; aggregate absent. | Referrals/consent owner | NOT VERIFIED |
| `FR-REF-007` — Referral lifecycle SHALL support `SENT`. | §5 requires delivery evidence; adapter absent. | Referrals/integration owner | NOT VERIFIED |
| `FR-REF-008` — Referral lifecycle SHOULD support `ACKNOWLEDGED`. | §5 requires validated external evidence; absent. | Referrals/integration owner | NOT VERIFIED |
| `FR-REF-009` — Referral lifecycle SHOULD support `SCHEDULED`. | §5 design only; scheduling integration absent. | Referrals/product owner | NOT VERIFIED |
| `FR-REF-010` — Referral lifecycle SHOULD support `COMPLETED`. | §5 forbids inferred completion; absent. | Referrals/clinical operations | NOT VERIFIED |
| `FR-REF-011` — Referral lifecycle SHOULD support `DECLINED`, `UNREACHABLE` and `EXPIRED` where relevant. | §5 reconciles states; transitions/clocks undecided. | Referrals/product owner | NOT VERIFIED |
| `FR-REF-012` — The user SHOULD be able to see applicable referral status. | §§5,7 require authorized accessible state; UI unavailable. | Patient app; accessibility | NOT VERIFIED |
| `FR-REF-013` — Appointment/referral destinations SHALL be integration-adapter based. | §§2,5 require ports; no adapter exists. | Architecture/integration owner | NOT VERIFIED |

## 8.3 Applicable notification, audit, and privacy requirements

| ID and exact requirement | Draft section / missing evidence | Human owner | Live status |
| --- | --- | --- | --- |
| `FR-NOTIF-001` — The system SHOULD notify users of relevant referral-status changes when consent/identity allow it. | §6; identity/consent/template/adapter absent. | Notifications; privacy | NOT VERIFIED |
| `FR-NOTIF-002` — The system MAY provide follow-up reminders after a referral, investigation or discharge. | §6; purpose/content/timing undecided. | Product; clinical; privacy | NOT VERIFIED |
| `FR-NOTIF-003` — The system MAY support medication-adherence reminders without changing medication instructions. | Outside current P13 referral scope; no inference from this draft. | Medication/clinical owner | NOT VERIFIED |
| `FR-NOTIF-004` — Notification channel/preferences SHALL be user-configurable where applicable. | §6; preference model absent. | Notifications/product | NOT VERIFIED |
| `FR-NOTIF-005` — Notifications MUST avoid exposing unnecessary sensitive health information on lock screens or insecure channels. | §§6–7; template/privacy tests absent. | Privacy/security/content | NOT VERIFIED |
| `FR-NOTIF-006` — Notification delivery SHOULD use a replaceable provider abstraction. | §§2,6; no adapter implemented or selected. | Architecture/notifications | NOT VERIFIED |
| `FR-AUDIT-002` — Provider/resource changes SHALL be auditable. | §§3,7 require lineage; audit implementation absent. | Audit/source governance | NOT VERIFIED |
| `FR-AUDIT-003` — Consent changes SHALL be auditable. | §5 depends on centralized consent; P4 events exist, referral-specific evidence absent. | Consent/audit owner | NOT VERIFIED FOR P13 |
| `FR-AUDIT-004` — Sensitive administrative actions SHALL be auditable. | §7; Admin Portal spec/workflow absent. | Admin governance/audit | NOT VERIFIED |
| `PRIV-001` — Only data required for the active purpose SHOULD be collected. | §§5–7; referral field allowlist undecided. | Privacy/data governance | NOT VERIFIED FOR P13 |
| `PRIV-002` — Data SHALL be used according to documented purposes and consent/governance. | §5; mandatory explicit referral consent, purpose/notice, and any additional applicable lawful/governance requirements remain pending. | Privacy/legal | NOT VERIFIED FOR P13 |
| `PRIV-003` — Sensitive transient data SHALL have explicit retention rules. | §§5–7; attempt/payload/log retention pending. | Privacy/operations | NOT VERIFIED FOR P13 |
| `PRIV-004` — Applicable deletion/withdrawal workflows SHALL be supported. | §5; post-send withdrawal/correction pending. | Privacy/referrals owner | NOT VERIFIED FOR P13 |
| `PRIV-005` — Referral sharing SHALL use a minimized payload. | §5; allowlist and evidence absent. | Privacy/referrals owner | NOT VERIFIED |
| `PRIV-006` — Anonymous-feeling mental-health first-contact mode SHALL avoid intentional collection of unnecessary identity. | P14 remains future; P13 must not force identity collection without approved need. | Privacy/P14 owner | NOT VERIFIED |
| `PRIV-007` — Operational logs SHALL exclude raw sensitive content by default. | §7 requires canary/redaction tests; P13 logs absent. | Security/observability | NOT VERIFIED FOR P13 |
| `PRIV-008` — Research datasets/workspaces SHALL be separated from normal production patient data access. | Synthetic directory fixtures must remain isolated; no P13 data exists. | Research/data governance | NOT VERIFIED FOR P13 |
| `PRIV-009` — Institutional aggregate analytics SHOULD avoid exposing identifiable individual mental-health conversations. | P13 analytics are not approved; transcript sharing/logging prohibited. | Privacy/institution owner | NOT VERIFIED FOR P13 |

## 8.4 `AC-P13-001..011`

| Criterion | Future evidence needed | Current status |
| --- | --- | --- |
| `AC-P13-001` — Provider registry stores source and verification metadata. | Approved model/migration plus real PostgreSQL constraints and source tests. | LIVE NOT VERIFIED |
| `AC-P13-002` — Resource registry stores source and verification metadata. | Approved model/migration plus real PostgreSQL constraints and source tests. | LIVE NOT VERIFIED |
| `AC-P13-003` — Stale/expired resources are identifiable. | UTC lifecycle/query/UI tests including revocation and source outage. | LIVE NOT VERIFIED |
| `AC-P13-004` — Specialty/service-type routing occurs before individual-provider selection. | Approved policy/taxonomy and ordering tests. | LIVE NOT VERIFIED |
| `AC-P13-005` — LLM-generated provider contact details are impossible through normal registry flow. | Import/query boundary, architecture, injection, and no-fabrication tests. | LIVE NOT VERIFIED |
| `AC-P13-006` — Referral requires appropriate explicit consent before external sharing. | Real authorization/consent/PostgreSQL/adapter tests. | LIVE NOT VERIFIED |
| `AC-P13-007` — Full raw transcript is not included by default. | Payload allowlist and capture/redaction tests. | LIVE NOT VERIFIED |
| `AC-P13-008` — Referral state machine supports required states. | Approved state model and direct-constructor/transition/race tests. | LIVE NOT VERIFIED |
| `AC-P13-009` — Duplicate referral side effects are idempotently controlled. | Outbox/job/adapter/webhook duplicate and ambiguity tests. | LIVE NOT VERIFIED |
| `AC-P13-010` — External referral adapter failures produce visible status/fallback. | Timeout/outage/ambiguous-effect UI and operational evidence. | LIVE NOT VERIFIED |
| `AC-P13-011` — Synthetic provider records are clearly marked if real verified data is unavailable. | Environment isolation, unmistakable labeling, and protected-mode refusal tests. | LIVE NOT VERIFIED |

---

# 9. Conditional future phase plan

| Future unit | Separately reviewable scope | Required approvals/evidence | STOP condition |
| --- | --- | --- | --- |
| P13-A — providers/resources domain | Possibly immutable nonmedical synthetic contracts, lifecycle validation, explicit metadata, and offline tests. | Final source/status taxonomy, ownership, source rights, fields, freshness, privacy/security review, and a separate prompt. | Any record implies real verification, contact, clinical suitability, persistence, or source selection. |
| P13-B — query/routing | Approved specialty-first policy contract, verified query, transparent filters, abstention. | Clinical taxonomy/mapping authority, geography/eligibility/ranking decisions, source registry, adversarial tests. | Any symptom mapping, threshold, provider ranking, or P9 authority is unapproved. |
| P13-C — referral domain/state | Approved aggregate/transitions, consent/minimization, persistence/outbox/idempotency, adapters. | Privacy/consent/identity/institution, schema/API, side-effect, retry/race/webhook decisions. | Recipient, payload, consent, state, idempotency, or external effect remains undecided. |
| P13-D — notification adapters | Approved intents/templates/preferences and one replaceable adapter. | Channel/provider/recipient/copy/retention/incident decisions and contract/security tests. | Sensitive copy, provider, consent, retry, or delivery semantics are unapproved. |
| P13-E — patient/admin UI | Accessible source/freshness, selection, consent, status, moderation, correction experiences. | `25_ADMIN_PORTAL_SPEC.md`, approved copy, roles/permissions, accessibility, privacy, source warning and release evidence. | Admin spec, real identity, source workflow, or patient-facing copy is missing. |

Only a separately reviewed prompt may authorize a narrow, nonmedical, synthetic engineering subset.
This draft does not authorize P13-A or any other implementation. P14 mental-health and P15 self-care
use cases cannot be used to infer clinical routes, contacts, urgent copy, or patient-facing content.

---

# 10. Open human decisions and final STOP rule

Accountable roles must decide and record:

1. registry, clinician, facility, institution, verifier, moderator, and integration identity;
2. provider/resource sources, licenses/permissions, jurisdictions, proof, cadence, expiry, correction,
   appeals, dual control, and revocation propagation;
3. care-category/specialty taxonomy, mapping authority, clinical validation, reason codes, abstention,
   geography, eligibility, transparent filters/ranking, and release scope;
4. patient/guardian/caregiver/institution authority, referral purpose, notice, mandatory explicit
   `REFERRAL_SHARING` consent, any additionally applicable lawful or governance requirements,
   recipient, field minimization, withdrawal, subject access, retention, and deletion;
5. registry/referral/notification schema, API, transactions, outbox, jobs, idempotency, retries,
   webhooks, ambiguous effects, corrections, and incident/rollback behavior;
6. patient/admin copy, source/freshness warnings, accessibility/localization, notification channels,
   templates, timing, preferences, and privacy;
7. verified urgent-resource fallback, source incidents, monitoring, pilot population/environment,
   residual-risk acceptance, expiry/re-review, and production release; and
8. the missing `docs/25_ADMIN_PORTAL_SPEC.md` before relevant P13-E governance/admin work.

If an applicable decision or authoritative evidence is absent, implementation must stop rather than
invent a policy, source, contact, approval, or safe outcome. Documentation and CI cannot close a
clinical, privacy, security, operational, provider-verification, pilot, or production gate.
