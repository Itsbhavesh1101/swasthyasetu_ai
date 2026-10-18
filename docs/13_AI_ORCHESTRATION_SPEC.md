# SwasthyaSetu AI
## 13 — AI Orchestration Specification

**Document ID:** `SSAI-AI-013`
**Status:** Canonical prerequisite specification; implementation not started
**Version:** `1.0.0-draft`
**Applies to:** P8-A and later approved AI consumers

---

# 1. Purpose and authority

This specification defines the future SwasthyaSetu-owned generative-AI orchestration boundary. It
implements the architecture intent of `FR-CORE-005`, `FR-CORE-007`, `FR-CORE-008`,
`NFR-SEC-012`, `NFR-SEC-013`, and `NFR-TEST-009` without assigning clinical decision authority to
an LLM.

The boundary is an in-process application component inside the FastAPI modular monolith. In this
document, **AI gateway** means this project-owned orchestration boundary. It does not mean a
separately deployed proxy, LiteLLM Proxy, MLflow AI Gateway, agent framework, model server, or new
network service.

The R2 AI adapter contract is guidance beneath canonical specifications and accepted R3 decisions.
Where it listed possible vendors, those names are candidates only and do not select a production
provider.

---

# 2. Scope and non-goals

P8-A owns:

- provider-neutral request/result contracts;
- `LLMProvider` and explicit compile-time adapter wiring;
- deadline, timeout, bounded-retry, error-normalization, and degradation behavior;
- prompt/schema/model version metadata transport;
- deterministic offline and unconfigured adapters;
- privacy-safe health and observability scaffolding.

P8-A does not own task prompts, clinical extraction schemas, clinical validation, fact promotion,
triage, safety policy, patient messaging, persistence, or a production provider selection.

P8-B owns the clinical-intake extraction task package. P8-C owns any authorized message API,
persistence, BFF, and patient UI. P9 owns deterministic physical safety; P12 owns speech and
translation; P14 owns mental-health routing; P15 owns governed self-care/Ayurveda behavior.

---

# 3. Ownership and topology

The required dependency direction is:

```text
task-specific application service
    -> AI orchestration service
        -> LLMProvider Protocol
            -> explicitly selected provider adapter
```

Task services own prompts, schemas, domain validation, and task-specific fallback. The gateway owns
shared operational policy. Provider structures and SDK types must not enter clinical domain types.
Adapters are registered explicitly at application composition time through the existing sealed
module/capability mechanism; runtime package scanning, entry-point discovery, arbitrary plugins,
and a global mutable service locator are prohibited.

An unavailable or disabled provider is a normal, typed state. No fake adapter may be selected
silently outside explicit test/development composition.

---

# 4. Provider contract

The future project-owned port is conceptually:

```python
class LLMProvider(Protocol):
    async def generate_structured(
        self, request: StructuredLLMRequest
    ) -> StructuredLLMResult: ...
```

The provider receives an already bounded request and a project-owned output-schema contract. It
does not choose the clinical task, prompt, schema, policy, fallback, safety route, or fact
verification state.

Provider adapters must:

1. translate project-owned contracts into provider calls;
2. apply the supplied deadline and token bound;
3. hold raw responses only in memory while parsing unless separately approved;
4. return normalized metadata and parsed candidate output;
5. map provider failures into the closed failure categories in this specification;
6. never expose credentials, provider exceptions, or raw payloads to domain/API callers.

---

# 5. `StructuredLLMRequest`

`StructuredLLMRequest` is an immutable, strictly validated, bounded value object. Its future schema
must include:

| Field | Rule |
|---|---|
| `operation_id` | Stable machine operation/task identifier; not free-form patient text. |
| `language_code` | Explicit supported language identifier. |
| `request_id` | Safe opaque correlation ID; contains no patient/session/encounter identifier. |
| `request_contract_version` | Version of this project-owned request shape. |
| `schema_id`, `schema_version` | Project-owned output contract identity. |
| `prompt_id`, `prompt_version` | Task-owned immutable prompt identity. |
| `input` | Task-owned structured, size-bounded minimum-necessary input. |
| `max_output_tokens` | Positive configured upper bound. |
| `deadline_at` or `timeout` | Explicit bounded execution deadline. |
| `retry_budget` | Non-negative bounded retry allowance supplied by policy. |
| `attempt` | Positive current attempt number, controlled by orchestration. |
| `provider_policy_id`, `provider_policy_version` | Approved operational selection policy, never clinical routing policy. |
| `provenance_context` | Opaque source references needed to link a result; no raw patient content. |

