# SwasthyaSetu AI

## 21 — ABDM / ABHA Integration Boundary and Governance Specification

> **DRAFT — PRE-P17 ARCHITECTURE / ACCOUNTABLE REVIEW ONLY; NOT AN APPROVED ABDM
> SPECIFICATION, CURRENT OFFICIAL API CONTRACT, ABHA LINKAGE FLOW, CONSENT MANAGER INTEGRATION,
> SANDBOX OR LIVE DATA EXCHANGE.**

**Document ID:** `SSAI-SPEC-021-DRAFT`

**Baseline:** `main` at `3c727c6015d7e5c4dd8b3a96b0b64796da00eeed`

**Date:** 2026-10-24

**Status:** Unapproved Pre-P17 governance and architecture proposal

**Runtime effect:** None

Accountable authorities remain unassigned roles: ABDM program/integration owner, institutional
legal entity and data controller, privacy/legal and consent owners, identity and authorization
owner, clinical governance and terminology owners, interoperability architect, security architect,
partner owner, accessibility/language owner, operations/incident owner, and pilot/production
release authority. No person is appointed and no approval is recorded by this document.

## 1. Product scope, dependency boundary, and current truth

### 1.1 Source hierarchy and evidence record

This draft is subordinate to approved clinical/safety policy and the canonical
[Project Master Specification](00_PROJECT_MASTER_SPEC.md),
[System Architecture](02_SYSTEM_ARCHITECTURE.md),
[Product Requirements](01_PRODUCT_REQUIREMENTS.md),
[Privacy and Consent Specification](26_PRIVACY_CONSENT_SPEC.md),
[Clinical Provenance Specification](12_CLINICAL_PROVENANCE_SPEC.md), accepted decisions in the
[Decision Log](implementation/37_DECISION_LOG.md), and the
[Master Implementation Plan](34_MASTER_IMPLEMENTATION_PLAN.md). The draft
[FHIR R4 Mapping Specification](20_FHIR_MAPPING_SPEC.md) and
[P16 readiness review](implementation/P16_READINESS_GATE_REVIEW.md) are prerequisites but grant no
P16 or P17 runtime authority. R3 decisions outrank dated R2-C research.

Repository evidence was inspected at the baseline SHA on 2026-10-24. External official ABDM
sources were not independently verified or reviewer-approved in this work; no URL, current protocol
version, endpoint, profile package, role eligibility, certificate, scope, token, callback, rate
limit, consent artifact, or mandatory demographic is adopted here.

### 1.2 As-built versus conditional future state

| Area         | As built at the baseline                                                                                                        | Conditional future state; not approved                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Core product | P4 pseudonymous sessions/consent, P5 patients/encounters/provenance and P7 manual text/touch intake work within existing bounds | Optional ABDM capability must not become a prerequisite for local intake, current records or generic urgent help         |
| Identity     | Internal actor/session/patient identifiers exist; no verified government identity integration exists                            | Protected external-identifier linkage may be considered only after official, legal, identity and institutional decisions |
| FHIR         | Spec 20 is an unapproved draft; mapper, validator, profile and HAPI sidecar are absent                                          | Independently approved P16 mappings and validation must precede any ABDM clinical artifact                               |
| ABDM         | Module/adapter directories are placeholders; Spec 21, provider, routes, callbacks, sandbox and credentials are absent           | P17-A/B/C/D are separately gated future work                                                                             |
| Consent      | Product consent records include typed purposes; no official exchange artifact handling exists                                   | Platform authorization and any official exchange authorization remain separate, jointly reviewed controls                |
| Documents    | Synthetic P11 contracts exist; live storage/source access remains blocked                                                       | DocumentReference or report exchange requires closed P11 and P16 source-access gates                                     |
| Operations   | Generic errors, outbox, feature and audit foundations exist                                                                     | External transaction, credential, callback, reconciliation and incident controls need explicit approval                  |

### 1.3 Scope and non-blocking fallback

