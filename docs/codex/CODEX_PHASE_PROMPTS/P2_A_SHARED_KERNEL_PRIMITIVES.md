# Codex Phase Prompt — P2-A Shared Kernel Types, Errors & Configuration

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P2-A`
**Phase unit:** P2-A — Shared Platform Kernel primitives: shared types, error model, actor context, and typed configuration
**Base branch:** `main`
**Expected base commit:** `a531305c4693e2acd7dc92d58bab1b0c3e0178b5`
**Implementation branch:** `phase/p2-a-shared-kernel-primitives`
**Scope:** Backend shared-kernel primitives only
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

# 0. Mission

Begin P2 — Shared Platform Kernel.

P2-A must strengthen the reusable, framework-light primitives that future modules depend on without implementing P2-B module/capability registration or P2-C feature flags/observability.

Implement only:

```text
shared opaque ID/time primitives
minimal base actor context
shared domain/application/dependency error model
complete canonical error-code registry
stable API error translation
typed application configuration sections with safe defaults
configuration validation and compatibility
tests and documentation
```

Do not implement:

```text
module registry
capability registry
feature-flag service
OpenTelemetry
request metrics
distributed tracing
database connectivity
SQLAlchemy
Alembic
events/outbox
jobs/workers
object storage
identity/session/consent business logic
clinical logic
AI/ML/QML
```

P2-A is a platform-kernel phase, not a product-feature phase.

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

Expected starting state:

```text
branch: main
HEAD: a531305c4693e2acd7dc92d58bab1b0c3e0178b5
working tree: clean
```

Verify `main` contains the completed P1 baseline:

```text
backend/app/main.py
backend/app/config/settings.py
backend/app/api/errors/
backend/app/api/middleware/request_context.py
backend/app/shared/observability/logging.py
backend/uv.lock

scripts/quality_gate.py
.github/workflows/ci.yml
infra/docker/backend.Dockerfile
deployments/local/compose.yaml

docs/codex/CODEX_PHASE_PROMPTS/P1_A_REPOSITORY_BACKEND_TOOLING.md
docs/codex/CODEX_PHASE_PROMPTS/P1_B_FRONTEND_WORKSPACES.md
docs/codex/CODEX_PHASE_PROMPTS/P1_C_DOCKER_CI_FOUNDATION.md
docs/codex/CODEX_PHASE_PROMPTS/P1_C_REVIEW_FIX_01_DOCKER_REPRODUCIBILITY.md
```

If the base commit differs:

1. inspect the intervening commits;
2. continue only if they are the expected user-approved merge/history;
3. report the actual base SHA.

If unrelated local changes exist, stop rather than overwriting them.

---

# 2. Create the Phase Branch

After preflight:

```text
git switch -c phase/p2-a-shared-kernel-primitives
```

If it already exists, inspect it first.

Do not implement directly on `main`.

Do not merge at the end.

---

# 3. Required Reading

Read before editing:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
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
```

Also inspect all existing P1 implementations that P2-A will extend:

```text
backend/app/config/
backend/app/api/errors/
backend/app/api/middleware/
backend/app/shared/
backend/app/main.py
backend/tests/
```

Do not reimplement working P1 behavior from scratch.

---

# 4. Known Specification Drift — Resolve Before Coding

There is a known documentation inconsistency.

The current accepted documents:

```text
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/38_PROGRESS_TRACKER.md
```

define:

```text
P2 = Shared Platform Kernel
P3 = Persistence, Migrations, Events, Outbox and Jobs
```

However, section 2 of:

```text
docs/implementation/36_DEPENDENCY_MAP.md
```

still contains older phase labels:

```text
P2 Persistence / migrations / API conventions
P3 Events / jobs / adapter foundation
```

This is documentation drift.

Before implementation, explicitly report:

```text
SPECIFICATION DRIFT DETECTED
```

with:

```text
source: docs/implementation/36_DEPENDENCY_MAP.md section 2
conflict: P2/P3 labels
canonical current sequence: Master Implementation Plan + Acceptance Criteria + Progress Tracker
resolution: P2 Shared Platform Kernel; P3 Persistence/Events/Jobs
```

This is not permission to redesign the architecture.

