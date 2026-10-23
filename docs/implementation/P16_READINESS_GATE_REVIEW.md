# SwasthyaSetu AI — P16 Readiness Gate Review

> **PROPOSED AND UNAPPROVED — HUMAN-DECISION INVENTORY ONLY**
>
> **NO OFFICIAL P16 GATE COUNT, SIGN-OFF, LIVE EXCHANGE OR IMPLEMENTATION AUTHORIZATION**

**Work unit:** `PRE-P16-FHIR-MAPPING-DESIGN`

**Baseline:** `main` at `34b3e17df672c68e9677ca3ae88bf07c7711ea0c`

**Date:** 2026-10-23

**Runtime effect:** None

## 1. Purpose and decision rule

This document prepares accountable review of the draft
[FHIR R4 Mapping and Validation Boundary Specification](../20_FHIR_MAPPING_SPEC.md). It does not
create an official approval program, decide clinical meaning, select a profile package, or grant a
person authority to sign. All human decisions remain unsigned and unapproved.

The current repository has no FHIR mapper, validator, gateway, profile package, endpoint,
sidecar, import/export API or ABDM integration. Therefore P16-A/B/C and P17 remain NOT STARTED and
all `FR-FHIR-001..011` and `AC-P16-001..010` live outcomes remain NOT VERIFIED.

Review uses this rule:

```text
documented proposal + green engineering checks
  != accountable human approval
  != clinical truth
  != consent to disclose
  != FHIR conformance
  != permission to activate P16 or P17
```

Where evidence is missing, ambiguous, expired or disputed, the relevant activity fails closed.
Possible synthetic/offline work listed below may begin only under a separate explicit prompt after
the applicable review permits that exact subset.

## 2. Current evidence baseline

- PR #45 merged at baseline `34b3e17df672c68e9677ca3ae88bf07c7711ea0c`; reviewed head
  `a0a1fb9b6eaf34ac31de5c0f70f2d59ee47cb27c` is tree-equivalent. PR #44 was closed unmerged.
- R3 sets FHIR R4 4.0.1 as the baseline and HAPI FHIR as a preferred conditional sidecar behind a
  project-owned boundary. This is not deployment or conformance evidence.
- ADR-004, ADR-008, ADR-010, ADR-021, ADR-022, ADR-035 and ADR-038 remain accepted and unchanged.
- P4 consent, P5 patient/encounter/fact/provenance, P7 deterministic manual intake and synthetic P11
  document contracts exist within their approved bounds.
- `backend/app/modules/interoperability/fhir/` and `backend/app/adapters/fhir/` are placeholders.
- `docs/21_ABDM_INTEGRATION_SPEC.md` is absent. No profile or terminology package is installed.
- Alembic remains `p7a_0007`; no database, API, feature flag, dependency or infrastructure change is
  authorized by this review.

## 3. Proposed review areas

These are descriptive review areas, not numbered official gates.

### 3.1 Internal domain stability and source provenance

**Accountable roles:** patient/encounter module owner; clinical provenance owner; clinical safety
lead; data architect; privacy lead; institutional data steward.

**Actual evidence:** immutable P5 domain types, typed verification states, explicit supersession,
PostgreSQL persistence, P7 intake structures and source-traceable summary contracts. Lower-trust
data cannot silently overwrite clinician-confirmed facts.

**Missing decisions/evidence:** which versions and statuses are exportable; external-source trust;
fact snapshot semantics; ambiguous/contradictory values; correction and deletion meaning; stale
source behavior; institution ownership; import review authority; reversible reconciliation.

**Required future artifact:** approved source eligibility matrix, version/snapshot contract,
correction and ambiguity policy, import-candidate authority workflow, provenance disclosure rules,
and domain-owner sign-off record.

**Relevant requirements:** `FR-FHIR-001..008`, `FR-FHIR-010`; `AC-P16-001..007`, `AC-P16-009..010`.

**Risk and required tests:** stale snapshot, missing source version, contradictory data, rejected or
superseded fact, concurrent clinician correction, lower-trust overwrite, missing import provenance,
rollback and lossiness. Tests must prove no direct authoritative write and no silent trust upgrade.