ABDM/ABHA is an optional adapter-based integration after independently verified P16 FHIR R4
mapping and validation. It need not block core product progress. P7 manual text/touch intake,
authorized local patient records and generic urgent help must continue when ABDM is disabled,
absent, unreachable, degraded or revoked.

P4 product/session identity, internal patient identity and an external ABHA identifier are distinct
namespaces and trust claims. They are never interchangeable. Potential patient, guardian,
assisted-use, institution, authorized-staff, partner, health-data custodian/recipient and consent
authority contexts require separate eligibility decisions. This draft does not claim SwasthyaSetu
has been admitted to any operational role.

P17-A approved-flow interfaces, P17-B sandbox adapter, P17-C synchronization/use cases and P17-D
failure/security/audit evidence are all **NOT STARTED**.

## 2. Official authority and source inventory

The following inventory names source classes a qualified integrator must later verify. URLs are
intentionally absent because none was independently checked and approved in this work. Every row is
**UNVERIFIED / HUMAN DECISION PENDING**.

| Required authoritative source                                         | Required future verification evidence                                                                                             | Current evidence date/version                                             | Accountable roles                                                  |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Current ABDM/NHA onboarding and participant-role rules                | Official publisher, URL, publication/update date, version, eligible legal entity and operating agreement                          | None verified as of 2026-10-24                                            | ABDM program owner; institutional legal/partner owner              |
| Current API and sandbox reference plus change logs                    | Official source, exact release, environment ownership, supported operations and deprecation lifecycle                             | Historical R2-C suggestions only; not current authority                   | Qualified ABDM integrator; interoperability architect              |
| Current ABHA lifecycle and supported identity/authentication factors  | Official versioned rules for creation/linkage/verification, guardian or assisted paths, unlink/recovery and assurance levels      | None verified                                                             | Identity owner; privacy/legal; institutional records owner         |
| Current health-information exchange and consent-manager specification | Official roles, purpose/scope/recipient/time semantics, revocation, discovery and transfer evidence                               | None verified                                                             | Consent owner; privacy/legal; ABDM integrator                      |
| Current published ABDM FHIR R4 implementation guide and package       | Published versus preview status, exact package/version/checksum, source, license, terminology dependencies and FHIR compatibility | A historical line is mentioned in R2-C; currency is explicitly unverified | Standards/conformance reviewer; terminology and licensing owners   |
| Applicable DPDP and healthcare privacy/legal obligations              | Jurisdiction, controller/processor roles, lawful authority, notice, minimization, retention, rights and breach duties             | Repository policy only; external legal determination absent               | Privacy officer; qualified legal counsel; institutional controller |
| Current operational support, security and incident requirements       | Credential/certificate ownership, service levels, support channel, incident and partner-notification obligations                  | None verified                                                             | Security, SRE/incident, partner and release owners                 |

No historical research statement becomes a current official protocol claim. A future source record
must preserve publisher, URL, retrieval date, publication/effective date, version, checksum where
applicable, reviewer, decision scope, expiry/re-review date and supersession history.

## 3. Bounded role and process inventory

This is a non-executable capability inventory. It deliberately avoids prescribing a government
step order, live endpoint, payload or user journey.

