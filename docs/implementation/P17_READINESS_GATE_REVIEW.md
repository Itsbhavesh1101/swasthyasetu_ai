# SwasthyaSetu AI — P17 Readiness Gate Review

> **DRAFT — PROPOSED ACCOUNTABLE REVIEW INVENTORY, NOT AN OFFICIAL ACCEPTED GATE COUNT OR
> APPROVED P17 FLOW**

**Work unit:** `PRE-P17-ABDM-ABHA-GOVERNANCE-READINESS`

**Baseline:** `main` at `3c727c6015d7e5c4dd8b3a96b0b64796da00eeed`

**Date:** 2026-10-24

**Runtime effect:** None

## 1. Purpose and decision rule

This document prepares review of the unapproved
[ABDM / ABHA Integration Boundary and Governance Specification](../21_ABDM_INTEGRATION_SPEC.md).
It does not establish a formal P17 gate count, appoint a signatory, approve a government protocol,
authorize a sandbox or satisfy AC-P17-001.

Current repository evidence is limited to product identity/consent and clinical foundations, the
unapproved P16 design, generic reliability/security primitives, and empty ABDM/FHIR placeholders.
No official protocol source was independently verified for adoption in this work. P17-A/B/C/D and
P16-A/B/C remain NOT STARTED; all live P16 and P17 outcomes remain NOT VERIFIED.

```text
draft design + PR review + six green CI jobs
  != official protocol currency
  != ABHA identity assurance
  != lawful disclosure or valid consent artifact
  != FHIR/ABDM conformance
  != partner, clinical, security or release approval
```

Statuses below describe missing evidence only. `OPEN` means a decision can be prepared but has not
been accepted. `BLOCKED` means a required predecessor or external authority is absent. Neither is
approval. Missing, ambiguous, expired or disputed evidence fails closed.

## 2. Proposed descriptive review areas

### 2.1 Official protocol, participants and onboarding — BLOCKED

**Accountable roles:** qualified ABDM integration owner; institutional legal-entity/partner owner;
privacy and legal counsel; interoperability architect; security owner; operations owner.

**Actual baseline evidence:** P17 requirements and roadmap exist; dated R2-C research discusses
candidate architecture. No current official source, operating role, onboarding agreement,
credential, sandbox or production destination is verified.

**Missing official authority:** current NHA/ABDM participant and role eligibility; official API and
sandbox source/version/change log; legal-entity eligibility; agreement; support and incident terms;
environment ownership; credential/certificate requirements; deprecation policy.

**Needed decisions/artifacts:** source register with publisher, verified URL, access/publication
dates, exact version and reviewer; approved SwasthyaSetu/institution role; partner agreement;
onboarding record; environment/credential owner; lifecycle and offboarding runbook.

**Relevant requirements:** `FR-ABDM-001..002`, `FR-ABDM-004`, `FR-ABDM-007`;
`AC-P17-001..002`, `AC-P17-004`.

**Negative tests/risks:** unknown role, stale documentation, preview mistaken for published,
wrong environment, expired agreement, unauthorized operation, credential copied between
environments, mock contacting live and unsupported version silently accepted.

**STOP:** no port, flow, endpoint, payload, sandbox or credential work until the current official
source and eligible operating role are independently verified and approved.

### 2.2 ABHA identity and relationship — BLOCKED

**Accountable roles:** identity/authorization owner; institutional records/identity steward;
privacy/legal owners; patient-safety owner; accessibility and assisted-use owner; qualified ABDM
identity reviewer.

**Actual baseline evidence:** P4 pseudonymous sessions, internal actors/patients and server-side
authorization exist. There is no real IdP activation, external identity linkage or ABHA flow.

**Missing official authority:** current identity assurance and lifecycle; supported factors;
patient, guardian, minor and assisted-use eligibility; linkage/unlink/recovery; protected display;
mismatch/collision and relationship rules; institution responsibilities.

**Needed decisions/artifacts:** typed namespace and protected-reference design; assurance matrix;
relationship authorization; source and lifecycle evidence; collision/no-match workflow;
enumeration resistance; unlink/recovery and support procedure; approved accessible copy.

**Relevant requirements:** `FR-ABDM-002`, `FR-ABDM-005`, `FR-ABDM-007`;
`AC-P17-001..002`, `AC-P17-005`.

