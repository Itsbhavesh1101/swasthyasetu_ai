# SwasthyaSetu AI
## 26 — Privacy and Consent Specification

**Document ID:** `SSAI-PRIV-026`
**Status:** Canonical privacy baseline; external-AI decisions remain approval-gated
**Version:** `1.0.0-draft`

---

# 1. Purpose and precedence

This specification consolidates the implemented P4–P7 privacy/consent boundary and defines the
decision gate for future P8 processing. It supports `PRIV-001..009`, `NFR-SEC-012..014`,
`FR-CORE-007`, and `FR-CORE-008` without claiming legal or regulatory compliance.

Approved clinical/safety policy, the Project Master Specification, System Architecture, Product
Requirements, and applicable law/governance decisions outrank implementation convenience.

---

# 2. Current implemented P4–P7 boundary

The current pseudonymous intake path uses:

```text
Authorization: Bearer <exact opaque session token>  # server-side only
subject_type = SESSION
purpose = GENERAL_PRODUCT_USE
scope includes clinical_intake
notice_version = privacy-v1
```

Every protected intake operation validates the exact bearer through `sessions.validate`, checks
active centralized consent for the exact subject/purpose/scope, and checks encounter/intake
ownership. Session creation or authentication never implies consent. Consent withdrawal blocks
later protected operations but does not silently close the session or erase governed server state.

`privacy-v1` is the implemented engineering notice boundary, not a jurisdiction-wide legal approval.
`PATIENT`-subject intake consent and authenticated continuity remain unactivated.

---

# 3. Patient web/BFF boundary

The patient browser receives only transient `HttpOnly`, `SameSite=Strict`, `Path=/` session cookies;
`Secure` applies in production/non-loopback use. The opaque bearer is read and forwarded by the BFF
server only. It is never exposed to client JavaScript, props, response bodies, browser
`Authorization` headers, or logs.

Clinical/session/consent responses use `Cache-Control: no-store`. Clinical data, session state, and
bearers must not enter:

```text
localStorage
sessionStorage
IndexedDB
Cache Storage or service-worker runtime caches
background sync/replay queues
URLs or query strings
analytics/session replay
logs, traces, metrics, or exception responses
```

The PWA cache remains limited to the approved generic shell allowlist. BFF validation rejects
malformed backend responses and does not relay raw failure bodies.

---

# 4. Data classification and minimization

Health-sensitive data includes utterances, chief complaint/HPI, answers, medications, allergies,
history, review of systems, investigations, contradictions, extracted candidates, evidence spans,
prompts containing patient context, and provider raw responses.

Collection and processing must be limited to the active documented purpose. Internal IDs and
version metadata are not automatically safe when linkable to a person; telemetry uses only the
minimum bounded operational metadata. No downstream capability receives an unrestricted patient
record when a smaller approved projection suffices.

---

# 5. Consent is not transitive

The implemented `GENERAL_PRODUCT_USE` consent covering `clinical_intake` authorizes the current
first-party deterministic intake operations only within their approved notice. It must not be
interpreted as automatic authorization for:

- third-party LLM/model processing or cross-border transfer;
- provider training, human review, or provider retention;
- research/export, referral sharing, ABDM exchange, or institutional analytics;
- future speech, translation, OCR, RAG, mental-health, or self-care processing.

Authentication, session creation, intake creation, feature enablement, or prior consent for another
purpose does not imply these uses.

---

# 6. External-model egress decision gate

Until every applicable item below is approved, **no real patient data may be sent to an external
model provider**:

1. named operation and demonstrated minimum-necessary fields;
2. provider/model/endpoints and permitted deployment environments;
3. purpose, lawful/governance basis, user information, and whether additional affirmative consent
   or notice is required;
4. processing region, transfer mechanism, retention, deletion, training use, abuse monitoring,
   human review, and subprocessors;
5. institutional DPA/procurement, security, regulatory, and clinical review;
6. credentials, network egress allowlist, access control, incident and breach handling;
7. data-flow/threat model and test evidence for logs, traces, retries, errors, and support tooling;
8. withdrawal/deletion behavior and effect on in-flight or provider-retained data;
9. documented fallback that preserves deterministic intake and generic urgent help.