Unknown fields are rejected. Strings, collections, nested depth, and serialized size require
task-specific hard limits. Non-finite numeric values are invalid. The request cannot contain
provider credentials, a patient-supplied endpoint, arbitrary headers, tool permissions, hidden
chain-of-thought requests, or a clinical route selected by the provider.

**OPEN DESIGN DECISION:** exact per-operation size, token, deadline, and retry limits must be set in
P8-A/P8-B configuration and tests before activation; this specification does not invent them.

---

# 6. `StructuredLLMResult`

`StructuredLLMResult` is immutable, bounded, and tied to the request. Its future schema must include:

| Field | Rule |
|---|---|
| request/operation IDs and request-contract version | Exact safe correlation with the originating request. |
| schema and prompt IDs/versions | Must match the requested compatible versions. |
| `provider_id`, `provider_model_id`, `provider_model_version` | Deployment-resolved technical identity; never clinical approval. |
| `provider_request_id` | Optional bounded provider correlation value safe for operational use. |
| `validated_payload` | Strict project-schema-compatible candidate data, not a domain fact. |
| `finish_reason` | Normalized bounded enum/value. |
| `usage` | Optional bounded input/output/total token counters; no content. |
| `latency_ms` | Non-negative finite duration. |
| `attempt_count` | Positive count not exceeding the request policy. |
| `provenance` | Prompt/schema/model/provider identities and source-reference linkage. |
| `raw_retained` | `false` by default; cannot itself authorize retention. |

The caller must independently perform task schema validation and domain validation. A successful
provider call is not a successful clinical extraction and never confirms a clinical fact.

---

# 7. Schema and prompt ownership

Provider response schemas are generated from or demonstrably equivalent to project-owned strict
contracts. A provider-specific JSON schema is not canonical. Each prompt package declares:

```text
prompt_id + prompt_version
compatible schema_id + schema_version
language
purpose
content hash
approval status where required
fallback behavior
synthetic regression fixtures
```

Breaking prompt/schema compatibility requires a new version and regression evidence. Patient text
is delimited data, never a system instruction, tool grant, provider configuration, or policy input.

---

# 8. Deadlines, attempts, and retries

One orchestration call has one total deadline. Every attempt, delay, and parse/validation action
must fit within it. Retry count and backoff are bounded and observable.

Potentially retryable failures are limited to:

- timeout where remaining deadline permits;
- rate limit when an allowed retry hint fits the deadline;
- explicitly classified transient provider unavailability/selected 5xx.

Do not retry:

- authentication or configuration failure;
- content-policy block;
- provider refusal unless the task explicitly defines a safe new request;
- schema-invalid output or deterministic schema/version incompatibility;
- validation failure caused by the caller contract;
- cancelled request or exhausted deadline;
- any mutation whose outcome is ambiguous without an idempotency contract.

A task may define one separate, explicit, bounded structured-format repair request after
`LLM_SCHEMA_INVALID`. That is a new task request with recorded provenance, not an infrastructure
retry, and must still fit the original deadline/budget. It may not weaken or change the schema.

Retries must not silently switch providers/models, enlarge patient context, weaken schemas, or ask a
provider to choose a clinical fallback. Provider fallback requires an approved, versioned
operational policy and equivalent privacy/clinical review.

---

# 9. Failure categories and degradation

The provider/orchestration boundary uses these closed future categories:

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

Adapters attach only bounded non-sensitive diagnostics. Orchestration returns typed failure or a
typed degraded result; it never returns fabricated payload data or claims success after failure.

Default degradation for clinical intake is the existing deterministic P7 structured text/touch
workflow, clarification, or honest temporary unavailability of the optional AI action. Deterministic
intake and generic urgent-help navigation remain available. No provider failure may produce a
diagnosis, advice, final triage route, or invented resource.

---

# 10. Privacy, security, and secrets