**Negative tests/risks:** pseudonymous session treated as government identity, guessed external
identifier, wrong patient/guardian/institution, collision, implicit merge, replay, enumeration,
timing disclosure, stale relationship, unauthorized recovery and identifier in URL/log.

**STOP:** no linkage, search, verification, relationship or user journey while official assurance,
eligibility, lifecycle and institutional policies are absent.

### 2.3 Consent and lawful disclosure — BLOCKED

**Accountable roles:** consent owner; privacy officer; qualified legal/DPDP counsel; institutional
data controller; identity/authorization owner; ABDM protocol reviewer; audit owner.

**Actual baseline evidence:** P4 has typed purpose-specific consent and revocation. The
`ABDM_EXCHANGE` enum value is only vocabulary. No official consent artifact or exchange exists.
General product/intake consent is not transitive. P13 referral consent remains independently
mandatory for actual external referral disclosure.

**Missing official authority:** purpose and lawful authority; official consent/grant semantics;
subject, recipient, institution, scope and temporal meaning; notice; withdrawal and in-flight
effects; retention; rights; evidence; product-to-official authorization interaction.

**Needed decisions/artifacts:** approved purpose/consent matrix; legal/privacy assessment; current
official artifact source; notice and accessible copy; minimum-data policy; recipient eligibility;
revocation race design; retention/deletion/legal-hold schedule; disclosure evidence and audit.

**Relevant requirements:** `FR-ABDM-003`, `FR-ABDM-005..007`;
`AC-P17-001`, `AC-P17-003`, `AC-P17-005..007`.

**Negative tests/risks:** intake or referral consent reused; FHIR Consent treated as authorization;
past, expired, revoked, wrong-purpose or wrong-recipient grant; forged artifact; field overreach;
revocation during queue; false deletion; feature flag or identifier treated as consent.

**STOP:** exchange is denied until both product authorization and any separately required official
authorization are current, purpose/recipient specific, independently validated and rechecked at the
side effect.

### 2.4 P16 FHIR validation and clinical/source authority — BLOCKED

**Accountable roles:** interoperability architect; clinical governance and terminology owners;
patient/encounter/document domain owners; provenance owner; conformance reviewer; privacy/security
owners.

**Actual baseline evidence:** draft Spec 20 defines FHIR R4 4.0.1 boundaries. P5 source/provenance
guards and synthetic P11 contracts exist. No mapper, profile package, validator, HAPI sidecar or
approved clinical mapping exists; P11 live access remains blocked.

**Missing official authority:** approved P16 mappings; exact current permitted ABDM implementation
guide/profile and terminology; package license/checksum; clinical source eligibility; uncertainty,
correction and DocumentReference access; independent conformance evidence.

**Needed decisions/artifacts:** approved P16 resource crosswalks; source/version snapshot policy;
pin-selected package manifest; terminology/license record; validator qualification; clinical
negative fixtures; source-access matrix; import-candidate/correction workflow.

**Relevant requirements:** P17 `FR-ABDM-003`, `FR-ABDM-005..006`; `AC-P17-001`,
`AC-P17-003`, `AC-P17-005..006`; all `FR-FHIR-001..011` and `AC-P16-001..010` as prerequisites.

**Negative tests/risks:** parseable but non-conformant artifact, wrong/preview package, mixed
patient, invalid reference, unknown terminology, stale source, inaccessible document, model risk or
unconfirmed extraction promoted to diagnosis, and lower-trust import overwriting confirmed fact.

**STOP:** P16 live acceptance is unverified. No ABDM clinical artifact, Bundle or import may be
created or trusted until applicable P16, P11 and clinical/source decisions close.

### 2.5 Adapter, partner and network security — BLOCKED

**Accountable roles:** security architect; application-security owner; identity/IAM owner;
network/platform owner; partner owner; interoperability architect; privacy officer; SRE/incident
owner.

**Actual baseline evidence:** typed adapter conventions, generic privacy-safe observability and
configuration foundations exist. ABDM adapter, partner, endpoint, route, callback, secret and
network path do not exist.

**Missing official authority:** authentication/token/certificate rules; credential custody and
rotation; approved destinations and operations; egress/DNS/IP/redirect policy; callback validation;
least privilege; payload/deadline limits; penetration evidence; partner incident obligations.