| Conditional capability                                | Status and owner roles                                                              | Preconditions and external evidence                                                              | Authorization/minimum disclosure                                                                           | Failure/idempotency boundary                                                                                  |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Enrollment/onboarding/configuration                   | **NOT IMPLEMENTED**; institutional/partner, legal, security and ABDM program owners | Official participant eligibility, agreements, approved environment and credential custody        | Administrative least privilege; no patient data required for configuration unless explicitly justified     | Failed onboarding cannot activate runtime; configuration is versioned, reviewable and reversible              |
| Optional external-identifier linkage/verification     | **NOT IMPLEMENTED**; identity, privacy/legal and institutional records owners       | Official identity lifecycle and assurance rules; supported patient/guardian/assisted eligibility | Fresh actor, subject and institution authority; disclose only protocol-required identity fields            | Owner-scoped replay protection; mismatch/collision stops without merge or existence leakage                   |
| Patient-initiated consent and grant handling          | **NOT IMPLEMENTED**; consent, privacy/legal and qualified ABDM owners               | Current official consent semantics and lawful-purpose decision                                   | Product consent and external artifact evaluated separately; exact purpose, scope, recipient and time bound | Duplicate, expired, revoked, late or contradictory artifacts fail closed and reconcile explicitly             |
| Purpose-limited health-information discovery/transfer | **NOT IMPLEMENTED**; interoperability, data-owner, privacy and partner owners       | Approved P16 projection, official participant role, recipient and protocol version               | Minimum authorized snapshot only; fresh object/institution/field authorization before side effect          | Idempotency binds source versions, purpose, recipient and operation; partial outcome is not success           |
| Status acknowledgement                                | **NOT IMPLEMENTED**; adapter and operations owners                                  | Official status vocabulary and delivery semantics                                                | Bounded technical metadata only; remote receipt is neither clinical acceptance nor consent validity        | Duplicate/late/out-of-order status is recorded without unsafe state regression                                |
| Revocation and disconnection                          | **NOT IMPLEMENTED**; consent, identity, privacy and operations owners               | Official propagation and lifecycle rules plus local legal retention decision                     | Fresh authorized request; no universal deletion or recall claim                                            | Stop queued side effects where possible; preserve lawful evidence and expose unresolved remote state honestly |
| Reconciliation                                        | **NOT IMPLEMENTED**; data/provenance, clinical governance and operations owners     | Official source identifiers/version semantics and approved mismatch procedure                    | Authorized minimum metadata; no direct authoritative overwrite                                             | Conflicts, ambiguity and missing provenance quarantine or reject; no automatic patient merge                  |

No QR, identity-factor, demographic-match, consent-manager, custodian/recipient or provider flow is
asserted. All patient-facing copy and journeys require an approved official source plus privacy,
accessibility, language and usability review.

## 4. Typed adapter separation and trust graph

### 4.1 Ownership and separation

A future project-owned `ABDMProvider` or narrower transport port belongs to
`interoperability.abdm` and remains subordinate to application authorization. It must not absorb or
replace:

- `FHIRMapper`, which would project approved internal snapshots;
- `FHIRValidationPort`, which would report structural/profile/terminology issues;
- optional `FHIRRepositoryPort`, which could hold a replaceable projection only;
- `FHIRRemoteClientPort`, which represents generic partner FHIR transport;
- `FHIRGatewayService`, which would orchestrate authorized mapping/validation;
- the consent module, identity/authorization services, clinical domain owners or audit owner.

All these names remain proposed design sketches where not already accepted. No executable API,
route, external payload or provider dependency is established.

### 4.2 Proposed internal envelope

```text
request_id and correlation_id
operation and internal_schema_version
official_protocol_reference and verified_version
actor_reference and institution_scope
internal_subject_reference
external_identifier_protected_reference
purpose and authorization_decision_reference
consent_artifact_protected_reference and version
source_object_references and versions
allowed_recipient_reference
issued_at_utc and expires_at_utc
idempotency_reference
bounded_status and normalized_error
auditable_outcome_reference
```

Every field is bounded, typed and minimum necessary. An external identifier, credential, token,
consent artifact or clinical payload never appears in a general log, metric, trace, error, browser
URL or support-console field. A protected reference does not grant access to the protected value.

### 4.3 Trust graph

```text
trusted principal
 -> current actor role and institution
 -> patient, encounter, object and field authorization
 -> exact purpose and eligible recipient
 -> product consent/authority decision
 -> separately validated official exchange artifact when required
 -> source-version snapshot
 -> approved P16 mapping and profile validation
 -> approved ABDM adapter and pinned destination
 -> atomic local evidence, audit and reconciliation
```

