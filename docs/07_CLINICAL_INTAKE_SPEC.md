# SwasthyaSetu AI
## 07 — Clinical Intake Specification

# Document Control

**Document ID:** `SSAI-INTAKE-007`
**Filename:** `07_CLINICAL_INTAKE_SPEC.md`
**Status:** Canonical P7 Prerequisite / Approved for Implementation
**Version:** `1.0.0`
**Owner:** `clinical_intake` bounded context
**Depends on:** `00_PROJECT_MASTER_SPEC.md`, `01_PRODUCT_REQUIREMENTS.md`, `02_SYSTEM_ARCHITECTURE.md`, `04_DOMAIN_MODEL.md`, `05_DATABASE_SCHEMA.md`, `06_API_CONTRACTS.md`, `29_ENGINEERING_STANDARDS.md`, `34_MASTER_IMPLEMENTATION_PLAN.md`

---

# 1. Purpose, Scope, and Non-Goals

This document defines the authoritative P7 contract for structured clinical intake. It turns the
existing P7 requirements into typed, deterministic domain, persistence, API, capability, and test
contracts. P7 must work without an LLM or any external provider.

P7 includes:

- one structured intake per applicable encounter;
- chief complaint, HPI, history, review-of-systems, and prior-investigation representation;
- versioned question and answer contracts;
- deterministic question-pack selection and missing-information detection;
- careful reuse of reliable longitudinal context through patient public capabilities;
- explicit contradictions and clarification;
- a completed **draft** suitable for later governed use.

P7 does not include diagnosis, treatment, medication advice, emergency or specialty routing,
clinical red-flag thresholds, a clinician-confirmed state, AI extraction, conversational messages,
speech/translation infrastructure, document/OCR flows, or production AYUSH interpretation.

The following remain explicit boundaries:

- `POST /api/v1/intakes/{intake_id}/messages` — **DEFERRED TO P8**;
- physical safety and triage rules — **DEFERRED TO P9 / CLINICAL APPROVAL REQUIRED**;
- voice, ASR, TTS, translation, and fully localized clinical packs — **DEFERRED TO P12**;
- deployment-approved Dashavidha question content — **CLINICAL APPROVAL REQUIRED**.

---

# 2. Requirement Mapping

| Requirement | P7 contract |
|---|---|
| `FR-INTAKE-001` | Chief complaint retains bounded patient wording. |
| `FR-INTAKE-002` | `TEXT` is a supported input mode and answer type. |
| `FR-INTAKE-003` | Voice is representable but disabled; implementation is deferred to P12. |
| `FR-INTAKE-004` | Every P7 question has a touch or text interaction; safety-critical designation awaits P9. |
| `FR-INTAKE-005` | The adaptive engine selects configured questions deterministically. |
| `FR-INTAKE-006` | Eligible reliable history may reduce repetition after explicit confirmation rules. |
| `FR-INTAKE-007` | `ChiefComplaint` is typed and versioned. |
| `FR-INTAKE-008` | `HistoryOfPresentIllness` is typed and versioned. |
| `FR-INTAKE-009` | HPI supports `onset`. |
| `FR-INTAKE-010` | HPI supports `duration`. |
| `FR-INTAKE-011` | HPI supports `location`. |
| `FR-INTAKE-012` | HPI supports `character`. |
| `FR-INTAKE-013` | HPI supports `severity`. |
| `FR-INTAKE-014` | HPI supports `progression`. |
| `FR-INTAKE-015` | HPI supports `associated_symptoms`. |
| `FR-INTAKE-016` | HPI supports `aggravating_factors`. |
| `FR-INTAKE-017` | HPI supports `relieving_factors`. |
| `FR-INTAKE-018` | Typed past-medical-history entries are supported. |
| `FR-INTAKE-019` | Typed past-surgical-history entries are supported. |
| `FR-INTAKE-020` | Typed medication-history entries are supported. |
| `FR-INTAKE-021` | Typed allergy-history entries are supported. |
| `FR-INTAKE-022` | Typed family-history entries are supported. |
| `FR-INTAKE-023` | Typed personal-history entries are supported. |
| `FR-INTAKE-024` | Typed review-of-systems entries are supported. |
| `FR-INTAKE-025` | Typed prior-investigation entries are supported. |
| `FR-INTAKE-026` | Missing information is explicit, machine-readable, and attributable to a pack/rule. |
| `FR-INTAKE-027` | Contradictions retain both references and require explicit clarification. |
| `FR-INTAKE-028` | Question delivery supports one-primary-question mode. |
| `FR-INTAKE-029` | Completion produces a draft, never diagnosis or clinician confirmation. |
| `FR-INTAKE-030` | A disabled-by-default AYUSH extension pack can be registered. |
| `FR-INTAKE-031` | Namespaced field capability exists; production field content requires clinical approval. |
| `FR-INTAKE-032` | Explicit compile-time question-pack registration supports future specialties. |

