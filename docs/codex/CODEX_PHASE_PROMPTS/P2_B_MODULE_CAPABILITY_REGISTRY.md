# Codex Phase Prompt — P2-B Module Manifest & Capability Registry

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P2-B`
**Phase unit:** P2-B — Module Manifest & Capability Registry
**Base branch:** `main`
**Expected base commit:** `6c8fe9f54fc16788acc9c478638864a5a69eb988`
**Implementation branch:** `phase/p2-b-module-capability-registry`
**Scope:** Shared-kernel module metadata, explicit module registration, and typed capability resolution only
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

# 0. Mission

Continue P2 — Shared Platform Kernel by implementing the architecture-approved module registration and capability-resolution foundation.

P2-A already established:

```text
shared UUID/time/request-ID primitives
minimal ActorContext
framework-independent shared error hierarchy
canonical ErrorCode registry
stable HTTP error envelope
typed configuration sections
privacy-safe structured logging
```

P2-B must now implement:

```text
typed module manifest metadata
typed capability identifiers/keys
explicit compile-time module registration
capability provider registration
capability resolution
dependency-graph validation
duplicate/conflict detection
missing-required-capability detection
sealed/finalized runtime registry
FastAPI composition integration without global service-locator behavior
tests and documentation
```

P2-B MUST NOT implement:

```text
feature-flag evaluation
OpenTelemetry
request metrics/tracing
database persistence
SQLAlchemy/Alembic
events/outbox
job dispatch
object storage
identity/auth/session/consent business logic
clinical feature modules
AI/ML/QML
dynamic plugin loading
runtime code discovery/import scanning
```

P2-C owns observability + feature flags.

P3 owns persistence/events/jobs/object storage.

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
HEAD: 6c8fe9f54fc16788acc9c478638864a5a69eb988
working tree: clean
```

Verify merged P2-A exists:

```text
backend/app/shared/errors/
backend/app/shared/security/actor.py
backend/app/shared/types/
backend/app/config/sections.py
backend/app/config/settings.py

docs/codex/CODEX_PHASE_PROMPTS/P2_A_SHARED_KERNEL_PRIMITIVES.md
```

Verify:

```text
docs/implementation/38_PROGRESS_TRACKER.md
```

currently records:

```text
P2-A COMPLETE
P2 PARTIAL
next: P2-B — Module Manifest & Capability Registry
```

If `main` legitimately advanced from the expected merge commit, inspect and report the actual base before proceeding.

If unrelated local changes exist, stop rather than overwrite them.

---

# 2. Create the Phase Branch

Create:

```text
git switch -c phase/p2-b-module-capability-registry
```

If that branch already exists:

1. inspect its commit history;
2. compare against `main`;
3. preserve legitimate user work;
4. continue only if clearly intended for P2-B.

Do not implement on `main`.

Do not merge at completion.

---

# 3. Required Reading

Read before editing:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
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
```

Inspect current implementation before editing:

```text
backend/app/main.py
backend/app/api/v1/router.py
backend/app/shared/
backend/app/modules/
backend/tests/
```

Do not code from assumptions.

---

# 4. Canonical Architecture Decisions

P2-B implements already-accepted architecture.

Important accepted decisions include:

```text
ADR-001 — Modular Monolith First
ADR-007 — Compile-Time Feature Registration
ADR-021 — Internal Contracts Are Typed
ADR-026 — No Arbitrary Runtime Plugin System
```

Relevant architecture requirements:

```text
ARCH-P-002 — strong module boundaries
ARCH-P-007 — contract-first boundaries
ARCH-P-010 — graceful degradation
ARCH-P-012 — feature isolation
```

Relevant product requirements:

```text
FR-CORE-004 — feature independence
FR-CORE-005 — typed contracts
FR-CORE-006 — versioned public interfaces
FR-CORE-010 — graceful degradation