No edge is inferred from possession of a session, identifier, FHIR resource, feature flag, prior
grant or remote receipt. Every side-effect edge is revalidated immediately before execution and
after an asynchronous delay.

## 5. Identity, linkage, relationship and collision boundaries

A typed external identifier is not proof of identity. Future linkage requires independently
verified principal, object and institution scope; official patient/guardian/assisted eligibility;
verified ownership; explicit purpose; protected display; source attribution; replay prevention;
and reviewed lifecycle, unlink, recovery and revocation semantics.

The design must:

- keep external and internal identifiers in different typed namespaces;
- never generate, guess or use a sample ABHA identifier resembling a real person;
- never substitute a pseudonymous P4 session for verified government identity, or the reverse;
- deny implicit patient merges and route mismatch/collision to approved protected review;
- prevent enumeration or existence disclosure through search, status, timing, logs or metadata;
- bind linkage evidence to actor, relationship, institution, protocol/source version and time;
- use protected references rather than identifiers in URLs and general observability;
- re-check relationship authority at each use, not merely at initial linkage.

Supported minors, guardians, assisted use, incapacity, recovery and delegation remain pending
official, legal and institutional review. No pathway is assumed from model memory.

## 6. Consent, authorization and lawful exchange

`GENERAL_PRODUCT_USE` with `clinical_intake` scope is not transitive to ABDM. The typed
`ABDM_EXCHANGE` purpose in current code is a vocabulary value, not an approved notice, official
artifact, lawful basis, patient grant or implementation. Platform purpose-specific consent and any
future official consent-manager or exchange authorization are distinct controls whose semantics,
scope, subject, recipient, institution, temporal validity, revocation and interaction require
accountable legal/privacy and official-protocol review.

Possession of a FHIR Consent resource, session token, external-identifier-like value, past grant or
generic feature flag never authorizes exchange. Each send or fetch requires:

1. a trusted authenticated principal and current relationship;
2. patient, encounter, object, field and institution authorization;
3. an exact approved purpose and recipient;
4. minimum necessary source fields and current source access;
5. valid active purpose-specific product consent or other specifically reviewed applicable
   authority where lawful;
6. any separately required valid official exchange authorization;
7. revalidation before the external side effect and after any queue delay;
8. immutable evidence and privacy-safe audit of the decision and result.

`REFERRAL_SHARING` consent is mandatory for actual external referral disclosure under the P13
policy. It does not automatically authorize unrelated ABDM exchange and must never be weakened or
treated as universal exchange consent.

Withdrawal and expiry stop new queued side effects where technically possible. Whether and how a
remote disclosure can be recalled, retained or deleted is an official/legal/partner decision; the
product must not claim deletion it cannot prove.

## 7. FHIR projection, source authority, and provenance

PostgreSQL and the P5/P7 owning modules remain authoritative. FHIR R4 4.0.1 is the accepted
architectural baseline, but P16 has no live mapper, selected profile, validator or sidecar. An ABDM
artifact may derive only from approved, source-verifiable P16 mappings and an independently
validated, pin-selected and permitted official implementation-guide/profile version.

The following cannot automatically become clinician-confirmed Observation, Condition,
prescription, diagnosis or clinical document:

- P8 unconfirmed extraction candidates;
- P9 safety routes or reason codes;
- ML risk scores;
- free-text symptoms or raw chat;
- raw model responses or OCR text;
- merely parseable FHIR resources.

P11 DocumentReference or DiagnosticReport use requires purpose authorization, verified source and
document access, lifecycle/retention approval and closed P11 live gates. A reference is not
permission to open or share a binary.

Inbound resources become non-authoritative import candidates. They retain sender, recipient,
source system, resource/version, mapping/profile/protocol versions, receipt time, original trust
state, uncertainty and correction history. Patient matching, deduplication and clinical review are
mandatory under future approved policy; no automatic overwrite, merge or trust promotion occurs.
Missing, unknown and contradictory values remain explicit rather than becoming false completeness.