Applicable `FR-ENC-001..006` are preserved through the existing encounter aggregate. Applicable
`FR-LANG-001`, `FR-LANG-002`, `FR-LANG-005`, and `FR-LANG-007` are represented without claiming
translated clinical packs. `FR-LANG-003..004` and `FR-LANG-006..012` remain P12 work.

P7 must also preserve `PRIV-001..004`, `PRIV-007`, `NFR-ACCESS-001..007`, `NFR-UX-001..006`,
`NFR-SEC-004`, `NFR-SEC-009`, and `NFR-SEC-014`: minimize collected data, enforce object-level
authorization, protect the session bearer, avoid sensitive logs, remain accessible, and state
missing information honestly. `NFR-TEST-001..005` require phase-appropriate unit, domain,
PostgreSQL, API-contract, and real patient-journey tests. `NFR-TEST-006..014` remain applicable only
when their later safety, multilingual, AI, OCR, interoperability, or model scopes are activated.

---

# 3. Terminology

| Term | Meaning |
|---|---|
| intake | The encounter-owned structured draft assembled during P7. |
| answer | A typed patient response, reuse decision, or allowed non-answer to one versioned question. |
| question definition | Immutable versioned configuration describing one question. |
| question pack | An immutable versioned, explicitly registered group of definitions and rules. |
| questionnaire instance | Encounter-specific application state for one registered pack version. |
| known history | Longitudinal patient context obtained through a patient public capability. |
| missing information | An unresolved configured requirement, not a diagnostic inference. |
| contradiction | Two referenced values that cannot be silently reconciled. |
| completed draft | A terminal structured intake; not a diagnosis or clinician-approved record. |

Machine identifiers use bounded ASCII codes. Question IDs are lowercase dotted names such as
`core.hpi.duration`; pack IDs are lowercase dotted or underscore-delimited names; versions are
immutable machine-readable strings. Display text is always resolved from a content/localization key.

---

# 4. Trust and Clinical-Authority Model

P7 records what was provided, reused, skipped, or clarified. It does not decide what is clinically
true. Source and confirmation status must remain visible.

Trust rules:

1. patient-entered answers are patient-reported, not clinician-confirmed;
2. reused history retains its original provenance and verification state;
3. showing or confirming known history does not rewrite the authoritative patient fact;
4. patient disagreement creates a contradiction or update candidate, never a destructive overwrite;
5. rejected and superseded facts are not reusable;
6. no configured question, engine result, or completion state is a diagnosis;
7. an LLM is neither required nor authoritative in P7.

No hidden chain-of-thought is stored. Machine reason codes and source references are sufficient.

---

# 5. Bounded-Context Responsibilities

`clinical_intake` owns:

- the intake aggregate and lifecycle;
- the three P7 tables defined in `05_DATABASE_SCHEMA.md`;
- question/answer/pack contracts and explicit registration;
- deterministic selection, missing-information, and contradiction state;
- its application services, routes, capabilities, events, and tests.

It consumes only public capabilities from sessions, consent, encounters, and patients. It must not
import their ORM models or repositories and must never write their tables.

Conceptual dependency direction is:

```text
sessions -> consent -> patients -> encounters -> clinical_intake
```

PostgreSQL is authoritative. JSONB is only a versioned serialization of the typed structures below,
not unrestricted clinical truth and not a competing longitudinal patient-history store.

---

# 6. Intake Lifecycle

The P7 lifecycle is the closed set:

```text
IN_PROGRESS -> COMPLETED
IN_PROGRESS -> ABANDONED
```