FR-EXT-003 — capability-based integration
FR-EXT-004 — feature registration
FR-EXT-008 — no central conditional explosion
FR-EXT-011 — architecture decisions
```

Do not create a new ADR merely to restate these accepted decisions.

---

# 5. P2-B Acceptance Targets

P2-B directly targets:

```text
AC-P2-004 — Module registration mechanism exists.
AC-P2-005 — Capability registry or equivalent public capability resolution exists.
AC-P2-009 — Shared kernel contains no feature-specific clinical logic.
```

P2-A already established:

```text
AC-P2-001
AC-P2-002
AC-P2-003
AC-P2-008
```

P2-C remains responsible for:

```text
AC-P2-006 — feature-flag abstraction
AC-P2-007 — risky optional features default safe/off
```

At completion:

```text
P2-B = COMPLETE
P2 = PARTIAL
```

Do not mark P2 complete before P2-C.

---

# 6. Shared-Kernel Principle

Keep this mechanism small.

The module/capability infrastructure exists to prevent:

```text
god services
vendor coupling
global feature-specific if/else chains
direct module internals access
runtime plugin chaos
hidden dependencies
```

It must not become:

```text
a dependency-injection framework
a generic application framework
a runtime plugin marketplace
a dynamic module loader
a global mutable service locator
```

Do not add a third-party DI/container package.

---

# 7. Placement

Use existing repository areas.

A reasonable implementation shape is:

```text
backend/app/shared/modules/
    __init__.py
    manifest.py
    registry.py

backend/app/shared/capabilities/
    __init__.py
    keys.py
    registry.py
```

or an equivalently cohesive structure under `backend/app/shared/`.

Do not create new top-level directories.

Do not put registration mechanics inside a clinical feature module.

Remove `.gitkeep` only where real files now exist.

---

# 8. Module Manifest

Implement an immutable typed runtime representation of the architecture's feature/module manifest.

The architecture gives this conceptual shape:

```yaml
id: providers
version: 1

capabilities:
  - providers.search
  - providers.read

requires:
  - consent.check

api_prefix:
  - /api/v1/providers

events_published:
  - ProviderVerified
  - ProviderExpired

events_consumed:
  - ResourceVerificationRequested

permissions:
  - provider:read
  - provider:manage

feature_flags:
  - provider_directory_enabled
