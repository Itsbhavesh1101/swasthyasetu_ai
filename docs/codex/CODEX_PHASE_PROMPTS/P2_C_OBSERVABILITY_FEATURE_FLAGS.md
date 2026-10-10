# Codex Phase Prompt — P2-C Observability & Feature Flags

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P2-C`
**Phase unit:** P2-C — Observability & Feature Flags
**Base branch:** `main`
**Expected base commit:** `0533847ebeb8f9d0ae9ee3541130158d38a1c6f4`
**Implementation branch:** `phase/p2-c-observability-feature-flags`
**Scope:** Complete P2 shared-kernel observability and feature-flag abstractions only
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

# 0. Mission

Complete P2 — Shared Platform Kernel.

P2-A established:

```text
shared UUID/time/request-ID primitives
minimal ActorContext
framework-independent errors
canonical ErrorCode registry
typed configuration
privacy-safe JSON logging
```

P2-B established:

```text
immutable module manifests
typed capability keys
explicit module/provider/router registration
order-independent capability dependency validation
sealed per-application registries
```

P2-C must implement only:

```text
provider-neutral feature-flag abstraction
configuration-backed initial feature-flag provider
safe/off behavior for absent or indeterminate optional flags
OpenTelemetry API/SDK observability foundation
content-free HTTP tracing
bounded request metrics
trace/log correlation where safe
observability configuration with external export disabled by default
tests/documentation
final P2 acceptance audit
```

P2-C is the final P2 unit.

If all P2 criteria and remote CI pass:

```text
P2-C = COMPLETE
P2 = COMPLETE
next = P3-A — SQLAlchemy & Alembic Persistence Foundation
```

Do not implement P3.

---

# 1. Mandatory Preflight

From repository root run:

```text
git rev-parse --show-toplevel
git branch --show-current
git status --short
git rev-parse HEAD
git remote -v
git log --oneline --decorate -8
```

Expected:

```text
branch: main
HEAD: 0533847ebeb8f9d0ae9ee3541130158d38a1c6f4
working tree: clean
```

Verify merged P2-A/P2-B assets exist:

```text
backend/app/shared/types/
backend/app/shared/errors/
backend/app/shared/security/actor.py
backend/app/shared/modules/
backend/app/shared/capabilities/
backend/app/config/sections.py
backend/app/shared/observability/logging.py
backend/app/main.py

docs/codex/CODEX_PHASE_PROMPTS/P2_A_SHARED_KERNEL_PRIMITIVES.md
docs/codex/CODEX_PHASE_PROMPTS/P2_B_MODULE_CAPABILITY_REGISTRY.md
```

Verify tracker currently says:

```text
P2 = PARTIAL
P2-A = COMPLETE
P2-B = COMPLETE
next = P2-C — Observability & Feature Flags
```

If `main` differs from expected only through the approved P2-B merge history, inspect and report the actual base.

If unrelated local changes exist, stop.

---

# 2. Create the Phase Branch

Create:

```text
git switch -c phase/p2-c-observability-feature-flags
```

If already present:

1. inspect its history;
2. compare with `main`;
3. preserve legitimate work;
4. continue only if it is clearly the intended P2-C branch.

Never implement directly on `main`.

Do not merge at completion.

---

# 3. Required Reading

Read before editing:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/06_API_CONTRACTS.md
docs/29_ENGINEERING_STANDARDS.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md

docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md

docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md

docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_ARCHITECTURE_RECONCILIATION.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md

docs/codex/CODEX_PHASE_PROMPTS/P2_A_SHARED_KERNEL_PRIMITIVES.md
docs/codex/CODEX_PHASE_PROMPTS/P2_B_MODULE_CAPABILITY_REGISTRY.md
```

Inspect actual code before editing:

```text
backend/app/main.py
backend/app/api/middleware/request_context.py
backend/app/shared/observability/
backend/app/config/sections.py
backend/app/config/settings.py
backend/app/shared/modules/
backend/app/shared/capabilities/
backend/tests/
backend/pyproject.toml
backend/uv.lock
```

---

# 4. Governing Decisions

P2-C implements already accepted decisions.

Relevant accepted decisions include:

```text
ADR-020 — Feature Flags for Staged/Risky Features
ADR-021 — Internal Contracts Are Typed
ADR-027 — Core Safety Paths Must Degrade Independently of Optional AI
ADR-038 — Dependency Profiles Are Architectural Boundaries
```

R3 technology decision:

```text
OpenTelemetry — ADOPT
OTel API/semantic context = observability contract
OTel Collector = later deployment concern
Prometheus = pilot concern
Grafana = optional
Loki = deferred
```

Do not create a new ADR merely to restate these decisions.

---

# 5. P2 Acceptance Targets

P2-C directly targets:

```text
AC-P2-006 — Feature-flag abstraction exists.
AC-P2-007 — Risky optional feature defaults are safe/off unless enabled.
AC-P2-008 — Structured logging is enabled without raw request-body logging by default.
AC-P2-009 — Shared kernel contains no feature-specific clinical logic.
```

P2-C must also re-verify:

```text
AC-P2-001 — typed settings
AC-P2-002 — stable error envelope
AC-P2-003 — request IDs
AC-P2-004 — module registration
AC-P2-005 — capability registry
```

P2 can be marked COMPLETE only when:

```text
AC-P2-001 through AC-P2-009 = PASS
remote mandatory CI = SUCCESS
```

---

# 6. Scope Boundary

Allowed:

```text
OpenTelemetry API
OpenTelemetry SDK
manual project-owned HTTP instrumentation
in-process tracer/meter providers
no-op/no-export default behavior
feature-flag protocol/interface
config-backed feature-flag provider
feature-flag value objects
tests using in-memory OTel exporters/readers
application composition wiring
safe observability config
```

Forbidden:

```text
OTel Collector deployment
Prometheus deployment
Grafana
Loki
Tempo
Jaeger
Datadog
Sentry
New Relic
Honeycomb
external telemetry endpoint activation
SQLAlchemy
Alembic
DB persistence
events/outbox
jobs/workers
object storage
auth/session/consent
clinical/product logic
AI/ML/QML
```

---

# 7. Dependency Authorization

P2-C explicitly activates only:

```text
opentelemetry-api
opentelemetry-sdk
```

Classification:

```text
CORE_RUNTIME
```

Do not add `opentelemetry-instrumentation-fastapi` unless manual instrumentation proves materially inadequate and you first report why.

Preferred implementation:

```text
manual project-owned middleware/boundary instrumentation
```

because it gives tighter control over privacy and recorded attributes.

Do not add:

```text
OTLP exporter
Prometheus exporter
Jaeger exporter
vendor exporter
auto-instrumentation distro
```

in P2-C.

---

# 8. Dependency Due Diligence

Before adding the OTel packages:

1. inspect the currently available stable compatible versions;
2. verify Python 3.12 support;
3. verify license;
4. verify no external telemetry occurs by default;
5. add only API + SDK;
6. update `backend/uv.lock`;
7. record exact resolved versions in final report.

Expected license family:

```text
Apache-2.0
```

If reality differs, report it.

Do not copy current web/package assumptions blindly.

---

# 9. Observability Architecture

Create a small project-owned observability boundary.

A reasonable conceptual shape:

```text
backend/app/shared/observability/
    logging.py
    telemetry.py
    http.py
```

Exact file split is implementation judgment.

The shared boundary should expose concepts such as:

```text
ObservabilityRuntime
tracer
meter
HTTP request observation
```

Do not expose vendor-specific exporter concepts to domain modules.

Do not turn observability into a service locator.

---

# 10. OpenTelemetry Provider Ownership

Prefer per-application/project-owned provider objects instead of repeatedly mutating global OTel providers during tests.

Requirements:

```text
create tracer provider explicitly
create meter provider explicitly
obtain tracer/meter from them
attach runtime to application composition
allow deterministic tests
avoid global-provider one-time-set warnings/leaks
```

If global provider APIs are used, isolate setup carefully and prove repeated `create_app()` tests remain deterministic.

Per-application ownership is preferred.

---

# 11. External Export Default

Default P2-C behavior:

```text
instrumentation available
external export OFF
no network telemetry egress
```

Current setting:

```text
observability.external_export_enabled = False
```

Preserve safe default.

P2-C does not implement an exporter.

If `external_export_enabled=True` is supplied in P2-C, do not silently pretend export is active.

Choose one safe behavior:

```text
reject configuration as unsupported in P2-C
```

or:

```text
record explicit disabled/unavailable state
```

Prefer fail-fast configuration rejection because a true flag that does nothing is misleading.

Document/test the chosen behavior.

---

# 12. No Collector Deployment

Do not modify Compose to add:

```text
otel-collector
prometheus
grafana
loki
jaeger
tempo
```

Do not add monitoring containers.

P22/P24 may deploy observability infrastructure later.

P2-C is application instrumentation only.

---

# 13. HTTP Tracing

Instrument HTTP requests with content-free tracing.

At minimum each request should produce a span with a safe name such as:

```text
HTTP GET
HTTP POST
```

or:

```text
HTTP GET /health/live
```

only when the route template is known.

Do not use actual user-controlled URL path values for span names if they may contain IDs.

Prefer route templates:

```text
/patients/{patient_id}
```

not:

```text
/patients/2e356cf4...
```

---

# 14. Safe Trace Attributes

Allowed/request metadata should be tightly allowlisted.

