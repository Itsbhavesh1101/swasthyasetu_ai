# SwasthyaSetu AI
## 30 — Testing Strategy

**Document ID:** `SSAI-TEST-030`
**Status:** Canonical cross-system testing strategy; P8 evidence is future
**Version:** `1.0.0-draft`

---

# 1. Purpose

This specification defines test ownership and required evidence for P8-A/B/C while preserving all
P1–P7 gates. It maps `AC-P8-001..010` to future tests; it does not mark any P8 criterion passed.

Tests use synthetic, clearly non-clinical fixtures. No real patient data, live provider credential,
billable external call, production endpoint, or unrestricted captured provider response belongs in
the default suite.

---

# 2. Test principles

1. Deterministic assertions outrank probabilistic prose grading for contracts and safety boundaries.
2. Provider behavior is tested through the project port; domain tests do not import vendor SDKs.
3. Invalid structured output fails closed and cannot partially mutate clinical state.
4. Authorization, consent, privacy, provenance, and deterministic-policy negative cases are first-class.
5. Unit tests are not substitutes for real PostgreSQL/API/browser evidence where persistence or
   end-to-end behavior is claimed.
6. Existing P1–P7 tests cannot be deleted, skipped, weakened, or bypassed to introduce P8.
7. Timing tests use controlled clocks/transports where possible and bounded generous integration limits.

---

# 3. Fixture model

P8 fixtures must be versioned and synthetic. A fixture records:

```text
case_id and category
operation/language
prompt_id + prompt_version
schema_id + schema_version
bounded synthetic input/context
provider response or normalized failure
expected candidate/result/failure
allowed variants where nondeterminism is intentionally tested
forbidden fields/outcomes
privacy and safety tags
```

The deterministic fake maps exact requests to explicit results, supports controlled delay/failure,
records attempts without retaining patient data, and rejects unexpected requests. Randomness and
wall-clock behavior are injected/controlled. Provider replacement tests run one shared contract
suite against every adapter plus the fake.

---

# 4. P8-A unit and contract matrix

| Area | Required evidence |
|---|---|
| Request/result values | Immutable, strict, bounded values; unknown keys, oversize input/output, invalid enums, and non-finite numbers reject. |
| Provider neutrality | Task/domain modules depend only on `LLMProvider`; provider objects/exceptions never escape. |
| Composition | Explicit compile-time registration; duplicates, missing provider, disabled provider, and production fake selection fail closed. |
| Offline behavior | Deterministic fake produces repeatable success and every normalized failure without network. |
| Replacement | Shared adapter contract passes with provider-specific transport mocked at its boundary. |
| Versioning | Prompt/schema/request/model identities round-trip; mismatches and unsupported versions reject. |
| Deadlines | Timeout applies to total call; exhausted/cancelled calls stop; latency is finite/non-negative. |
| Retry | Timeout, rate-limit, and selected transient 5xx obey bounded attempts/deadline. |
| No-retry | Auth, configuration, content-policy block, refusal, schema-invalid output, incompatible schema, invalid caller input, and exhausted deadline do not trigger infrastructure retry. |
| Optional repair | A task-approved format repair is a separately recorded bounded request, keeps the exact schema, and fits the original deadline/budget. |
| Failure mapping | Timeout/rate-limit/refusal/auth/5xx/unknown exceptions map to the closed categories without raw diagnostics. |
| Observability | Safe operation/version/attempt/latency/usage present; raw prompt/output, bearer, IDs, secrets, and PHI absent. |
| Health | Disabled/unconfigured/configured/degraded states are accurate and do not perform a live model call. |

Security/architecture fitness tests must detect direct provider imports in clinical modules, runtime
plugin discovery, raw-payload logging, unbounded retry, and unauthorized network gateway/service
configuration.

---

# 5. P8-B extraction unit and adversarial matrix

| Area | Required evidence |
|---|---|
| Valid extraction | Strict candidate schema accepts each approved candidate type with linked source/provenance. |
| JSON/shape | Empty, malformed/truncated JSON, wrong root, extra keys, missing fields, wrong types, duplicate/oversize arrays, and unsupported schema reject wholly. |
| Values | Non-finite/out-of-range numbers, invalid dates/enums, oversized strings, and invalid Unicode/control content reject safely. |
| Version spoofing | Mismatched request/result prompt, schema, model, provider, operation, or source reference rejects. |
| Evidence | Out-of-range spans, unrelated spans, absent sources, stale source hash/version, and cross-source references reject. |
| Hallucination | Unsupported/fabricated fields, diagnoses, medicines, allergies, dosage, provider/resource, advice, or route never become a candidate/fact. |
| Negation/temporality | High-risk negation, double negation, uncertainty, historical vs current, patient vs third party, and ambiguous duration lead to correct candidate/clarification/abstention. |
| Injection | Direct/indirect/encoded prompt injection, fake system text, tool request, schema override, model-result spoofing, and secret request cannot alter trusted authority. |
| Uncertainty | Missing evidence and ambiguous attribution produce explicit uncertainty/abstention, not guessed values. |
| Provenance | Candidate links source, prompt/schema/model/provider versions and remains AI-extracted/unconfirmed. |
| Promotion guard | Candidate cannot directly create/confirm/supersede facts or create diagnosis, medication change, summary approval, self-care, or final triage. |
| Degradation | Every provider/schema/domain failure leaves deterministic P7 intake usable. |