```

FR-EXT-004 additionally requires feature declarations for:

```text
identifier
capabilities
required permissions
required capabilities
APIs
events
configuration
feature flags
data ownership
```

P2-B should therefore define a generic typed manifest capable of representing those categories.

Do not implement the actual systems behind:

```text
permissions
events
configuration
feature flags
data ownership
```

They are metadata in P2-B.

---

# 9. Manifest Fields

The manifest should have clear immutable fields equivalent to:

```text
module_id
version
provided_capabilities
required_capabilities
api_prefixes / APIs
events_published
events_consumed
required_permissions
configuration_keys
feature_flags
data_ownership
```

Use tuples/frozen sets/immutable value objects where practical.

Do not use mutable default lists.

Do not add healthcare-specific fields.

Do not invent clinical safety classification metadata here unless a canonical document requires it.

---

# 10. Manifest Identity

Module identifiers must be stable and machine-readable.

Examples from the architecture:

```text
identity
sessions
consent
patients
providers
resources
referrals
```

Do not pre-create all future module manifests.

Tests should use synthetic neutral module IDs such as:

```text
alpha
beta
catalog
example
```

Production `main` may still contain zero active product module registrations after P2-B.

That is acceptable.

P2-B proves the mechanism; later phases register their real modules.

---

# 11. Manifest Version

Use a simple explicit manifest/public-contract version.

The architecture example uses:

```text
version: 1
```

Prefer a positive integer unless another canonical document already freezes a different type.

Do not introduce semantic-version parsing dependency.

Do not equate:

```text
manifest version
application version
database migration version
API version
```

They are separate concepts.

---

# 12. Capability Identifier

Implement a typed capability identifier/key.

Canonical examples include:

```text
identity.current_actor
consent.check
patients.read
patients.timeline
intake.start
safety.evaluate
ocr.extract
llm.extract
providers.search
referrals.create
fhir.export
risk.predict
notifications.send
```

Do not create all of these as active providers now.

The identifier representation should:

```text
be immutable
be hashable
be stable
support equality
have a safe string representation
reject obvious empty/invalid values if validation is implemented
```

Avoid an over-restrictive grammar that would make future canonical capability names impossible.

A simple dotted-name rule is acceptable if it supports current examples.

---

# 13. Typed Capability Key

Capability resolution must be typed at the Python API boundary.

A good conceptual design is:

```python
CapabilityKey[T]
```

where:

```text
name identifies the capability
T expresses the expected public contract/protocol
```

Exact implementation is up to Codex.

Possible patterns include:

```text
generic dataclass
generic named value object
Protocol-aware key
```

Do not use `Any` as the normal public capability-resolution contract.

Do not require a third-party DI library.

---

# 14. Capability Provider Registration

Support explicit provider registration during application composition.

Conceptually:

```text
CapabilityKey[T] -> implementation of T
```

Registration must be explicit.

Do not:

```text
scan Python packages
use entry-point discovery
import arbitrary modules by string
load Python code from config
watch directories
allow request-time provider registration
```

This is compile-time/deployment-time composition.

---

# 15. Capability Registry

Implement a registry with at least:

```text
register capability provider during composition
resolve capability by typed key
detect duplicate capability provider
detect missing capability
enumerate registered capability names for diagnostics/tests if safe
```

Resolution should fail clearly and deterministically if a required capability is unavailable.

Do not silently return `None` for a required capability.

Optional capability semantics are not required in P2-B unless the canonical design already needs them.

---

# 16. No Global Mutable Service Locator

Do not create:

```python
CAPABILITIES = {}
```

as a global registry imported throughout the application.

Do not let domain code call a process-wide singleton.

Preferred model:

```text
composition root creates registry
registry is finalized/sealed
resolved public capability is injected/passed into consumers
```

The registry may be stored on:

```text
application.state
```

as composition metadata for future FastAPI dependencies, if useful.

But business/domain code should not depend on `FastAPI.app.state`.

---

# 17. Registry Finalization / Sealing

After application composition, runtime registration should stop.

Implement an explicit concept such as:

```text
finalize()
seal()
build()
```

or an immutable builder/result pattern.

After finalization:

```text
new module registration fails
new capability provider registration fails
existing resolutions remain available
```

This enforces ADR-007/ADR-026 and prevents accidental request-time plugin mutation.

Do not overengineer concurrency primitives.

Application composition is single-process startup work.

---

# 18. Module Registration

Implement explicit module registration.

A module registration should conceptually associate:

```text
ModuleManifest
zero or more module routers
zero or more capability provider bindings
```

Do not require every module to expose a router or capability.

Later modules may be:

```text
API-only
capability-only
event-only
worker-oriented
```

P2-B should keep the representation generic.

---

# 19. Duplicate Module Detection

Registering the same `module_id` twice must fail during composition.

Do not silently replace the earlier module.

Do not use "last writer wins."

The failure should be typed and testable.

Do not add a new public HTTP `ErrorCode` merely for startup configuration errors.

These are composition/startup errors unless deliberately mapped later.

---

# 20. Capability Declaration Integrity

A module's actual capability provider bindings must agree with its manifest.

At minimum detect:

```text
module binds capability it did not declare as provided
duplicate capability provider across modules
required capability unavailable after all modules are registered
```

If a declared provided capability has no concrete binding, decide conservatively:

- either reject at finalization, or
- explicitly support declaration-only metadata with clear semantics.

Prefer fail-fast consistency for active module registrations.

Document the chosen behavior and test it.

---

# 21. Required Capability Validation

Required capabilities should be validated across the entire module set after registration, not in fragile registration order.

This must work:

```text
register module A requiring beta.read
register module B providing beta.read
finalize -> PASS
```

even if A is registered first.

This must fail:

```text
register module A requiring missing.read
finalize -> typed startup error
```

Do not create order-dependent hidden behavior.

---

# 22. Cycles

P2-B does not need a full graph-theory dependency solver unless canonical requirements demand it.

Capability dependencies can be cyclical at metadata level in future.

Do not reject cycles unless they create a concrete startup problem.

The required check is:

```text
required capability has a provider
```

not topological sorting.

---

# 23. API Router Integration

Current P1/P2-A composition supports:

```python
create_app(..., api_v1_routers=(...))
```

and:

```python
build_api_v1_router(...)
```

P2-B should integrate module registration with router composition without breaking existing behavior.

Preferred direction:

```text
module registrations can contribute APIRouter instances
the API v1 router includes those routers
```

Preserve:

```text
/api/v1
```

Do not introduce a new API version.

Do not create real product endpoints.

---

# 24. Backward Compatibility

Existing tests and construction patterns from P1/P2-A must remain valid unless there is a compelling architecture reason to migrate them.

In particular preserve:

```text
create_app(Settings(...))
health endpoints
stable error envelope
request IDs
structured logging
P1 deployment container startup
```

If `api_v1_routers` remains for low-level transport tests, that is acceptable.

If it is intentionally superseded, migration must be narrow and all tests updated.

Do not create a broad app-factory rewrite.

---

# 25. Application State

If registry objects are attached to FastAPI app state, use explicit names such as:

```text
application.state.module_registry
application.state.capability_registry
```

Do not expose them through an HTTP debug endpoint.

Do not serialize provider objects.

Do not log object representations that may later contain secrets.

---

# 26. No Real Module Activation

P2-B MUST NOT activate:

```text
identity
sessions
consent
patients
encounters
clinical_intake
safety
mental_health
documents
providers
referrals
FHIR
ABDM
ML
```

Do not add their `public.py` implementations yet.

Do not convert every placeholder module folder into boilerplate.

The repository structure explicitly says:

> Do not create empty ceremony for every subfolder on day one.

Honor that rule.

Use synthetic module registrations in tests.

---

# 27. Public Module Interface Pattern

The architecture expects mature modules eventually to expose:

```text
<module>/public.py
```

P2-B may define a generic registration contract that future `public.py` files can implement/use.

Do not create fake `public.py` files for all future modules.

Do not put module internals into the shared registry.

Only public capability bindings should enter the registry.

---

# 28. Permissions Metadata

Manifest permissions are declarations only in P2-B.

Do not implement:

```text
authorization checks
role mappings
permission evaluator
JWT/OIDC claims
Keycloak
```

P4 owns authorization baseline.

Manifest permissions should remain typed immutable string metadata.

---

# 29. Event Metadata

Manifest event publication/consumption fields are metadata only.

Do not implement:

```text
event envelope
event bus
outbox
event dispatcher
subscriptions
Kafka/NATS/RabbitMQ
```

P3 owns events/outbox.

Do not import future event modules.

---

# 30. Feature-Flag Metadata

Manifest `feature_flags` is declaration metadata only.

Do not implement flag evaluation.

Do not make module activation depend on feature flags in P2-B.

P2-C owns:

```text
FeatureFlag interface
safe defaults
feature evaluation
```

---

# 31. Configuration Metadata

Manifest configuration declarations may list generic configuration keys/namespaces.

Do not create provider configuration behavior beyond P2-A's typed settings.

Do not dynamically read configuration to import code.

Do not activate external providers.

---

# 32. Data Ownership Metadata

Manifest may declare logical data ownership names.

No table/schema exists yet.

Do not add SQLAlchemy or database models.

Do not hardcode future table names unless already canonical.

Safe generic examples in tests:

```text
alpha_records
catalog_metadata
```

or use logical ownership labels rather than SQL table names.

---

# 33. Startup Failure Semantics

Invalid composition should fail early.

Examples:

```text
duplicate module ID
duplicate capability provider
undeclared provider binding
missing required capability
registration after seal/finalize
```

These should produce clear typed startup/composition exceptions.

Do not:

```text
log warning and continue
silently replace provider
degrade a required capability to None
```

---

# 34. Internal Error Types

Create narrow internal exception types for registry/composition failures.

Examples:

```text
ModuleRegistrationError
DuplicateModuleError
CapabilityRegistrationError
CapabilityNotFoundError
DuplicateCapabilityError
MissingRequiredCapabilityError
RegistrySealedError
```

Do not create a huge hierarchy if fewer types remain clear.

These are not automatically public API errors.

Do not add new canonical `ErrorCode` values unless the public API contract is explicitly changed.

---

# 35. Type Safety

Use Python typing rigorously.

The registry API should support patterns where:

```python
capability = registry.resolve(SOME_TYPED_KEY)
```

returns the expected contract type to mypy.

Avoid:

```python
def resolve(name: str) -> object:
```

as the only public interface.

It is acceptable to have a low-level internal map to `object` if the public typed key preserves caller typing and the implementation uses a narrow `cast`.

Keep casts localized and justified.

---

# 36. Capability Contract Test Fixture

Tests may define a synthetic protocol:

```python
class GreetingCapability(Protocol):
    def greet(self) -> str: ...