Possible safe attributes:

```text
http.request.method
http.route
http.response.status_code
swasthyasetu.request_id
service.name
```

Use the semantic-convention names available in the installed OTel version where appropriate.

Do not record:

```text
request body
response body
query string
raw URL
Authorization
Cookie
Set-Cookie
patient ID extracted from route
session token
form fields
document text
conversation text
FHIR payload
LLM prompt/response
```

No clinical content in span attributes/events.

---

# 15. Exception Privacy

Do NOT automatically attach raw exception messages/stack traces to spans at this phase.

Unhandled exceptions may contain:

```text
PHI
secrets
provider details
raw user values
```

For an internal failure:

```text
set span/error status
record safe error code where available
```

Do not call exception-recording helpers that serialize unrestricted exception data unless sanitized.

Existing public error behavior remains privacy-safe.

---

# 16. Request Metrics

Implement minimal HTTP request metrics.

At minimum:

```text
request count
request duration
```

Optional:

```text
error count
```

Do not create excessive metrics.

Do not add product/clinical metrics in P2-C.

---

# 17. Metric Attributes / Cardinality

Metric attributes MUST remain bounded and non-sensitive.

Allowed examples:

```text
http.request.method
http.route
http.response.status_code
```

Do NOT use:

```text
request_id
patient_id
session_id
encounter_id
document_id
URL query
provider response text
user-entered values
```

No high-cardinality IDs in metric labels.

This is mandatory.

---

# 18. Route Templates

For matched routes, use FastAPI/Starlette route templates where available.

For unmatched routes use a bounded value such as:

```text
unmatched
```

Do not use the raw unmatched path as a metric attribute.

This protects cardinality and privacy.

---

# 19. Trace/Log Correlation

Enhance JSON logging to include trace context only when valid/current.

Safe fields may include:

```text
trace_id
span_id
```

Represent them consistently.

Do not add trace-state/baggage wholesale.

Do not place arbitrary baggage values into logs.

Existing `request_id` behavior must remain.

---

# 20. Baggage

Do not use OTel baggage for patient/session/clinical data in P2-C.

Do not introduce baggage propagation conventions.

Future cross-service propagation can be governed when services are extracted.

---

# 21. Telemetry Resource

Use a safe resource/service identity.

At minimum:

```text
service.name = swasthyasetu-backend
```

Do not include:

```text
hostnames
usernames
machine-specific filesystem paths
cloud credentials
patient identifiers
```

Environment label may be included only if low-risk and already canonical.

Do not expose secrets.

---

# 22. Middleware Integration

Current HTTP request boundary is:

```text
RequestContextMiddleware
```

Preserve its contract.

Preferred design:

```text
resolve request ID
enter content-free observation
call downstream
produce safe response/error
record route/status/duration
structured log
exit observation
```

It is acceptable to integrate telemetry through the existing request-context middleware rather than stacking another middleware if that gives clearer ordering/privacy.

Keep responsibilities separated through helper/runtime objects.

Do not duplicate request-ID generation.

---

# 23. Existing Error Behavior

Preserve:

```text
stable error envelope
request_id in errors
generic PROCESSING_FAILED for unhandled errors
no internal exception leakage
```

Telemetry must not cause an alternate error response.

If telemetry itself fails, it must not break the request path.

However, do not use broad silent exception swallowing everywhere.

Keep telemetry implementation simple enough that runtime instrumentation failures are rare and isolated.

---

# 24. Observability Failure Semantics

Observability is operational support, not clinical authority.

Application correctness must not depend on:

```text
exporter
collector
metrics backend
trace backend
```

Since P2-C has no external exporter, there is no network failure path.

Instrument creation must not make unrelated workflows unavailable.

---

# 25. Feature-Flag Architecture

Implement a provider-neutral feature-flag interface.

Suggested conceptual pieces:

```text
FeatureFlagName / FeatureFlag
FeatureFlagProvider Protocol
FeatureFlagService
ConfigurationFeatureFlagProvider
```

Exact names may differ.

Keep the interface small.

---

# 26. Feature-Flag Identifier

Feature flags use stable machine-readable names.

Canonical architecture examples:

```text
voice_intake_enabled
mental_health_enabled
ayurveda_selfcare_enabled
provider_directory_enabled
abdm_enabled
qml_inference_enabled
preventive_care_enabled
```

P2-C MUST NOT activate these real features.

Do not register production flags simply because examples exist.

Tests should use neutral flags:

```text
example_feature
synthetic_optional_feature
```

A reasonable validation grammar is lowercase snake case.

Do not over-constrain future names unnecessarily.

---

# 27. Safe Default

Critical invariant:

```text
unknown / absent / indeterminate optional flag => disabled
```

Never:

```text
unknown flag => enabled
provider failure => enabled
parse failure => enabled
```

For P2-C's configuration-backed provider, absence means `False`.

This directly satisfies AC-P2-007.

---

# 28. Mandatory Safety Is Not a Feature Flag

Do not create feature flags for mandatory safety controls.

Do not implement a flag such as:

```text
disable_crisis_safety
disable_red_flags
```

Mandatory safety logic must never be made optional by this abstraction.

Later risky features may depend on mandatory safety, but P2-C does not implement clinical safety dependency evaluation.

---

# 29. Configuration-Backed Provider

Implement an initial immutable configuration-backed provider.

P2-A currently has:

```python
class FeaturesSettings(ConfigurationSection):
    ...
```

Evolve this safely.

Prefer a deeply immutable representation.

A simple acceptable shape:

```text
enabled: tuple[str, ...] = ()
```

or equivalent immutable configuration.

Then:

```text
configured name present => true
absent => false
```

Do not use a mutable dictionary inside an otherwise frozen settings model unless you explicitly freeze/copy it safely.

---

# 30. Environment Configuration

Preserve all P1 environment variables.

If feature settings can be supplied via nested Pydantic environment JSON, document a safe example.

For example conceptually:

```text
SWASTHYASETU_FEATURES={"enabled":["example_feature"]}
```

The exact serialization depends on Pydantic Settings behavior.

Use only synthetic example flags in documentation.

Default `.env.example` should not enable any feature.

---

# 31. FeatureFlagProvider Protocol

The provider interface should be framework-independent.

A minimal API may be:

```python
class FeatureFlagProvider(Protocol):
    def is_enabled(self, flag: FeatureFlag) -> bool: ...
```

or async only if justified.

Configuration lookup is local and synchronous, so do not make it async without reason.

Do not add context targeting yet.

---

# 32. No User Targeting / Rollouts

P2-C does NOT implement:

```text
percentage rollout
per-user targeting
patient cohort targeting
role targeting
organization targeting
remote flag service
experimentation/A-B testing
```

These can be added later if requirements justify them.

Avoid premature complexity and privacy risk.

---

# 33. FeatureFlagService

A small service may wrap the provider to establish the stable application contract.

It should:

```text
evaluate a typed flag
return bool
default safely
contain no clinical rules
```

Do not add global singleton state.

Per-application composition is preferred.

---

# 34. Application Composition

At `create_app()` time:

```text
create feature flag provider/service from Settings
create observability runtime from Settings
attach/inject them explicitly
```

Safe application-state names may include:

```text
application.state.feature_flags
application.state.observability
```

Do not expose them via debug HTTP endpoints.

Do not make domain modules import global app state.

Future FastAPI dependencies can inject them.

---

# 35. Module Manifest Interaction

P2-B manifests contain:

```text
feature_flags: tuple[str, ...]
```

In P2-C these remain declaration metadata.

Do not automatically enable a module because a manifest names a flag.

Do not implement conditional module registration yet.

Do not make registration depend on flag evaluation.

Later module phases can explicitly decide how flags gate optional behavior.

---

# 36. Feature-Flag Error Semantics

For valid but unconfigured flag:

```text
False
```

For syntactically invalid flag definition at development/composition time:

```text
fail validation
```

Do not create a public HTTP error for flag lookups in P2-C.

`FEATURE_DISABLED` already exists in the canonical ErrorCode registry for later product APIs.

Do not invent another public code.

---

# 37. OpenTelemetry Tests — Provider Setup

Add deterministic tests proving:

```text
observability runtime can be constructed repeatedly
no global-provider conflict occurs
no external exporter is configured by default
service resource has expected safe name
```

Tests must not send network traffic.

---

# 38. OpenTelemetry Tests — Tracing

Use SDK test/in-memory facilities where appropriate.

Test a synthetic request and prove:

```text
a request span is produced
method is recorded
route template is recorded
status is recorded
request ID may be correlated
raw request body is absent
query string is absent
Authorization is absent
Cookie is absent
synthetic sensitive value is absent
```

Do not depend on a real collector.

---

# 39. OpenTelemetry Tests — Exceptions

Test an endpoint that raises a synthetic exception containing a marker such as:

```text
synthetic-sensitive-internal-detail
```

Verify:

```text
HTTP response remains generic
span marks failure safely
exported span attributes/events do not contain the synthetic internal detail
logs do not contain the synthetic internal detail unless current logging already emits it (it must not)
```

Do not record unrestricted exception stack/events.

---

# 40. OpenTelemetry Tests — Metrics

Use an in-memory metric reader or equivalent SDK test facility.

After synthetic requests verify:

```text
request counter increments
duration metric records
metric attributes contain bounded method/route/status
metric attributes do not contain request_id
metric attributes do not contain raw URL/query/patient-like IDs
```