- `IN_PROGRESS` is the only editable state and includes initial, answering, clarification, and review UI.
- `COMPLETED` is terminal and means completed draft only.
- `ABANDONED` is terminal and preserves an incomplete draft for governed retention/resume policy.

An intake is created directly as `IN_PROGRESS`; P7 does not add unsupported clinician-approved or
diagnosis states. The preliminary `DRAFT` and `READY_FOR_REVIEW` labels in the broad domain model are
represented as UI/workflow substates inside `IN_PROGRESS`, not additional P7 persistence states.

`completed_at` is null unless status is `COMPLETED`. It is a timezone-aware UTC instant assigned in
the same transaction as the terminal transition. `ABANDONED` does not misuse `completed_at`.
Terminal states cannot be reopened in P7.

Every mutation requires `expected_version`. A successful mutation increments the positive integer
`version` exactly once; a stale version fails with a conflict and makes no partial write.

---

# 7. Encounter Relationship

P7 enforces one intake per encounter through `clinical_intakes.encounter_id UNIQUE NOT NULL`.

Starting an intake requires an existing, authorized encounter whose type is `GENERAL_INTAKE` or
`KIOSK_INTAKE` and whose state permits intake work (`CREATED` or `IN_PROGRESS`). Mental-health,
clinician-review, document-review, research-only, terminal, or unknown encounters are rejected.

Starting the intake may transition `CREATED` to `IN_PROGRESS` through the encounters public
capability in the same explicitly coordinated application operation. The intake never creates a
competing care episode. Completing or abandoning it does not automatically complete or abandon the
encounter, and it never bypasses the encounter lifecycle.

---

# 8. Session and Consent Prerequisites

P7's activated access path is pseudonymous/session-bound:

```text
subject_type = SESSION
purpose = GENERAL_PRODUCT_USE
required_scope = ["clinical_intake"]
notice_version = privacy-v1 for the current P6 notice
```

Every start, read, answer, complete, and abandon operation must:

1. read the bearer from `Authorization` server-side;
2. call `sessions.validate` for the encounter's exact `session_id`;
3. call centralized `consent.check`/`require_consent` for that session and scope;
4. verify the requested intake belongs to that exact authorized encounter/session.

Cross-session access fails closed. Consent is evaluated at operation time; intake creation or prior
authentication never implies consent. Consent withdrawal blocks later reads and mutations except a
separately governed data-rights workflow.

`PATIENT`-subject consent is not activated in P7. Authenticated patient continuity may reuse trusted
`ActorContext` and patient-self authorization only after its consent contract is explicitly approved.

---

# 9. Structured Intake Aggregate

```text
ClinicalIntake
  intake_id: OpaqueId
  encounter_id: OpaqueId
  status: IN_PROGRESS | COMPLETED | ABANDONED
  chief_complaint: ChiefComplaint?
  hpi: HistoryOfPresentIllness?
  history_sections: HistorySections
  missing_information: tuple[MissingInformation, ...]
  contradictions: tuple[Contradiction, ...]
  started_at: UTC datetime
  completed_at: UTC datetime?
  version: positive integer
```

Collections have deterministic order. The aggregate contains no diagnosis, treatment recommendation,
triage route, safety decision, clinical score, model score, or unrestricted extension bucket.

---

# 10. Chief Complaint Schema

`chief_complaint` JSONB serializes exactly:

```json
{
  "schema_version": "chief-complaint.v1",
  "patient_wording": "bounded patient-provided text",
  "display_key": "core.chief_complaint.other",
  "normalized_code": null,
  "coding_system": null,
  "source_answer_id": "uuid"
}
```

- `schema_version` selects this closed shape.
- `patient_wording` preserves the bounded original wording and is sensitive.
- `display_key` is a configured non-clinical presentation key, not generated interpretation.
- `normalized_code` and `coding_system` are optional configured codes; P7 never requires AI.
- `source_answer_id` references the answer that established the value.

Unknown keys are rejected. Normalization may only come from approved deterministic question-pack
configuration and must not imply diagnosis.

---

# 11. HPI Schema

`hpi` JSONB serializes:

