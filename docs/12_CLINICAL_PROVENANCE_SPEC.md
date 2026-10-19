# SwasthyaSetu AI

## 12 — Clinical Provenance Specification

**Document ID:** `SSAI-SPEC-012`
**Status:** Canonical Pre-P10 Prerequisite — TECHNICAL SPECIFICATION, NOT CLINICAL APPROVAL
**Version:** `1.0.0`
**Scope:** P10 source provenance, fact review, correction, and source-traceable summaries

---

# 1. Authority and boundary

This specification refines the P5 provenance model for P10. It does not activate clinician access,
create an authentication provider, approve clinical content, authorize a database migration, or
implement any endpoint. `ClinicalFact` is authoritative only inside the `patients` owner;
`FactProvenance` and longitudinal provenance reads belong to `provenance`. The future `summaries`
module consumes authorized, minimum-necessary public projections and must never mutate P5 storage.

Current implementation evidence:

- `backend/app/modules/patients/clinical.py` implements typed immutable facts and guarded explicit
  supersession;
- `backend/app/modules/provenance/domain.py` implements the canonical provenance and verification
  values;
- `backend/app/modules/provenance/application.py` implements fact provenance and timeline reads;
- `backend/app/modules/patients/infrastructure.py` persists facts/provenance and locks the existing
  fact during supersession;
- the future fact-review APIs in `docs/06_API_CONTRACTS.md` §15 are conceptual and are not routes;
- `backend/app/modules/summaries/` has no implementation.

These are working P5 capabilities, not evidence of a trusted clinician, encounter assignment,
clinical review, summary persistence, or P10 acceptance.

# 2. Fact provenance and trust

## 2.1 Canonical provenance shape

Every clinical fact carries one `FactProvenance` with:

| Field                                   | Meaning and constraint                                                       |
| --------------------------------------- | ---------------------------------------------------------------------------- |
| `source_type`                           | Required typed origin; never inferred from UI copy.                          |
| `source_id`                             | Opaque identifier of an authorized source object, when one exists.           |
| `source_ref`                            | Bounded locator/reference, not raw source content or an authorization grant. |
| `extractor_type`                        | Bounded extraction mechanism identifier, when applicable.                    |
| `provider`, `model_id`, `model_version` | Provider/model lineage for model-derived material.                           |
| `prompt_version`, `schema_version`      | Exact bounded contract versions used by extraction.                          |
| `confidence`                            | Optional finite value from 0 through 1; **not clinical certainty**.          |
| `created_at`                            | Required timezone-aware instant normalized to UTC.                           |
| `created_by`                            | Trusted actor identifier when an authorized actor caused the record.         |

Canonical `ProvenanceSourceType` values are `PATIENT_REPORT`, `CAREGIVER_REPORT`, `CLINICIAN`,
`OCR`, `DOCUMENT_AI`, `FHIR_IMPORT`, `ABDM_IMPORT`, `HIS_IMPORT`, `MODEL_INFERENCE`, `ADMIN`, and
`SYSTEM`. Source evidence is typed and minimum-necessary. Raw prompts, chat/extraction messages,
whole OCR blobs, model output, or sensitive source text are not provenance payloads by default and
may not be persisted without a separate approved data contract, lawful purpose, retention policy,
and access control.

A source reference is not proof that the viewer may open the source. Source-detail access is checked
again against the authenticated actor, patient/encounter scope, assignment, institution, consent or
other lawful basis, source-owner permission, and source lifecycle. Missing, deleted, expired, or
unauthorized sources render as `SOURCE_UNAVAILABLE`; the system must not fabricate evidence or leak
whether a forbidden object exists. P11 document views and P16/P17 FHIR/ABDM source links are deferred.

## 2.2 Verification states and hierarchy

The exact states are `EXTRACTED`, `LOW_CONFIDENCE`, `NEEDS_CONFIRMATION`, `PATIENT_CONFIRMED`,
`CLINICIAN_CONFIRMED`, `REJECTED`, and `SUPERSEDED`.

| Existing state        | Confirm                          | Reject                           | Correct/supersede                    | Guard                                                             |
| --------------------- | -------------------------------- | -------------------------------- | ------------------------------------ | ----------------------------------------------------------------- |
| `EXTRACTED`           | to `CLINICIAN_CONFIRMED`         | to `REJECTED`                    | distinct active replacement          | Authorized clinician review only.                                 |
| `LOW_CONFIDENCE`      | to `CLINICIAN_CONFIRMED`         | to `REJECTED`                    | distinct active replacement          | Confidence never substitutes for review.                          |
| `NEEDS_CONFIRMATION`  | to `CLINICIAN_CONFIRMED`         | to `REJECTED`                    | distinct active replacement          | Review establishes disposition of the claim, not universal truth. |
| `PATIENT_CONFIRMED`   | to `CLINICIAN_CONFIRMED`         | to `REJECTED`                    | distinct active replacement          | Patient confirmation is not clinician confirmation.               |
| `CLINICIAN_CONFIRMED` | idempotent same disposition only | not an in-place transition       | clinician-confirmed replacement only | Lower-trust replacement is prohibited.                            |
| `REJECTED`            | prohibited                       | idempotent same disposition only | prohibited                           | Terminal historical claim.                                        |
| `SUPERSEDED`          | prohibited                       | prohibited                       | prohibited                           | Terminal historical claim linked to replacement.                  |

