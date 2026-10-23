# SwasthyaSetu AI

## 20 — FHIR R4 Mapping and Validation Boundary Specification

> **DRAFT — PRE-P16 TECHNICAL GOVERNANCE; NO MAPPERS, VALIDATORS, REAL PATIENT
> EXCHANGE OR PRODUCTION APPROVAL IMPLEMENTED**

**Document ID:** `SSAI-SPEC-020-DRAFT`

**Status:** Unapproved Pre-P16 technical design

**Baseline:** `main` at `34b3e17df672c68e9677ca3ae88bf07c7711ea0c`

**Date:** 2026-10-23

**Runtime effect:** None

This document is a proposal for accountable review. It is not a clinical policy, an approved
FHIR profile, permission to disclose data, a conformance result, or authorization to begin P16.

## 1. Scope, authority, and current truth

### 1.1 Source hierarchy

This draft is subordinate to the approved clinical and safety policy and the canonical
[Project Master Specification](00_PROJECT_MASTER_SPEC.md),
[System Architecture](02_SYSTEM_ARCHITECTURE.md),
[Product Requirements](01_PRODUCT_REQUIREMENTS.md),
[Privacy and Consent Specification](26_PRIVACY_CONSENT_SPEC.md),
[Domain Model](04_DOMAIN_MODEL.md),
[Database Schema](05_DATABASE_SCHEMA.md),
[API Contracts](06_API_CONTRACTS.md),
[Clinical Provenance Specification](12_CLINICAL_PROVENANCE_SPEC.md), and accepted decisions in the
[Decision Log](implementation/37_DECISION_LOG.md). The
[R3 technology baseline](research/r3/R3_FINAL_TECHNOLOGY_STACK.md) outranks the research-derived
[FHIR adapter draft](research/fhir/FHIR_ADAPTER_CONTRACT_DRAFT.md). The accepted
[ADR-004](adr/ADR-004-fhir-boundary.md) remains controlling.

The governing decisions preserved here are:

- ADR-004: FHIR is an interoperability boundary, not the internal domain model;
- ADR-008: PostgreSQL is the transactional source of truth;
- ADR-010: AI-derived facts retain provenance and verification state;
- ADR-021: important internal boundaries use typed contracts;
- ADR-022: engineering must not invent real clinical policy;
- ADR-035: HAPI FHIR is the preferred conditional conformance sidecar behind the provider boundary;
- ADR-038: dependencies activate only in their approved profile and phase.

### 1.2 As-built state

At the recorded baseline:

- internal P5 patients, encounters, clinical facts, verification and provenance are implemented;
- P7 deterministic manual text/touch intake remains the supported intake path;
- P11 contains synthetic document-domain contracts, but real document storage, source access and
  patient processing remain blocked by P11 governance;
- `backend/app/modules/interoperability/fhir/` and `backend/app/adapters/fhir/` contain placeholders
  only;
- no FHIR mapper, validator, gateway, remote client, projection repository, sidecar, route,
  implementation-guide package, terminology service, external endpoint or credential exists;
- `docs/21_ABDM_INTEGRATION_SPEC.md` is absent, so P17 ABDM/ABHA workflows are not specified;
- P16-A, P16-B and P16-C are NOT STARTED and every live P16 acceptance outcome is unverified.

### 1.3 Authoritative truth and non-goals

The owning patient, encounter, clinical-fact, document and consent modules, persisted in
PostgreSQL where implemented, remain authoritative. A FHIR resource is a versioned, replaceable
interoperability projection. It is not a second source of clinical truth and does not grant access
to its source objects.

Mapping must preserve P5 verification, correction and supersession meaning and P7 provenance. It
must not turn ambiguity into certainty, turn an extracted candidate into a clinician-confirmed
fact, or overwrite source history. FHIR availability must never be required for core intake,
emergency navigation, or access to a valid local clinical source.

This draft does not define field-level mappings, activate any transport, choose an ABDM profile,
or authorize real import or export. ABDM is a separately specified P17 concern.

## 2. Proposed responsibility and port separation