```text
schema_version: hpi.v1
onset: StructuredValue?
duration: DurationValue?
location: StructuredValue?
character: StructuredValue?
severity: SeverityValue?
progression: StructuredValue?
associated_symptoms: list[StructuredValue]
aggravating_factors: list[StructuredValue]
relieving_factors: list[StructuredValue]
```

`StructuredValue` contains `value`, optional `display_key`, and `source_answer_ids`. `DurationValue`
contains a non-negative decimal `value`, a configured unit code, and source references. `SeverityValue`
contains a configured scale ID/version and the selected value; P7 defines no medical threshold or
interpretation. Empty, unknown, or refused values live in answer/missing state rather than fabricated
HPI values. Every field is optional until a registered rule makes it required.

---

# 12. History Sections

`history_sections` JSONB is a closed object:

```text
schema_version: history-sections.v1
past_medical: list[HistoryReference]
past_surgical: list[HistoryReference]
medications: list[HistoryReference]
allergies: list[HistoryReference]
family: list[HistoryReference]
personal: list[HistoryReference]
review_of_systems: list[HistoryReference]
prior_investigations: list[HistoryReference]
```

`HistoryReference` contains:

```text
entry_id: UUID
display_value: bounded typed display value
source_kind: ANSWER | REUSED_HISTORY
source_answer_id: UUID?
source_fact_id: UUID?
verification_state: canonical VerificationState?
confirmation_state: NOT_REQUESTED | PENDING | CONFIRMED | DISAGREED
```

Medication, allergy, procedure, observation, and investigation values align with existing patient
domain types. The intake stores only the minimum snapshot/reference required for an encounter draft;
the patient module remains authoritative for longitudinal facts.

---

# 13. Review of Systems and Prior Investigations

A review-of-systems entry contains configured `system_key`, configured `finding_key` or bounded
patient wording, status `POSITIVE | NEGATIVE | UNKNOWN | NOT_ASKED`, source references, and no
diagnostic interpretation.

A prior-investigation entry contains bounded investigation type, optional date/time, optional
patient-provided result summary, optional document reference, source references, and verification
state. P7 does not interpret ranges, images, or results and does not activate OCR.

---

# 14. Missing-Information Model

Each `missing_information` JSONB item has exactly:

```text
missing_id: UUID
field_or_question_key: bounded machine key
reason_code: REQUIRED_UNANSWERED | CONDITIONAL_UNANSWERED | RECONFIRMATION_REQUIRED | CLARIFICATION_REQUIRED
requiredness: REQUIRED | CONDITIONAL
source_pack_id: machine ID
source_pack_version: version
source_rule_id: machine ID
resolution_state: OPEN | RESOLVED | WAIVED
resolution_answer_id: UUID?
```

`WAIVED` is allowed only when the pack explicitly permits skip/refusal. P7 does not label an item
“clinically relevant” from model intuition; relevance comes only from approved registered rules.

---

# 15. Contradiction Model

Each `contradictions` JSONB item has exactly:

```text
contradiction_id: UUID
field_key: machine key
left_ref: SourceReference
right_ref: SourceReference
source_pack_id: machine ID
source_rule_id: machine ID
status: OPEN | CLARIFICATION_REQUIRED | RESOLVED
resolution_ref: UUID?
created_at: UTC datetime
resolved_at: UTC datetime?
```

`SourceReference` identifies an answer ID or patient fact ID plus its source/verification state; it
does not copy an entire record. Both sides remain available. The engine must not silently choose a
winner, and resolution records what the patient clarified without overwriting longitudinal truth.

---

# 16. Question-Definition Schema

```text
QuestionDefinition
  question_id: lowercase dotted ID
  question_version: immutable version
  section: CHIEF_COMPLAINT | HPI | PAST_MEDICAL | PAST_SURGICAL |
           MEDICATIONS | ALLERGIES | FAMILY | PERSONAL | ROS |
           PRIOR_INVESTIGATIONS | EXTENSION
  content_key: localized prompt key
  help_content_key: localized help key?
  answer_type: AnswerType
  requiredness: REQUIRED | OPTIONAL | CONDITIONAL
  applicability_rule_ids: tuple[RuleId, ...]
  sensitive: bool
  input_modes: non-empty subset of TEXT | TOUCH | VOICE
  validation: ValidationConstraints
  dependency_question_ids: tuple[QuestionId, ...]
  allow_unknown: bool
  allow_prefer_not_to_answer: bool
  history_binding: HistoryBinding?
  order: non-negative integer
```