**Separately possible later synthetic/offline subset:** immutable mapping-context and provenance
contract tests using unmistakably synthetic identifiers, only after architecture and source owners
approve those shapes.

**STOP:** source eligibility, version or correction authority is undefined; a mapper would infer
clinical meaning; or import could mutate an owning module without reviewed confirmation.

### 3.2 Source-backed resource crosswalks and terminology

**Accountable roles:** licensed clinical terminology lead; interoperability architect; patient,
encounter, document and consent owners; institutional clinical informatics owner.

**Actual evidence:** canonical requirements name Patient, Encounter, Observation,
AllergyIntolerance, medication resources, DiagnosticReport, DocumentReference and Consent. The
domain model identifies internal owners. No field-level crosswalk is approved.

**Missing decisions/evidence:** source-backed field meaning; Patient identifier policy; encounter
class/status; Observation codes/units; allergy certainty/status; MedicationStatement versus
MedicationRequest authority; report composition; document metadata; consent representation;
Provenance subset; unknown/absent values; terminology source, version, license and lifecycle.

**Required future artifact:** clinician- and source-qualified per-resource crosswalks with exact
internal source, eligibility, cardinality, absent/unknown behavior, code-system version, lossiness,
prohibited inference and reviewer signatures.

**Relevant requirements:** `FR-FHIR-002..009`; `AC-P16-002..007`, `AC-P16-010`.

**Risk and required tests:** patient identity leakage, unit/code mismatch, patient report presented
as prescription, extraction candidate presented as Observation, model risk presented as Condition,
document reference granting binary access, and round-trip mutation. Every undefined mapping stays
TBD and fails closed.

**Separately possible later synthetic/offline subset:** typed mapping DTOs and explicit rejection
fixtures for unsupported/unknown fields, after the exact crosswalk is approved.

**STOP:** a required mapping relies on memory, vendor defaults, invented clinical policy or an
unlicensed/unversioned terminology source.

### 3.3 R4 profile conformance and independent validation

**Accountable roles:** interoperability architect; standards/conformance reviewer; clinical
terminology lead; security lead; legal/licensing reviewer; SRE/operations owner.

**Actual evidence:** R3 adopts FHIR R4 4.0.1 and prefers HAPI behind the provider/sidecar boundary.
Research proposes structural, profile and terminology validation. No running validator, package or
conformance result exists.

**Missing decisions/evidence:** exact profiles and implementation-guide packages; authoritative
package source; license; checksum; FHIR compatibility; terminology dependency; blocking issue
policy; independent validation method; HAPI version/digest, hardening, backup, upgrade and rollback.

**Required future artifact:** approved versioned package manifest and license record, conformance
test plan, qualified validator report, independently reviewed golden/negative synthetic fixture set,
private sidecar threat review and operations runbook.

**Relevant requirements:** `FR-FHIR-001`, `FR-FHIR-007..011`; `AC-P16-001`, `AC-P16-007..010`.

**Risk and required tests:** parseable but non-conformant JSON, wrong R4 version, unknown profile,
bad terminology/reference, mixed-patient Bundle, package drift, validator disagreement, no
validator, unsafe HAPI defaults and sidecar outage. A vendor success response is not clinical truth.

**Separately possible later synthetic/offline subset:** closed-version schema tests with no public
downloads, only after package/source/licensing approval. A HAPI spike needs its own explicit scope.

**STOP:** profile/package or validation authority is unknown; the validator is public or unhardened;
required validation is unavailable; or conformance is claimed from parsing alone.

### 3.4 Identity, authorization, consent, legal and minimization

**Accountable roles:** identity and authorization owner; privacy officer; legal/DPDP counsel;
consent owner; institutional data controller; clinical safety lead; audit owner.

**Actual evidence:** server-side actor/object authorization and distinct P4 consent purposes exist.
`GENERAL_PRODUCT_USE` with `clinical_intake` scope authorizes neither FHIR nor ABDM exchange.
`REFERRAL_SHARING` governs actual external referral sharing and cannot authorize unrelated FHIR
exchange. No live authenticated IdP is configured.

