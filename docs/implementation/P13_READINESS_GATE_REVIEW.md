# P13 provider routing, registry, referral, and notification readiness gate review

> **DRAFT — PROPOSED PRE-P13 GATES, UNAPPROVED; NO CLINICAL POLICY, PROVIDER VERIFICATION, REFERRAL AUTHORIZATION, OR LIVE ACCEPTANCE**

**Review date:** 2026-10-23

**Evidence baseline:** `main @ 568ad42047d6671971a9de3834c47b9de0687641`

**P13 state:** NOT STARTED

**Alembic head:** `p7a_0007`

# 1. Review conclusion

The repository is ready for accountable review of a P13 design draft, not for live provider
discovery, clinical specialty routing, referral sharing, notifications, or source administration.
Provider, resource, and referral module paths are placeholders; none is registered; no registry,
route, table, migration, real contact, source import, delivery adapter, or admin workflow exists.
The patient UI honestly reports referrals and verified urgent contacts as unavailable.

The matrix below is a proposed P13-specific review inventory. The project has not established an
official P13 gate count; these eight proposed gates are not approvals and do not reuse P11's nine-
gate model. Every gate is **OPEN** or **BLOCKED** pending accountable human decisions and evidence.
Documentation, synthetic tests, a feature flag, and CI cannot grant human approval or pass
`AC-P13-001..011`.

# 2. Proposed, unapproved gate matrix

## Gate 1 — Verified provider/resource sources, rights, and freshness governance

**Status:** **OPEN — NO VERIFIED SOURCE OR PRODUCTION RECORD**

- **As-built evidence:** provider/resource paths contain `.gitkeep`; the conceptual domain/schema
  names source, verification, expiry, and status fields; the UI contains no real contact.
- **Undecided:** authoritative sources, licenses/permissions, jurisdictions, publisher/institution,
  verifier identity/proof, verification/recheck/expiry cadence, final status vocabulary, correction,
  appeal, dual control, revocation propagation, and stale disclosure policy.
- **Accountable reviewers:** provider/resource governance owner; institutional owner; privacy/legal;
  security; data governance; clinical safety for urgent resources; operations.
- **Decision artifacts:** source register and rights evidence; field-level provenance rules; closed
  lifecycle/state decision; UTC/freshness policy; verifier/moderator role matrix; correction,
  incident, suspension, rollback, and re-review procedure.
- **Principal risks:** fake or poisoned sources, malicious contacts/URLs, expired crisis resources,
  scraped PII, invalid licenses, source impersonation, moderator abuse, cross-jurisdiction claims.
- **Required negative/failure tests:** missing/forged proof; unknown/revoked/expired source; clock
  skew/future timestamp; source conflict; malicious URL/redirect; duplicate/superseded record;
  source outage; unauthorized moderation; revocation during query; protected-mode synthetic refusal.
- **Possible separately authorized synthetic scope:** immutable nonreal source/record contracts and
  pure lifecycle tests with reserved identifiers, no contacts, persistence, imports, or egress.
- **STOP condition:** any live source, rights, verifier, freshness, jurisdiction, or urgent-resource
  decision is missing, or synthetic data could appear as verified production truth.

## Gate 2 — Care-category/specialty taxonomy and clinical policy authority

**Status:** **BLOCKED — NO APPROVED TAXONOMY OR CLINICAL ROUTING POLICY**

- **As-built evidence:** P7 deterministic intake is non-diagnostic; P9-C live safety remains blocked;
  `clinical/policies/provider_routing/` is a placeholder; no mapping/ranking exists.
- **Undecided:** care categories, specialty/service taxonomy, symptom/context mapping authority,
  reason codes, ambiguity/abstention, exclusions, geography/age/institution eligibility, policy
  versioning, clinical validation, transparent ranking factors, and release population.
- **Accountable reviewers:** clinical governance; specialty-domain reviewers; patient safety;
  product; application architecture; accessibility/content; institutional care-navigation owner.
- **Decision artifacts:** source-backed taxonomy and policy; reviewer/signoff record; validation
  corpus and results; reason-code/version lifecycle; abstention and rollback policy; approved copy.
- **Principal risks:** diagnosis by directory, unsafe specialty/urgency inference, P9 downgrade,
  opaque/commercial ranking, discrimination, unsuitable age/geography route, LLM authority.
- **Required negative/failure tests:** missing/unknown signal; unsupported taxonomy/version;
  ambiguous/conflicting context; hard-safety presence; disabled provider/facility; no result; source
  expiry; LLM-supplied specialty/contact; ranking manipulation; policy rollback.