Initial `AnswerType` is closed:

```text
TEXT
SINGLE_CHOICE
MULTI_CHOICE
BOOLEAN
NUMBER
DATE
DURATION
SEVERITY_SCALE
```

Validation constraints are type-specific and bounded: text length; enumerated option IDs; finite
number range/unit; ISO date bounds; duration units/range; or a configured severity-scale ID/version.
Constraints validate representation only. Any clinically meaningful threshold is **CLINICAL APPROVAL
REQUIRED**. Unknown keys and incompatible constraints fail pack registration.

`VOICE` may be declared as future-capable metadata but cannot be enabled in P7; every active P7
question must include `TEXT` or `TOUCH`.

---

# 17. Answer Schema

`intake_answers.answer` is a closed discriminated object:

```text
schema_version: intake-answer.v1
answer_type: AnswerType
value: type-specific value or null
selected_option_ids: list[machine ID]?
unit: configured machine unit?
response_disposition: ANSWERED | UNKNOWN | PREFER_NOT_TO_ANSWER | SKIPPED
language_code: en | hi | configured future code
original_text: bounded text?
```

Only fields valid for the discriminator may be populated. `SKIPPED`, `UNKNOWN`, and
`PREFER_NOT_TO_ANSWER` are accepted only when the question configuration permits them. The table's
`source_type` is the closed P7 set:

```text
PATIENT_TEXT
PATIENT_TOUCH
REUSED_HISTORY
```

`REUSED_HISTORY` answers must reference the source fact through the aggregate/history representation
and cannot claim patient confirmation unless a separate patient confirmation answer exists. Voice
source types are deferred to P12.

Repeated answers are append-only. The aggregate deterministically selects the newest accepted answer
by `answered_at`, then answer ID, while preserving prior answer references for review/contradiction.

---

# 18. Question-Pack Schema and Registry

```text
QuestionPack
  pack_id: machine ID
  version: immutable version
  schema_version: question-pack.v1
  kind: CORE | COMPLAINT | SPECIALTY | AYUSH_EXTENSION
  approval_state: ENGINEERING_APPROVED | CLINICAL_APPROVAL_REQUIRED | APPROVED
  content_version: immutable version
  supported_languages: tuple[language code, ...]
  applicability_rules: tuple[RuleDefinition, ...]
  contradiction_rules: tuple[RuleDefinition, ...]
  questions: tuple[QuestionDefinition, ...]
  order: non-negative integer
```

The registry uses explicit compile-time registration under ADR-007. Registration rejects duplicate
pack/version or question/version keys, dependency cycles, unresolved rules, unsupported answer
contracts, enabled voice-only questions, and unapproved production packs. No filesystem scanning,
entry-point discovery, remote code, or global mutable service locator is allowed.

P7 ships an engineering-safe core structural pack. Complaint, specialty, and AYUSH content may be
registered later only through reviewed code/configuration and deployment.

---

# 19. Questionnaire-Instance Schema

The `questionnaire_instances` row belongs to the intake's encounter and records one pack application.
Its status is `ACTIVE | COMPLETED | ABANDONED`.

`responses` JSONB serializes exactly:

```text
schema_version: questionnaire-responses.v1
pack_id: machine ID
pack_version: immutable version
answer_refs: ordered list[{question_id, question_version, answer_id}]
skipped_question_refs: ordered list[{question_id, question_version, disposition}]
last_selected_question_id: machine ID?
engine_version: immutable version
```

Answers remain authoritative in `intake_answers`; this object is the versioned pack-instance index,
not a second free-form answer store. `questionnaire_id`/`questionnaire_version` columns equal the
registered `pack_id`/`version`.

---

# 20. Deterministic Adaptive-Engine Contract

Input:

```text
intake state and version
immutable registered pack versions
eligible reliable patient context
prior accepted answers
resolved/open contradictions
```

Output is one of:

```text
NextQuestion(question definition, pack ID/version, reason rule IDs)
ClarificationRequired(contradiction ID, question definition)
CompletionReady(missing_information = empty)
Incomplete(missing_information)
```