Test unmatched route behavior uses bounded `unmatched` instead of raw path.

---

# 41. Logging Tests

Preserve all P2-A privacy tests.

Add tests for:

```text
trace_id/span_id appear when a valid current span exists
trace_id/span_id absent cleanly when there is no active recording span
request body still not logged
Authorization/cookies still not logged
```

Do not emit arbitrary span attributes into logs.

---

# 42. Feature-Flag Tests

Add tests for:

```text
flag identifier validation
default absent flag = false
explicit configured flag = true
unconfigured valid flag = false
settings default has zero enabled flags
settings are immutable
configuration provider immutable behavior
no real feature flag enabled by default
```

Use synthetic flag names.

---

# 43. Feature-Flag Provider Failure

The initial provider is in-memory/config-backed and should not have I/O failure.

Do not invent remote provider failure handling yet.

The interface should be replaceable later.

If a future provider fails, architecture requires safe-off for risky features, but P2-C need not simulate network providers.

---

# 44. Settings Validation

Extend:

```text
ObservabilitySettings
FeaturesSettings
```

without breaking P1/P2-A access.

Preserve:

```text
settings.app_name
settings.environment
settings.debug
settings.api_v1_prefix
settings.log_level
```

Do not break existing nested sections.

---

# 45. Observability Settings Suggested Shape

Keep it minimal.

Possible fields:

```text
tracing_enabled: bool = True
metrics_enabled: bool = True
external_export_enabled: bool = False
service_name: str = "swasthyasetu-backend"
```

This is guidance, not mandatory exact syntax.

Requirements:

```text
external export off by default
service name non-empty
no exporter endpoint required
no secret
```

If tracing/metrics are disabled, application must still work normally.

---

# 46. Feature Settings Suggested Shape

Prefer immutable configuration.

For example:

```text
enabled: tuple[str, ...] = ()
```

Validate/normalize through the same feature-flag identifier rules where practical.

Duplicate configured names should be rejected or deterministically deduplicated.

Prefer rejection for configuration clarity.

Do not enable anything by default.

---

# 47. OTel Instrument Names

Use stable project-owned instrument names.

Examples:

```text
swasthyasetu.http.server.requests
swasthyasetu.http.server.duration
```

or semantic-convention names if the installed OTel package provides a stable applicable convention.

Do not create dozens of instruments.

Document the names selected.

---

# 48. Duration Unit

Choose a conventional explicit duration unit:

```text
ms
```

or:

```text
s
```

Be consistent between instrument declaration/tests/docs.

Do not mix units.

Existing structured access logs currently use:

```text
duration_ms
```

Using milliseconds for the custom histogram is acceptable.

---

# 49. Status Semantics

Trace status:

```text
5xx -> ERROR
normal successful/client response -> do not falsely mark internal error
```

Do not treat every 4xx as server exception.

Metrics can record exact bounded status code.

---

# 50. Health Endpoints

Health requests may be instrumented like other HTTP requests.

Do not make readiness depend on:

```text
OTel exporter
collector
metrics backend
feature-flag provider network
```

There is no external provider in P2-C.

Current `/health/live` and `/health/ready` contracts must remain unchanged.

---

# 51. Feature Flags Are Not Authorization

Explicitly preserve ADR-020:

```text
feature flag != permission
feature flag != authentication
feature flag != consent
```

Do not implement access control with feature flags.

A later endpoint must still enforce authorization independently.

---

# 52. Feature Flags Are Not Clinical Policy

Do not use flags for:

```text
red-flag thresholds
crisis route decisions
contraindications
diagnosis logic
self-care eligibility rules
model thresholds
```

Feature flags control availability/staging, not patient-specific clinical decisions.

---

# 53. Feature Flags and Risky Features

The only P2-C invariant required now is:

```text
risky optional feature has no positive activation unless explicitly configured
```

Do not invent which future features are clinically risky beyond existing architecture examples.

Do not activate examples.

---

# 54. Observability and Audit Separation

Do not implement audit persistence in P2-C.

Remember:

```text
OTel telemetry != product audit trail
```

Future audit events remain a governed product data stream.

Do not log consent/policy changes as a substitute for audit storage.

---

# 55. No Sensitive Metrics

Never emit patient-identifying or health-value metrics.

Forbidden examples:

```text
symptom="chest pain"
diagnosis="..."
patient_id="..."
ABHA="..."
medication="..."
mental_health_route="..."
```

P2-C metrics are operational HTTP metrics only.

---

# 56. No Sensitive Traces

Do not include:

```text
medical free text
document OCR content
prompt text
response text
FHIR bodies
ABDM payloads
provider contact data
```

in traces.

Tests should explicitly protect this invariant.

---