**Needed decisions/artifacts:** threat model and data-flow diagram; endpoint registry; SSRF/egress
design; authentication profile; secret/key runbook; callback verification based on official
evidence; error/logging review; penetration report; incident disable/rotation/notification plan.

**Relevant requirements:** `FR-ABDM-001..002`, `FR-ABDM-005`, `FR-ABDM-007`;
`AC-P17-002`, `AC-P17-005`, `AC-P17-007`.

**Negative tests/risks:** loopback/link-local/metadata/private target, DNS rebinding, redirect
escape, token leakage, replayed callback, wrong partner, over-privileged credential, malformed or
oversized response, timeout, downgrade, public admin surface and PHI in observability.

**STOP:** no external traffic or callback until partner/destination, authentication, credential,
least-privilege, SSRF, logging and incident controls are approved and independently tested.

### 2.6 Synthetic mock, sandbox and conformance — BLOCKED

**Accountable roles:** qualified ABDM integrator; interoperability/conformance owner; quality owner;
security/privacy owners; legal/terms reviewer; test-data owner; institutional sandbox sponsor.

**Actual baseline evidence:** no ABDM mock, fixture, package or sandbox exists. The repository has
generic adapter test patterns only. Historical research cannot establish current conformance.

**Missing official authority:** approved offline-mock scope; unmistakably synthetic fixture policy;
current official sandbox access/terms; endpoint and credential owner; permitted test data/region;
published IG/profile/version/license; conformance oracle and evidence retention.

**Needed decisions/artifacts:** zero-egress mock contract; synthetic data manifest; current source
record; package manifest; sandbox onboarding; environment-isolation proof; golden/negative suite;
reproducible evidence report and explicit non-production disclaimer.

**Relevant requirements:** `FR-ABDM-002`, `FR-ABDM-004`, `FR-ABDM-007`;
`AC-P17-001..004`, `AC-P17-007`.

**Negative tests/risks:** realistic identifier, patient data in fixture, network egress from mock,
mock selected in live mode, sandbox credential in repository, profile drift, parser-only success
claimed as conformance, sandbox claimed as production certification.

**STOP:** no mock or sandbox work under this documentation phase. A separate prompt may authorize a
bounded offline synthetic subset only after architecture/privacy/security review; sandbox additionally
requires official onboarding and source verification.

### 2.7 Transaction consistency, provenance and resilience — OPEN, NOT APPROVED

**Accountable roles:** application/data architect; interoperability owner; consent owner;
provenance/audit owners; security owner; SRE/incident owner; clinical domain owners.

**Actual baseline evidence:** PostgreSQL transactions, transactional outbox, idempotency concepts,
typed errors and provenance primitives exist. They are not wired to ABDM and establish no official
operation semantics.

**Missing decisions:** safe/retriable operations; remote receipt meaning; idempotency scope;
callback ordering; ambiguous timeout; consent revoked during send; source drift; atomic local
evidence; reconciliation; import correction; audit/retention and disaster recovery.

**Needed decisions/artifacts:** official operation matrix; state machine; idempotency/correlation
contract; outbox/evidence design; callback replay/order policy; reconciliation runbook; provenance
schema; consent/source recheck; failure/degraded-mode and no-data-loss proof.

**Relevant requirements:** `FR-ABDM-001`, `FR-ABDM-003`, `FR-ABDM-005..007`;
`AC-P17-002..003`, `AC-P17-005..007`.

**Negative tests/risks:** duplicate or late callback, idempotency collision, partial transfer,
remote commit after timeout, unsafe retry, revocation or source correction during queue, missing
provenance, false success, local rollback erasing valid intake and audit/event inconsistency.

**STOP:** generic primitives cannot be treated as P17 evidence. No state machine or retry policy is
implemented until official supported-operation semantics and accountable decisions exist.

### 2.8 Patient UX, operations and release — BLOCKED

**Accountable roles:** product owner; patient identity/support owner; privacy/legal and consent
owners; accessibility and qualified language reviewers; clinical safety owner; P21 governance
owner; partner/institution owner; SRE/incident and pilot/production release authorities.

**Actual baseline evidence:** accessible P6/P7 shell and generic unavailable states exist. There is
no ABDM screen, approved copy/translation, support workflow, P21 maker-checker runtime, pilot or
production decision.