Rules are versioned/config-driven predicates over typed fields. P7 permits only deterministic
operators such as existence, equality to configured option IDs, membership, boolean composition,
answer disposition, reliable-history availability, and contradiction state. No arbitrary prompt,
LLM call, model score, diagnosis, or triage rule is allowed.

Evaluation order is stable:

1. validate all input and referenced versions;
2. select applicable enabled pack versions;
3. surface configured open clarification questions;
4. calculate configured missing required information;
5. select the lowest `(pack.order, question.order, pack_id, question_id)` eligible unanswered item;
6. otherwise return completion-ready.

Equal input and registry versions must produce equal output. Engine/version and rule IDs are recorded
for reproducibility. P7 completion is impossible while unresolved required missing information or
required contradictions remain.

---

# 21. Reliable-History Reuse

History is read only through existing `patients.read` / `patients.facts.list` public capabilities or
a future patient-owned public context capability. Direct patient-table access is prohibited.

Deterministic eligibility rules:

- exclude `REJECTED` and `SUPERSEDED` facts;
- use only fact categories explicitly bound by the active pack;
- preserve fact ID, provenance source, and verification state;
- never treat reuse as a patient answer or patient confirmation;
- show/reconfirm the concise value when the pack requires confirmation;
- record patient agreement as a new answer reference;
- record disagreement as a contradiction/update candidate;
- never write or supersede a patient fact from the intake module.

P7 does not invent a trust threshold. Each permitted verification state for reuse must be explicitly
approved in pack metadata. Until approved, reuse may be shown for confirmation but cannot suppress a
required question.

---

# 22. Source and Provenance Semantics

Every answer records source type, question/version, pack/version, and UTC time. Reused values retain
the patient fact ID and canonical verification state. Original patient wording is retained only where
needed and is treated as health-sensitive.

Intake completion does not publish longitudinal clinical facts. Any future promotion to patient
history belongs to a separate governed reconciliation workflow that preserves provenance and the
existing supersession guard.

---

# 23. AYUSH Extension Architecture

An AYUSH extension is a normal explicitly registered `AYUSH_EXTENSION` pack with:

- a namespaced pack and question ID prefix;
- immutable schema/content versions;
- approval metadata;
- the same typed answer and provenance rules;
- no independent engine or persistence silo.

The extension capability exists for `FR-INTAKE-030..031`. Actual Dashavidha fields, interpretation,
Prakriti/Dosha scoring, thresholds, remedies, treatment, and diagnostic logic are **CLINICAL APPROVAL
REQUIRED** and are not production content in P7.

---

# 24. Accessibility, Input Modes, and Language Boundary

Every P7-C question must support keyboard operation, programmatic labels/instructions, visible focus,
accessible errors, 44px targets, 320px/390px reflow, reduced motion, forced colors, and persistent
urgent help. One-primary-question mode is the default for sensitive/complex sections.

P7 supports text and touch. Current session language preferences are `en` and `hi`, but a language
preference is not proof that a reviewed Hindi clinical pack exists. If a localized prompt is missing,
the UI must honestly state unavailability rather than silently machine-translate. Speech, TTS,
translation, Hinglish, and romanized-Hindi processing remain P12-owned.

---

# 25. API Contracts

All responses use `Cache-Control: no-store`, typed schemas, the common error envelope, server-side
authorization, and no bearer echo. `expected_version` is required for mutations after start.

## 25.1 Start intake

`POST /api/v1/encounters/{encounter_id}/intake`

- authorization: exact session bearer for the encounter;
- consent: active session consent covering `clinical_intake`;
- request: `{ "pack_ids": ["core.intake"] }`, with server-controlled versions;
- response: intake view, version, and next-question state;
- state: creates `IN_PROGRESS`, and coordinates permitted encounter start;
- idempotency: encounter uniqueness is the durable key; an existing authorized intake is returned
  rather than duplicated; conflicting pack request returns `409`.

## 25.2 Read intake

`GET /api/v1/intakes/{intake_id}`

- authorization/consent: revalidated for the exact session and encounter;
- response: minimized structured state, source labels, missing/contradiction summaries, version, and
  next-question state; no raw unrelated longitudinal record;
- state: none; GET is safe and idempotent.

## 25.3 Record answer

`POST /api/v1/intakes/{intake_id}/answers`