The broad accepted `FHIRProvider` or sidecar language describes an external interoperability
boundary. For P16 review, the following more precise project-owned contracts are proposed. Their
names and shapes are not accepted APIs or classes until architecture review approves them.

| Proposed responsibility | Owner | Boundary and non-authority |
|---|---|---|
| `FHIRMapper` | SwasthyaSetu interoperability mapping | Deterministically projects approved internal snapshots and parses inbound data into non-authoritative candidates. It does not authorize exchange or decide clinical truth. |
| `FHIRValidationPort` | SwasthyaSetu port; qualified adapter behind it | Reports structural, profile and terminology issues with exact versions. It does not decide patient authorization or clinical validity. |
| `FHIRRepositoryPort` (optional) | Interoperability only | May store/query a replaceable FHIR projection if a reviewed use case justifies it. It never replaces domain repositories or PostgreSQL truth. |
| `FHIRRemoteClientPort` | Interoperability transport | Performs only allowlisted operations against approved destinations with bounded timeouts and safe retries. The R3 `httpx`-style candidate adds no dependency in this draft. |
| `FHIRGatewayService` | Application orchestration | Re-checks actor/object/institution authority, purpose and consent; snapshots source versions; invokes mapping and validation; and records evidence. Transport is separately gated. |
| `ABDMProvider` | Future P17 adapter | Owns ABDM-specific transport and workflows. It is not interchangeable with FHIR validation and remains absent. |

HAPI FHIR remains a conditional, private conformance/validation sidecar candidate and an optional
projection repository candidate. It is not deployed, configured or proven here. No Java type or
vendor object may leak into application or domain contracts. Vendor issue severity cannot control
SwasthyaSetu safety policy.

## 3. Proposed versioned contracts and provenance

All contracts below are design-only typed shapes. Required values use closed enums and bounded
strings; unknown fields and unsupported versions fail closed.

### 3.1 Mapping request context

```text
mapping_request_id
direction: EXPORT | IMPORT_CANDIDATE
fhir_version: R4_4_0_1
mapping_id + mapping_revision
source_type + source_ids[] + source_versions[]
source_status + source_verification_state
patient_id + encounter_id?
source_owner_module
institution_id? + tenant_scope?
purpose + permission_decision_ref
consent_or_reviewed_authority_ref
target_profile? + implementation_guide_id? + implementation_guide_version?
source_time? + snapshot_time_utc + transformation_time_utc
correlation_id
```

The initial closed version is exactly FHIR R4 4.0.1. Every timestamp is RFC3339, timezone-aware
and normalized to UTC. Source time and transformation time are different facts. A consent or
lawful-ground reference records a separately evaluated precondition; it is not a property of a
clinical field and cannot be inferred from one.

### 3.2 Mapping result

```text
mapping_request_id
resource_type + logical_projection_id
fhir_version + mapping_id + mapping_revision
resource_or_candidate
source_refs[] + source_versions[]
provenance
absent_or_unknown_elements[]
warnings[] + blocking_issues[]
lossiness[] + round_trip_limitations[]
profile_claims[]
correlation_id
```

Unknown, absent, contradictory and unsupported source values stay explicitly unknown, absent,
contradictory or unsupported. They are never guessed. A profile claim is permitted only after the
exact approved profile is selected and successfully validated.

### 3.3 Provenance and evidence

Proposed exchange provenance retains the source owner, object identifiers and versions, source
verification state, mapping revision, selected FHIR and profile versions, transformation time,
actor and institution decision references, validator metadata, destination identifier and outcome.
Clinical fact provenance and technical exchange provenance remain related but distinct.

No raw clinical narrative, full resource, document content, token, identifier set or source text is
emitted to general logs, metrics, traces, error stacks or CI artifacts. Telemetry is limited to
bounded operation, resource type, version, endpoint identifier, timing, outcome, issue counts and
correlation identifiers.

### 3.4 Normalized errors

Proposed error families include unsupported FHIR version, unsupported resource, mapping failure,
source stale, provenance missing, authorization denied, consent invalid, profile unavailable,
validation failed, endpoint disallowed, remote unavailable, authentication failed, conflict, rate
limited, timeout and idempotency conflict. Failures are explicit; partial output is not presented as
success, and sensitive diagnostics remain protected.