Correct the phase-label graph in `36_DEPENDENCY_MAP.md` so it matches the accepted current phase structure:

```text
P0 Governance / repository foundation
 |
P1 Repository + tooling foundation
 |
P2 Shared Platform Kernel
 |
P3 Persistence / migrations / events / jobs / adapter foundation
 |
...
```

Do not otherwise rewrite R3 technology decisions.

No ADR is required for this editorial reconciliation unless implementation reveals a genuine architecture change.

Most importantly:

```text
DO NOT add SQLAlchemy/Alembic/database code in P2-A.
```

---

# 5. P2 Canonical Requirements

P2 is governed primarily by:

```text
FR-CORE-004 — Feature independence
FR-CORE-005 — Typed contracts
FR-CORE-006 — Versioned public interfaces
FR-CORE-009 — Configuration-driven behavior
FR-CORE-010 — Graceful degradation

FR-EXT-003 — Capability-based integration
FR-EXT-004 — Feature registration
FR-EXT-005 — Feature flags
FR-EXT-011 — Architecture decision records
```

P2-A directly implements only the portions appropriate to shared types/errors/configuration.

P2-B owns:

```text
module registration
module manifest
capability registry/resolution
```

P2-C owns:

```text
feature-flag abstraction
safe flag defaults
OpenTelemetry skeleton
request metrics/content-free tracing
observability completion
```

Do not pull P2-B/P2-C work into P2-A.

---

# 6. P2 Acceptance Criteria Relevant to P2-A

P2-A should directly establish or strengthen:

```text
AC-P2-001 — Typed application settings exist.
AC-P2-002 — Stable error envelope exists.
AC-P2-003 — Correlation/request IDs propagate through HTTP flow.
AC-P2-008 — Structured logging is enabled without raw request-body logging by default.
AC-P2-009 — Shared kernel contains no feature-specific clinical logic.
```

P2-A may preserve/verify existing P1 behavior for some of these.

Do not claim the whole P2 phase complete.

The following remain for later P2 units:

```text
AC-P2-004 — module registration
AC-P2-005 — capability registry
AC-P2-006 — feature-flag abstraction
AC-P2-007 — risky optional features default safe/off
```

At the end:

```text
P2-A: COMPLETE if its criteria pass
P2: PARTIAL
```

---

# 7. Shared Kernel Placement

Use the existing shared-kernel directories:

```text
backend/app/shared/domain/
backend/app/shared/errors/
backend/app/shared/security/
backend/app/shared/types/
backend/app/shared/utils/
```

Create real modules only where P2-A needs them.

Remove `.gitkeep` only from directories that gain real tracked content.

Do not create a generic dumping ground.

Rules:

```text
shared kernel contains only genuinely cross-cutting primitives
no feature-specific clinical concepts
no provider-specific SDK objects
no database models
no FastAPI types in framework-independent shared modules
```

---

# 8. Shared ID Primitives

Create a small, typed ID foundation.

Goals:

```text
opaque UUID-based identifiers
clear generation helper
framework-independent
no sequential IDs
deterministic parsing/validation where needed
easy later specialization by modules
```

Do not invent every future domain ID now.

A good design may use:

```text
UUID
NewType
small frozen value object
```

but avoid unnecessary abstraction.

At minimum provide a well-tested way to:

```text
generate a UUID4 identifier
accept/represent an existing UUID safely
serialize/stringify predictably where relevant
```

Do not create patient/session/encounter entity classes in P2-A.

---

# 9. Time Utility

Create a single shared UTC time helper.

It must return timezone-aware UTC.

Expected semantics:

```python
utc_now() -> datetime
```

with:

```text
tz-aware
UTC
testable
no naive datetime
```

Do not add a third-party datetime library.

Use standard library.

Do not create a global mutable clock framework unless genuinely needed.

If a small injectable clock protocol improves future testability without overengineering, it may be introduced.

---

# 10. Request/Correlation ID Primitive

P1 already implements request IDs.

Do not break its contract.

Current API behavior must remain:

```text
optional inbound X-Request-ID
validate allowed format
generate opaque request ID if invalid/missing
store in request state/context
return X-Request-ID response header
include in error envelope
include in structured logs
```

P2-A may move generation/validation into shared typed primitives if that improves ownership.

