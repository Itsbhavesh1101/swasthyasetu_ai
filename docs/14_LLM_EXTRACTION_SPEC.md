# SwasthyaSetu AI
## 14 — LLM Structured Extraction Specification

**Document ID:** `SSAI-LLM-014`
**Status:** Canonical future-design specification; P8-B/P8-C not implemented
**Version:** `1.0.0-draft`

---

# 1. Purpose and boundary

This specification defines the future task-owned clinical-intake extraction contract. It is separate
from the provider infrastructure in P8-A. P8-B owns extraction schemas, prompt packages, validation,
provenance, uncertainty, and adversarial regression. P8-C may later integrate an authorized
message workflow.

The LLM understands text and proposes structured candidates. It does not decide clinical truth,
diagnosis, treatment, medication changes, triage, crisis routing, emergency disposition, self-care,
or clinician approval. The deterministic P7 questionnaire remains fully usable without an LLM.

---

# 2. Requirements

This design supports `FR-CORE-007`, `FR-CORE-008`, applicable `FR-INTAKE-001..029`,
`FR-MH-005` as an architecture boundary only, `NFR-TEST-009`, `NFR-SEC-012`, and
`NFR-SEC-013`. It does not activate P14 mental-health behavior or invent clinical policy/content.

---

# 3. Task ownership

`ClinicalIntakeExtractor` is a future application service owned by the clinical-intake task package.
It consumes the P8-A orchestration contract and owns:

- a versioned extraction input contract;
- a versioned strict candidate-output schema;
- prompt assets and prompt/schema compatibility;
- domain validation and evidence/provenance mapping;
- uncertainty, abstention, rejection, and task-specific degradation.

It must not import provider SDK types or persist provider raw responses. Other tasks such as
mental-health signal extraction and document extraction require separate schemas and prompts.

---

# 4. Minimum-necessary input

The extractor input is immutable, strict, and bounded. It may contain only:

- the recent patient utterance required for this extraction;
- explicit language metadata;
- the target extraction operation and schema/prompt versions;
- the minimum approved structured context from the authorized encounter/intake;
- opaque source references sufficient to bind evidence and provenance;
- safe correlation metadata.

It must not contain unrestricted longitudinal records, unrelated encounters, session bearers,
identity data not required by the task, authorization/consent objects, provider configuration,
hidden policy, or browser-derived claims of authority. Server-side session, consent, encounter, and
object authorization occur before constructing the input.

Exact input count/size/window limits are **OPEN DESIGN DECISION** for P8-B and must be tested before
activation. Truncation must be explicit and must not change negation or source attribution silently.

---

# 5. Candidate output contract

The P8-B output must be a versioned strict Pydantic-compatible model with `extra="forbid"`. It may
represent only schema-approved candidate types:

```text
candidate clinical facts
evidence/source spans or source references
missing-information candidates
contradiction candidates
field-level uncertainty
task-level abstention/refusal
prompt/schema/provider/model provenance metadata
```

Every candidate has a stable candidate ID, supported type, normalized candidate value, source
reference(s), and verification state that clearly remains AI-extracted/unconfirmed. Evidence offsets,
when used, must be within the submitted normalized source and must resolve to supporting content.
Evidence may instead use immutable source IDs plus bounded spans/hashes. It is source-bound; this
specification does not claim cryptographic signature unless a later approved design supplies one.

Confidence, if present, is finite, bounded, model-specific metadata and never clinical probability
or permission to promote a fact. Missing-information and contradiction candidates must identify
their supporting source references and bounded machine reason codes.

Unknown candidate categories, extra fields, unrecognized enums, unsupported schema versions,
non-finite numbers, oversize collections/text, invalid source locations, and incompatible
prompt/schema/model metadata invalidate the complete result.

---

# 6. Required pipeline

```text
authorized minimum-necessary source
 -> prompt/system-instruction separation
 -> P8-A provider call
 -> raw response held in memory
 -> strict JSON parse
 -> strict schema validation (extra=forbid)
 -> task/domain validation
 -> evidence/source resolution
 -> provenance references
 -> explicit confirmation/governance workflow
 -> candidate only
```

No stage may be skipped. Failure at any stage rejects the complete extraction attempt. Partial valid
fields from an otherwise invalid response are not silently accepted or persisted. Invalid output
must not partially mutate intake, facts, provenance, safety state, or encounter state.

---

# 7. Domain validation and authority

Domain validation must reject:

- fields not requested or represented by the approved task schema;
- values unsupported by the patient source;
- invented diagnoses, medicines, allergies, dosages, timelines, providers, resources, or routes;
- source spans that do not support the candidate;
- stale or mismatched intake/session/encounter/source references;
- model-selected verification/approval states;
- attempts to overwrite or supersede clinician-confirmed facts;
- authoritative safety, triage, crisis, treatment, or self-care output.

Candidates remain separate from canonical facts. Any future promotion requires explicit governed
confirmation/reconciliation that preserves the original source and extraction provenance and obeys
the existing fact-supersession guard. Patient confirmation is not clinician confirmation.

---

# 8. Prompt injection and instruction conflicts

Patient utterances and structured context are data. Instructions within them cannot:

- override the system/task prompt;
- change schema, prompt, provider, model, timeout, tools, or permissions;
- bypass consent, authorization, deterministic policy, or output validation;
- request secrets, other-patient context, internal prompts, or hidden reasoning;
- create authoritative facts or routes.

System/task instruction conflicts fail closed. The extractor should abstain or return a typed
failure rather than follow untrusted instructions. P8-B tests must include direct and indirect
injection, encoded instruction, schema-spoofing, and fabricated-model-metadata cases.