```json
{
  "question_id": "core.hpi.duration",
  "question_version": "1.0.0",
  "answer": {"schema_version": "intake-answer.v1", "answer_type": "DURATION", "value": 2, "unit": "day", "response_disposition": "ANSWERED", "language_code": "en"},
  "source_type": "PATIENT_TOUCH",
  "expected_version": 3
}
```

- authorization/consent: revalidated;
- response: new version, accepted answer reference, next-question state, missing information, and
  contradiction summaries;
- state: allowed only while `IN_PROGRESS`; answer plus aggregate/instance update are atomic;
- idempotency: clients must not blindly retry an ambiguous failure. If `Idempotency-Key` is supplied,
  the standard actor/session + operation semantics apply; same key/different request is `409`.

## 25.4 Complete intake

`POST /api/v1/intakes/{intake_id}/complete`

Request: `{ "expected_version": 8 }`.

- authorization/consent: revalidated;
- state: atomic `IN_PROGRESS -> COMPLETED`, with UTC `completed_at` and version increment;
- validation: all configured required items resolved and required contradictions clarified;
- idempotency: a repeated authorized completion returns the completed draft; a stale conflicting
  mutation returns `409`.

## 25.5 Abandon intake

An abandon capability is required by the lifecycle. P7-C may expose
`POST /api/v1/intakes/{intake_id}/abandon` with `{ "expected_version": n }`; if not exposed, ending
the session does not silently mutate the intake and it remains resumable until governed retention.
Final endpoint activation is an **OPEN DESIGN DECISION** for P7-C.

## 25.6 Deferred messages

`POST /api/v1/intakes/{intake_id}/messages` is **DEFERRED TO P8** and excluded from all P7 acceptance.

---

# 26. Persistence Mapping

P7-A implements only the existing future tables:

| Table | Typed ownership |
|---|---|
| `clinical_intakes` | Aggregate identity, lifecycle, version, and the five versioned JSON projections. |
| `intake_answers` | Immutable typed answer records and source type. |
| `questionnaire_instances` | Applied pack/version state and typed response-reference index. |

Required constraints include one intake per encounter, known status/source values, positive version,
UTC timestamps, completed-at/status consistency, foreign keys, and JSON object/array shape checks
where PostgreSQL can enforce them. Application deserialization must reject unknown schema versions,
unknown keys, malformed values, and references to unregistered question/pack versions.

All three tables are owned solely by `clinical_intake`. No new table is authorized by this spec.

---

# 27. Concurrency and Idempotency

Aggregate changes use one PostgreSQL transaction and optimistic `version`. Answer insertion,
questionnaire-instance update, aggregate projections, missing/contradiction recomputation, event
outbox write, and version increment succeed or roll back together.

The encounter unique constraint makes start race-safe. Stale writes fail with `409 RESOURCE_CONFLICT`.
The server never merges two concurrent clinical answers silently. Mutation retries follow the common
idempotency contract; the browser has no offline queue or replay mechanism.

---

# 28. Privacy and Logging

Health-sensitive fields include raw chief complaint/HPI, answers, medication/allergy content,
family/personal history, ROS, investigations, and contradictions.

Never log these values, full consent payloads, `Authorization`, session tokens, or unrestricted
request/response bodies. Operational telemetry may include request ID, operation, status, duration,
error code, non-sensitive question/pack IDs, and immutable version IDs. API and BFF responses are
`no-store`; browser storage and Cache Storage must not contain intake data.

---

# 29. Error Model

P7 uses the common error envelope. Expected codes include:

```text
AUTHENTICATION_REQUIRED
AUTHORIZATION_DENIED
CONSENT_REQUIRED
SESSION_EXPIRED
RESOURCE_NOT_FOUND
RESOURCE_CONFLICT
VALIDATION_ERROR
INVALID_STATE_TRANSITION
DEPENDENCY_UNAVAILABLE
```

Validation details may identify machine field/question keys but must not echo sensitive answers.
Missing approved pack/localization content fails honestly; it is never replaced with generated content.

---

# 30. Public Capabilities and Events

Candidate public capability IDs are:

```text
intake.start
intake.read
intake.answer
intake.complete
intake.next_question
```