Do not expose an unsafe arbitrary inbound header.

Keep the existing maximum/character safety policy unless a higher-priority spec says otherwise.

Tests must prove propagation still works.

---

# 11. Base Actor Context

The P2 master plan requires a base actor representation for later authorization.

Implement only the smallest generic actor context that can be defined without inventing P4 identity/authorization policy.

It may represent generic context such as:

```text
actor identifier when known
session identifier when known
request/correlation identifier when useful
authentication presence/state at a generic level
```

But P2-A MUST NOT define:

```text
patient role policy
clinician role policy
admin permissions
resource authorization
OIDC/JWT behavior
Keycloak claims
session token lifecycle
consent rules
```

P4 owns those.

Do not create route authorization dependencies in P2-A.

The type must be:

```text
framework-independent
immutable/frozen where practical
safe for pseudonymous/unknown actor state
```

If a role enum is not required for the base context, do not invent one yet.

---

# 12. Shared Error Model

Refactor the current foundation error types into a clean shared error layer.

Desired conceptual hierarchy:

```text
SwasthyaSetuError / project base
├── DomainError
├── ApplicationError
└── DependencyError
```

Exact names may differ if existing conventions are better.

The shared error layer must:

```text
be framework-independent
not import FastAPI
not import Starlette
not construct JSONResponse
carry stable machine-readable error code
carry safe public message
carry safe structured details where applicable
preserve exception cause internally when useful
not expose stack traces/secrets in public output
```

Do not create a deep exception hierarchy.

Use composition/simple subclasses.

---

# 13. Canonical ErrorCode Registry

The existing P1 implementation contains only a subset of the canonical API codes.

P2-A must align the shared error-code registry with `06_API_CONTRACTS.md`.

Canonical initial codes:

```text
VALIDATION_ERROR
AUTHENTICATION_REQUIRED
AUTHORIZATION_DENIED
RESOURCE_NOT_FOUND
RESOURCE_CONFLICT
INVALID_STATE_TRANSITION
FEATURE_DISABLED
CONSENT_REQUIRED
SESSION_EXPIRED
RATE_LIMITED
DEPENDENCY_TIMEOUT
DEPENDENCY_UNAVAILABLE
PROCESSING_FAILED
POLICY_UNAVAILABLE
INSUFFICIENT_INFORMATION
UNSUPPORTED_MEDIA_TYPE
PAYLOAD_TOO_LARGE
```

Do not invent clinical-specific codes.

Modules may add documented codes later through governed contracts.

The registry should have one authoritative location.

Avoid duplicate enums in API and shared layers.

---

# 14. Stable HTTP Error Envelope

Preserve the canonical API envelope exactly:

```json
{
  "error": {
    "code": "CONSENT_REQUIRED",
    "message": "Consent is required for this operation.",
    "request_id": "req_...",
    "details": {}
  }
}
```

The API transport layer owns serialization.

Shared/domain exceptions should not directly return HTTP responses.

Keep:

```text
code stable/machine-readable
message safe to expose
request_id present
details non-sensitive
no exception class names
no stack traces
```

Do not silently change existing frontend-consumable shape.

---

# 15. HTTP Error Translation

Centralize framework translation at the API boundary.

Use an explicit mapping from shared error semantics/codes to HTTP status.

Preserve existing behavior where canonical.

Expected mappings include appropriate use of:

```text
400
401
403
404
409
413
415
422
429
503
```

If `DEPENDENCY_TIMEOUT` needs a status not explicitly frozen by the canonical API document, choose conservatively and document the mapping rather than inventing a new public envelope.

Do not put HTTP status codes into domain rules.

Unhandled exceptions must still return a generic privacy-safe `PROCESSING_FAILED`.

---

# 16. Dependency Errors

Provide a generic dependency error representation for future adapters.

It must be provider-neutral.

Examples of concepts:

```text
dependency unavailable
dependency timeout
```

Do not add:

```text
OpenAIError
PaddleOCRError
HAPIError
KeycloakError
```

in shared kernel.

Vendor-specific adapter errors will later map into these generic categories.

No retry logic belongs in P2-A.

---

# 17. Configuration Architecture

Expand the typed configuration foundation without activating future providers.

