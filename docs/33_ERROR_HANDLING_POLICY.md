# SwasthyaSetu AI
## 33 — Error Handling Policy

**Document ID:** `SSAI-ERR-033`
**Status:** Canonical error/degradation policy; P8 error types are future design
**Version:** `1.0.0-draft`

---

# 1. Purpose

This policy defines safe error propagation across domain/application code, external adapters,
orchestration, APIs, BFFs, and patient UI. Failures are typed, observable, privacy-safe, and honest.
No layer may swallow a material failure or fabricate success.

---

# 2. Existing application error contract

The implemented API envelope remains:

```json
{
  "error": {
    "code": "DEPENDENCY_UNAVAILABLE",
    "message": "This feature is temporarily unavailable.",
    "request_id": "req_...",
    "details": {}
  }
}
```

`code` is stable and machine-readable; `message` is safe for users; `request_id` is an opaque safe
correlation ID; `details` is bounded and must not contain stack traces, class names, SQL, secrets,
tokens, provider payloads, prompts, patient text, or internal topology.

Existing `ErrorCode` values and their HTTP mappings remain authoritative. This documentation-only
unit adds no runtime enum, handler, endpoint, or transport mapping.

---

# 3. Layered exception model

```text
provider/transport exception
 -> adapter normalized dependency failure
 -> orchestration typed outcome/failure
 -> task-specific application error/degraded result
 -> approved HTTP translation at API boundary
 -> minimized BFF error
 -> patient-safe UI state
```

Domain code raises domain validation/state errors and does not know HTTP or provider exceptions.
Adapters catch only exceptions they can classify, preserve the cause internally where safe, and
never expose vendor exception objects. Application services decide task degradation and transaction
semantics. Only API error handlers translate approved application codes to HTTP.

Unexpected errors become the existing safe processing failure, retain server-side correlation, and
do not expose internal messages.

---

# 4. Current error families

The existing registry includes validation, authentication, authorization, consent/session,
not-found, conflict/state-transition, feature/policy, rate-limit, dependency timeout/unavailable,
processing, insufficient-information, media-type, and payload-size errors.

Use the narrowest existing code that accurately describes a public failure. Object-level
authorization must not reveal another subject's resource. Validation details may identify bounded
machine field keys but cannot echo submitted health text.

All clinical/session/consent/intake success and error responses use `Cache-Control: no-store`.

---

# 5. Future P8 provider failure categories

The following are internal future design categories, not new public `ErrorCode` values in this phase:

```text
LLM_TIMEOUT
LLM_RATE_LIMIT
LLM_AUTH_FAILURE
LLM_PROVIDER_UNAVAILABLE
LLM_REFUSAL
LLM_SCHEMA_INVALID
LLM_CONTENT_POLICY_BLOCK
LLM_UNKNOWN
```

Each typed failure carries only bounded operational fields such as category, operation, safe
request ID, retry eligibility, attempt count, and version identifiers. It excludes raw request,
raw response, credentials, endpoints with secrets, provider exception text, and patient identifiers.

**OPEN DESIGN DECISION:** P8 implementation must decide whether any new public error codes are
needed. Until approved, adapters/orchestration map to existing application dependency/validation/
processing codes at the task boundary without leaking provider-specific categories publicly.

---

# 6. Retry eligibility

| Failure | Retry policy |
|---|---|
| Timeout | Bounded retry only if operation policy permits and total deadline remains. |
| Rate limit | Bounded retry only when an allowed delay fits the deadline. |
| Selected transient 5xx/unavailable | Bounded retry according to versioned policy. |
| Structured-format/schema failure | No infrastructure retry; an approved task may issue one separately recorded bounded repair request without weakening schema. |
| Authentication/configuration | No retry; fail closed and alert operationally. |
| Content-policy block | No automatic retry with evasion/rephrasing. |
| Refusal | No retry unless task policy defines a materially different safe request. |
| Caller validation/version mismatch | No retry; caller/task defect. |
| Cancelled/exhausted deadline | No retry. |
| Unknown | No retry by default. |

Retries use one total deadline and bounded attempt budget. They cannot silently change provider,
model, region, context, consent purpose, prompt/schema version, temperature policy, or clinical
authority. Side-effecting/ambiguous operations require explicit idempotency before retry.