P5 currently enforces that a replacement has a distinct identifier, identical fact type and
patient/encounter scope, an active state, and cannot lower the trust of a clinician-confirmed fact.
P10-D must add review operations without weakening those guards. No candidate, prediction, summary,
P7 answer, P8 extraction, or P9 decision may be silently promoted to `CLINICIAN_CONFIRMED`.
Confirmation records a governed reviewer disposition; it does not make a claim eternally true or
transfer clinical responsibility beyond the approved workflow.

# 3. Protected review workflow

## 3.1 Preconditions on every request

Before confirm, reject, or correct, the server must:

1. authenticate a trusted active actor through the configured provider;
2. require the exact review permission (a role label or client header is insufficient);
3. resolve the target fact server-side and verify patient, encounter, assignment and institution
   scope, plus source access where source detail is requested;
4. verify the encounter is in a review-permitted lifecycle state and re-evaluate any applicable
   consent/lawful-purpose decision;
5. reject cross-patient, cross-encounter, cross-institution, unassigned, expired, disabled, or
   revoked actors with content-free `401`/`403`/`404` policy that does not disclose object existence;
6. validate an expected version and an actor-scoped idempotency key for a mutation.

URL identifiers, browser state, client-supplied role, institution, assignment, consent, source
ownership, or verification state are never authority. Current `RoleCode.CLINICIAN`,
`ENCOUNTER_READ_ASSIGNED`, and `SUMMARY_CONFIRM` constants are prerequisites only: no implemented
assignment source or live clinician authentication currently proves these preconditions.

## 3.2 Atomic dispositions

- **Confirm:** lock/read the current fact; verify its expected state/version; create the minimized
  review evidence and transition it to `CLINICIAN_CONFIRMED` atomically.
- **Reject:** lock/read the current fact; preserve its value and provenance; transition it to
  `REJECTED` atomically. Rejection is not deletion.
- **Correct:** create a distinct replacement fact with its own `CLINICIAN` provenance, then mark the
  original `SUPERSEDED` with `superseded_by_fact_id`, in one transaction. The original value,
  source, and history remain intact. Correction actor, UTC time, and bounded reason/evidence may be
  stored only after their retention and privacy contract is approved.

Any future audit/outbox record must be content-minimized and transactionally consistent with the
fact disposition. This specification does not authorize an audit table, event type, migration, or
retention period.

## 3.3 Concurrency, replay, and failure

- Optimistic expected-version checks plus row locking prevent two reviewers from both applying a
  stale disposition. A losing confirm/correct/reject returns `RESOURCE_CONFLICT` and the current
  minimized state; it does not auto-merge.
- Same actor + operation + idempotency key + equivalent request returns the same logical outcome.
  Reuse with a different request returns `409`; keys are bounded and never globally transferable.
- A repeated terminal disposition may be idempotent only when actor scope, target, request and
  resulting state match. It must not rewrite timestamps or provenance.
- Assignment/role revocation, consent change where applicable, or terminal encounter transition is
  rechecked inside the mutation boundary. A stale UI cannot retain authority.
- Fact, provenance, review evidence, and authorized audit/outbox changes commit together or all roll
  back. Ambiguous client timeouts are recovered by idempotency lookup, not blind replay.
- Errors contain stable codes, request correlation and no clinical value, source text, identifiers,
  tokens, prompts, or model output. Telemetry records only bounded operational metadata.

P5 ends at fact persistence, read/provenance capabilities and guarded supersession. P10-D begins at
authenticated clinician disposition APIs, review-specific authorization, lifecycle/audit semantics,
and end-to-end PostgreSQL/HTTP evidence.

# 4. Source-traceable summary read model

## 4.1 Inputs and assertions

A clinically meaningful summary assertion must point to one or more supplied, authorized source
items with source kind, opaque source identifier/reference, verification state and source version
or immutable snapshot identity where available. Summary generation accepts bounded read projections;
it does not query or mutate another module's ORM entities directly.

Inputs retain their type:

- P5 `ClinicalFact`: typed fact plus provenance and verification state;
- P7 structured intake answer/draft: patient-reported, non-diagnostic information pinned to its
  pack/version and never relabeled as a verified clinical fact;
- P8 extraction candidate: detached `AI_EXTRACTED_UNCONFIRMED` candidate only. P8-C Stage 3 remains
  blocked and a candidate cannot enter a production summary path without its separate approvals and
  explicit review;