## 4. Traceable future resource matrix

No row is a field-level crosswalk or implementation approval. Undefined clinical, identity,
terminology and profile meanings are **TBD — accountable human decision required**.

| FHIR R4 resource | Internal authoritative source | Eligible future projection | Unknown, provenance and lossiness | Preconditions and pending decisions |
|---|---|---|---|---|
| Patient | `patients` aggregate, demographics and approved identifiers | Minimum identity/demographic subset required by an approved exchange | Preserve source/version; do not synthesize names, sex/gender, birth date, address or identifiers. Identity matching and round-trip merge are lossy and TBD. | Trusted actor, object/institution scope, minimum necessary purpose, approved identifier and demographics policy, consent/authority, profile and recipient. |
| Encounter | `encounters` aggregate | Supported lifecycle and relationship snapshot | Preserve exact encounter version/status/time; absent class, participant or service provider stays absent. External status reconciliation is TBD. | Approved encounter semantics, actor assignment, institution policy, profile and recipient scope. |
| Observation | Accepted P5 observation/clinical-fact projection | Supported authoritative lab/vital facts with units and verification | Keep value, unit, source, reference range and verification distinct. P8 extraction candidates and model scores cannot become confirmed Observation. | Clinical/terminology owners approve code, unit and status mapping; source is current and authorized. |
| AllergyIntolerance | P5 allergy fact | Only an accepted allergy record meeting future verification policy | Patient report, extracted mention and clinician confirmation remain distinguishable; free-text discomfort is not silently promoted. | Clinical owner approves status, certainty and coding rules; exact crosswalk is TBD. |
| MedicationStatement / MedicationRequest and relevant medication resources | P5 medication facts plus future authoritative ordering source | Resource choice follows the approved source meaning | Historical/patient-reported use is not an order. Missing dose, route, frequency or unit stays missing. Round-trip equivalence is not assumed. | Clinical and interoperability owners approve resource variant, status, coding and ordering authority. |
| DiagnosticReport | Authoritative supported investigation/report projection | A report with its exact source and linked results when approved | A document label or extraction candidate is not a report conclusion. Missing result links and interpretation stay absent. | Clinical owner approves report semantics and reference closure; selected profile remains TBD. |
| DocumentReference | P11 document metadata after all live P11 gates | Minimum metadata/reference required by an approved exchange | It does not grant binary read/share access. Quarantined, deleted, expired or unauthorized content remains unavailable without existence leakage. | P11 ownership, storage, retention, source-access, consent, recipient and URL/token safety approvals must first close. |
| Consent | Authoritative P4 consent record | Deliberate interoperability projection only where required | FHIR Consent cannot override internal authorization. Purpose, scope, subject, notice and revocation meaning may be lossy. | Privacy/legal and consent owners approve the representation and its authority; general intake consent is insufficient. |
| Provenance | P5 provenance plus exchange evidence | Deliberate minimum exchange subset | Internal provenance may be richer; omission never upgrades trust. Source reference is not source-access permission. | Clinical provenance, privacy and security owners approve disclosure and recipient visibility. |
| Bundle / Composition | Already mapped resources and a future approved package | Assemble a closed, reference-complete document/transaction only where applicable | Reject mixed-patient or unresolved references; preserve per-resource sources and snapshot versions. | Exact package, profile, entry ordering, operation and destination are TBD; ABDM bundles are P17-only. |

FHIR Condition is intentionally excluded as an automatic model-risk, symptom, safety-route or
unconfirmed extraction projection. A future Condition mapping would require separately approved
problem/diagnosis authority and clinical rules.

## 5. Direction, corrections, and data authority

### 5.1 Design-only export path

```text
trusted actor
 -> fresh actor, object and institution authorization
 -> purpose and consent or other specifically reviewed applicable authority
 -> minimum authorized versioned snapshot
 -> mapper
 -> required profile validation
 -> approved gateway and destination
 -> exchange evidence and audit
```