# 57. No Sensitive Logs

Preserve current allowlist.

If adding:

```text
trace_id
span_id
status
provider
model_version
policy_version
```

only allow fields that are explicitly safe.

P2-C itself does not need provider/model/policy fields.

Do not broaden to arbitrary `extra`.

---

# 58. OTel Package Isolation

Only shared observability and transport-composition code should import OTel in P2-C.

Do not import OTel from:

```text
shared/errors
shared/types
shared/security
shared/modules
shared/capabilities
future clinical module placeholders
```

Keep observability replaceable/localized.

---

# 59. No Auto-Instrumentation Environment Dependency

Do not require:

```text
opentelemetry-instrument
OTEL_EXPORTER_OTLP_ENDPOINT
OTEL_SERVICE_NAME
```

to start the app.

The application should start normally with project settings and no external OTel environment.

---

# 60. No Telemetry Egress

Tests should be able to prove no exporter is configured by default.

Do not initiate DNS/network connections.

Do not use hosted observability SaaS.

---

# 61. Dependency Lock

After adding OTel API/SDK:

```text
uv lock
uv sync --locked --dev
```

Commit the updated:

```text
backend/pyproject.toml
backend/uv.lock
```

Do not modify frontend dependency files.

---

# 62. Dependency Report

Final report must include for each OTel dependency:

```text
package
requested constraint
resolved version
R3 class = CORE_RUNTIME
license
import locations
reason
external egress behavior
```

If transitive OTel packages appear, identify them separately as transitives.

---

# 63. No CI Infrastructure Expansion

Existing CI already runs:

```text
backend
frontend
docker/postgres
Playwright
security
```

Do not add a Collector service to CI.

The backend test suite should exercise OTel in-memory.

Security scan will cover the new packages.

---

# 64. Test Count / Regression

Existing merged P2-B baseline has:

```text
65 backend tests
```

Add appropriate P2-C tests without deleting valid existing tests.

Do not weaken:

```text
request privacy tests
error privacy tests
registry tests
frontend tests
Playwright tests
```

---

# 65. Application Factory Compatibility

Preserve current signature behavior:

```python
create_app(
    settings=None,
    api_v1_routers=(),
    module_registrations=(),
)
```

You may add optional explicit composition arguments for testing observability/feature providers if needed, but avoid a bloated app factory.

Prefer constructing defaults from `Settings`.

Do not break existing callers.

---

# 66. App State

If used, expected safe state may include:

```text
application.state.settings
application.state.module_registry
application.state.capability_registry
application.state.feature_flags
application.state.observability
```

Do not expose a generic mutable container.

Do not put secrets in state representations/logs.

---

# 67. Feature Flag API Surface

A reasonable service call:

```python
feature_flags.is_enabled(SYNTHETIC_FLAG)
```

must:

```text
return bool
never return tri-state to normal consumers
safe-off absent flag
```

If provider internals distinguish UNKNOWN, the service must collapse risky unknown to false.

The configuration provider itself does not need UNKNOWN.

---

# 68. Typed Feature Flag Constant

Future modules should define a typed flag constant in their public contract rather than scatter raw strings.

P2-C should make that pattern easy.

Do not define real future module constants now.

Use synthetic constants in tests only.

---

# 69. Feature Flag Immutability

Feature flag configuration must not be mutated at request time.

No endpoint to toggle flags in P2-C.

No admin UI.

No database update.

Configuration changes require process/config restart at this stage.

That is acceptable.

---

# 70. Later Evolution

Design so a later provider can implement the same interface from:

```text
database
remote config service
governed admin system
```

without changing consumers.

Do not implement those providers now.

---

# 71. P2-B Registry Compatibility

Do not alter P2-B semantics:

```text
explicit compile-time module registration
sealed registry
typed capability resolution
no dynamic plugins
```

Feature flags do not unseal/reconfigure module registry at runtime.

Do not make feature flags dynamically load Python modules.

---

# 72. Feature Manifest Compatibility

Keep P2-B manifest metadata valid.

If validating manifest `feature_flags` more strongly using a shared identifier type would cause a broad migration, defer it.

P2-C does not need to rewrite P2-B manifest.

Document that manifest names are declaration metadata and runtime flag keys should follow the same naming convention.

---

# 73. Documentation Updates

Update only affected docs.