- P9 synthetic decisions: prohibited as patient or clinician safety content.

Only assertions derived from supplied structured/source-backed inputs are allowed. The generator
must abstain rather than infer a diagnosis, causality, negation, or reassuring absence. Missing
medications/allergies are `UNKNOWN` or `NOT_RECORDED`, never “none,” “no known allergies,” or “not
taking medication” unless an authorized source explicitly supports that assertion.

## 4.2 Versions, edits, and freshness

Each summary is an immutable versioned snapshot with its exact source references and source versions.
Canonical statuses are `DRAFT`, `CLINICIAN_EDITED`, `CONFIRMED`, `REJECTED`, and `SUPERSEDED`.
Clinician edits create a new version and retain per-assertion source links or mark the assertion as a
clinician-authored fact requiring its own governed provenance. A text edit cannot silently create a
canonical diagnosis or fact.

Before display or confirmation, compare current source states/versions with the snapshot. A changed,
rejected, superseded, deleted, or newly relevant source marks the affected summary `STALE` in the
read projection (not a new persisted canonical status without schema approval), identifies bounded
affected sections, and requires regeneration/review. A previously confirmed summary remains
historical; it is not silently rewritten. A source reference is not permanent evidence when access
or source lifecycle has changed.

Summary and source-detail responses are minimized, bounded, `Cache-Control: no-store`, permissioned
per request, and excluded from browser persistence, query strings, logs and telemetry. Unauthorized
or unavailable details yield safe placeholders and stable errors, not raw source fallback.

# 5. Ownership and design gaps

| Concern                       | Owner                                   | Current state / gap                                                                       |
| ----------------------------- | --------------------------------------- | ----------------------------------------------------------------------------------------- |
| Fact lifecycle and storage    | `patients`                              | P5 working; no clinician review service/API.                                              |
| Provenance values and reads   | `provenance`                            | P5 working; source viewer authorization is not implemented.                               |
| Encounter lifecycle/read      | `encounters`                            | Working patient/session scope; clinician assignment source absent.                        |
| Structured intake             | `clinical_intake`                       | P7 deterministic patient flow; not a clinical fact store.                                 |
| Summary domain/read model     | `summaries`                             | **DESIGN-IMPLEMENTATION GAP:** placeholder only; conceptual schema only.                  |
| Clinician identity/assignment | `identity` plus future assignment owner | **OPEN:** provider binding, directory, assignment policy/source and object checks absent. |
| Audit/retention               | future governed owner                   | **OPEN:** no approved review audit persistence or duration.                               |

# 6. Traceability

| Requirement   | Contract in this specification                                            | Future evidence                                     |
| ------------- | ------------------------------------------------------------------------- | --------------------------------------------------- |
| `FR-PROV-001` | Required typed `source_type`.                                             | Unit + PostgreSQL round-trip.                       |
| `FR-PROV-002` | Bounded `source_id`/`source_ref`, separately authorized.                  | Missing/forbidden/source-owner tests.               |
| `FR-PROV-003` | Optional bounded confidence, never clinical certainty.                    | Validation and presentation tests.                  |
| `FR-PROV-004` | Exact states and guarded transition matrix.                               | Domain, concurrency and API tests.                  |
| `FR-PROV-005` | Model/provider/prompt/schema lineage where applicable.                    | Strict serialization tests; P8 gate remains closed. |
| `FR-PROV-006` | Policy version belongs to routing output, not clinical fact confirmation. | P9 boundary tests; no synthetic display.            |
| `FR-PROV-007` | External origin retained when later P16/P17 are approved.                 | Deferred interoperability tests.                    |
| `FR-SUM-008`  | Per-assertion source references and drift detection.                      | Summary unit/PostgreSQL/API tests.                  |
| `AC-P10-005`  | Authorized confirm/correct/reject design.                                 | P10-D real actor + API evidence.                    |
| `AC-P10-006`  | Immutable source/history and linked supersession.                         | Atomic rollback/concurrency tests.                  |
| `AC-P10-007`  | Permissioned source inspection and unavailable state.                     | IDOR/source-access/privacy tests.                   |

# 7. Required future tests

Deterministic unit/fixture tests must cover the transition matrix, lower-trust overwrite refusal,
contradictory sources, missing sources, bounded provenance, drift, and no invented summary assertion.
Real PostgreSQL and HTTP/security tests must separately cover other tenant/patient/encounter/source,
unassigned/disabled/expired actor, withdrawn or missing consent where applicable, terminal encounter,
stale version, concurrent correct+reject and correct+confirm, duplicate/replayed keys, transaction and
outbox failure rollback, retry after ambiguous response, content-free errors, and no PHI in logs,
metrics or traces. Offline synthetic tests are not substitutes for these implementation tests or for
clinical, privacy, identity, data-governance and production approval.