**Missing decisions/evidence:** eligible actors/recipients; patient, encounter, institution and
field-level access; exchange purposes; whether a purpose uses explicit consent or another
specifically reviewed applicable authority where lawful; notice; withdrawal; in-flight revocation;
retention; audit; disclosure evidence; data-subject rights and breach response.

**Required future artifact:** approved authorization matrix, purpose/consent decision, minimum-data
profiles, legal/privacy assessment, notice and withdrawal workflow, audit evidence contract,
retention/deletion schedule and named institutional controller decision.

**Relevant requirements:** `FR-FHIR-001..010`; `AC-P16-002..009`.

**Risk and required tests:** cross-subject/cross-tenant/wrong-institution access, forged authority,
missing/expired/revoked/wrong-purpose consent, field overreach, mass export, stale authorization,
revocation during queued send, existence disclosure and excess data. Export denies by default.

**Separately possible later synthetic/offline subset:** pure authorization-decision contract tests
with no patient data, only after the decision matrix is approved.

**STOP:** trusted identity, object/institution authorization, purpose, minimum necessary scope or
applicable consent/authority is absent or cannot be re-checked at send time.

### 3.5 Adapter and outbound endpoint security

**Accountable roles:** security architect; application security owner; network/platform owner;
identity owner; interoperability owner; SRE/incident-response owner; privacy officer.

**Actual evidence:** accepted ports/adapters architecture, repository HTTP conventions, typed error
policy and privacy-safe observability rules. No FHIR endpoint or credential is configured.

**Missing decisions/evidence:** destination registry; base URL ownership; egress allowlist; DNS and
redirect policy; SSRF controls; authentication; secret custody/rotation; TLS; least privilege;
allowed operations; payload limits; timeout/retry/circuit behavior; HAPI private network posture;
incident disable and credential revocation.

**Required future artifact:** threat model, data-flow diagram, destination onboarding record,
network/SSRF design, authentication profile, secret and key runbook, safe-operation retry matrix,
logging review, penetration findings and incident/rollback plan.

**Relevant requirements:** `FR-FHIR-001`, `FR-FHIR-010..011`; `AC-P16-001`, `AC-P16-008`.

**Risk and required tests:** localhost/link-local/metadata/private-network targets, DNS rebinding,
redirect escape, credential leakage, unauthorized operation, oversized response, timeout, 429/503,
malformed OperationOutcome, non-idempotent replay, sensitive logs and public administrative UI.

**Separately possible later synthetic/offline subset:** fake adapter contract/error tests with no
network egress after architecture/security approval; a real client or sidecar is not included.

**STOP:** destination is not allowlisted and accountable; secrets or PHI could be logged; SSRF and
network isolation are unproven; or the sidecar can become authoritative.

### 3.6 Import authority, identity matching and reversibility

**Accountable roles:** clinical governance lead; patient identity/record-management owner;
institutional data steward; provenance owner; privacy officer; interoperability architect.

**Actual evidence:** canonical provenance includes `FHIR_IMPORT`; the domain protects
clinician-confirmed facts from lower-trust supersession. No import route or identity matching policy
exists.

**Missing decisions/evidence:** trusted-source tiers; source authentication; identity match and
merge policy; deduplication keys; candidate review; clinical confirmation; correction/supersession;
external deletion; data loss; conflict resolution; versioned reversibility and quarantine lifecycle.

**Required future artifact:** source trust registry, identity-match policy, non-authoritative import
candidate contract, clinical review and owner-module transaction design, conflict/correction
workflow, rollback/reconciliation runbook and privacy-approved quarantine rules.

**Relevant requirements:** `FR-FHIR-001..011`; `AC-P16-001..010`.

**Risk and required tests:** missing provenance, stale identity link, false merge, duplicate import,
changed remote version, correction overwrite, unsupported resource, mixed patient, partial commit,
ambiguous remote state and attempted direct ORM write.

**Separately possible later synthetic/offline subset:** immutable import-candidate parsing and
rejection tests after the trust and identity policy is accepted; no persistence or clinical update.