---

# 7. Structured-output failures

Invalid JSON, unexpected fields, missing required values, unsupported versions, spoofed metadata,
bad source references, non-finite numbers, oversize output, and domain-invalid candidates fail
closed. No partial fields are promoted, persisted, emitted as facts, or passed into deterministic
safety logic.

Provider success does not override parser/schema/domain failure. A repair attempt, if approved, is
a new recorded attempt under the same deadline and does not expose invalid output to the patient.

---

# 8. Disabled, unconfigured, and degraded modes

The AI capability defaults disabled/unconfigured. Its caller receives a typed unavailable/degraded
outcome and uses the task-approved fallback. For clinical intake, the fallback is the existing P7
deterministic questionnaire/manual text/touch flow or an honest optional-feature-unavailable state.

An external timeout or outage cannot:

- mark an extraction/intake mutation successful;
- remove or block deterministic intake;
- remove generic urgent-help navigation;
- fabricate a result, diagnosis, route, provider, or advice;
- silently select a fake or different provider.

Feature-flag evaluation failure for risky optional AI defaults off. Flags are not authorization,
consent, privacy approval, or clinical policy.

---

# 9. Transactions and partial mutation

Do not hold a database transaction open during a remote model call. The future workflow must use an
explicit state boundary appropriate to its approved persistence design. After provider return,
schema/domain/provenance validation and any persistence happen atomically where they form one
business mutation.

Provider failure or invalid output leaves authoritative clinical state unchanged. An injected
candidate/provenance/aggregate/outbox failure rolls back the complete mutation. Ambiguous client
POST failures are not automatically replayed; clients refetch authoritative state before a
user-directed retry.

---

# 10. Correlation, logging, and observability

Request correlation uses a generated/validated bounded opaque request ID containing no patient
data. It may flow through adapter metadata and safe logs. Provider request IDs are optional
restricted operational metadata and must not be exposed or used as high-cardinality metric labels
without review.

Log/trace/metric records may contain operation, status, normalized error category, attempt count,
latency, and prompt/schema/model/provider version IDs. They must not contain raw patient text,
prompt/rendered context, provider output, evidence text, bearer/cookies, credentials, consent body,
SQL, stack trace in public responses, or full request/response bodies.

---

# 11. HTTP and BFF behavior

HTTP translation occurs only for an activated, documented API. P8-A/B internal errors do not create
an endpoint. P8-C must update `06_API_CONTRACTS.md` and add contract tests before activating the
deferred message route.

The BFF allows only documented safe codes/messages, applies bounded upstream timeout, validates the
entire response, sets `no-store`, and replaces malformed/raw upstream failures with a generic safe
error. It never returns the bearer, raw provider diagnostics, clinical input, or internal URL.

Authorization/not-found behavior remains non-enumerating. Rate-limit retry hints, if exposed, are
bounded and do not authorize automatic replay of a clinical mutation.

---

# 12. Patient-facing copy

Patient copy must state what failed and what safe action is actually available without claiming a
save, diagnosis, safety decision, or clinician review. Approved patterns include:

- optional AI assistance is temporarily unavailable;
- continue with the structured questions;
- review the saved draft before retrying;
- submitted information was not saved when atomic completion is unknown/failed.

Copy must never fabricate medical advice, emergency routing, provider contacts, or reassurance.
Generic urgent help remains visible independently of the optional AI dependency.

---

# 13. Test requirements

Tests cover every normalized provider category, allowed retry and no-retry case, total deadline,
malformed/oversize/spoofed output, injected application/persistence failure, no partial mutation,
safe envelope/status, `no-store`, correlation, and absence of synthetic PHI/secrets in logs/traces/
metrics/browser responses. See `30_TESTING_STRATEGY.md` for the P8 matrix.

---

# 14. Open decisions

1. **OPEN DESIGN DECISION:** public P8 error codes/status mappings, if any, during the owning API phase.
2. **OPEN DESIGN DECISION:** exact per-operation timeout, retry, backoff, and circuit-breaker policy.
3. **PRIVACY/SECURITY APPROVAL REQUIRED:** support/audit access to provider correlation metadata.
4. **CLINICAL APPROVAL REQUIRED:** patient-facing clinical/degraded wording beyond generic safe copy.