The P2 master plan expects typed sections for:

```text
app
database
security
object_storage
llm
ocr
speech
fhir
abdm
observability
features
```

Create a clean typed configuration structure using Pydantic/Pydantic Settings already present.

Do not add a new settings framework.

---

# 18. Configuration Compatibility

P1 already uses these environment variables:

```text
SWASTHYASETU_APP_NAME
SWASTHYASETU_ENVIRONMENT
SWASTHYASETU_DEBUG
SWASTHYASETU_API_V1_PREFIX
SWASTHYASETU_LOG_LEVEL
```

P1 Docker/Compose currently relies on at least:

```text
SWASTHYASETU_ENVIRONMENT
SWASTHYASETU_DEBUG
SWASTHYASETU_LOG_LEVEL
```

P2-A must not silently break them.

If settings are reorganized into nested sections:

```text
preserve legacy P1 environment compatibility
add tests for the compatibility contract
document any new nested environment naming
```

Do not require P1 deployment files to be rewritten merely because settings classes were reorganized.

---

# 19. Configuration Safe Defaults

Default configuration must keep undeployed optional systems inactive.

Do not silently activate:

```text
database integration
object storage
LLM
OCR
speech
FHIR
ABDM
experimental features
external telemetry exporter
```

P2-A defines configuration shape, not active integrations.

Do not invent production URLs, credentials, model names, tenant IDs, or clinical policy values.

---

# 20. Configuration Secret Types

Where a future setting is inherently secret, use an appropriate secret-aware type such as:

```text
SecretStr
```

or keep the field absent/optional until its phase if there is no justified field yet.

Do not log secret values.

Do not stringify secret values into diagnostics.

Do not add real secrets to `.env.example`.

---

# 21. Minimal Section Design

Do not over-specify providers that have not been selected.

For each typed section:

```text
define only fields justified by current architecture
use safe defaults
prefer provider-neutral names
avoid speculative options
```

A section with no current phase-specific implementation may remain deliberately minimal.

Do not fill configuration classes with dozens of guessed fields.

---

# 22. Database Configuration Boundary

P2-A may define typed database configuration shape if needed by the canonical settings structure.

It MUST NOT:

```text
import SQLAlchemy
create an engine
connect to PostgreSQL
create a DSN automatically from production-like secrets
change readiness to depend on DB
run migrations
```

P3 owns persistence.

The current local PostgreSQL service remains an infrastructure foundation only.

---

# 23. Object Storage / AI / FHIR / ABDM Configuration Boundaries

P2-A may define disabled/minimal provider-neutral config sections.

Do not implement ports/adapters yet unless already required by P2-A canonical scope.

Do not add provider SDKs.

Do not add network calls.

Do not validate connectivity.

No R3 benchmark-gated technology is activated by configuration classes existing.

---

# 24. Observability Configuration Boundary

P2-C owns OpenTelemetry and metrics/tracing.

P2-A may define an observability settings section needed for typed configuration.

Preserve P1 JSON logging.

Do not add:

```text
opentelemetry packages
collector
Prometheus
Grafana
trace exporter
metrics exporter
```

Do not change logging to capture request bodies.

---

# 25. Features Configuration Boundary

P2-C owns the feature-flag abstraction.

P2-A may define a typed `features` configuration namespace only if needed for the master-plan settings structure.

Do not implement:

```text
FeatureFlagService
flag evaluation
rollout percentages
user targeting
database-backed flags
remote flag provider
```

No risky feature should become active.

---

# 26. Structured Logging Regression

P1 structured logging already:

```text
uses JSON
uses an allowlist of operational fields
carries request_id context
does not log request body by default
```

Preserve it.

Add/retain tests proving that request body content does not appear in normal access logs.

Do not add raw:

```text
conversation
document text
tokens
Authorization header
cookies
FHIR payloads
secrets
```

to logs.

P2-C will extend observability later.

---

# 27. Framework Boundary

Shared kernel modules should not depend on transport/framework packages unless the type is specifically transport-owned.

Good:

```text
shared/errors -> Python/Pydantic only
shared/types -> standard library
shared/security actor context -> standard library/domain types
api/errors -> FastAPI/Starlette translation
```

Bad:

```text
shared/domain imports FastAPI Request
shared/errors returns JSONResponse
shared/types imports SQLAlchemy
```

---

# 28. Dependency Policy

P2-A should require **no new runtime dependency** beyond the existing P1 backend stack.

Expected:

```text
Python stdlib
Pydantic v2
pydantic-settings
```

Do not add:

```text
SQLAlchemy
Alembic
asyncpg
psycopg
OpenTelemetry
dependency-injector
attrs
pendulum
arrow
feature flag SDK
JWT/OIDC library
```

If Codex believes a new dependency is unavoidable:

```text
STATUS: BLOCKED — DEPENDENCY REVIEW REQUIRED
```

and explain why.

Do not install it silently.

---

# 29. Suggested File Shape

Use judgment and existing repository conventions.

A reasonable shape could be:

```text
backend/app/shared/types/
    __init__.py
    ids.py
    time.py

backend/app/shared/security/
    __init__.py
    actor.py

backend/app/shared/errors/
    __init__.py
    base.py
    codes.py

backend/app/config/
    __init__.py
    settings.py
    sections.py

backend/app/api/errors/
    models.py
    handlers.py
```

This is guidance, not permission to create unnecessary files.

Prefer cohesive modules over ceremony.

---

# 30. Existing Error Import Compatibility

Search the repository before moving error classes.

If current imports exist, update them deliberately.

Do not leave multiple authoritative `ErrorCode` or `ApplicationError` definitions.

Short-lived compatibility re-exports are acceptable if they prevent unnecessary breakage, but document them and avoid permanent duplication.

---

# 31. Settings Access Compatibility

Current code accesses:

```text
settings.app_name
settings.environment
settings.debug
settings.api_v1_prefix
settings.log_level
```

Before changing this API, inspect every caller.

Prefer preserving these access patterns in P2-A unless there is a strong architectural reason to migrate them.

If nested typed sections are introduced, compatibility properties/aliases may be used.

Do not create a widespread unrelated refactor.

---

# 32. Health Endpoint Compatibility

P2-A must preserve:

```text
GET /health/live
GET /health/ready
```

Current readiness remains dependency-free because no required application dependency is implemented.

Do not add future services to readiness just because config sections exist.

---

# 33. API Version Compatibility

Preserve:

```text
/api/v1
```

No new product endpoint is required in P2-A.

Do not add actor/config/error debug endpoints.

Do not expose settings over HTTP.

---

# 34. Tests — Shared IDs

Add unit tests proving at least:

```text
new IDs are valid UUID4 values
distinct generations produce distinct IDs
existing valid UUID representation is handled predictably if parsing helper exists
invalid values fail deterministically if parsing is exposed
```

Do not test probabilistic uniqueness with huge loops.

---

# 35. Tests — Time

Add unit tests proving:

```text
UTC-aware datetime
zero UTC offset
no naive datetime
```

If an injectable clock/protocol is implemented, test deterministic substitution.

---

# 36. Tests — Actor Context

Test:

```text
unknown/pseudonymous-safe base context can exist without identity data
context is immutable if designed frozen
no role/authorization inference occurs
```

Do not invent P4 role tests.

---

# 37. Tests — Error Model

Test:

```text
canonical error codes exist
shared errors are framework-independent
application error -> stable public envelope
dependency unavailable/timeout -> stable safe mapping
validation errors do not echo submitted sensitive values
unhandled exceptions -> generic PROCESSING_FAILED
details remain safe/structured
request_id remains present
```

Do not assert stack traces in responses.

---

# 38. Tests — Settings

Test:

```text
default settings load
P1 environment variables still load
invalid environment rejected
invalid API prefix rejected
nested/minimal sections are typed
optional future integrations default inactive/unconfigured
secret fields do not reveal raw value via normal representation
unknown extra env does not crash if canonical behavior remains extra=ignore
settings are immutable/frozen
```

Do not contact external services in settings tests.

---

# 39. Tests — Correlation IDs

Preserve/add coverage for:

```text
client valid X-Request-ID propagates
invalid ID replaced
missing ID generated
response header matches error-envelope request_id
request context reaches structured logger
```

No raw header dump.

---

# 40. Tests — Logging Privacy

Add/retain a test that sends a request with a synthetic sensitive-looking body/string and proves normal request logging does not contain it.