```

and a synthetic implementation.

This is preferred over using real healthcare modules.

Test typed key registration/resolution with neutral fixtures.

Do not add a production greeting capability.

---

# 37. Module Manifest Tests

Add tests for at least:

```text
manifest is immutable
module ID/version required
metadata defaults are immutable/empty
manifest records provided/required capabilities
manifest records API/event/permission/config/flag/data-ownership metadata
invalid obvious identifiers rejected if validation exists
```

Do not test invented clinical metadata.

---

# 38. Module Registry Tests

Add tests for:

```text
register one module
register multiple modules
retrieve/inspect manifest by ID if supported
duplicate module ID rejected
registration after finalization rejected
finalized registry is stable
```

---

# 39. Capability Registry Tests

Add tests for:

```text
typed registration/resolution
duplicate capability provider rejected
missing capability resolution rejected
registration after finalization rejected
provider binding belongs to declared module capability
```

---

# 40. Required Capability Graph Tests

Add tests proving:

```text
requirement satisfied by later-registered provider passes
missing required capability fails finalization
multiple modules may require the same provider
provider cannot be silently replaced
```

Do not require registration order.

---

# 41. App Composition Tests

Test application integration with synthetic modules:

```text
synthetic module router is mounted under /api/v1
synthetic module manifest is available in app composition state if designed
synthetic capability is resolvable after app creation
missing required capability causes app construction failure
duplicate module causes app construction failure
```

Do not expose registry over HTTP.

---

# 42. Existing API Version Test

Current test:

```text
test_registered_module_router_is_mounted_below_v1_prefix
```

must continue to pass or be cleanly migrated to the new module-registration mechanism.

Still verify:

```text
/api/v1/<route> -> reachable
/<route> -> 404
```

---

# 43. Dependency Policy

P2-B should add **no new application dependency**.

Expected implementation uses:

```text
Python stdlib
dataclasses
typing
collections
FastAPI already present at transport composition boundary
Pydantic only if justified for manifest serialization
```

Prefer plain frozen dataclasses/value objects for runtime module/capability structures when behavior/invariants dominate serialization.

Do not add:

```text
dependency-injector
pluggy
stevedore
importlib-metadata plugin framework
entrypoint loaders
network registry
```

If Codex believes a new package is required:

```text
STATUS: BLOCKED — DEPENDENCY REVIEW REQUIRED
```

Do not install silently.

---

# 44. No Dynamic Plugin Loading

Explicitly prohibited:

```text
importlib.import_module from config values
pkgutil scanning
filesystem plugin scanning
setuptools entry-point discovery
loading arbitrary Python paths
executing manifest-provided code
hot-loading modules after startup
```

Compile-time explicit imports are the accepted architecture.

---

# 45. No Persistence

Do not add:

```text
SQLAlchemy
Alembic
asyncpg
psycopg
database session
ORM models
migrations
module tables
registry tables
```

The module/capability registry is in-process composition metadata in P2-B.

P3 handles persistence.

---

# 46. No Feature Flags

Do not implement:

```text
FeatureFlagService
FeatureFlagProvider
is_enabled()
percentage rollout
flag database
remote flag API
```

P2-C owns this.

Manifest metadata may list flag names only.

---

# 47. No OpenTelemetry

Do not add:

```text
opentelemetry-api
opentelemetry-sdk
OTLP exporter
metrics
tracing middleware
```

P2-C owns observability expansion.

P1/P2-A JSON logging remains unchanged.

---

# 48. No Product Behavior

No:

```text
patient creation
session creation
consent checking
provider search
clinical intake
safety evaluation
mental-health logic
self-care
OCR
speech
FHIR
ABDM
model inference
```

The tests must use neutral synthetic modules/capabilities.

---

# 49. Logging / Privacy

Do not log:

```text
capability implementation repr
manifest configuration values
future secrets
patient/user data
```

Startup diagnostics may safely log/count:

```text
module_id
manifest version
capability name
```

only if necessary.

P2-B does not require new startup logging.

---

# 50. Documentation

Update only affected documentation.

Expected:

```text
README.md
backend/README.md if developer composition guidance is needed
REPOSITORY_TREE.txt
docs/implementation/38_PROGRESS_TRACKER.md
```

Do not modify:

```text
docs/implementation/36_DEPENDENCY_MAP.md
```

unless a new factual issue is discovered; P2-A already reconciled its P2/P3 labels.

Do not add an ADR unless a genuinely new architecture decision is required.

---

# 51. Progress Tracker Before Remote CI

After local implementation passes but before branch CI is observed:

```text
P2-B: PARTIAL — REMOTE CI VERIFICATION PENDING
P2: PARTIAL
```

Record:

```text
base SHA
branch
implementation SHA
local tests
AC-P2-004 local result
AC-P2-005 local result
remaining P2-C work
```

Do not prematurely mark P2 complete.

---

# 52. Progress Tracker After Remote CI

Only after all mandatory branch CI jobs are green may P2-B be recorded:

```text
P2-B: COMPLETE
P2: PARTIAL
```

Recommended next action:

```text
P2-C — Observability & Feature Flags
```

P2 remains partial because:

```text
AC-P2-006
AC-P2-007
```

are not implemented until P2-C.

---

# 53. Backend Verification

Run:

```text
cd backend
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
```

Run import/application smoke.

All must pass.

---

# 54. Full Project Regression

From root run:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

P1 and P2-A must remain green.

Do not change frontend behavior.

---

# 55. Dependency Diff

Run:

```text
git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
```

Expected:

```text
no dependency changes
```

If any dependency file changes unexpectedly, investigate before commit.

---

# 56. Security / Architecture Audit

Before commit verify:

```text
no global mutable service locator
no arbitrary dynamic imports
no plugin scanning
no network registry
no request-time registration
no persistence
no feature-flag engine
no OTel
no auth/permissions enforcement
no clinical logic
no real patient data
no secrets
```

---

# 57. Git Diff Audit

Run:

```text
git status --short
git diff --stat
git diff
git diff --check
```

Inspect every changed file.

Ensure generated caches/build outputs are not committed.

---

# 58. Commit & Push

After local verification:

```text
git add <P2-B files only>
git commit -m "feat: establish P2-B module capability registry"
git push -u origin phase/p2-b-module-capability-registry
```

Do not merge.

Do not force-push.

---

# 59. Remote CI

The existing CI triggers on:

```text
phase/**
```

Verify all mandatory jobs:

```text
Backend quality
Frontend quality
Docker and PostgreSQL
Playwright Chromium
Security scans
```

If GitHub CLI is available:

```text
gh run list --branch phase/p2-b-module-capability-registry
gh run watch <run-id> --exit-status
```

Equivalent verification is acceptable.

Do not claim CI success without evidence.

---

# 60. Closure Commit

If the implementation commit is pushed before CI completes:

1. leave tracker P2-B partial;
2. wait for green CI;
3. update tracker to P2-B complete;
4. keep P2 partial;
5. record run ID/URL;
6. create a small closure commit;
7. push same branch.

Do not merge.

---

# 61. Acceptance Evaluation

At finalization report all P2 criteria:

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

Expected after successful P2-B:

```text
AC-P2-001 PASS
AC-P2-002 PASS
AC-P2-003 PASS
AC-P2-004 PASS
AC-P2-005 PASS
AC-P2-006 NOT YET IMPLEMENTED
AC-P2-007 NOT YET IMPLEMENTED
AC-P2-008 PASS
AC-P2-009 PASS
```

Use actual evidence, not expected text, if behavior differs.

Do not mark overall P2 complete.

---

# 62. Final Report Format

Return exactly these sections.

## STATUS

One of:

```text
COMPLETE
PARTIAL
BLOCKED
FAILED
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

Describe only P2-B.

## MODULE MANIFEST

Report:

```text
manifest type/location
module identifier representation
manifest version representation
metadata fields
immutability behavior
validation behavior
```

## MODULE REGISTRATION

Report:

```text
registration type/location
duplicate-module behavior
finalization/sealing behavior
router composition behavior
app-state/composition exposure if any
```

## CAPABILITY MODEL

Report:

```text
capability identifier type
typed capability key strategy
provider binding strategy
resolution API
duplicate-provider behavior
missing-capability behavior
```

## DEPENDENCY GRAPH VALIDATION

Report:

```text
required-capability validation
registration-order independence
undeclared provider detection
missing required provider behavior
```

## FILES CHANGED

Group:

```text
shared kernel
FastAPI composition
tests
documentation
```

## DEPENDENCIES

Expected:

```text
No new runtime or dev dependency.
```

If changed, list exact package/version/classification/license/reason.

## TESTS

Report:

```text
new tests
total backend test count
synthetic module/capability fixtures
```

## VERIFICATION

Report exact results for:

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
dependency-file diff
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

Report all:

```text
AC-P2-001 ... AC-P2-009
```

using:

```text
PASS
FAIL
BLOCKED
NOT APPLICABLE
NOT YET IMPLEMENTED
```

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
Compile-time explicit registration only: YES/NO
No runtime plugin discovery/loading: YES/NO
No global mutable service locator: YES/NO
Registry sealed/finalized before runtime use: YES/NO
No persistence introduced: YES/NO
No SQLAlchemy/Alembic added: YES/NO
No feature-flag evaluation pulled forward: YES/NO
No OpenTelemetry pulled forward: YES/NO
No event/outbox implementation pulled forward: YES/NO
No auth/permission enforcement pulled forward: YES/NO
No clinical/business feature implemented: YES/NO
No AI/ML/QML added: YES/NO
No new dependency added: YES/NO
P2-A contracts preserved: YES/NO
```

## DEVIATIONS

List all deviations and reasons.

## BLOCKERS / OPEN DECISIONS

Only genuine unresolved items.

## PROGRESS TRACKER

State:

```text
P2-B status
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

If P2-B is complete:

```text
P2-C — Observability & Feature Flags
```

Do not implement it.

---

# 63. Success Definition

P2-B is complete only when:

- a typed immutable module manifest exists;
- it can express FR-EXT-004 registration metadata;
- modules register explicitly at application composition;
- duplicate module IDs fail deterministically;
- a typed capability key/identifier model exists;
- capability providers register explicitly;
- duplicate providers fail deterministically;
- missing capability resolution fails deterministically;
- required capability validation is independent of registration order;
- active provider bindings agree with their declaring module manifests;
- the registry cannot be mutated after composition finalization;
- no dynamic plugin discovery/loading exists;
- no global mutable service locator exists;
- synthetic module routers compose under `/api/v1`;
- existing P1/P2-A behavior remains compatible;
- no dependency is added unless explicitly approved;
- no P2-C/P3/product/clinical work is pulled forward;
- backend and frontend quality gates pass;
- all mandatory GitHub Actions jobs pass;
- P2-B is recorded COMPLETE while P2 remains PARTIAL;
- the feature branch is pushed but not merged.

Stop after P2-B.