Approval must be operation- and deployment-specific. A provider adapter existing in code is not
approval, and feature flags cannot substitute for consent or policy.

---

# 7. In-memory processing and retention defaults

P8 request context and provider raw output are held in memory only for the bounded operation by
default. Raw provider responses, rendered prompts, hidden reasoning, and complete message bodies are
not persisted or exported to telemetry by default.

The system may persist only approved structured candidates and provenance references in a future
P8-C design, and only after its schema, purpose, authorization, retention, deletion, and transaction
semantics are approved. Research/evaluation retention requires a separate isolated workflow and
approved dataset; production patient data cannot silently become research data.

No retention duration is invented here. `PRIV-003`, `PRIV-004`, legal holds, backup deletion, and
provider deletion remain **PRIVACY/SECURITY APPROVAL REQUIRED**.

---

# 8. Telemetry, audit metadata, and error privacy

Permitted operational/audit-safe metadata may include:

```text
safe request correlation ID
operation and normalized status/error category
prompt/schema/provider/model version identifiers
feature/configuration state
attempt count, latency, bounded usage
approval/policy version references
actor/subject class where non-identifying and necessary
```

Prohibited metadata includes raw patient text, source spans, provider raw output, full structured
clinical payloads, names/identifiers, bearer/cookies, credentials, consent bodies, and SQL/internal
exceptions. Opaque patient/session/encounter IDs are excluded from generic telemetry unless a
separately approved audit record requires access-controlled linkage.

Audit records capture who/what/when/purpose/version/outcome without duplicating health content.
Access to retained candidates/messages/provenance must use server-side least privilege and exact
subject/object authorization.

---

# 9. Withdrawal, deletion, and in-flight work

Consent is rechecked at protected operation time. Withdrawal blocks new processing under that
consent. The future P8-C design must define the consistency boundary for an operation already in
flight, cancellation behavior, and whether any completed structured candidate remains under an
approved retention basis.

Withdrawal is not a promise of immediate deletion from every governed store. Deletion requests,
legal retention, backups, provider deletion, and audit preservation require explicit workflows and
honest user copy. The current P4–P7 contracts are unchanged by this documentation unit.

---

# 10. India DPDP and healthcare review

The platform is intended to remain compatible with a future India DPDP/healthcare legal review, but
this specification does not claim compliance, select a lawful basis, set age/guardian rules, define
cross-border legality, or approve a notice. These require counsel/institutional privacy review and
current deployment facts.

---

# 11. Traceability

| Requirement | Policy evidence | Status |
|---|---|---|
| `PRIV-001` | Sections 4 and 6 require minimum-necessary input. | SPECIFIED / P4–P7 BASELINE IMPLEMENTED |
| `PRIV-002` | Sections 5–6 prevent purpose/consent inference. | SPECIFIED |
| `PRIV-003` | Section 7 requires explicit retention; duration unresolved. | APPROVAL REQUIRED |
| `PRIV-004` | Section 9 requires governed deletion/withdrawal workflows. | PARTIAL / FUTURE |
| `PRIV-005` | Referral payload remains separately minimized and out of P8. | DEFERRED TO P13 |
| `PRIV-006` | Unnecessary identity collection remains prohibited. | SPECIFIED |
| `PRIV-007` | Sections 3 and 8 prohibit sensitive logs. | IMPLEMENTED BASELINE / FUTURE TESTS REQUIRED |
| `PRIV-008` | Section 7 separates research and production data. | SPECIFIED |
| `PRIV-009` | Section 8 excludes identifiable conversation analytics. | SPECIFIED |
| `NFR-SEC-013` | External AI receives only approved minimum context. | FUTURE — NOT VERIFIED |

---

# 12. Open decisions

1. **PRIVACY/SECURITY APPROVAL REQUIRED:** external-provider egress, purpose/legal basis, region,
   retention, deletion, training use, human review, subprocessors, DPA, and additional consent.
2. **OPEN DESIGN DECISION:** P8-C message/candidate persistence and in-flight revocation consistency.
3. **PRIVACY/SECURITY APPROVAL REQUIRED:** exact retention/deletion schedules and final notice(s).
4. **CLINICAL APPROVAL REQUIRED:** clinical prompt/content and confirmation workflow.