## 8. Environment taxonomy and authority separation

The following is only a proposed taxonomy; no feature flag or environment is deployed:

| Mode                     | Proposed meaning                                                                 | Data and network boundary                                                         | Authority boundary                                                                              |
| ------------------------ | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `DISABLED`               | No ABDM capability selectable                                                    | No external traffic or identifier handling                                        | Required default until separately approved                                                      |
| `SYNTHETIC_OFFLINE_MOCK` | Deterministic contract testing with conspicuously fake, non-identifying fixtures | Zero external traffic; no realistic identifiers, credentials or patient data      | Engineering evidence only, under a separate prompt                                              |
| `APPROVED_SANDBOX`       | Qualified integration against an officially verified non-production environment  | Approved synthetic/test policy, credentials, region, endpoint, packages and owner | Requires onboarding, terms, security/privacy and conformance decisions; not production approval |
| `PILOT`                  | Bounded institution/population/time deployment                                   | Explicit data, monitoring, support and stop rules                                 | Separate clinical/privacy/security/partner/legal and institutional release record               |
| `PRODUCTION`             | Approved live operation                                                          | Production credentials, destinations, retention and incident controls             | Separate accountable production authorization and recurring review                              |

A sandbox result does not confer production authorization or certification. This draft neither
creates demo tokens nor installs packages, probes endpoints, provisions environments or claims
compliance.

## 9. Transport, callbacks, state and failure semantics

Any future authorized adapter requires:

- pinned destination ownership and allowed operations;
- TLS and verified authentication with least-privilege credentials and rotation;
- egress, IP/DNS and redirect allowlisting plus SSRF and rebinding defenses;
- bounded connection/read/overall deadlines and payload limits;
- bounded exponential retry only for officially documented safe/idempotent operations;
- correlation, owner-scoped idempotency, outbox/evidence and explicit reconciliation;
- duplicate, late, out-of-order and partial callback handling;
- webhook signature, replay and time validation using an algorithm selected only from verified
  official evidence;
- atomic local evidence for intent/result without pretending remote atomicity;
- honest pending, failed, uncertain and reconciliation-required states;
- withdrawal propagation where technically and legally permitted and provable.

Remote receipt does not equal clinical acceptance, authorization, consent validity or final
delivery. Non-idempotent mutations are not blindly retried. An ambiguous timeout remains unknown
until reconciliation. A callback never directly mutates clinical truth and cannot regress a final
state without reviewed semantics.

No callback route or URL is implemented here. Raw clinical payloads, identifiers and tokens are
excluded from errors, general logs, metrics, traces, CI, retry records and support consoles.
Storage, retention, legal hold, deletion and backup remain unapproved decisions.

## 10. Security, accessibility and incident posture

### 10.1 Proposed future negative tests

- forged or stolen external identity/session reference;
- wrong patient, institution, guardian, relationship or tenant;
- identity mismatch, collision, enumeration and timing disclosure;
- replayed, expired, revoked, wrong-purpose or insufficient-scope consent;
- unauthorized patient discovery, wrong recipient or excessive fields;
- ambiguous export source, stale versions or missing provenance;
- unconfirmed fact, model risk or raw model output promoted to clinical truth;
- manipulated FHIR payload, mixed patient, invalid reference or unpinned package;
- replayed callback, duplicate receipt, out-of-order status and partial success;
- retry after consent revocation or authorization change;
- SSRF, redirect escape, DNS rebinding, token leakage and over-privileged credentials;
- lost network, validator/HAPI/ABDM outage and ambiguous remote commit;
- offline mock contacting a live destination or using realistic identifiers;
- downgrade to anonymous, no-consent or unvalidated operation;
- optional integration failure blocking P7 intake or generic urgent help.

These are proposed future tests, not current compliance evidence.

### 10.2 Patient experience and accessibility