An abandon capability may be added only with the P7-C decision above. The module manifest requires
`sessions.validate`, `consent.check`, encounter read/transition capabilities, and patient public read
capabilities. Composition remains explicit and compile-time.

Useful versioned outbox events are:

```text
ClinicalIntakeStarted
ClinicalIntakeAnswerRecorded
ClinicalIntakeCompleted
ClinicalIntakeAbandoned
```

Payloads contain IDs, status, aggregate version, pack/engine version, and timestamps—not full raw
history or answers. Delivery is at-least-once; consumers must be idempotent.

---

# 31. Testing Requirements

P7-A tests domain invariants, closed serialization, unknown-version rejection, migration constraints,
one-intake uniqueness, pseudonymous encounter linkage, optimistic concurrency, atomic rollback,
compile-time pack registration, dependency-cycle rejection, and AYUSH registration without content.

P7-B tests deterministic next-question selection, stable tie-breaking, missing fields, configured
skip/refusal, repeatability, history eligibility, rejected/superseded exclusion, confirmation,
contradictions, pack/version behavior, and zero LLM/network dependency.

P7-C tests real PostgreSQL and APIs, exact-session IDOR protection, consent withdrawal, stale writes,
resume/review/complete, P6 cookie/BFF security, keyboard operation, reflow, privacy/no-cache rules,
and absence of diagnostic language or browser persistence.

---

# 32. P7-A / P7-B / P7-C Ownership

| Unit | Owns |
|---|---|
| P7-A | Domain types, closed serializers, module skeleton/manifest, three tables, migration, repositories, registry contracts. |
| P7-B | Deterministic engine, pack registration/validation, history reuse, missing/contradiction logic, repeatability tests. |
| P7-C | Thin APIs, authorization/consent integration, BFF/client/UI, resume/review/complete journeys, real E2E. |

No unit may pull P8, P9, P12, or later-domain implementation forward.

---

# 33. Deferred Work

- AI/conversational extraction and `/messages`: P8.
- physical safety policy, red flags, emergency criteria, triage: P9 and clinical approval.
- clinician review/confirmation and summaries: P10.
- documents/OCR: P11.
- speech, TTS, translation, and clinical localization expansion: P12.
- mental-health routing: P14.
- patient-subject consent and authenticated continuity activation: separately governed future work.
- promotion of intake statements into longitudinal facts: future reconciliation workflow.

---

# 34. Open Decisions

1. **OPEN DESIGN DECISION:** whether P7-C exposes the explicit abandon endpoint or retains incomplete
   `IN_PROGRESS` state when a session ends.
2. **OPEN DESIGN DECISION:** approved P7 core question wording, requiredness rules, option sets, and
   localized Hindi content. Structural synthetic fixtures may be used until approval.
3. **CLINICAL APPROVAL REQUIRED:** reusable verification-state allowlist that may suppress a question.
4. **CLINICAL APPROVAL REQUIRED:** all AYUSH/Dashavidha production fields and content.
5. **DEFERRED:** retention/deletion durations pending privacy governance.

None of these decisions authorizes invented clinical content. P7-A can implement contracts and safe
synthetic fixtures; production activation waits for the applicable approval.

---

# 35. AC-P7 Traceability

| Criterion | Future evidence | Unit |
|---|---|---|
| `AC-P7-001` | Start succeeds with registered deterministic core pack and no LLM. | P7-A/P7-C |
| `AC-P7-002` | Typed chief-complaint round trip. | P7-A |
| `AC-P7-003` | All required HPI fields serialize and round trip. | P7-A |
| `AC-P7-004` | Six required history groups represent typed entries. | P7-A |
| `AC-P7-005` | ROS and investigations represent typed entries. | P7-A |
| `AC-P7-006` | Equal input/version produces equal next question. | P7-B |
| `AC-P7-007` | Eligible history reduces repetition only under explicit rules. | P7-B |
| `AC-P7-008` | Compile-time specialty pack fixture registers without engine changes. | P7-A/P7-B |
| `AC-P7-009` | AYUSH extension fixture registers with no production clinical content. | P7-A/P7-B |
| `AC-P7-010` | Completion remains a draft and exposes no diagnosis state/content. | P7-A/P7-C |

All criteria remain **NOT YET IMPLEMENTED** until their future phase evidence passes.