**Missing decisions/evidence:** opt-in journey and verified copy; translated equivalence; identity
mismatch/support; kiosk/guardian/assisted use; accessibility; status truth; administrative
separation; partner support; monitoring without PHI; breach/incident/rollback; pilot population,
stop rules and production sign-off.

**Needed decisions/artifacts:** approved user journey/copy and language matrix; accessibility and
usability report; support/escalation runbook; P21 maker-checker/credential governance; operational
SLIs and privacy-safe telemetry; incident drill; bounded pilot protocol; separate production record.

**Relevant requirements:** `FR-ABDM-002..005`, `FR-ABDM-007`;
`AC-P17-001`, `AC-P17-003..005`, `AC-P17-007`.

**Negative tests/risks:** false success/identity assurance, inaccessible consent/error, unsafe
translation, kiosk leakage, no cancellation, hidden pending state, provider outage removing P7,
self-approval, audit bypass, pilot treated as production and support disclosure to wrong subject.

**STOP:** no patient UI, admin control, pilot or production activation until official flows,
identity/consent, accessibility/language, P21 governance, operations and release decisions close.

## 3. P17 requirement and acceptance crosswalk

Every live status is **NOT VERIFIED**.

| Canonical requirement                                                                              | Review areas | Missing decision/evidence                                                         |
| -------------------------------------------------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------- |
| FR-ABDM-001 — ABDM integration SHALL be isolated behind an integration layer.                      | 1, 5, 7      | Approved role and architecture; typed port/adapter and boundary tests             |
| FR-ABDM-002 — The product SHALL support ABHA-related flows when enabled and technically available. | 1, 2, 6, 8   | Current official flow, eligible actors, safe configuration, UX and implementation |
| FR-ABDM-003 — ABDM data exchange SHALL respect applicable consent.                                 | 3, 4, 7, 8   | Approved product/official consent interaction and end-to-end enforcement          |
| FR-ABDM-004 — Development SHALL support ABDM sandbox/test workflows before production integration. | 1, 6         | Approved offline mock; official sandbox onboarding and reproducible evidence      |
| FR-ABDM-005 — ABDM failure SHALL not destroy locally valid patient intake data.                    | 4, 5, 7, 8   | Failure-isolation, transaction/reconciliation and P7 regression proof             |
| FR-ABDM-006 — Imported records SHALL retain source metadata.                                       | 4, 7         | Non-authoritative import contract and complete source/version/correction evidence |
| FR-ABDM-007 — ABDM integration SHALL be feature/configuration controlled.                          | 1, 5, 6, 8   | Approved safe-off environment/configuration and mock/live isolation               |

| Canonical acceptance criterion                                                          | Review areas | Why LIVE NOT VERIFIED                                                   |
| --------------------------------------------------------------------------------------- | ------------ | ----------------------------------------------------------------------- |
| AC-P17-001 — Approved ABDM integration specification exists before real implementation. | 1–8          | Spec 21 is an unapproved draft; official and human decisions are absent |
| AC-P17-002 — ABDM access occurs through adapter.                                        | 1, 5, 7      | Only placeholders exist                                                 |
| AC-P17-003 — Consent-aware exchange is enforced.                                        | 3, 4, 7      | No approved consent semantics or exchange implementation exists         |
| AC-P17-004 — Sandbox/mock path exists.                                                  | 6            | Neither offline mock nor approved sandbox exists                        |
| AC-P17-005 — ABDM failure does not destroy valid local clinical data.                   | 4, 7, 8      | No P17 failure-injection evidence exists                                |
| AC-P17-006 — Import/export provenance is retained.                                      | 4, 7         | Provenance primitives exist, not end-to-end P17 evidence                |
| AC-P17-007 — Retries/idempotency are tested for supported operations.                   | 5–7          | Supported official operations and P17 tests are absent                  |

## 4. P16 prerequisite STOP

All `FR-FHIR-001..011` and `AC-P16-001..010` remain live NOT VERIFIED. Spec 20 and the P16
readiness inventory are unapproved designs; P16-A/B/C are NOT STARTED. No selected ABDM profile,
FHIR mapper, validator, HAPI sidecar, source-backed clinical crosswalk or import/export API exists.