Expected:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
docs/implementation/38_PROGRESS_TRACKER.md
```

Update:

```text
backend/.env.example
```

only if adding safe synthetic/default observability/feature settings materially helps local development.

Do not enable external export or real features in `.env.example`.

No need to create `31_OBSERVABILITY_SPEC.md` in this phase unless a canonical instruction explicitly requires it.

P2-C implements only the foundation already defined by master architecture.

---

# 74. Decision Log

Do not create a new ADR if implementation follows:

```text
ADR-020
R3 OpenTelemetry ADOPT decision
```

Create an ADR only if a real architecture change is needed.

Do not rewrite historical ADRs.

---

# 75. Progress Tracker — Local Stage

Before remote CI evidence:

```text
P2-C = PARTIAL — REMOTE CI VERIFICATION PENDING
P2 = PARTIAL
```

Record:

```text
base SHA
branch
implementation SHA
OTel dependencies
tests
local quality gates
AC-P2-006/007 local pass
```

Do not mark P2 COMPLETE yet.

---

# 76. Progress Tracker — Remote Closure

After all mandatory branch CI jobs pass:

```text
P2-C = COMPLETE
P2 = COMPLETE
```

Record:

```text
CI run ID
CI URL
head SHA
all AC-P2-001 through AC-P2-009 PASS
next = P3-A — SQLAlchemy & Alembic Persistence Foundation
```

If CI cannot be verified:

```text
P2 remains PARTIAL
```

Do not fabricate closure.

---

# 77. Backend Verification

From `backend/` run:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
```

Run app import smoke.

All must pass.

---

# 78. Full Regression

From root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

P1/P2-A/P2-B must remain green.

Do not modify frontend behavior.

---

# 79. Targeted Privacy Verification

Run targeted tests proving:

```text
request body excluded from logs
Authorization excluded from logs/traces
Cookie excluded from traces
query string excluded from traces
synthetic internal exception detail excluded from response/logs/traces
request ID excluded from metric labels
raw URL/path IDs excluded from metrics
```

Use synthetic values only.

---

# 80. Dependency Diff

Inspect:

```text
git diff -- backend/pyproject.toml backend/uv.lock
git diff -- package.json pnpm-lock.yaml
```

Expected:

```text
backend changes only for approved OTel packages/lock
frontend dependency files unchanged
```

No unrelated package upgrades.

---

# 81. Security Scan

Existing CI Trivy/Gitleaks must pass with new dependencies.

If a HIGH/CRITICAL vulnerability is introduced:

1. investigate dependency/version;
2. choose a safe compatible version if possible;
3. do not broadly ignore;
4. report blocker if no safe version satisfies phase requirements.

Do not weaken security workflow.

---

# 82. Git Audit

Run:

```text
git status --short
git diff --stat
git diff
git diff --check
```

Inspect every file.

Confirm no:

```text
patient data
real secret
trace dump
generated telemetry output
mlruns
OTel collector config
build/cache artifacts
```

are committed.

---

# 83. Commit & Push

After local verification:

```text
git add <P2-C files only>
git commit -m "feat: establish P2-C observability and feature flags"
git push -u origin phase/p2-c-observability-feature-flags
```

Do not merge.

Do not force-push.

---

# 84. Remote CI

Verify all existing mandatory jobs:

```text
Backend quality
Frontend quality
Docker and PostgreSQL
Playwright Chromium
Security scans
```

If GitHub CLI is available:

```text
gh run list --branch phase/p2-c-observability-feature-flags
gh run watch <run-id> --exit-status
```

Do not claim SUCCESS without evidence.

---

# 85. Closure Commit

If implementation is committed before CI completes:

1. leave tracker partial;
2. push;
3. wait for green CI;
4. update tracker;
5. set P2-C COMPLETE;
6. set P2 COMPLETE;
7. record run evidence;
8. set next unit P3-A;
9. commit documentation closure;
10. push same branch.

Do not merge.

---

# 86. P2 Final Acceptance Audit

Report all:

```text
AC-P2-001 — Typed application settings
AC-P2-002 — Stable error envelope
AC-P2-003 — Correlation/request IDs
AC-P2-004 — Module registration
AC-P2-005 — Capability registry
AC-P2-006 — Feature-flag abstraction
AC-P2-007 — Safe/off risky optional defaults
AC-P2-008 — Privacy-safe structured logging
AC-P2-009 — No feature-specific clinical logic in shared kernel
```

For P2 COMPLETE, every one must be:

```text
PASS
```

---

# 87. Global Architecture Audit

Explicitly verify:

```text
no persistence
no SQLAlchemy
no Alembic
no DB connection from application
no event/outbox
no jobs/workers
no object-store implementation
no auth/session/consent behavior
no clinical logic
no AI/ML/QML
no dynamic plugins
P2-B registries remain sealed
feature flags do not act as authorization
feature flags do not act as clinical policy
external telemetry export remains disabled
no telemetry infrastructure deployed
```

---

# 88. Final Report Format

Return exactly these sections.

## STATUS

One of:

```text
COMPLETE
PARTIAL
BLOCKED
FAILED
```

`COMPLETE` requires remote CI evidence and all P2 criteria passing.

## BRANCH / GIT