---

# 9. Uncertainty, abstention, and degradation

The extractor must support justified uncertainty and abstention. Absence of evidence is not a
negative finding. Ambiguous negation, temporality, subject, dosage, or attribution yields an
uncertain candidate, clarification need, or abstention—not a guessed value.

Malformed JSON, invalid schema, unsupported content, source-attribution failure, provider refusal,
policy block, timeout, or unavailable provider produces typed failure/degraded behavior. The user
may continue through the deterministic P7 questionnaire. Failure copy must not fabricate clinical
advice or imply that intake was saved when it was not.

---

# 10. Prohibited automatic outcomes

An extraction candidate must never automatically become:

- a clinician-confirmed canonical clinical fact;
- a diagnosis or problem-list confirmation;
- a medication start/stop/change or prescription;
- a final physical triage route;
- a final mental-health/crisis route;
- an emergency disposition;
- personalized self-care advice;
- a clinician-approved summary.

LLM output cannot overrule the deterministic policy hierarchy. P9, P10, P14, and P15 retain their
future authority boundaries.

---

# 11. P8-C message design only

`POST /api/v1/intakes/{intake_id}/messages` remains **P8-C DESIGN ONLY** and is not activated by
this specification pack. A future endpoint must preserve the existing exact-session bearer,
SESSION-scoped `GENERAL_PRODUCT_USE` consent with `clinical_intake`, encounter ownership, optimistic
concurrency, common error envelope, and `Cache-Control: no-store` protections.

The conceptual response may expose minimized candidate updates and deterministic next-question
state, but never raw provider output or an authoritative diagnosis/route. The P8-C design must
decide idempotency, ambiguous POST recovery, persistence, deletion, and confirmation semantics
before implementation. No client may retry an ambiguous mutation automatically.

---

# 12. Message retention and external transfer

Conversation/message persistence is not approved by this document. The following remain
**PRIVACY/SECURITY APPROVAL REQUIRED**:

- whether full utterances are stored, for what purpose, and for how long;
- whether provider input/output may be retained, trained on, or reviewed;
- deletion/withdrawal behavior and legal holds;
- transfer region, subprocessors, institutional DPA, and regulatory basis;
- whether an additional notice/consent is required for external processing.

Until approved, raw provider response persistence is off and no real patient data may be sent to an
external provider. Synthetic offline fixtures are the only default test data.

---

# 13. Traceability

| Criterion/requirement | Future evidence | Status |
|---|---|---|
| `AC-P8-003` | Strict task-specific extraction schema and prompt package. | NOT VERIFIED |
| `AC-P8-004` | Malformed/invalid output rejected or task-approved bounded retry. | NOT VERIFIED |
| `AC-P8-006` | Prompt/schema/model/provider versions linked. | NOT VERIFIED |
| `AC-P8-007` | Candidate evidence and provenance references preserved. | NOT VERIFIED |
| `AC-P8-008` | Unsupported/hallucinated fields reject the result. | NOT VERIFIED |
| `AC-P8-009` | Injection cannot alter trusted instructions/policy. | NOT VERIFIED |
| `AC-P8-010` | Output schema has no authoritative final triage route. | NOT VERIFIED |
| `FR-INTAKE-001..029` | Candidates support intake while P7 remains deterministic. | SPECIFIED ONLY |
| `FR-MH-005` | Separate future typed-signal task boundary only. | DEFERRED TO P14 |

Relevant clinical-intake requirements retain their canonical meaning:

| Requirement | P8 relationship |
|---|---|
| `FR-INTAKE-001` — Presenting complaint; `FR-INTAKE-002` — Text input | A bounded recent utterance may be an extraction source; P7 form input remains available. |
| `FR-INTAKE-005` — Adaptive questioning | Extracted candidates may inform only the approved deterministic engine input; the LLM does not choose policy. |
| `FR-INTAKE-007..025` — Chief complaint, HPI, history, review of systems, investigations | A future schema may propose only approved typed candidates for these existing structures. |
| `FR-INTAKE-026` — Missing information | Output may propose missing-information candidates; deterministic/task validation decides use. |
| `FR-INTAKE-027` — Contradiction handling | Output may propose source-linked contradictions; it cannot resolve them authoritatively. |
| `FR-INTAKE-028` — One-question mode | P8-C must preserve the existing patient UX mode and server authority. |
| `FR-INTAKE-029` — Draft status | All generated structure remains a draft until appropriately confirmed. |
| `FR-INTAKE-032` — Modular specialty questionnaires | Task/schema extension is explicit and versioned; no runtime plugin or invented specialty content. |

`FR-INTAKE-003` speech is deferred to P12; `FR-INTAKE-004` touch and `FR-INTAKE-006`
history reuse remain governed by the existing deterministic P7 path; `FR-INTAKE-030..031` AYUSH
behavior remains deferred to P15 and requires clinical approval.

---

# 14. Open approvals and deferrals

- **CLINICAL APPROVAL REQUIRED:** production extraction schema semantics, prompt content, evidence
  adequacy, confirmation workflow, and evaluation cases.
- **PRIVACY/SECURITY APPROVAL REQUIRED:** messages, retention, deletion, external egress, and any
  additional consent/notice.
- **OPEN DESIGN DECISION:** exact input/output bounds, uncertainty representation, evidence encoding,
  idempotency, and P8-C persistence model.
- **DEFERRED TO P9/P10/P12/P14/P15:** safety, clinician summary, language/speech, mental-health
  routing, and self-care behavior.