Requests use the minimum necessary approved context. Raw prompts, patient utterances, provider raw
responses, credentials, session bearers, and clinical payloads are prohibited in logs, traces,
metrics, exception messages, URLs, and analytics.

Provider credentials are deployment secrets scoped per integration. They are not prompt fields,
module globals, source-controlled values, or browser-visible configuration. Endpoint and model
selection are allowlisted deployment configuration; patients cannot supply endpoint, proxy,
headers, model, schema, or credentials.

No real patient data may leave SwasthyaSetu for an external provider until the decision gate in
`26_PRIVACY_CONSENT_SPEC.md` is approved. General intake consent alone is insufficient.

Raw provider responses are transient in-memory data by default. Any retention for evaluation is a
separate approved research flow with isolated storage, access, retention, and deletion policy.

---

# 11. Observability and health

Permitted telemetry includes:

```text
safe request correlation ID
operation ID
prompt/schema/provider/model version identifiers
attempt count
latency
normalized finish/failure category
bounded token usage/cost metadata where available
feature/configuration state without secrets
```

It excludes raw input/output, patient/session/encounter identifiers, bearer tokens, consent
payloads, and provider credentials. High-cardinality provider request IDs are not metrics labels.

Health must distinguish `disabled`, `unconfigured`, `configured`, and `degraded`. It must not make a
live billable/model request by default. AI health never controls core API/database readiness and
must not report a provider as clinically approved.

---

# 12. Offline and unconfigured behavior

P8-A must provide a deterministic offline provider for tests. Fixtures map exact versioned requests
to exact project-owned results/failures and never use network access, time variance, hidden random
state, or real patient data.

The default runtime provider is disabled/unconfigured and fails closed with typed degraded behavior.
Production must reject an accidental fake provider selection. Feature flags are safe-off operational
gates, never authorization, consent, or clinical policy.

---

# 13. Future direct provider-adapter approval path

A real direct adapter may be proposed only after documenting:

- provider/model identity and supported structured-output behavior;
- dependency class, version, license, security posture, and replaceability;
- endpoint allowlist, credentials, region, purpose, retention, training use, and subprocessors;
- DPA/institutional/regulatory review and the privacy/consent basis for egress;
- timeout, retry, quota, cost, health, telemetry, and failure behavior;
- contract, sandbox, injection, privacy, and outage tests;
- explicit non-production and production activation controls.

Adapter implementation, benchmark selection, and production approval are different states. No
production model/provider is selected by this document.

---

# 14. Traceability and acceptance status

| Criterion/requirement | Specification evidence | Status |
|---|---|---|
| `AC-P8-001` | Sections 3–6 define a provider-neutral gateway/port. | FUTURE — NOT VERIFIED |
| `AC-P8-002` | Section 12 defines deterministic offline behavior. | FUTURE — NOT VERIFIED |
| `AC-P8-004` | Sections 7–9 define schema rejection and bounded repair. | FUTURE — NOT VERIFIED |
| `AC-P8-005` | Sections 8–9 define typed timeout/dependency degradation. | FUTURE — NOT VERIFIED |
| `AC-P8-006` | Sections 5–7 define prompt/model/schema traceability. | FUTURE — NOT VERIFIED |
| `FR-CORE-007/008` | Results remain provenance-linked candidates; no silent promotion. | SPECIFIED ONLY |
| `NFR-SEC-012/013` | Patient input cannot become policy; context is minimized. | SPECIFIED ONLY |
| `NFR-TEST-009` | Invalid/missing structured output is a required failure path. | SPECIFIED ONLY |

P8 and `AC-P8-001..010` remain not started/not verified until implementation evidence exists.

---

# 15. Open decisions

1. **PRIVACY/SECURITY APPROVAL REQUIRED:** any external provider, real-patient egress, region,
   retention, training-use setting, subprocessors, and contract/DPA.
2. **CLINICAL APPROVAL REQUIRED:** any prompt/output used in clinical or safety-sensitive behavior.
3. **OPEN DESIGN DECISION:** exact operation limits, retry/backoff policy, provider selection policy,
   and whether any direct SDK is necessary.
4. **DEFERRED:** network AI gateway, multi-provider routing/failover, RAG, agent tooling, and model
   serving until a later approved need/ADR.