Any future patient-facing ABDM state is opt-in, honest and reversible where policy permits. It must
distinguish unavailable, pending, failed, declined, expired, revoked, mismatch and reconciliation
states without false success or assurance. Mobile/kiosk use, keyboard access, focus, screen-reader
announcements, reflow and non-color-only status require testing. Translated identity, consent and
error copy needs qualified source, privacy, language, accessibility and usability review. Generic
urgent help and manual intake remain independently reachable.

### 10.3 Incidents and rollback

Human decisions must assign credential compromise, privacy breach, partner notification, patient
support, unsafe data, remote outage, feature disable, reconciliation, evidence retention and
recovery responsibilities. Rollback can disable a version or destination; it cannot claim to recall
previous disclosures. Pilot and production each require separate stop rules and release records.

## 11. FR-ABDM traceability

Every row is **LIVE NOT VERIFIED**. This unapproved draft does not satisfy live requirements.

| ID          | Exact canonical wording                                                              | Sections     | Current implementation evidence                   | Required official/human decision                                                                   | Required future technical artifact                                                        |
| ----------- | ------------------------------------------------------------------------------------ | ------------ | ------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| FR-ABDM-001 | ABDM integration SHALL be isolated behind an integration layer.                      | §§4, 9       | ABDM module/adapter placeholders only             | Architecture, official participant role and trust-boundary approval                                | P17-A typed port, dependency tests and qualified adapter contracts                        |
| FR-ABDM-002 | The product SHALL support ABHA-related flows when enabled and technically available. | §§1, 3, 5, 8 | No ABHA linkage or official flow                  | Current official flow, eligible roles, identity assurance, UX and institution approval             | Separately approved P17-A/C use cases and identity/linkage tests                          |
| FR-ABDM-003 | ABDM data exchange SHALL respect applicable consent.                                 | §6           | P4 consent primitives only; no official artifact  | Purpose, lawful authority, product/official consent interaction, recipient and revocation decision | Authorization/consent enforcement with race, expiry and revocation tests                  |
| FR-ABDM-004 | Development SHALL support ABDM sandbox/test workflows before production integration. | §§2, 8       | No sandbox/mock path                              | Official sandbox source, onboarding, terms, credentials, data and profile decision                 | P17-B offline mock then approved sandbox adapter/evidence; no production inference        |
| FR-ABDM-005 | ABDM failure SHALL not destroy locally valid patient intake data.                    | §§1, 9–10    | P7 local intake exists; no ABDM integration       | Degraded-mode, incident, reconciliation and support approval                                       | P17-D outage/partial/rollback tests proving local data and P7 remain intact               |
| FR-ABDM-006 | Imported records SHALL retain source metadata.                                       | §7           | P5 provenance supports `ABDM_IMPORT`; no importer | Trusted source, identity match, import-review and correction policy                                | Non-authoritative import candidate, provenance and no-overwrite tests                     |
| FR-ABDM-007 | ABDM integration SHALL be feature/configuration controlled.                          | §8           | Generic safe/off feature foundation; no ABDM flag | Environment taxonomy, role access, startup validation and release approval                         | Explicit phase-scoped configuration with safe-off, mock/live isolation and rollback tests |

## 12. AC-P17 traceability

Every row is **LIVE NOT VERIFIED**. In particular, this unapproved draft does **not** satisfy
AC-P17-001, which requires an approved specification.