**STOP:** identity is ambiguous; source trust is missing; an import could directly update clinical
truth; or correction and rollback semantics are undefined.

### 3.7 Synthetic test and conformance evidence plan

**Accountable roles:** quality engineering owner; interoperability architect; clinical terminology
reviewer; security test owner; privacy reviewer; SRE owner.

**Actual evidence:** repository quality and CI conventions plus research-derived benchmark plans.
There are no P16 fixtures or tests; this documentation does not add them.

**Missing decisions/evidence:** approved synthetic fixture vocabulary; golden-resource authority;
round-trip expectations and known lossiness; cross-resource closure; validator oracle;
timeout/retry/idempotency semantics; performance bounds; privacy test evidence and independent
review criteria.

**Required future artifact:** versioned synthetic fixture manifest, resource and Bundle matrix,
golden/invalid expectations, independent validation report, security/privacy negative suite,
sidecar-failure isolation test and traceability to every FR/AC.

**Relevant requirements:** `FR-FHIR-001..011`; `AC-P16-001..010`.

**Risk and required tests:** happy-path-only evidence, real patient fixtures, merely parseable JSON,
false round-trip equivalence, unknown fields accepted, flaky network tests, hidden retry, partial
success, log leakage, core intake blocked by sidecar and risk-to-diagnosis mapping.

**Separately possible later synthetic/offline subset:** reviewed deterministic DTO/mapping fixtures
without external network, real clinical content or runtime registration; only by separate prompt.

**STOP:** fixtures contain patient data; expected clinical meaning lacks an accountable source;
tests omit negative/failure cases; or CI success is presented as human/conformance approval.

### 3.8 P17 ABDM dependency and rollout

**Accountable roles:** ABDM program/integration owner; privacy/legal/consent owners; security and
identity owners; interoperability architect; partner/institution owner; clinical safety lead;
SRE/incident and release owners.

**Actual evidence:** canonical P17 requirements and acceptance criteria exist. Generic FHIR R4 is a
prerequisite. `docs/21_ABDM_INTEGRATION_SPEC.md`, sandbox evidence, producer-specific profiles and
approved consent flows are absent.

**Missing decisions/evidence:** approved Spec 21; current official package/profile source and
license; ABHA identity and consent flows; sandbox contract; partner roles; credential custody;
producer requirements; transaction/idempotency rules; incident and rollback; pilot and production
approval.

**Required future artifact:** approved Spec 21, current authoritative source record, sandbox test
report, security/privacy/consent assessment, producer conformance evidence, partner agreement,
operations runbook and explicit pilot/production decisions.

**Relevant requirements:** P16 `FR-FHIR-001`, `FR-FHIR-010..011`, `AC-P16-001`, `AC-P16-008`; future
P17 `FR-ABDM-001..007` and `AC-P17-001..007` only.

**Risk and required tests:** guessed profile or endpoint, general consent reused, production data on
public sandbox, credential leak, replay/duplicate exchange, provider outage destroying local data,
source provenance loss and P17 scope hidden in P16.

**Separately possible later synthetic/offline subset:** none under Pre-P16. Any ABDM mock or sandbox
work needs approved Spec 21 and its own explicitly bounded P17 prompt.

**STOP:** Spec 21 is absent; current official requirements or consent are unapproved; sandbox or
partner authority is missing; or ABDM evidence is used to claim P16 completion.

## 4. Owner and risk register

Role names describe accountability; they do not identify or appoint a person.