Use synthetic text only.

Do not add real health data.

---

# 41. No Persistence

Do not modify:

```text
deployments/local/compose.yaml
```

except if a factual documentation-only correction is absolutely necessary.

Do not add DB application settings that trigger connectivity.

No new:

```text
backend/app/db/
migrations/
alembic.ini
SQLAlchemy models
repository implementation
```

P3-A owns those.

---

# 42. No Module/Capability Registry Yet

P2-B owns:

```text
module manifest
explicit module registration
capability declaration
typed capability resolution
duplicate capability errors
missing capability errors
```

Do not implement them now.

If existing P1 router registration resembles module registration, leave it as-is unless P2-A needs a small type import refactor.

---

# 43. No Feature Flags Yet

P2-C owns feature flags.

Do not create a partial flag engine in P2-A.

Do not add environment booleans for hypothetical product features merely to claim progress.

---

# 44. No OpenTelemetry Yet

P2-C owns OTel skeleton.

Do not add OTel dependencies or exporters.

P1 JSON logs remain sufficient for P2-A.

---

# 45. No Clinical/Product Logic

P2-A shared kernel must contain no:

```text
symptom logic
triage
mental-health routes
self-care
Ayurveda
provider routing
patient/encounter behavior
consent behavior
diagnosis
risk scores
medical thresholds
```

No clinical source material needs to be modified.

---

# 46. Documentation Updates

Update only what P2-A actually changes.

Expected:

```text
README.md if current-status text needs advancing to P2
REPOSITORY_TREE.txt
docs/implementation/36_DEPENDENCY_MAP.md phase-label drift correction
docs/implementation/38_PROGRESS_TRACKER.md
```

Update `37_DECISION_LOG.md` only if a genuinely new durable architecture decision is required.

Do not create an ADR for routine shared-kernel implementation already mandated by canonical architecture.

---

# 47. Progress Tracker

After successful local verification and remote CI:

```text
P2-A: COMPLETE
P2: PARTIAL
```

Record:

```text
branch
base SHA
implementation SHA
requirement IDs
acceptance criteria
tests
quality gates
CI run
known remaining P2-B/P2-C work
```

Do not mark:

```text
P2 = COMPLETE
```

until P2-B and P2-C pass.

Recommended next action should become:

```text
P2-B — Module Manifest & Capability Registry
```

---

# 48. Quality Gates

Run at least:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

The frontend should remain untouched behaviorally, but P1 regression must stay green.

Also run:

```text
git diff --check
```

If Docker/container files are unchanged, a local rebuild is not mandatory for P2-A, but remote CI must remain green.

---

# 49. Backend Direct Verification