| ID         | Exact canonical wording                                                    | Sections  | Current evidence                       | Required future evidence                                                                    |
| ---------- | -------------------------------------------------------------------------- | --------- | -------------------------------------- | ------------------------------------------------------------------------------------------- |
| AC-P17-001 | Approved ABDM integration specification exists before real implementation. | §§1–13    | This document is an unapproved draft   | Accountable approval of a source-verified revision with bounded scope and signatures        |
| AC-P17-002 | ABDM access occurs through adapter.                                        | §§4, 9    | Placeholder only                       | Implemented P17 adapter/port, module-boundary and provider-leakage tests                    |
| AC-P17-003 | Consent-aware exchange is enforced.                                        | §6        | No exchange                            | Approved consent semantics plus fresh authorization, revocation/race and minimization tests |
| AC-P17-004 | Sandbox/mock path exists.                                                  | §8        | No ABDM mock or sandbox                | Deterministic offline mock and separately approved official sandbox evidence                |
| AC-P17-005 | ABDM failure does not destroy valid local clinical data.                   | §§1, 9–10 | No integration; P7 works independently | Failure injection, transaction/outbox, ambiguous outcome and P7 isolation proof             |
| AC-P17-006 | Import/export provenance is retained.                                      | §§4, 7, 9 | Provenance primitives only             | End-to-end source/sender/recipient/version/outcome evidence and correction tests            |
| AC-P17-007 | Retries/idempotency are tested for supported operations.                   | §9        | Generic primitives only                | Official operation-specific retry matrix and replay/duplicate/partial callback tests        |

## 13. P16 and cross-domain prerequisite map

| Dependency                             | Current status                                                                                  | P17 STOP consequence                                                               |
| -------------------------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `FR-FHIR-001..011` / `AC-P16-001..010` | P16-A/B/C NOT STARTED; every live outcome NOT VERIFIED                                          | No clinical FHIR artifact may be sent or trusted; Spec 20 is design only           |
| P4 sessions, identity and consent      | Pseudonymous sessions and consent primitives exist; real external identity/authorization absent | No session-to-ABHA substitution; no consent transitivity                           |
| P5 clinical facts/provenance           | Authoritative local types and correction guards exist                                           | Preserve versions/trust; inbound data stays candidate until approved review        |
| P7 intake                              | Manual path is supported                                                                        | Must remain functional during every ABDM failure/disabled mode                     |
| P11 documents                          | Synthetic contracts; live storage/access gates remain 0/9 approved                              | No binary/document source exposure or DocumentReference authority                  |
| P13 referral policy                    | Runtime NOT STARTED; `REFERRAL_SHARING` remains mandatory for external referral disclosure      | Referral consent cannot be weakened or reused as universal ABDM consent            |
| P21 administration                     | Runtime NOT STARTED                                                                             | No production configuration, maker-checker, credential or release workflow         |
| Global privacy/security                | Reviews and runtime controls remain phase-specific                                              | No patient data, external traffic, endpoint or credential before explicit approval |

## 14. P17 phase ownership and explicit STOP

| Future unit | Intended scope                       | Current state and gate                                                                                                    |
| ----------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| P17-A       | Approved-flow interfaces             | **NOT STARTED**; requires approved Spec 21, official source and architecture/identity/consent decisions                   |
| P17-B       | Sandbox adapter                      | **NOT STARTED**; requires approved offline-mock scope, then official sandbox onboarding/security/profile evidence         |
| P17-C       | Synchronization/use-case integration | **NOT STARTED**; requires P16 conformance, trusted identity, authorization, consent, partner and clinical-source approval |
| P17-D       | Failure/security/audit tests         | **NOT STARTED**; requires supported-operation semantics, incident, audit and release decisions                            |

P8-C/P9-C patient-facing Stage 3 remain BLOCKED; P10/P11 live remain 0/9 approved; P12, P13,
P14, P15, P16, P17 and P21 runtime remain NOT STARTED. P15 clinical/readiness STOP remains intact.

**STOP:** do not begin P16-A/B/C or P17-A/B/C/D, install an ABDM/FHIR dependency, acquire a
profile, create a payload/fixture resembling official or patient data, configure an endpoint,
provision credentials, start a sandbox, expose a callback, link identity or claim approval. The
next action is accountable review through
[P17_READINESS_GATE_REVIEW.md](implementation/P17_READINESS_GATE_REVIEW.md), official source
verification and a separately authorized prompt from the then-current main SHA.