Queued sends must re-check authorization, consent, source versions and destination eligibility at
send time. Revocation or source drift stops the send. Idempotency keys are owner scoped and bind the
snapshot, mapping revision, operation and destination. Non-idempotent operations are not blindly
retried. Partial remote outcomes require explicit reconciliation and cannot be reported as complete.

### 5.2 Design-only import candidate path

```text
approved authenticated source
 -> size/type/version gate
 -> structural and selected-profile validation
 -> source and exchange provenance
 -> mapper to non-authoritative import candidate
 -> deduplication and identity review
 -> clinical/operational confirmation under approved policy
 -> owning-module transaction, correction evidence and audit
```

An import never directly deserializes into authoritative patient rows. Missing provenance,
ambiguous identity, unsupported version, stale linkage, mixed subjects, invalid references or
unreviewed source authority causes rejection or protected quarantine. Quarantine storage, access,
retention and deletion require their own approved design.

Deduplication, patient identity matching and cross-institution trust remain pending institution
policy. No automatic patient merge is allowed. Corrections create traceable new state and preserve
prior provenance. A lower-trust import cannot overwrite clinician-confirmed data. Deletion,
revocation and external correction do not erase the internal audit trail; their exact lawful
retention behavior is pending review. Rollback restores a known configuration/version and does not
claim to recall data already sent.

### 5.3 Independent validation meanings

These statuses must never be collapsed:

1. structurally valid FHIR R4 JSON;
2. conformant to a named, pinned profile;
3. terminology-validated against pinned sources;
4. clinically truthful and appropriately verified;
5. authorized for this patient, actor, purpose and institution;
6. eligible for this recipient and destination.

Passing one gives no evidence that another passed.

## 6. Conformance and profile governance

R3 adopts only **FHIR R4 4.0.1** as the project baseline. No implementation-guide package, profile
URL, terminology release, ABDM package, license, conformance certificate or validation result is
selected by this draft.

The proposed validation modes are:

- `STRUCTURAL`: closed resource/version/schema checks;
- `PROFILE`: structural checks plus named, pinned profile constraints;
- `PROFILE_AND_TERMINOLOGY`: profile checks plus pinned terminology validation.

Every installed package would require an approved source, exact ID/version, FHIR compatibility,
license and rights review, checksum, lifecycle status, installation evidence and rollback plan.
Packages are pre-approved and pre-installed; an inbound reference must never trigger a public
download. Unsupported versions and unknown profiles fail closed.

A qualified HAPI adapter may later report issues and engine/package metadata. SwasthyaSetu owners,
not the vendor, define which issue codes are blocking, warning or informational. HAPI is not a
working validator until a separately reviewed private deployment, hardened configuration, pinned
image, package lifecycle and independent test evidence exist. Exact consent representation,
medication resource choice, terminology and institutional policy remain human-review pending.

Future tests must cover closed-world versions, valid golden synthetic resources, missing required
elements, wrong profile, bad terminology, invalid and cyclic references, mixed-patient bundles,
unknown extensions, resource-size limits, lossiness, and expected rejection. Parseable JSON alone
is not conformance evidence.

## 7. Security, privacy, consent, and availability

`GENERAL_PRODUCT_USE` with `clinical_intake` scope does not authorize FHIR or ABDM exchange.
`REFERRAL_SHARING` is mandatory for actual external referral sharing under its own canonical
policy, but it does not authorize every FHIR exchange. Every exchange needs a reviewed purpose and
either valid purpose-specific consent or another specifically reviewed applicable authority where
lawful, plus every additionally applicable legal and governance requirement.

Before real transfer or patient-level lookup, accountable reviewers must decide recipient and
institution eligibility, source and destination regions, authentication, least privilege,
object/field authorization, minimization, audit evidence, retention and deletion, revocation,
breach response, outbound allowlisting, network isolation and incident rollback. Export is denied
by default.

Remote base URLs are configuration owned, normalized and allowlisted; user-controlled URLs,
redirect escape, loopback, link-local, metadata, private-network and DNS-rebinding targets are
rejected according to the approved network policy. Secrets are indirect references and never
logged. HAPI administrative/test surfaces and unused capabilities remain private and disabled.