- **Possible separately authorized synthetic scope:** nonmedical symbolic ordering/abstention
  contracts only, with no symptom rules, clinical categories, or patient-facing result.
- **STOP condition:** any taxonomy, mapping, threshold, policy source, reviewer, population, or
  interaction with P9 authority is absent or inferred from model output.

## Gate 3 — Identity, institution, ownership, and sharing consent

**Status:** **OPEN — REFERRAL AUTHORITY AND SHARING CONSENT UNDECIDED**

- **As-built evidence:** P4 provides sessions, ActorContext, centralized consent, and a
  `REFERRAL_SHARING` purpose; current patient onboarding grants only `GENERAL_PRODUCT_USE` /
  `clinical_intake`, which cannot authorize external referral sharing. Real IdP and clinician/admin
  workflows remain unconfigured.
- **Undecided:** patient/guardian/caregiver authority, institution/recipient identity, destination
  proof, referral purpose/scope/notice, mandatory explicit `REFERRAL_SHARING` consent, any
  additionally applicable lawful or governance requirements, exact fields, grant expiry,
  withdrawal, cross-institution access, subject rights, and contact handling.
- **Accountable reviewers:** privacy/legal and consent owner; identity/security; institutional owner;
  patient/guardian governance; referrals owner; data protection/governance.
- **Decision artifacts:** role/permission and object-ownership matrix; recipient/destination binding;
  approved sharing notice/scope; consent and withdrawal rules; field-level minimization; access,
  deletion, correction, and cross-institution policy.
- **Principal risks:** IDOR, unauthorized guardian/caregiver action, recipient substitution,
  consent transitivity, over-sharing, cross-institution leakage, consent withdrawal race.
- **Required negative/failure tests:** wrong session/actor/patient/institution; missing/wrong/expired/
  withdrawn consent; stale authorization; substituted recipient; extra field/raw transcript; close/
  revoke concurrent with dispatch; enumeration; unauthorized status read.
- **Possible separately authorized synthetic scope:** pure authorization/consent decision contracts
  using opaque synthetic subjects, without API, patient data, persistence, or external sharing.
- **STOP condition:** a live operation lacks exact subject, actor, institution, recipient, purpose,
  minimum fields, explicit active purpose-specific `REFERRAL_SHARING` consent, or nonenumerating
  authorization; additionally applicable lawful or governance requirements must also be met and
  cannot replace the mandatory referral consent.

## Gate 4 — Registry models, APIs, persistence, and query architecture

**Status:** **OPEN — CONCEPTUAL SCHEMA/API ONLY; NO MIGRATION AUTHORIZED**

- **As-built evidence:** canonical docs contain conceptual provider/resource tables and endpoints;
  PostgreSQL/outbox/module-registration primitives exist; no P13 ORM, repository, API, capability,
  table, or migration exists. Alembic remains `p7a_0007`.
- **Undecided:** final immutable/domain models, status constraints, source normalization, contact and
  facility ownership, institution scoping, query/filter/cursor contract, API authorization/error
  behavior, persistence indexes, concurrency, audit/outbox, cache/search derivation, and retention.
- **Accountable reviewers:** application/data architecture; providers/resources owners; API owner;
  security; privacy; operations; database reviewer.
- **Decision artifacts:** reviewed contracts and ownership diagram; schema/migration plan; API and
  capability contracts; consistency/transaction model; query/freshness semantics; data retention;
  real PostgreSQL and security test plan.
- **Principal risks:** cross-module writes, weak constraints, unbounded enumeration, SQL/filter
  injection, stale cache authority, contact leakage, inconsistent source versions, unsafe SSRF.
- **Required negative/failure tests:** direct-constructor invalid states; extra/oversize fields;
  cross-institution query; invalid cursor/filter; SQL/injection-like input; stale cache; concurrent
  supersession; atomic rollback; migration upgrade/downgrade/check; no unverified normal result.
- **Possible separately authorized synthetic scope:** strict immutable contracts and in-memory
  registry mechanics after Gate 1 vocabulary review; no public route, DB, real contacts, or runtime.
- **STOP condition:** schema/API ownership, source truth, authorization, consistency, retention, or
  migration review is unresolved.

## Gate 5 — Referral lifecycle, minimization, idempotency, and external side effects

**Status:** **BLOCKED — NO APPROVED TRANSITIONS, PAYLOAD, OR DESTINATION ADAPTER**