From `backend/` run the existing checks directly or through the quality gate:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
```

Run import smoke.

All must pass.

---

# 50. Dependency Lock Check

P2-A is expected to add no dependency.

After implementation:

```text
git diff -- backend/pyproject.toml backend/uv.lock
```

Expected:

```text
no dependency change
```

If changed, explain exactly why and re-evaluate against section 28.

---

# 51. Security / Privacy Audit

Before commit verify:

```text
no secrets
no real patient data
no request-body logging
no Authorization/cookie logging
no provider credentials
no debug settings endpoint
no permissive auth bypass
```

P2-A should not require new security infrastructure.

---

# 52. Diff Audit

Run:

```text
git status --short
git diff --stat
git diff
git diff --check
```

Inspect every changed file.

Explicitly confirm no unrelated changes.

---

# 53. Commit & Push

When local checks pass:

```text
git add <P2-A files only>
git commit -m "feat: establish P2-A shared kernel primitives"
git push -u origin phase/p2-a-shared-kernel-primitives
```

Do not merge.

Do not force-push.

Do not squash historical P1 work.

---

# 54. Remote CI

The existing P1 CI workflow applies to `phase/**`.

After pushing, verify the workflow.

All existing mandatory jobs should remain green:

```text
Backend quality
Frontend quality
Docker and PostgreSQL
Playwright Chromium
Security scans
```

If GitHub CLI is available:

```text
gh run list --branch phase/p2-a-shared-kernel-primitives
gh run watch <run-id> --exit-status
```

Equivalent safe verification is acceptable.

Do not claim remote CI success without observing it.

---

# 55. Completion Commit

If the implementation commit is pushed before CI evidence is available, keep P2-A `PARTIAL` in the tracker.

After the branch CI is green:

1. update tracker to `P2-A COMPLETE`;
2. keep overall P2 `PARTIAL`;
3. record the CI run;
4. create a small closure commit if needed;
5. push same branch.

Do not merge.

---

# 56. Failure Handling

If a test reveals a legitimate issue:

```text
fix the implementation
add/retain regression coverage
rerun relevant gates
```

Do not:

```text
skip test
weaken assertion
disable mypy rule
add broad Ruff ignore
hide CI failure
```

---

# 57. Final Report Format

Return exactly the following sections.

## STATUS

One of:

```text
COMPLETE
PARTIAL
BLOCKED
FAILED
```

## SPECIFICATION DRIFT

Report:

```text
Detected: YES/NO
Source
Conflict
Resolution
Files reconciled
```

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

Describe only P2-A.

## SHARED TYPES

Report:

```text
ID primitive
time primitive
request/correlation primitive changes
actor context
```

## ERROR MODEL

Report:

```text
shared error hierarchy
authoritative ErrorCode location
canonical codes implemented
HTTP translation location
public envelope compatibility
```

## CONFIGURATION

Report each typed section and its safe default behavior:

```text
app
database
security
object_storage
llm
ocr
speech
fhir
abdm
observability
features
```

Also report P1 env compatibility.

## FILES CHANGED

Group:

```text
shared kernel
configuration
API error boundary
tests
documentation
```

## DEPENDENCIES

Expected:

```text
No new runtime dependency
```

If anything changed, list:

```text
name
version
classification
reason
license
```

## TESTS

List newly added/updated tests and counts.

## VERIFICATION

Report exact results for:

```text
uv lock --check
Ruff
format
mypy
pytest
compile/import smoke
backend quality gate
frontend quality gate
git diff --check
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

## P2 ACCEPTANCE STATUS

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

Use:

```text
PASS
FAIL
BLOCKED
NOT APPLICABLE
NOT YET IMPLEMENTED
```

Expected P2-A pattern:

```text
001 PASS
002 PASS
003 PASS
004 NOT YET IMPLEMENTED
005 NOT YET IMPLEMENTED
006 NOT YET IMPLEMENTED
007 NOT YET IMPLEMENTED
008 PASS
009 PASS
```

Do not force the expected pattern if actual evidence differs.

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
No persistence introduced: YES/NO
No SQLAlchemy/Alembic added: YES/NO
No module/capability registry pulled forward: YES/NO
No feature-flag engine pulled forward: YES/NO
No OpenTelemetry pulled forward: YES/NO
No auth/session/consent business logic pulled forward: YES/NO
No clinical logic introduced: YES/NO
No AI/ML/QML dependency introduced: YES/NO
No real secret/patient data committed: YES/NO
Stable API error envelope preserved: YES/NO
P1 deployment compatibility preserved: YES/NO
```

## DEVIATIONS

List all deviations.

## BLOCKERS / OPEN DECISIONS

Only genuine unresolved issues.

## PROGRESS TRACKER

State:

```text
P2-A status
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

If P2-A is complete:

```text
P2-B — Module Manifest & Capability Registry
```

Do not implement it.

---

# 58. Success Definition

P2-A is complete only when:

- specification drift is reconciled without pulling persistence into P2;
- shared UUID/time primitives exist and are tested;
- a minimal framework-independent actor context exists;
- shared error types are framework-independent;
- the full canonical initial API error-code registry has one authoritative location;
- API error envelope remains stable;
- request/correlation IDs continue to propagate;
- settings are typed and structured for the P2 platform sections;
- P1 environment compatibility is preserved;
- optional/future integrations default inactive or unconfigured;
- no new runtime dependency is added unless explicitly approved;
- logs remain structured and content-free by default;
- backend tests/lint/types pass;
- frontend regression gates pass;
- remote CI remains green;
- P2-A is recorded complete while overall P2 remains partial;
- no P2-B/P2-C/P3/product/clinical work is pulled forward;
- branch is pushed but not merged.

Stop after P2-A.