Clinical/safety evaluation cases require review before real activation. LLM-as-judge may support
exploratory evaluation but cannot replace exact assertions for forbidden behavior, source linkage,
route authority, or schema compliance.

---

# 6. P8-C future integration matrix

P8-C is not implemented. Before completion it will require:

## Unit and contract

- strict request/response/BFF validators and bounded message input;
- same-origin/content-type protections and no automatic retry on ambiguous POST;
- safe common error envelope and `Cache-Control: no-store` on success and error;
- no raw provider output or unexpected nested data relayed to the browser;
- disabled/unconfigured/consent-required/degraded UI states.

## Real PostgreSQL/API

- exact-session authorization, cross-session IDOR rejection, active/withdrawn consent, closed/expired
  session, patient-bound deferral, and unsupported encounter rejection;
- stale/mismatched intake/encounter/source/version rejection;
- transaction rollback after injected candidate/provenance/aggregate/outbox failures;
- concurrent messages/answers with explicit optimistic-conflict behavior and no partial rows;
- malformed/provider failure causes no partial clinical mutation;
- completed/terminal lifecycle behavior consistent with P7 read/write rules;
- deletion/retention behavior only after privacy approval.

## Browser/Playwright

- real FastAPI/PostgreSQL authorized message journey and deterministic-form fallback;
- consent withdrawal and session-close boundaries;
- no bearer or clinical data in localStorage, sessionStorage, IndexedDB, Cache Storage, service
  worker queues, URL/query, analytics, or console;
- no ambiguous POST replay after timeout/navigation;
- generic PWA cache allowlist unchanged;
- accessible keyboard/focus/error/degraded behavior and draft-only transparency;
- injection-like patient text rendered as text and never treated as UI/system instruction.

---

# 7. Privacy and security verification

Automated capture tests inspect logs, traces, metrics, error bodies, test reports, screenshots, and
browser storage for seeded canary strings representing synthetic PHI, bearer tokens, credentials,
prompts, and raw model output. Absence must be asserted on success, validation failure, timeout,
retry, provider exception, and application exception paths.

Network tests prove disabled/offline modes make no egress. Future real-adapter sandbox tests verify
endpoint allowlisting, TLS, credentials redaction, request minimization, timeout, provider retention
configuration where observable, and no patient-controlled endpoint/header/model selection.

Feature tests prove safe-off defaults and that flags cannot bypass authorization, consent, schema
validation, provenance, or deterministic safety policy.

---

# 8. Test-level ownership

| Level | Owner/evidence |
|---|---|
| Unit | Immutable values, parser/schema/domain rules, retry classifier, error mapping, fake provider. |
| Contract | Every `LLMProvider` adapter, prompt/schema compatibility, public capability, BFF/API shapes. |
| Integration | Adapter transport sandbox/mock, observability capture, future real PostgreSQL atomicity. |
| Security/privacy | Injection, egress, secrets, PHI leakage, IDOR, consent, browser storage. |
| E2E | Future P8-C patient journey with real app/PostgreSQL and deterministic fake provider. |
| Clinical evaluation | Clinician-reviewed synthetic/adversarial extraction set before activation. |

---

# 9. AC-P8 traceability

| Criterion | Required future evidence | Phase | Current status |
|---|---|---|---|
| `AC-P8-001` | Provider-neutral port and architecture/import tests. | P8-A | NOT YET VERIFIED |
| `AC-P8-002` | Deterministic offline fake success/failure contract suite. | P8-A | NOT YET VERIFIED |
| `AC-P8-003` | Strict task-specific extraction schema tests. | P8-B | NOT YET VERIFIED |
| `AC-P8-004` | Malformed JSON/schema and bounded-repair tests. | P8-A/B | NOT YET VERIFIED |
| `AC-P8-005` | Timeout/dependency typed-degradation and P7 fallback tests. | P8-A/C | NOT YET VERIFIED |
| `AC-P8-006` | Prompt/model/schema compatibility and provenance assertions. | P8-A/B | NOT YET VERIFIED |
| `AC-P8-007` | Evidence/source and provenance chain through future integration. | P8-B/C | NOT YET VERIFIED |
| `AC-P8-008` | Unsupported/hallucinated fields rejected; promotion guards. | P8-B/C | NOT YET VERIFIED |
| `AC-P8-009` | Injection/system-authority adversarial tests. | P8-B/C | NOT YET VERIFIED |
| `AC-P8-010` | Schema/domain/API negative tests for authoritative triage. | P8-B/C | NOT YET VERIFIED |

---

# 10. Regression and CI gates

Every P8 branch must keep the existing six CI jobs green:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

The backend gate includes formatting, lint, typing, unit tests, and import/compile checks. Persistence
uses a clean real PostgreSQL migration cycle. Frontend includes formatting, lint, strict typecheck,
workspace tests, and production builds. P8 tests are added to the narrowest appropriate gate; CI
must not be weakened or configured to skip them.

P1–P7 regression expectations include exact-session/consent protections, intake lifecycle and
optimistic concurrency, pack pinning, source/provenance distinctions, draft-only semantics,
`no-store`, no browser clinical persistence, and deterministic intake without an LLM.

---

# 11. Exit evidence by subphase

P8-A may complete only with its unit/contract/security tests and all six CI jobs passing. P8-B adds
the extraction/adversarial/provenance suite and required clinical review status. P8-C adds real
PostgreSQL/API/BFF/browser evidence plus approved privacy/consent behavior.

No passing specification or mock-only test marks `AC-P8-001..010` complete by itself.