- **As-built evidence:** consent/outbox/job abstractions exist generically; canonical states are
  documented; there is no referral aggregate, table, route, adapter, attempt, webhook, or send.
- **Undecided:** state meanings/transitions/terminal correction, offer expiry, priority authority,
  minimized payload, narrative policy, idempotency identities, transaction/outbox boundary, retry,
  ambiguous send reconciliation, cancel/withdraw races, external confirmation, and status visibility.
- **Accountable reviewers:** referrals/application owner; privacy/consent; clinical/product owner;
  integration/API architecture; security; operations; database/audit owner.
- **Decision artifacts:** reviewed state machine; consent/payload contract; destination contract;
  idempotency and transactional design; attempt/outbox/job model; retry/reconciliation runbook;
  webhook and correction policy; accessible patient status copy.
- **Principal risks:** offer treated as consent, duplicate disclosure, false `SENT`/`COMPLETED`, raw
  transcript leakage, retry after ambiguous effect, cancellation race, spoofed callback.
- **Required negative/failure tests:** every illegal transition; stale version; duplicate create/send/
  webhook; injected state/outbox failure; timeout before/after remote acceptance; revoked consent;
  cancel/late acknowledgement; wrong destination; malformed/spoofed/replayed webhook; partial rollback.
- **Possible separately authorized synthetic scope:** pure nonmedical aggregate/state/idempotency
  contracts with no adapter, contact, patient record, persistence, job, or public API.
- **STOP condition:** any consent, recipient, field, transition, idempotency, side-effect, retry,
  correction, or external evidence rule is unapproved.

## Gate 6 — Notification and webhook privacy, security, retries, and incidents

**Status:** **OPEN — NO CHANNEL, TEMPLATE, PROVIDER, OR WEBHOOK APPROVED**

- **As-built evidence:** notifications is not a registered product module; canonical docs describe a
  replaceable adapter and safe template intent; no provider/channel/message/recipient exists.
- **Undecided:** notification purpose, channels, providers, recipient verification, preferences,
  template/copy/locales, safe variables, timing, retry/deadline, retention, delivery semantics,
  webhook keys/signatures, incident response, fallback, and status correction.
- **Accountable reviewers:** notifications owner; privacy/legal; security; content/localization;
  accessibility; operations; integration owner.
- **Decision artifacts:** approved versioned templates and locale pack; preference/consent contract;
  provider/processor/region terms; webhook signing/replay design; retry/idempotency policy; privacy
  assessment; incident/rollback runbook.
- **Principal risks:** lock-screen health leakage, wrong recipient, link preview leakage, spoof/replay,
  duplicate delivery, retry storms, secret exposure, false referral acknowledgement.
- **Required negative/failure tests:** wrong/withdrawn preference; recipient mismatch; sensitive
  variable; insecure link; invalid/old signature; replay/duplicate; provider timeout/rate limit;
  ambiguous delivery; template/version/locale missing; telemetry canary leakage.
- **Possible separately authorized synthetic scope:** adapter-neutral intent/failure contracts with
  non-sensitive synthetic templates and no delivery, provider dependency, or network.
- **STOP condition:** channel/provider/recipient/copy/privacy/signature/retry/incident decisions are
  absent, or notification state could mutate referral truth.

## Gate 7 — Patient/admin UI, source warnings, copy, and accessibility

**Status:** **BLOCKED — ADMIN PORTAL SPEC MISSING; PATIENT P13 UI UNIMPLEMENTED**

- **As-built evidence:** patient `/referrals` is an honest unavailable state; `/urgent-help` contains
  no verified contacts; admin-web is a foundation shell; `docs/25_ADMIN_PORTAL_SPEC.md` is absent.
- **Undecided:** user journeys, provider/resource fields, source/freshness/limitation warnings,
  consent review, status/correction, moderation/dual-control UI, approved copy/locales, accessibility,
  analytics, link behavior, and safe empty/degraded states.
- **Accountable reviewers:** patient and admin app owners; accessibility; content/localization;
  source governance; privacy/security; clinical safety; product/institution owner.
- **Decision artifacts:** separate Admin Portal spec; approved wireflows/copy; role/permission map;
  source warning patterns; accessibility review; browser privacy/storage design; moderation evidence.
- **Principal risks:** unverified provider presented as endorsed, stale warning hidden, inaccessible
  consent/status, admin privilege abuse, XSS/malicious links, analytics leakage, translated-copy drift.