No PHI, raw narrative, full FHIR payload, document URL, credential, patient fixture or model prompt
may enter source code, CI artifacts, general logs, metrics, traces, browser persistent storage or
error responses. Tests use unmistakably synthetic data. An unavailable validator, HAPI sidecar,
remote destination or ABDM service fails the exchange honestly while local P7 intake, emergency
navigation and authorized local records remain available.

## 8. Proposed threat and negative-test inventory

These are future, separately scoped tests—not evidence that P16 passes:

| Area | Required negative cases |
|---|---|
| Authorization | Unauthorized patient or encounter; cross-tenant access; wrong institution; forged actor/decision; field overreach; mass export. |
| Consent and purpose | Missing, expired, revoked or wrong-purpose consent; intake consent reused for exchange; referral consent reused for unrelated exchange; revocation during queued send. |
| Source trust | Unverified/stale source; missing provenance; wrong patient link; clinician correction overwritten; import promoted without review; inferred diagnosis; model risk conflated with Observation or Condition. |
| Version and conformance | Wrong FHIR version; unknown profile/terminology; missing package; invalid reference; mixed-patient Bundle; duplicate entries; validator disagreement; no validator; unsafe HAPI defaults. |
| Network and destination | User-controlled endpoint; SSRF; redirect escape; disallowed recipient; expired credential; endpoint timeout; 429/503; malformed remote outcome; ABDM outage isolation. |
| Consistency | Replay; idempotency collision; duplicate response; concurrent correction; partial transaction; ambiguous remote commit; stale snapshot; rollback to incompatible mapping. |
| Documents and privacy | Binary URL or signed-token leak; unauthorized `DocumentReference`; deleted/quarantined source; raw narrative/full resource in log, trace, metric, error, browser storage or CI artifact. |
| Scope control | Runtime route or feature flag accidentally enabled; profile downloaded dynamically; unsupported operation accepted; P17 behavior smuggled into P16. |

## 9. Phase ownership

| Unit | Future bounded ownership | Current status and gate |
|---|---|---|
| P16-A | Typed FHIR R4 DTOs, mapping context/results and reviewed resource mappings | **NOT STARTED**. Requires architecture, clinical, provenance, identity and terminology decisions plus a separate prompt. |
| P16-B | Validator/gateway ports, qualified sidecar adapter and conformance evidence | **NOT STARTED**. Requires package, license, security, operations and independent-validation approval plus a separate prompt. |
| P16-C | Authorized export/import APIs and end-to-end negative tests | **NOT STARTED**. Requires trusted identity, consent/legal, recipient, audit, retention, incident and pilot approval plus a separate prompt. |
| P17 | ABDM/ABHA adapter, sandbox and producer-specific workflows | **NOT STARTED**. `21_ABDM_INTEGRATION_SPEC.md` is absent; no P17 evidence can complete P16. |

## 10. FR-FHIR traceability

Every row is **LIVE NOT VERIFIED**. This documentation is design evidence only.