| Decision/risk | Accountable roles | Current state | Required recorded decision |
|---|---|---|---|
| Port/service contract and module boundary | Architecture owner; interoperability owner | OPEN | Accept/revise precise ports, direction and dependency rules |
| Clinical source eligibility and mappings | Clinical governance; terminology lead; domain owners | BLOCKED | Source-backed crosswalk and prohibited-inference approval |
| Patient identity and institution matching | Identity/records owner; institutional steward | BLOCKED | Match, collision, merge and no-match policy |
| Consent, purpose, lawful authority and minimization | Privacy officer; legal counsel; consent owner; controller | BLOCKED | Per-purpose authority, notice, withdrawal and minimum-data decision |
| Profiles, terminology and package rights | Standards reviewer; terminology lead; legal/licensing | BLOCKED | Exact source/version/license/lifecycle and profile approval |
| HAPI/validator qualification | Interoperability; security; SRE; quality | OPEN, not approved | Private topology, hardening, evidence, upgrade and rollback decision |
| Outbound destinations and credentials | Security; network/platform; partner owner; SRE | BLOCKED | Allowlist, auth, secret custody, operation and incident approval |
| Import review and clinical authority | Clinical governance; provenance; domain owners | BLOCKED | Candidate-only workflow, confirmation, correction and rollback |
| Audit, retention, deletion and breach response | Privacy; legal; audit; SRE/incident | BLOCKED | Evidence, retention, purge, legal hold and response policy |
| Synthetic/conformance test authority | Quality; standards; clinical terminology; security/privacy | OPEN, not approved | Fixture provenance, oracle, negative coverage and independent review |
| ABDM/P17 | ABDM owner; partner; privacy/legal/security; release | BLOCKED | Approved Spec 21 and separate sandbox/pilot/production records |

## 5. Acceptance evidence required before implementation claims

The canonical `AC-P16-001..010` remain unchanged and LIVE NOT VERIFIED. Future evidence must include:

- explicit module dependency proof for AC-P16-001;
- reviewed synthetic Patient, Encounter, Observation, AllergyIntolerance, medication,
  DiagnosticReport and DocumentReference mappings for AC-P16-002..007;
- pinned, independently qualified structural/profile/terminology validation for AC-P16-008;
- origin/source/version persistence and correction tests for AC-P16-009;
- direct and adversarial proof that model risk, symptom, route and unconfirmed extraction cannot
  become a confirmed Condition for AC-P16-010;
- authorization, consent, privacy, SSRF, timeout, retry, idempotency, concurrency, partial-failure,
  log-redaction and sidecar-outage negatives across the applicable criteria.

Passing these technical checks would still require applicable accountable human approval before
live processing or production exchange.

## 6. Unsigned decision template

```text
Decision record ID:
Review area and bounded decision:
Scope, population, institution and destination:
Canonical requirements and acceptance criteria:
Evidence reviewed, exact versions and dates:
Clinical/source authority:
Privacy/legal basis and purpose-specific consent decision:
Identity, authorization and minimization decision:
Security, network, secret and audit decision:
Profile, terminology, license and validator decision:
Known lossiness, contraindications and excluded cases:
Required positive and negative tests:
Retention, deletion, incident, rollback and expiry:
Accountable role(s):
Named authorized reviewer(s):
Decision: APPROVE BOUNDED SCOPE | REJECT | REQUEST CHANGES | DEFER
Conditions and expiry/re-review date:
Signatures/references:
```

This template is intentionally unsigned. Repository authorship, PR approval and green CI do not
populate any decision field.

## 7. Preserved governance and next action

- P7 deterministic manual text/touch intake remains available and unchanged.
- P8-C and P9-C patient-facing Stage 3 remain BLOCKED.
- P10 and P11 live approval remains 0/9; synthetic contracts are not live approval.
- P12, P13, P14, P15, P16, P17 and P21 runtime remain NOT STARTED.
- P15's clinical/readiness STOP remains intact; Pre-P16 grants no P15 engineering permission.
- No FHIR profile, mapping, validation, export/import, HAPI deployment, ABDM flow, consent policy,
  production destination, feature flag or infrastructure is activated.

**Next accountable action:** circulate the draft Spec 20 and this inventory to the roles above.
Record bounded decisions and missing evidence without inventing approvals. If reviewers permit a
specific synthetic/offline P16-A subset, issue a new phase prompt from the then-current main SHA.
Otherwise keep P16 and P17 stopped.

**STOP:** this branch ends after independent review preparation. Do not begin P16-A/B/C or P17,
process real patient data, install a FHIR dependency, deploy a validator or expose an exchange API.