- **Required negative/failure tests:** loading/empty/stale/expired/revoked/outage; keyboard/screen
  reader/focus; 320/390px reflow; forced colors; malicious text/URL rendered safely; IDOR; no
  browser health/contact persistence; missing locale; unauthorized admin action; no false success.
- **Possible separately authorized synthetic scope:** static unavailable/degraded and synthetic
  source-warning component tests only after the owning UI prompt; no real provider or clinical copy.
- **STOP condition:** `25_ADMIN_PORTAL_SPEC.md`, roles, copy, accessibility, source-warning, privacy,
  or patient/admin authorization evidence is missing.

## Gate 8 — Resilience, verified urgent fallback, incident response, pilot, and release

**Status:** **BLOCKED — NO VERIFIED URGENT FALLBACK OR RELEASE AUTHORIZATION**

- **As-built evidence:** generic urgent-help navigation and P7 manual intake remain independent;
  verified urgent resources are explicitly not configured; no P13 operational service exists.
- **Undecided:** verified fallback source/jurisdiction, offline/cache disclosure, dependency SLOs,
  source incident/removal, monitoring without sensitive data, kill switch, rollback, recovery,
  support/escalation, pilot population/environment, residual risk, expiry/re-review, and release.
- **Accountable reviewers:** clinical safety/resource owner; operations/SRE; security; privacy/legal;
  accessibility/content; product/institution release owner.
- **Decision artifacts:** verified fallback register and maintenance proof; threat/privacy/clinical
  reviews; SLO/capacity and observability plan; incident/source-recall and rollback drills; pilot and
  production decision records with scope, date, expiry, owner, monitoring, and stop criteria.
- **Principal risks:** false promise of urgent help, stale crisis contact, optional-provider outage
  breaking intake, silent failover to unapproved data, unmonitored harm, engineering evidence
  misrepresented as release approval.
- **Required negative/failure tests:** registry/source/provider/DB/job outage; stale cache; revoked
  urgent resource; network partition; deadline/retry exhaustion; kill switch; rollback; canary leak;
  P7/manual and generic urgent navigation remain usable; no fake contact or success.
- **Possible separately authorized synthetic scope:** process-local failure-state and rollback
  mechanics using nonmedical tokens, never a bundled contact or patient-facing route.
- **STOP condition:** verified fallback, source maintenance, incident/rollback, monitoring, pilot, or
  production decision is absent, or fallback depends on optional AI/provider availability.

# 3. Current status and acceptance truth

| Area | Current status |
| --- | --- |
| Proposed Gate 1 | OPEN |
| Proposed Gate 2 | BLOCKED |
| Proposed Gate 3 | OPEN |
| Proposed Gate 4 | OPEN |
| Proposed Gate 5 | BLOCKED |
| Proposed Gate 6 | OPEN |
| Proposed Gate 7 | BLOCKED |
| Proposed Gate 8 | BLOCKED |
| P13-A/B/C/D/E | NOT STARTED |
| `FR-DIR-001..017`, `FR-REF-001..013`, applicable `FR-NOTIF-001..006`, `FR-AUDIT-002..004`, `PRIV-001..009` | LIVE NOT VERIFIED FOR P13 |
| `AC-P13-001..011` | LIVE NOT VERIFIED |

This is a proposed review model, not an established `0/8` approval program. Status labels record
missing decisions only. They do not authorize synthetic engineering work without a separate prompt.

# 4. Future adversarial and failure-test catalogue

Future phase-specific plans must select applicable cases and add exact expected outcomes:

1. direct-constructor invalid/unknown/extra/oversize source, provider, resource, referral, attempt,
   contact, URL, timestamp, state, policy, and version values;
2. forged, missing, future-dated, expired, stale, suspended, revoked, conflicting, and superseded
   source evidence, including clock/UTC and concurrent refresh;
3. unmistakably synthetic record rejected in protected environments and never labeled verified;
4. LLM prompt/output, user text, or imported content attempting to create contacts, specialty,
   urgency, verification, eligibility, ranking, consent, or state authority;
5. malicious URL/redirect, SSRF target, Unicode/control spoof, SQL/filter injection, XSS, oversized
   import, source poisoning, and moderator/admin privilege abuse;
6. wrong actor/session/patient/guardian/institution/recipient/destination, IDOR enumeration, revoked
   role, stale authorization, and cross-institution disclosure;
7. missing/wrong-purpose/expired/withdrawn consent, extra payload fields, raw transcript, bearer,
   unrestricted history, contact or sensitive text in logs/errors/metrics/analytics/browser storage;