| ID | Canonical wording | This draft | As-built evidence | Required future artifact |
|---|---|---|---|---|
| FR-FHIR-001 | The platform SHALL support FHIR-compatible interoperability. | §§1–9 | Placeholder directories only | Approved architecture plus implemented and independently verified P16-A/B/C boundary |
| FR-FHIR-002 | Internal patient data SHALL be mappable to/from an appropriate FHIR Patient representation where applicable. | §4 Patient, §5 | P5 patient domain only | Approved Patient crosswalk, identity policy, mapper and import-candidate tests |
| FR-FHIR-003 | Encounter data SHALL be mappable to FHIR Encounter. | §4 Encounter | P5 encounter domain only | Approved lifecycle crosswalk and mapping tests |
| FR-FHIR-004 | Supported lab/vital data SHALL be mappable to FHIR Observation. | §4 Observation | P5 clinical-fact types only | Approved unit/code/status rules and mapping tests |
| FR-FHIR-005 | Allergy data SHALL be mappable to FHIR AllergyIntolerance. | §4 AllergyIntolerance | P5 allergy type only | Approved verification/status crosswalk and tests |
| FR-FHIR-006 | Medication data SHALL support appropriate FHIR medication-related mapping. | §4 Medication | P5 medication type only | Approved resource-choice/authority rules and tests |
| FR-FHIR-007 | Supported reports SHALL be mappable to FHIR DiagnosticReport. | §4 DiagnosticReport | No FHIR report mapping | Approved report semantics, reference closure and tests |
| FR-FHIR-008 | Uploaded medical documents SHALL be mappable to FHIR DocumentReference where appropriate. | §4 DocumentReference | Synthetic P11 contracts; live storage/access blocked | Closed P11 gates, approved minimal mapping and access-denial tests |
| FR-FHIR-009 | Consent SHALL support interoperability mapping where required. | §4 Consent, §7 | Authoritative P4 consent only | Privacy/legal-approved representation that never replaces internal authorization |
| FR-FHIR-010 | FHIR export/import SHALL undergo schema/profile validation as applicable. | §§5–6 | No validator or approved profile package | Pinned package, qualified validator, independent conformance and failure tests |
| FR-FHIR-011 | FHIR infrastructure/vendor choice SHALL remain isolated from core domain logic. | §2 | Empty adapter/module placeholders; accepted ADR-004/035 | Approved typed ports, adapter contract tests and dependency-boundary proof |

## 11. AC-P16 traceability

Every row is **LIVE NOT VERIFIED**. No acceptance criterion passes because this draft exists.

| ID | Canonical wording | This draft | As-built evidence | Required future evidence |
|---|---|---|---|---|
| AC-P16-001 | FHIR mapping layer is separate from core domain entities. | §§1–2 | Placeholder boundary only | P16-A dependency tests and architecture review |
| AC-P16-002 | Patient mapping exists. | §4 Patient | None | Implemented mapper plus reviewed positive/negative fixtures |
| AC-P16-003 | Encounter mapping exists. | §4 Encounter | None | Implemented mapper plus lifecycle fixtures |
| AC-P16-004 | Observation mapping exists. | §4 Observation | None | Implemented mapper with units, uncertainty and trust tests |
| AC-P16-005 | Allergy mapping exists. | §4 AllergyIntolerance | None | Implemented mapper with verification/status tests |
| AC-P16-006 | Medication-related mapping exists. | §4 Medication | None | Implemented approved resource variants and authority tests |
| AC-P16-007 | DocumentReference/DiagnosticReport mapping exists where applicable. | §4 resources | None; live P11 access blocked | Implemented minimal mappings after P11 gates, with access and reference tests |
| AC-P16-008 | FHIR validation tests pass. | §6, §8 | No validator/profile tests | Independent structural/profile/terminology evidence against pinned versions |
| AC-P16-009 | Imported data retains origin provenance. | §§3, 5 | P5 provenance types only | Non-authoritative import pipeline and persistence/review tests |
| AC-P16-010 | Predictive risk output is not silently mapped as confirmed Condition. | §§4, 8 | Canonical P5/P9/P10 invariant only | Direct/adversarial mapping tests proving rejection and no partial output |

## 12. Unresolved accountable owners and STOP boundary

Architecture/interoperability, clinical/terminology, privacy/legal/consent, security, identity and
authorization, data governance, institutional/partner, operations/SRE, accessibility/product and
release governance roles must review the bounded decisions recorded in
[P16_READINESS_GATE_REVIEW.md](implementation/P16_READINESS_GATE_REVIEW.md). No named signatory or
approval is asserted.

**STOP:** do not begin P16-A/B/C or P17, install dependencies, deploy HAPI, acquire profile packages,
process real patient data, expose an endpoint or claim conformance until a separately authorized
phase closes its applicable human decisions with recorded evidence. P8-C/P9-C Stage 3 remain
blocked; P10/P11 live approval remains 0/9; P12, P13, P14, P15, P16, P17 and P21 runtime remain NOT
STARTED. P15's clinical/readiness STOP remains unchanged.