Consequently, no P17 clinical artifact, FHIR Bundle, document reference or inbound resource can be
produced, validated, sent or accepted. P16 technical completion would itself remain insufficient
without P17 identity, consent, official-protocol, partner, security and release decisions.

## 5. Owner and risk register

Role labels do not appoint a person or grant authority.

| Decision/risk                                   | Accountable roles                                            | Status             | Required recorded decision                                             |
| ----------------------------------------------- | ------------------------------------------------------------ | ------------------ | ---------------------------------------------------------------------- |
| Official protocol currency and participant role | ABDM program owner; institutional legal/partner owner        | BLOCKED            | Current official source/version, eligible role and agreement           |
| External identity and relationship              | IAM owner; records steward; privacy/legal; patient support   | BLOCKED            | Assurance, linkage, guardian/assisted, collision and unlink policy     |
| Consent/lawful disclosure                       | Consent owner; privacy officer; legal counsel; controller    | BLOCKED            | Exact purpose, dual authorization, recipient, revocation and retention |
| P16 mapping/conformance                         | Interoperability; clinical/terminology; conformance reviewer | BLOCKED            | Approved P16 plus current pin-selected profile and validator evidence  |
| Partner/network/credential security             | Security; network/platform; IAM; partner; incident owner     | BLOCKED            | Endpoint/auth/secret/SSRF/callback/incident approval                   |
| Mock/sandbox and test data                      | QA; ABDM integrator; privacy/security; sandbox sponsor       | BLOCKED            | Zero-egress fixture scope and official sandbox onboarding              |
| Transaction and provenance semantics            | Architecture/data; consent; audit/provenance; SRE            | OPEN, NOT APPROVED | Operation-specific retry, state, evidence and reconciliation design    |
| UX/accessibility/language/support               | Product; accessibility/language; privacy; patient support    | BLOCKED            | Reviewed journeys, copy, errors, support and status semantics          |
| Administration and release                      | P21 governance; institution; operations; release authority   | BLOCKED            | Maker-checker, pilot, stop rules and separate production sign-off      |

## 6. Unsigned bounded decision and evidence template

```text
Decision record ID:
Bounded scope, population, institution and operating role:
Official publisher, source URL, access date and publication/effective date:
Protocol/API/IG/profile/terminology exact version and checksum:
Source currency and supersession review:
Review decision: APPROVE BOUNDED SCOPE | REJECT | REQUEST CHANGES | DEFER
Exact purpose and product consent/authority mechanism:
Official exchange authorization mechanism, if separately required:
Approved recipient, destination and permitted operations:
Identity/guardian/assisted relationship and assurance:
Mock or sandbox environment, region and credential owner:
PHI/test-data, minimization, telemetry and support policy:
Retention, deletion, legal hold and breach/incident duties:
Excluded flows, populations, data and operations:
Verification, negative-test and independent conformance evidence:
Rollback, disconnection, reconciliation and expiry/re-review date:
Accountable role(s):
Named authorized reviewer(s): PENDING
Signatures and external decision references: PENDING
```

Repository authorship, PR approval and CI may be evidence that documentation checks passed; they do
not populate or approve this template.

## 7. Preserved governance and next action

- P7 manual intake and generic urgent help remain independent and unchanged.
- P8-C/P9-C patient-facing Stage 3 remain BLOCKED.
- P10/P11 live approval remains 0/9; P11 draft security/privacy material is not platform approval.
- P12, P13, P14, P15, P16, P17 and P21 runtime remain NOT STARTED.
- P13 `REFERRAL_SHARING` remains mandatory for actual referral disclosure and is not universal ABDM
  consent.
- P15 clinical/readiness STOP remains intact.
- No official version, endpoint, role, identity factor, profile, flow, credential, sandbox, payload,
  patient data, legal conclusion, clinical mapping, feature flag or production decision is adopted.

**Next accountable action:** the unassigned roles must independently verify current official
sources, establish institutional/participant eligibility, and record bounded decisions using the
unsigned template. If and only if an approved Spec 21 and P16 prerequisites exist, a new prompt may
scope P17-A. Otherwise P17 remains stopped.

**STOP:** this branch ends with documentation review preparation. Do not begin P17-A/B/C/D,
P16-A/B/C, external browsing that changes state, source/package acquisition, sandbox probing,
credential provisioning, callback/API work, patient flows or live data exchange.