8. every illegal referral transition, stale optimistic version, terminal mutation, duplicate create,
   duplicate send, concurrent cancel/withdraw, late acknowledgement, and audited correction;
9. injected persistence/outbox/job/adapter failure at each boundary proving atomic authoritative state
   and honest ambiguous-side-effect handling without exactly-once claims;
10. webhook wrong adapter/key/signature/timestamp/schema/referral/destination, replay, reordering,
    duplicate, late event, and unsupported version;
11. registry, source, provider, database, job, notification, and network outage; deadline and retry
    exhaustion; stale cache; no false success, fake fallback, or safety inference;
12. loading/empty/degraded/stale/revoked states, keyboard/screen-reader/focus, 320/390px reflow,
    forced colors, approved localization/version mismatch, and safe link rendering; and
13. P7 manual intake and generic urgent-help navigation remain independent throughout failures.

# 5. Unsigned human decision and evidence checklist

Roles are accountable categories only. No person, signature, approval ID, or decision is recorded.

- [ ] **Source/provider/resource governance:** sources, rights, jurisdictions, verification proof,
  lifecycle, cadence, correction, appeal, dual control, revocation, and urgent-resource maintenance.
- [ ] **Clinical governance and safety:** taxonomy, mapping, reason codes, ambiguity/abstention,
  exclusions, P9 separation, validation cases, approved copy, and release population.
- [ ] **Identity/security/institution owner:** actors, providers/facilities/institutions, recipient
  binding, permissions, object authorization, moderator/admin controls, MFA, and audit.
- [ ] **Privacy/legal and consent owner:** purpose, notice, sharing scope, minimum fields, mandatory
  explicit active purpose-specific `REFERRAL_SHARING` consent, any additionally applicable lawful or
  governance requirements, patient/guardian/caregiver authority, withdrawal, retention/deletion,
  rights, and processor terms. Additional requirements cannot replace referral consent.
- [ ] **Application/data/API architecture:** module capabilities, models, schema/migration, API/error,
  consistency, concurrency, outbox/jobs, idempotency, webhook, correction, and data ownership.
- [ ] **Notification/integration owner:** destination/provider contracts, channel, template, preference,
  signatures, retries, ambiguous delivery, incident handling, and rollback.
- [ ] **Patient/admin/accessibility/content owners:** complete `25_ADMIN_PORTAL_SPEC.md`; approve flows,
  warnings, copy/locales, accessible states, moderation, browser privacy, and analytics boundaries.
- [ ] **Operations/SRE and release owner:** source/provider health, SLO/capacity, safe telemetry,
  incidents/recall, kill switch, rollback/recovery, pilot scope, monitoring, expiry, and production
  release decision.

Required evidence includes scoped signed decision records; source/license/verification artifacts;
approved policy and copy; reviewed data flow, threat, privacy, clinical-safety, accessibility, and
operational assessments; schema/API/transaction designs; synthetic and real PostgreSQL/security/
failure evidence; pilot monitoring/rollback criteria; and exact-SHA CI for a future implementation.
None is supplied or approved here.

# 6. Preserved cross-phase restrictions

- P8-C patient-facing Stage 3 remains **BLOCKED**: no patient clinical data egress, AI message API,
  candidate promotion, or model-supplied provider truth.
- P9-C patient-facing Stage 3 remains **BLOCKED**: no live safety policy, route, API, persistence, or
  clinical result presentation; directory policy cannot infer a P9 decision.
- P10 live remains **0/9 approved**: no trusted clinician assignment/review/source/summary workflow.
- P11 live remains **0/9 approved (5 OPEN, 4 BLOCKED)** and P11-E remains unimplemented.
- P12 runtime remains **NOT STARTED**; its draft language specification authorizes no translation,
  localized safety copy, speech, provider, or patient data flow.
- P7 deterministic non-diagnostic manual text/touch intake remains available and independent.
- P14 mental-health and P15 self-care cannot bootstrap provider policy, crisis contacts, clinical
  routes, or patient-facing content through P13.

# 7. Decision and next action

This pack approves nothing. The next action is independent review by the accountable roles, creation
of the separate `docs/25_ADMIN_PORTAL_SPEC.md` before relevant P13-E work, and explicit disposition
of the proposed gates. Only after the applicable decisions are recorded may a new, narrowly scoped
prompt consider P13-A synthetic engineering contracts. Do not begin P13-A/B/C/D/E from this draft.