Report:

```text
base branch
base SHA
implementation branch
implementation SHA
closure SHA if any
remote SHA
main SHA
working-tree state
```

## SCOPE IMPLEMENTED

Describe only P2-C.

## FEATURE FLAG MODEL

Report:

```text
identifier type/location
provider protocol
service interface
configuration provider
unknown/absent behavior
immutability
application composition
```

## FEATURE FLAG SAFETY

Explicitly report:

```text
Default optional flag state
Unknown valid flag state
Real product flags enabled by default
Feature flag used as authorization
Feature flag used as clinical policy
```

## OBSERVABILITY MODEL

Report:

```text
project-owned runtime type/location
tracer provider strategy
meter provider strategy
service/resource identity
external exporter state
application composition
```

## HTTP TRACING

Report:

```text
span naming
safe attributes
route-template behavior
5xx/error behavior
exception-content behavior
```

## REQUEST METRICS

Report:

```text
instrument names
units
metric attributes
cardinality protections
request_id label status
raw path/query label status
```

## LOG CORRELATION

Report:

```text
request_id behavior
trace_id behavior
span_id behavior
raw content behavior
```

## CONFIGURATION

Report changes to:

```text
ObservabilitySettings
FeaturesSettings
environment compatibility
external export safety
```

## FILES CHANGED

Group:

```text
feature flags
observability
configuration
HTTP/application composition
tests
dependencies
documentation
```

## DEPENDENCIES

For each direct new dependency report:

```text
package
constraint
resolved version
R3 class
license
import locations
reason
network/egress behavior
```

Also note relevant transitive additions.

## TESTS

Report:

```text
new test count
total backend test count
feature-flag tests
trace privacy tests
metric cardinality/privacy tests
log-correlation tests
regression tests
```

## VERIFICATION

Report:

```text
uv lock --check
Ruff
format check
mypy
pytest
compile/import smoke
backend quality gate
frontend quality gate
git diff --check
dependency diff
```

## CI

Report:

```text
run ID
URL
head SHA
Backend quality
Frontend quality
Docker and PostgreSQL
Playwright Chromium
Security scans
overall result
```

## P2 FINAL ACCEPTANCE

Report:

```text
AC-P2-001
AC-P2-002
AC-P2-003
AC-P2-004
AC-P2-005
AC-P2-006
AC-P2-007
AC-P2-008
AC-P2-009
```

using canonical status vocabulary.

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
External telemetry egress disabled by default: YES/NO
No Collector/Prometheus/Grafana/Loki deployed: YES/NO
No raw body/query/auth/cookie telemetry: YES/NO
No request/patient/session IDs in metric labels: YES/NO
No unrestricted exception recording in spans: YES/NO
Unknown/absent optional flags safe-off: YES/NO
No real product feature enabled by default: YES/NO
Feature flags not authorization: YES/NO
Feature flags not clinical policy: YES/NO
No persistence/P3 work introduced: YES/NO
No auth/clinical/AI work introduced: YES/NO
P2-A contracts preserved: YES/NO
P2-B registry contracts preserved: YES/NO
```

## DEVIATIONS

List all deviations.

## BLOCKERS / OPEN DECISIONS

Only real remaining items.

## PROGRESS TRACKER

State:

```text
P2-C status
overall P2 status
CI evidence status
next recommended unit
```

## MERGE

State:

```text
MERGE PERFORMED: NO
```

## RECOMMENDED NEXT UNIT

If P2 is complete:

```text
P3-A — SQLAlchemy & Alembic Persistence Foundation
```

Do not implement it.

---

# 89. Success Definition

P2-C is successful only when:

- a provider-neutral feature-flag interface exists;
- the initial config-backed provider is immutable and deterministic;
- absent/unknown optional flags are disabled;
- no real product feature is enabled by default;
- feature flags are not used for authorization or clinical policy;
- OpenTelemetry API/SDK are integrated behind project-owned observability code;
- no external telemetry exporter is active by default;
- HTTP request tracing is content-free;
- trace route values use bounded templates, not raw patient-specific paths;
- exception details are not indiscriminately recorded;
- request count and duration metrics exist;
- metric labels are bounded and exclude IDs/raw URL/query;
- structured logs retain request ID and can correlate safe trace/span IDs;
- existing error/request/module/capability behavior remains compatible;
- no Collector/Prometheus/Grafana/Loki is deployed;
- no P3/product/clinical/AI work is pulled forward;
- all local backend/frontend gates pass;
- Gitleaks/Trivy remain green;
- all mandatory remote CI jobs pass;
- AC-P2-001 through AC-P2-009 all PASS;
- P2-C is marked COMPLETE;
- overall P2 is marked COMPLETE;
- branch is pushed but not merged.

Stop after P2-C.
