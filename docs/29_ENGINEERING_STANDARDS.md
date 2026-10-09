# SwasthyaSetu AI
## 29 — Engineering Standards

**Document ID:** `SSAI-ENG-029`  
**Filename:** `29_ENGINEERING_STANDARDS.md`  
**Status:** Foundation / Engineering Source of Truth  
**Version:** `1.0.0-draft`  
**Depends on:**
- `00_PROJECT_MASTER_SPEC.md`
- `01_PRODUCT_REQUIREMENTS.md`
- `02_SYSTEM_ARCHITECTURE.md`

**Primary implementation agent:** Codex  
**Primary purpose:** Define how SwasthyaSetu AI code must be written, reviewed, tested, evolved, and verified.

---

# 1. Purpose

This document defines the coding and engineering rules for SwasthyaSetu AI.

It exists so that:

- Codex produces consistent code across phases;
- architectural boundaries remain intact;
- safety-critical logic stays testable;
- frontend and backend contracts do not drift;
- database changes remain controlled;
- external providers remain replaceable;
- new features can be added without introducing architectural debt;
- quality gates are objective rather than subjective.

These standards apply to all future project phases unless explicitly overridden by a higher-priority approved architecture/safety decision.

---

# 2. Engineering Principles

The implementation SHALL follow these principles.

## ENG-P-001 — Correctness before cleverness

Prefer clear, explicit, testable code over compact or overly abstract code.

## ENG-P-002 — Safety before convenience

Safety-critical behavior must remain deterministic, observable, versioned, and testable.

## ENG-P-003 — Strong typing

Public/internal contracts should use explicit types.

## ENG-P-004 — Small modules

Files, classes, and services should have narrow responsibility.

## ENG-P-005 — Stable boundaries

Cross-module dependencies must use documented public interfaces.

## ENG-P-006 — No hidden side effects

Important side effects must be explicit in application services, jobs, events, or adapters.

## ENG-P-007 — Test with implementation

Tests are part of the feature, not a later cleanup step.

## ENG-P-008 — Replaceable integrations

External technologies remain behind ports/adapters.

## ENG-P-009 — Fail visibly

A subsystem must not silently pretend success after a dependency failure.

## ENG-P-010 — Documentation follows behavior

Public behavior changes require documentation updates.

---

# 3. Technology Baseline

The baseline stack is:

## Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- async-capable HTTP client
- structured logging
- OpenTelemetry

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- strict TypeScript configuration
- typed API access

## AI / ML

- project-owned provider-agnostic `LLMProvider`
- direct LLM provider adapters first; network AI gateway is optional/conditional
- scikit-learn as the primary classical baseline toolkit
- XGBoost/PyTorch only when the task justifies them
- MLflow only in the research/lifecycle profile
- SHAP/Optuna in research/evaluation workflows as needed
- ONNX Runtime for approved portable inference only after parity testing
- PennyLane as primary QML research framework
- Qiskit Machine Learning as secondary QML comparison framework
- pgvector/Sentence-Transformers-style embedding adapters only after an approved RAG use case

Research/model-training dependencies SHALL NOT automatically become patient API runtime dependencies.

## Infrastructure

- Docker
- Docker Compose for local development
- PostgreSQL transactional outbox for reliable internal events
- project-owned `JobDispatcher`; evaluate PostgreSQL-native durable jobs before adding cache/broker infrastructure
- OpenTelemetry as observability contract
- GitHub Actions or equivalent CI
- Trivy and Gitleaks in CI
- Terraform/OpenTofu only when infrastructure code is introduced
- Keycloak, SeaweedFS, Valkey, OpenBao, HAPI FHIR, MLflow, Prometheus/Grafana and similar services activate only in their approved phase/profile

The exact package versions will be pinned in project configuration.

---

# 4. Repository Engineering Philosophy

The repository SHALL prefer:

```text
one monorepo
+
strong module boundaries
+
shared tooling
+
one source of truth for contracts
```

Do not split into separate repositories early unless an approved ADR requires it.

---

# 5. Python Version

Production backend code SHALL target:

```text
Python >= 3.12
```

The project should pin a specific supported minor version in:

- development tooling;
- Docker;
- CI.

Codex must not introduce code requiring a different Python version without an approved change.

---

# 6. Python Package Management

The final package manager will be defined during repository foundation.

Whichever tool is selected SHALL support:

- lockfile;
- reproducible install;
- development dependencies;
- script commands.

Do not maintain multiple conflicting Python dependency managers.

---

# 7. Python Typing Rules

## ENG-PY-001

All public functions and methods SHALL have explicit parameter and return types.

## ENG-PY-002

Domain/application interfaces SHALL be fully typed.

## ENG-PY-003

Use `Any` only when unavoidable and document the reason.

## ENG-PY-004

Prefer:

```python
str | None
```

over legacy:

```python
Optional[str]
```

when project style allows.

## ENG-PY-005

Prefer typed domain objects over dictionaries.

Avoid:

```python
def process(data: dict) -> dict:
    ...
```

Prefer:

```python
def process(data: IntakeRequest) -> IntakeResult:
    ...
```

## ENG-PY-006

Use `Protocol` where structural interfaces improve replaceability.

## ENG-PY-007

Do not suppress type errors globally to avoid fixing design problems.

---

# 8. Pydantic Standards

Pydantic models should be used for:

- API request/response contracts;
- adapter contracts;
- event payloads;
- external structured AI outputs;
- validated configuration;
- serialized application DTOs.

Avoid using Pydantic models as a universal replacement for domain entities when behavior/invariants belong in the domain layer.

---

# 9. Pydantic Validation

Validation SHOULD be:

- local;
- explicit;
- deterministic;
- minimal.

Do not embed network calls or database access inside model validators.

Example:

```python
class ReferralCreateRequest(BaseModel):
    provider_id: UUID
    consent_id: UUID
    priority: ReferralPriority
```

Business checks such as:

```text
is consent still valid?
is provider active?
```

belong in application/domain services.

---

# 10. Python Dataclasses and Domain Models

Use plain dataclasses/value objects when:

- serialization is not the primary concern;
- domain invariants are central;
- framework independence matters.

Pydantic is acceptable for immutable domain value objects if consistently used.

Avoid making every domain class an ORM entity.

---

# 11. Function Size

There is no rigid line limit.

However, if a function:

- performs multiple unrelated actions;
- mixes validation, persistence, vendor calls, and formatting;
- requires many nested branches;
- is hard to unit test;

it should be decomposed.

A function should usually represent one coherent operation.

---

# 12. Class Design

Prefer composition over inheritance.

Use inheritance only where:

- polymorphism is real;
- behavior is substitutable;
- interfaces benefit.

Avoid deep class hierarchies.

---

# 13. Async Standards

Use `async` for I/O-bound application operations when the chosen libraries support it.

Typical async operations:

- database calls;
- HTTP calls;
- object storage;
- LLM calls;
- OCR service calls;
- FHIR/ABDM integration.

Do not make CPU-heavy ML/OCR computation run directly on the event loop.

CPU-heavy work should move to:

- worker thread;
- process;
- background worker;
- external model service.

---

# 14. Blocking Code Rule

Codex MUST NOT introduce blocking I/O in async request paths without justification.

Examples to avoid:

```python
requests.get(...)
time.sleep(...)
```

inside async FastAPI flow.

Use async equivalents or isolate blocking work.

---

# 15. FastAPI Route Standards

Route handlers SHALL be thin.

A route handler should primarily:

1. parse/validate request;
2. obtain actor/context;
3. call application use case;
4. map result;
5. return response.

Do not put clinical rules in route handlers.

Bad:

```python
@router.post("/triage")
async def triage(req):
    if req.chest_pain and req.shortness_of_breath:
        ...
```

Good:

```python
decision = await triage_service.evaluate(command)
```

---

# 16. FastAPI Dependency Injection

FastAPI dependencies MAY provide:

- DB session;
- authenticated actor;
- settings;
- application service;
- request correlation ID.

Avoid large dependency trees that hide important behavior.

---

# 17. API Router Structure

Each module owns its API routes.

Example:

```text
modules/
  providers/
    api/
      routes.py
      schemas.py
```

A central API router may register module routers.

Do not maintain one giant `routes.py` for the entire application.

---

# 18. API Versioning

Public APIs use:

```text
/api/v1
```

Breaking public contract changes require explicit migration/version strategy.

Codex must not silently alter a request/response shape consumed by another application.

---

# 19. API Naming

Use nouns/resources consistently.

Good:

```text
GET /providers
GET /providers/{provider_id}
POST /referrals
```

Avoid unclear action names unless the action is inherently command-like.

Acceptable:

```text
POST /encounters/{id}/complete
POST /consents/{id}/revoke
```

---

# 20. HTTP Semantics

Use HTTP status codes intentionally.

Typical mapping:

```text
200 OK
201 Created
202 Accepted
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
429 Too Many Requests
503 Dependency Unavailable
```

Do not always return `200` with `"success": false`.

---

# 21. API Error Standard

All errors use a stable envelope.

Example:

```json
{
  "error": {
    "code": "CONSENT_REQUIRED",
    "message": "Consent is required for this operation.",
    "request_id": "..."
  }
}
```

Internal stack traces MUST NOT be returned to clients.

---

# 22. Error Codes

Error codes:

- are stable;
- uppercase snake case;
- machine-readable;
- documented where public.

Examples:

```text
FEATURE_DISABLED
CONSENT_REQUIRED
PROVIDER_STALE
DOCUMENT_PROCESSING_FAILED
DEPENDENCY_TIMEOUT
INVALID_STATE_TRANSITION
```

---

# 23. Domain Exceptions

Domain errors should be domain-specific.

Example:

```python
class InvalidReferralTransition(DomainError):
    ...
```

Do not raise generic `Exception` for expected domain states.

---

# 24. Exception Handling

Do not catch exceptions broadly unless:

- adding context;
- converting to a typed boundary error;
- implementing rollback/fallback;
- logging at a system boundary.

Avoid:

```python
try:
    ...
except Exception:
    pass
```

especially in healthcare/safety workflows.

---

# 25. Logging Standards

Use structured logging.

Log fields should include when relevant:

```text
request_id
correlation_id
module
operation
status
duration_ms
error_code
provider
model_version
policy_version
```

Never log unnecessary:

- patient conversation;
- raw document text;
- secrets;
- bearer tokens;
- passwords;
- full external AI prompts;
- full FHIR records.

---

# 26. Sensitive Logging Rule

Before adding a log statement, ask:

> Would this expose health or identity data if production logs were accessed?

If yes, log metadata instead.

Bad:

```python
logger.info("Patient said %s", transcript)
```

Good:

```python
logger.info(
    "intake extraction complete",
    extra={
        "encounter_id": encounter_id,
        "schema_version": schema_version,
        "status": "valid",
    },
)
```

Exact identifier logging policy may later be restricted further by privacy standards.

---

# 27. Correlation IDs

Every incoming request SHALL receive/propagate a request or correlation ID.

Background jobs and events SHOULD preserve correlation IDs.

---

# 28. SQLAlchemy Standards

Use SQLAlchemy 2.x declarative style.

ORM models belong inside owning modules/infrastructure.

Do not expose ORM models directly as API responses.

Do not use ORM entities as universal domain DTOs.

---

# 29. Database Session Standards

Transaction boundaries should be explicit.

Application services SHOULD own transaction semantics for use cases.

Avoid committing deep inside repository helper methods.

Preferred:

```text
application use case
   |
repository calls
   |
commit once
```

---

# 30. Repository Pattern

Repositories should expose domain-relevant operations.

Avoid generic "CRUD repositories" when domain-specific methods are clearer.

Good:

```python
get_active_provider(...)
save_referral(...)
list_pending_referrals(...)
```

Avoid an enormous universal repository abstraction.

---

# 31. Cross-Module Data Access

A repository may access only the tables it owns unless an architecture-approved shared read model exists.

Prohibited:

```text
documents repository directly updates patients.medications table
```

Use module application/public service or domain event.

---

# 32. Database Queries

Avoid N+1 query patterns.

Use:

- explicit eager loading;
- joined/selectin loading;
- purpose-built query DTOs.

Measure before over-optimizing.

---

# 33. Raw SQL

Raw SQL is allowed when:

- ORM is insufficient;
- performance matters;
- complex reporting requires it.

Raw SQL must be:

- parameterized;
- tested;
- documented;
- isolated.

Never build SQL using untrusted string concatenation.

---

# 34. Alembic Migration Rules

Every persistent schema change requires a migration.

Migration files SHALL:

- have clear names/messages;
- avoid unrelated changes;
- document destructive changes;
- handle indexes/constraints;
- be testable in CI.

Codex must not modify DB models without checking whether a migration is required.

---

# 35. Migration Safety

Production-sensitive migration patterns:

Prefer:

```text
add
backfill
switch
remove later
```

over:

```text
rename/drop immediately
```

for breaking schema evolution.

---

# 36. Migration Rollback

If downgrade is unsafe or impossible, the migration must state why.

Do not write fake downgrade logic that risks data corruption.

---

# 37. Database Constraints

Important invariants should be enforced in DB when possible.

Examples:

- uniqueness;
- non-null;
- referential integrity;
- enum/check constraints;
- idempotency keys.

Application validation alone is insufficient for critical invariants.

---

# 38. IDs

Use opaque identifiers such as UUIDs.

Do not expose sequential internal IDs unnecessarily.

External IDs require explicit namespace/source.

---

# 39. Timestamp Standards

Use timezone-aware UTC timestamps in persistent systems.

Avoid naive datetime values.

Use:

```python
datetime.now(timezone.utc)
```

or equivalent project utility.

---

# 40. Enum Standards

Use explicit enums for finite states.

Examples:

```text
ReferralStatus
DocumentStatus
EncounterStatus
VerificationState
```

Do not scatter raw string literals across the codebase.

---

# 41. State Machine Standards

Workflow state transitions SHALL be explicit.

A state transition function/service should:

- validate current state;
- validate requested transition;
- emit domain event when appropriate;
- preserve audit metadata.

Never set states arbitrarily from random callers.

---

# 42. Pydantic / ORM Separation

Use separate models for:

```text
API DTO
Domain
Persistence
```

when behavior/representation differs materially.

For simple entities, duplication can be minimized, but do not force one model to serve every concern.

---

# 43. Frontend TypeScript Standards

TypeScript SHALL use:

```json
{
  "strict": true
}
```

Do not disable strictness globally.

---

# 44. TypeScript `any`

Avoid `any`.

Use:

```text
unknown
```

plus narrowing when input is uncertain.

If `any` is necessary, comment why.

---

# 45. Frontend Components

Components should be:

- small;
- composable;
- accessible;
- typed.

Avoid monolithic page components containing:

- fetch logic;
- validation;
- formatting;
- business policy;
- all UI state.

---

# 46. Frontend Feature Structure

Feature-specific code lives under feature boundaries.

Example:

```text
features/
  referrals/
    api/
    components/
    hooks/
    schemas/
    pages/
```

Shared UI belongs in a shared design-system area.

---

# 47. Frontend Server vs Client Components

Use server components where they improve simplicity/security.

Use client components when needed for:

- interaction;
- browser APIs;
- local state;
- live form behavior.

Do not mark entire page trees `"use client"` without reason.

---

# 48. Frontend Forms

Forms SHALL use:

- typed schemas;
- accessible labels;
- inline validation;
- server-side validation as authority.

Client validation improves UX but does not replace backend validation.

---

# 49. Frontend Error States

Every asynchronous screen should handle:

```text
loading
success
empty
error
permission denied
feature disabled
```

Safety-sensitive screens may have additional degraded states.

---

# 50. Frontend Accessibility

Every interactive control requires:

- keyboard usability;
- visible focus;
- accessible label;
- sufficient contrast;
- semantic HTML.

Do not use clickable `<div>` elements when a button/link is appropriate.

---

# 51. Tailwind Standards

Use Tailwind consistently.

Avoid:

- large repeated class strings;
- hard-coded arbitrary values everywhere;
- inconsistent spacing/color semantics.

Reusable visual patterns belong in components or design tokens.

---

# 52. Design Tokens

Shared design should define:

- spacing;
- typography;
- radii;
- states;
- status severity;
- focus behavior.

Do not encode clinical severity solely by color.

Use:

- label;
- icon;
- text;
- color.

---

# 53. API Client Standards

Frontend API access should use centralized typed clients.

Do not scatter raw `fetch()` calls across components.

Benefits:

- auth;
- headers;
- errors;
- request IDs;
- schema consistency.

---

# 54. OpenAPI

FastAPI-generated OpenAPI should be treated as a contract artifact.

Where feasible, generate TypeScript client/types from OpenAPI.

Avoid manually duplicating complex request types in frontend.

---

# 55. External Adapter Standards

Every adapter SHALL:

- implement a documented port;
- expose typed inputs/outputs;
- map provider-specific errors;
- define timeout;
- define retry policy;
- expose health/telemetry;
- avoid leaking provider objects into domain layer.

---

# 56. Adapter Error Mapping

Example external error:

```text
OpenAI timeout
```

becomes:

```text
LLMDependencyTimeout
```

Domain/application code should not need to know vendor exception classes.

---

# 57. Adapter Timeouts

All network adapters SHALL configure explicit timeouts.

No infinite waits.

Timeout values should be centrally configurable.

---

# 58. Adapter Retries

Retry only errors likely to be transient.

Do not retry:

- authentication failure;
- invalid request;
- schema validation error;
- permission denial.

Use bounded retries.

---

# 59. Circuit Breakers

Circuit breakers MAY be used for unstable providers.

Do not introduce circuit-breaker libraries unless operational value justifies them.

---

# 60. Idempotency Standards

Side-effecting external actions SHOULD have idempotency protection where retry is possible.

Examples:

- referral creation;
- notification delivery;
- external sync.

---

# 61. LLM Prompt Engineering Standards

Prompts are versioned assets.

Each prompt package SHOULD define:

```text
prompt_id
prompt_version
input_schema
output_schema
model assumptions
fallback behavior
test fixtures
```

Do not embed major prompts as anonymous strings inside route handlers.

---

# 62. LLM Structured Output

Clinical/safety extraction MUST use validated structured output.

Example workflow:

```text
LLM response
   |
parse
   |
Pydantic validation
   |
business logic
```

Malformed output never reaches safety logic as if valid.

---

# 63. LLM Retries

A malformed structured output may receive a bounded repair/retry attempt when safe.

If validation still fails:

- return typed failure;
- invoke degraded behavior;
- do not invent missing fields.

---

# 64. LLM Temperature

Safety-sensitive extraction SHOULD use deterministic/low-variance settings.

Exact settings are task/model-specific and belong with prompt configuration.

---

# 65. LLM Context Minimization

Send only context necessary for the task.

Do not send an entire lifetime patient record to a model when a small structured subset is sufficient.

---

# 66. LLM Chain-of-Thought

The application MUST NOT request or persist hidden chain-of-thought reasoning.

Use:

- structured reason codes;
- extracted fields;
- explicit supporting evidence.

---

# 67. RAG Standards

RAG corpus ingestion SHALL preserve:

- source;
- version;
- chunk/document identity;
- authorization scope.

Retrieved content should be treated as evidence/context, not automatically trusted clinical truth.

---

# 68. Embedding Standards

Embedding model/version should be recorded when index compatibility matters.

Changing embedding model may require reindexing.

---

# 69. OCR Engineering Standards

OCR pipeline stages should be separable:

```text
preprocess
ocr
layout
classification
entity extraction
validation
```

Do not combine them into one opaque function.

---

# 70. OCR Confidence

Low-confidence OCR output must remain distinguishable from trusted information.

Thresholds belong in configuration/policy, not random call-site constants.

---

# 71. Document Parser Registry

Document types should register processors.

Example:

```python
parser_registry.register(DocumentType.LAB_REPORT, LabReportProcessor(...))
```

Avoid central `if/elif` growth.

---

# 72. ML Code Standards

ML training code SHALL separate:

- data loading;
- preprocessing;
- feature engineering;
- training;
- evaluation;
- artifact saving.

No giant notebook-only production workflow.

---

# 73. Notebooks

Notebooks MAY be used for exploration.

Production/reproducible training logic should move into Python modules/scripts.

Notebooks should not be the only source of model logic.

---

# 74. Reproducibility

ML experiments should record:

- code commit;
- dataset version;
- seed;
- parameters;
- environment;
- metrics;
- artifacts.

---

# 75. Data Leakage Prevention

Train/test leakage checks are mandatory for predictive tasks.

Codex should explicitly reason about:

- duplicate subjects;
- temporal leakage;
- preprocessing fit scope;
- target leakage.

---

# 76. ML Evaluation

No single metric should be treated as universal.

Depending on task, use:

- sensitivity;
- specificity;
- precision;
- recall;
- F1;
- AUROC;
- AUPRC;
- calibration;
- confusion matrix;
- subgroup evaluation.

---

# 77. QML Standards

QML code SHALL separate:

- classical preprocessing;
- encoding;
- circuit definition;
- training;
- backend;
- evaluation.

Framework/backend-specific code belongs in adapters or research implementation modules.

---

# 78. QML Benchmark Fairness

Classical vs QML comparison must share:

- target;
- split;
- preprocessing assumptions;
- evaluation metrics.

Do not optimize one side unfairly.

---

# 79. Model Promotion

Training a model does not activate it in patient workflows.

Promotion requires:

- registered artifact;
- evaluation;
- approval status;
- configured feature/use case.

---

# 80. Model Artifact Integrity

Model artifacts should have:

- checksum;
- version;
- metadata.

Do not load arbitrary untrusted serialized model files in production.

---

# 81. Security Coding Standards

All code must consider:

- injection;
- XSS;
- CSRF;
- SSRF;
- path traversal;
- unsafe deserialization;
- authz;
- secret leakage;
- upload risks.

---

# 82. Authorization Rule

Authorization is enforced on backend application/use-case boundaries.

Frontend hiding is not authorization.

---

# 83. Object-Level Authorization

Any endpoint operating on a resource by ID must check that the actor is authorized for that resource.

Avoid IDOR vulnerabilities.

---

# 84. Secrets

Never commit:

- API keys;
- DB passwords;
- JWT signing secrets;
- cloud credentials;
- private keys.

Use environment variables/local `.env` for development and secret management in deployed environments.

---

# 85. Environment Files

`.env.example` may contain:

```text
VARIABLE_NAME=
```

Never real secrets.

---

# 86. File Upload Security

Validate:

- size;
- MIME;
- extension consistency;
- content signature where appropriate;
- filename sanitization;
- storage path;
- processing isolation.

Do not trust user-provided filename.

---

# 87. Path Handling

Use generated object keys.

Never construct filesystem paths directly from untrusted filename input.

---

# 88. HTML/Markdown Rendering

User/generated content must be escaped/sanitized.

If Markdown rendering is supported, use a safe allowlist.

---

# 89. SQL Injection

Use SQLAlchemy parameterization.

Never concatenate raw user input into SQL.

---

# 90. Prompt Injection

Treat user/document content as untrusted data.

Do not allow uploaded document text to override system/policy instructions.

Safety decisions remain deterministic.

---

# 91. Dependency Policy

Every added dependency should answer:

1. what does it solve?
2. do we already have a dependency for this?
3. license?
4. maintenance?
5. security?
6. size/complexity?
7. replaceability?

Avoid dependency bloat.

---

# 92. Dependency Pinning

Production dependencies should be pinned/locked.

CI should install from lockfiles.

---

# 93. Dependency Updates

Do not perform broad unrelated dependency upgrades inside feature work unless necessary.

Separate major dependency upgrades into dedicated changes when possible.

---

# 94. License Awareness

Before incorporating code, datasets, models, or libraries, verify license compatibility.

Record license information for major third-party assets.

Do not assume "on GitHub" means unrestricted use.

---

# 95. Dataset Governance

Dataset metadata SHOULD include:

- name;
- source;
- license;
- version;
- intended use;
- sensitive data classification;
- preprocessing lineage.

---

# 96. Test Pyramid

The project test strategy includes:

```text
unit
module integration
contract
adapter
database
frontend component
E2E
clinical safety
LLM regression
OCR fixture
multilingual
security
performance
ML/QML evaluation
```

Not every file needs every test category.

---

# 97. Unit Tests

Unit tests should:

- be fast;
- isolate domain logic;
- avoid network;
- avoid real external providers.

Use mocks/fakes only at boundaries.

---

# 98. Integration Tests

Integration tests SHOULD use real:

- PostgreSQL;
- repository layer;
- application service;

where practical.

Avoid mocking the database for database-specific behavior.

---

# 99. Contract Tests

Contract tests SHALL verify:

- API schema;
- event schema;
- adapter interface behavior.

---

# 100. E2E Tests

E2E tests cover critical journeys.

Examples:

- patient intake -> summary;
- document upload -> extraction status;
- safety red flag -> urgent route;
- mental-health crisis fallback;
- referral consent -> status;
- clinician confirmation.

---

# 101. Safety Tests

Safety tests are first-class.

Changes affecting:

- safety policy;
- crisis handling;
- self-care gating;
- mental-health routing;

must run dedicated golden/adversarial tests.

---

# 102. Regression Test Rule

Every confirmed safety defect should receive a regression test before the fix is considered complete.

---

# 103. Test Naming

Test names should describe behavior.

Good:

```python
def test_referral_cannot_be_sent_without_consent():
```

Bad:

```python
def test_case_4():
```

---

# 104. Test Data

Use synthetic/fake test data.

Do not place real patient health data into the source repository.

---

# 105. Test Determinism

Tests should be deterministic.

Control:

- random seeds;
- current time;
- external responses.

Avoid flaky timing-dependent assertions.

---

# 106. Time in Tests

Abstract current time when business logic depends on it.

Avoid hard-coding `datetime.now()` deep in domain rules if it makes testing difficult.

---

# 107. External Providers in Tests

Tests should use:

```text
MockLLM
MockOCR
MockFHIR
MockABDM
MockNotification
```

Real provider tests belong in optional sandbox/integration suites.

---

# 108. LLM Evaluation Tests

LLM tests should verify structured outcomes, not exact wording unless wording is clinically/governance controlled.

Examples:

```text
schema valid
required field extracted
negation handled
unsafe route not delegated
prompt injection ignored
```

---

# 109. Snapshot Tests

Use snapshots sparingly.

Do not use snapshots to avoid thinking about correct behavior.

Large generated snapshots are difficult to review.

---

# 110. Code Coverage

Coverage is a signal, not the goal.

Higher coverage is expected for:

- safety policy;
- state transitions;
- authorization;
- critical parsing;
- consent.

Do not chase arbitrary global coverage by testing trivial lines.

---

# 111. Formatting and Linting

Backend should use automated formatting/linting.

Recommended baseline:

- Ruff for linting/formatting;
- mypy or pyright for type checking.

Final selection occurs in repository foundation.

Frontend should use:

- ESLint;
- Prettier or compatible formatting;
- TypeScript compiler.

Codex must run configured tools before declaring completion.

---

# 112. Ruff Standards

If Ruff is selected:

- project configuration lives centrally;
- avoid per-file ignores unless justified;
- do not disable large rule sets to make CI green.

---

# 113. Type Checking

Backend type checking SHALL include all application/domain modules.

Frontend SHALL run:

```text
tsc --noEmit
```

or equivalent build-time type check.

---

# 114. Pre-Commit Hooks

Pre-commit hooks MAY run fast checks.

CI remains authoritative.

Do not rely solely on local hooks.

---

# 115. CI Required Checks

Baseline required checks:

```text
backend format/lint
backend typecheck
backend unit tests
backend integration tests
frontend lint
frontend typecheck
frontend tests
migration validation
contract tests
dependency/security checks
```

Phase-specific checks may add:

```text
safety tests
FHIR validation
OCR fixtures
ML evaluation
QML tests
```

---

# 116. No Skipped Failing Tests

Codex must not solve a failing test by:

- deleting it;
- marking it skipped;
- weakening assertion;

unless the specification genuinely changed and the reason is documented.

---

# 117. No Test-Only Production Hacks

Do not add behavior such as:

```python
if settings.environment == "test":
    bypass_safety()
```

Tests should use dependency injection, mocks, or fixtures.

---

# 118. Feature Flag Tests

A flagged feature should test:

- disabled;
- enabled;
- misconfigured.

Risky features should default safely when configuration is absent.

---

# 119. Documentation Standards

Documentation must stay close to implementation.

Required updates may include:

- API contract;
- domain model;
- DB schema;
- architecture;
- implementation plan;
- module README;
- runbook.

---

# 120. Code Comments

Comments should explain **why**, not restate **what**.

Bad:

```python
# increment i
i += 1
```

Good:

```python
# Keep policy ordering stable so reason-code precedence is reproducible.
```

---

# 121. Docstrings

Public domain/application interfaces SHOULD have docstrings when behavior is not obvious.

Do not write enormous redundant docstrings for trivial accessors.

---

# 122. TODOs

TODO comments require:

- issue/reference if possible;
- clear scope;
- reason.

Avoid indefinite:

```text
TODO fix later
```

---

# 123. Dead Code

Do not leave large commented-out code blocks.

Use version control.

---

# 124. Feature Completeness

Do not create fake/stub "implemented" features returning hard-coded success unless the phase explicitly calls for scaffolding.

If a component is intentionally a stub:

- label it;
- feature-flag it;
- document status;
- ensure UI does not misrepresent capability.

---

# 125. Mock Data in Production UI

Demo/mock provider records or patient data must be clearly separated from production configuration.

Do not silently fall back to fake doctors if provider API fails.

---

# 126. Git Branching

The exact branching model may evolve.

Minimum:

- meaningful branch names;
- small cohesive changes;
- do not mix unrelated features.

Suggested:

```text
feat/phase-05-intake
fix/referral-idempotency
chore/dependency-update
```

---

# 127. Commit Standards

Commits should communicate purpose.

Suggested style:

```text
feat(intake): add structured HPI schema
fix(safety): preserve crisis fallback on extractor timeout
test(referrals): add consent-required regression case
```

Do not require perfect conventional commits if it slows development, but history should remain understandable.

---

# 128. Pull Request Standards

Every meaningful implementation change SHOULD summarize:

- what changed;
- why;
- requirement IDs;
- architecture impact;
- database migrations;
- tests run;
- safety/privacy impact;
- known limitations.

Codex-generated PR descriptions should be factual.

---

# 129. Code Review Checklist

Review:

```text
[ ] requirement implemented
[ ] module boundary respected
[ ] types clear
[ ] no duplicated domain model
[ ] no direct cross-module table writes
[ ] external SDK behind adapter
[ ] errors handled
[ ] security reviewed
[ ] privacy considered
[ ] tests added
[ ] migrations present
[ ] logs safe
[ ] documentation updated
```

---

# 130. Safety Review Checklist

For safety-impacting work:

```text
[ ] deterministic rule
[ ] reason code
[ ] policy version
[ ] hard override precedence
[ ] clarification behavior
[ ] degraded mode
[ ] regression cases
[ ] human/clinical approval required?
```

---

# 131. Privacy Review Checklist

For data-impacting work:

```text
[ ] minimum data
[ ] purpose
[ ] consent
[ ] retention
[ ] logs
[ ] external processors
[ ] deletion
[ ] audit
```

---

# 132. Performance Review Checklist

For latency-sensitive work:

```text
[ ] DB query count
[ ] blocking calls
[ ] payload size
[ ] cache justification
[ ] async work
[ ] timeout
[ ] metrics
```

---

# 133. Naming — Python

Use:

```text
snake_case       functions/variables/modules
PascalCase       classes/types
UPPER_SNAKE      constants
```

Avoid abbreviations unless widely understood.

Prefer:

```text
clinical_summary
```

over:

```text
clin_sum
```

---

# 134. Naming — TypeScript

Use:

```text
camelCase        variables/functions
PascalCase       components/types
UPPER_SNAKE      true constants if appropriate
```

React components use PascalCase.

---

# 135. Naming — Database

Prefer consistent snake_case.

Table names should be plural or singular consistently once defined.

The database schema specification will freeze convention.

---

# 136. Naming — Events

Use past tense:

```text
DocumentUploaded
ReferralCreated
ConsentRevoked
```

Events describe something that already happened.

---

# 137. Naming — Commands

Use imperative verb:

```text
CreateReferral
ConfirmClinicalFact
CompleteEncounter
```

---

# 138. Naming — Queries

Use descriptive query names:

```text
GetPatientTimeline
SearchProviders
GetEncounterSummary
```

---

# 139. Magic Values

Avoid unexplained hard-coded thresholds.

Bad:

```python
if score > 7:
```

Good:

```python
if score >= policy.priority_threshold:
```

Clinical thresholds must be versioned policy values.

---

# 140. Configuration Standards

Configuration should use typed settings.

Group configuration by concern:

```text
database
redis
object_storage
llm
ocr
speech
fhir
abdm
observability
security
```

---

# 141. Environment-Specific Configuration

Do not branch behavior across code using:

```python
if ENV == "production":
```

everywhere.

Use configuration/adapters.

Environment checks should remain centralized.

---

# 142. Feature Configuration

Feature flags and runtime configuration should be separate from secrets.

Example:

```text
VOICE_INTAKE_ENABLED=true
```

versus:

```text
LLM_API_KEY=...
```

---

# 143. Default Configuration Safety

Defaults should be safe.

Examples:

- experimental features off;
- debug off in production;
- external referral disabled without config;
- self-care disabled without approved pack;
- model not active without approval.

---

# 144. Background Job Standards

Jobs should:

- be idempotent when possible;
- record status;
- record failure reason code;
- use correlation IDs;
- use bounded retries;
- avoid hiding permanent failures.

---

# 145. Job Retry Policy

Retry based on error class.

Example:

```text
network timeout       retry
HTTP 429              retry/backoff
invalid schema        do not retry endlessly
permission denied     do not retry
```

---

# 146. Dead-Letter Handling

Repeatedly failing external jobs should enter a visible failed/dead-letter state.

Do not drop silently.

---

# 147. Event Handler Standards

Handlers should:

- accept versioned event;
- be idempotent;
- minimize side effects;
- log metadata;
- avoid calling unrelated modules recursively without control.

---

# 148. Outbox Standards

Outbox records should include:

- event ID;
- event type;
- version;
- payload;
- timestamp;
- delivery status;
- retry metadata.

---

# 149. Event Payload Privacy

Domain events should carry the minimum required data.

Prefer references:

```json
{
  "patient_id": "...",
  "document_id": "..."
}
```

over copying full sensitive document text.

---

# 150. Caching Rules

Cache may improve performance but must not alter correctness.

Do not cache safety decisions across contexts unless explicitly designed.

Cache invalidation must be defined.

---

# 151. Redis Rules

Redis is optional and ephemeral.

Do not store authoritative:

- consent;
- clinical truth;
- referrals;
- safety decisions;

only in Redis.

---

# 152. Object Storage Standards

Object keys should be opaque.

Metadata belongs in DB.

Do not derive public URL from untrusted filenames.

Prefer short-lived signed access URLs.

---

# 153. Document Retention

Workers must not create orphaned derived files indefinitely.

Derived artifacts should be linked to document lifecycle.

---

# 154. Data Serialization

Use stable, explicit schemas.

Avoid Python pickle for untrusted or long-term exchange.

Use:

- JSON;
- Parquet;
- standardized model formats;
- safe framework-specific artifact formats;

as appropriate.

---

# 155. Health Checks

Expose separate health concepts.

Example:

```text
/live
/ready
```

Liveness:

- process running.

Readiness:

- required dependencies available enough to serve.

Do not make optional QML availability block API readiness.

---

# 156. Dependency Health

Optional integrations should report status individually.

Examples:

```text
llm
ocr
speech
fhir
abdm
notifications
```

---

# 157. Observability Standards

Every major operation should expose:

- success count;
- error count;
- duration.

Safety workflows add:

- route;
- reason-code aggregate;
- fallback count.

Never use sensitive labels.

---

# 158. Metrics Cardinality

Avoid labels like:

```text
patient_id
message_text
document_name
```

High cardinality and privacy risk.

---

# 159. Tracing Standards

Spans should represent operations.

Examples:

```text
intake.extract
safety.evaluate
document.ocr
providers.search
referral.send
```

No sensitive payloads in spans.

---

# 160. Alerting

Alerts should focus on actionable issues.

Examples:

- repeated crisis fallback failure;
- resource registry stale;
- referral failure spike;
- DB unavailable;
- schema validation failures;
- purge job failures.

---

# 161. Local Development

Developers/Codex should be able to run:

```text
docker compose up
```

or an equivalent documented command for infrastructure.

Application development may run services locally for faster reload.

---

# 162. Local Setup Must Be Reproducible

README/setup scripts SHALL document:

- prerequisites;
- env setup;
- database start;
- migrations;
- backend start;
- frontend start;
- tests.

---

# 163. Seed Data

Seed scripts may provide:

- fake users;
- fake providers;
- test resources;
- synthetic documents metadata.

Seed data must be obviously non-production.

---

# 164. Development Fixtures

Development-only sample clinical data should use synthetic names and scenarios.

Avoid real personal data.

---

# 165. Docker Standards

Docker images should:

- be reproducible;
- avoid unnecessary packages;
- run as non-root where practical;
- use multi-stage builds where useful;
- expose health checks;
- not contain secrets.

---

# 166. Docker Compose

Local Compose should:

- use named volumes;
- isolate services;
- provide health dependencies;
- keep environment documented.

Do not make local development depend on production cloud services.

---

# 167. Container Logging

Containers should log to stdout/stderr in structured format.

Do not write unbounded log files inside containers.

---

# 168. Production Configuration

Production image must not require rebuilding merely to change environment configuration.

Configuration should be injected at runtime.

---

# 169. Infrastructure as Code

When cloud infrastructure begins:

- use Terraform/OpenTofu;
- review changes;
- no manual undocumented production resources where avoidable.

---

# 170. Database Backup Tests

Backups are not trusted until restore is tested.

Detailed schedule belongs in deployment specification.

---

# 171. Code Generation

Generated code is acceptable for:

- API clients;
- schemas;
- protobuf-like artifacts if later used.

Generated code should live in a clear directory and should not be manually edited.

---

# 172. Generated Files

Generated files should state:

```text
DO NOT EDIT MANUALLY
```

and document generator command.

---

# 173. Security Scanning

CI should eventually include:

- SAST;
- dependency vulnerability scan;
- container scan;
- secret scan.

A critical/high finding should block release unless explicitly accepted.

---

# 174. SBOM

Production release SHOULD generate a software bill of materials once deployment hardening begins.

---

# 175. Git Secrets

Automated secret scanning should prevent accidental commit of credentials.

If secret leakage occurs:

1. rotate secret;
2. remove from history if required;
3. add regression guard;
4. document incident.

Deleting the file alone is insufficient.

---

# 176. Authorization Tests

Each privileged endpoint should test at least:

- authorized role;
- unauthorized role;
- unauthenticated actor where applicable.

---

# 177. Pseudonymous Session Security

Pseudonymous session tokens must be:

- random;
- high entropy;
- short-lived/managed;
- not predictable.

Do not expose internal numeric IDs.

---

# 178. Clinical Policy Code

Safety policy should favor:

- pure functions;
- explicit inputs;
- deterministic outputs.

Example:

```python
def evaluate_red_flags(
    signals: PhysicalSafetySignals,
    policy: RedFlagPolicy,
) -> SafetyDecision:
    ...
```

This improves auditability and testing.

---

# 179. Policy Data

Policy values should not be scattered through code.

Prefer:

```text
policy version + validated config
```

with code implementing the evaluation semantics.

---

# 180. Reason Codes

Safety and routing outputs must use enums/registered reason codes.

Do not return arbitrary AI prose as reason code.

---

# 181. Clinical Content Separation

Clinical content should remain separate from generic application UI strings.

Examples:

```text
clinical/policies/
clinical/knowledge/
clinical/localization/
```

---

# 182. Clinical Content Changes

A wording change may be safety-significant.

Codex must not "improve" crisis wording or medical guidance stylistically without specification approval.

---

# 183. No Fabricated Clinical Policy

If a clinical rule is missing, Codex must stop and flag:

```text
SPECIFICATION_REQUIRED
```

instead of inventing a threshold.

---

# 184. Provider Data Rules

Provider contact information must come from:

- verified local registry;
- validated adapter.

Do not use LLM generation.

---

# 185. Self-Care Content Rules

Self-care patient guidance must come from:

- approved knowledge;
- explicit eligibility.

Do not create treatment content from generic model knowledge during implementation.

---

# 186. Resource Fallback

Critical resources may have a bundled fallback configuration.

Fallback must be:

- versioned;
- testable;
- updateable;
- clearly owned.

---

# 187. Clinical Fact Mutation

Confirmed clinical facts require explicit service methods.

Do not mutate ORM fields ad hoc.

---

# 188. Immutable History

Where clinical history changes, preserve provenance rather than simply overwriting important facts.

Exact event/history model is deferred to domain schema.

---

# 189. Testing Safety Precedence

Tests must verify:

```text
hard safety override > low model risk
hard safety override > self-care eligibility
hard safety override > LLM reassurance
```

---

# 190. ML Safety Integration

Model outputs are inputs to application policy only when approved.

A model service must not directly call:

```text
create_referral
show_self_care
route_emergency
```

---

# 191. Research/Production Separation

Production code may call only approved model versions.

Research experiments cannot be selected implicitly by latest timestamp.

---

# 192. Feature Development Workflow

For each new feature:

1. identify requirement IDs;
2. identify module;
3. review architecture;
4. define contracts;
5. define data changes;
6. define safety/privacy impact;
7. implement;
8. test;
9. observe;
10. update docs.

---

# 193. Codex Pre-Implementation Checklist

Before editing code, Codex must:

```text
[ ] inspect current repository
[ ] read master spec
[ ] read architecture
[ ] read engineering standards
[ ] read current phase
[ ] read relevant module specs
[ ] identify requirement IDs
[ ] identify owning module
[ ] identify affected contracts
[ ] identify DB migration needs
[ ] identify tests
```

---

# 194. Codex Implementation Rules

Codex SHALL:

- make the smallest coherent change that fully satisfies the phase;
- preserve unrelated working behavior;
- reuse established patterns;
- add tests;
- run required commands;
- document failures honestly;
- update progress/docs when requested.

---

# 195. Codex Must Not

Codex MUST NOT:

- rewrite unrelated modules for style;
- add dependencies casually;
- disable tests to pass CI;
- introduce another framework solving the same problem;
- bypass module interfaces;
- modify safety policy without authorization;
- invent placeholder medical rules and present them as real;
- hard-code secrets;
- make large architecture changes silently.

---

# 196. Codex Output Format

After implementation, Codex should report:

```text
1. Summary
2. Requirement IDs implemented
3. Files created
4. Files modified
5. Database migrations
6. Tests added
7. Commands run
8. Test/lint/typecheck results
9. Architecture deviations
10. Known limitations
11. Remaining work
```

---

# 197. Codex Failure Reporting

If a command fails:

- provide command;
- provide relevant error;
- explain whether fixed;
- do not claim success.

---

# 198. No Premature Completion

Codex may not mark a phase complete when:

- tests fail;
- migrations are missing;
- acceptance criteria remain unmet;
- a safety-critical spec is missing.

It should report `PARTIAL` or `BLOCKED`.

---

# 199. Code Review by Phase

Every implementation phase should end with a repository audit.

Audit:

- git diff;
- architecture compliance;
- tests;
- dead code;
- dependencies;
- migrations;
- documentation.

---

# 200. Definition of Done — Backend Feature

A backend feature is complete when applicable:

```text
[ ] requirements implemented
[ ] public contracts typed
[ ] domain logic isolated
[ ] persistence implemented
[ ] migration added
[ ] authz enforced
[ ] errors typed
[ ] logs safe
[ ] metrics added
[ ] unit tests pass
[ ] integration tests pass
[ ] contract tests pass
[ ] docs updated
```

---

# 201. Definition of Done — Frontend Feature

```text
[ ] requirements implemented
[ ] typed API usage
[ ] loading state
[ ] empty state
[ ] error state
[ ] authorization/feature state
[ ] accessibility
[ ] responsive behavior
[ ] component tests where appropriate
[ ] E2E updated
[ ] no duplicated API contracts
```

---

# 202. Definition of Done — Safety Feature

```text
[ ] clinician-approved policy available
[ ] deterministic evaluation
[ ] reason codes
[ ] policy version
[ ] hard override tests
[ ] ambiguity tests
[ ] degraded-mode tests
[ ] multilingual implications reviewed
[ ] observability
[ ] rollback/kill switch considered
```

---

# 203. Definition of Done — External Integration

```text
[ ] port defined
[ ] adapter implemented
[ ] timeout
[ ] retry
[ ] error mapping
[ ] auth/config
[ ] sandbox/mock
[ ] contract tests
[ ] observability
[ ] failure fallback
[ ] data-sharing reviewed
```

---

# 204. Definition of Done — ML/QML

```text
[ ] dataset versioned
[ ] preprocessing reproducible
[ ] split reproducible
[ ] seed controlled where relevant
[ ] metrics recorded
[ ] baseline comparison
[ ] artifacts registered
[ ] limitations documented
[ ] tests pass
[ ] no automatic production activation
```

---

# 205. Definition of Done — Database Change

```text
[ ] ORM/model updated
[ ] migration created
[ ] indexes/constraints reviewed
[ ] migration up tested
[ ] downgrade/irreversibility documented
[ ] integration tests updated
[ ] schema docs updated
```

---

# 206. Quality Gate Commands

Exact commands will be frozen during repository setup.

The repository SHOULD eventually provide simple top-level commands similar to:

```text
make lint
make typecheck
make test
make test-integration
make test-e2e
make migrate-check
make ci
```

or equivalent package scripts.

Codex should not need to remember long tool-specific commands.

---

# 207. Task Runner

A lightweight task runner such as:

- Makefile;
- justfile;
- npm scripts;

may centralize commands.

Use one clear convention.

---

# 208. CI Parity

Local quality commands should closely match CI.

Avoid a situation where local tests pass but CI uses undocumented steps.

---

# 209. Formatting Before Diff Review

Codex should format/lint before final diff review so generated noise is minimized.

---

# 210. No Giant Generated Refactor

Do not allow autoformat/import tooling to rewrite unrelated files unless required.

Large unrelated diffs reduce review quality.

---

# 211. Backwards Compatibility

When a feature is already consumed by another module/UI:

- preserve behavior;
- migrate consumers atomically;
- or version contract.

Do not break downstream code silently.

---

# 212. Deprecation

Deprecated API/contract fields should have:

- deprecation note;
- replacement;
- removal plan.

---

# 213. Telemetry Before Optimization

Do not optimize performance based only on intuition.

Measure:

- latency;
- DB queries;
- provider timing;
- queue duration.

Then optimize.

---

# 214. Database Indexing

Add indexes based on:

- FK joins;
- high-value filters;
- ordering/search needs;
- uniqueness.

Do not index every column.

---

# 215. Pagination

List endpoints with potentially unbounded results must paginate.

Do not load all providers/patients/documents into memory.

---

# 216. Bulk Processing

Bulk imports/processing should use:

- chunking;
- bounded memory;
- job status;
- partial-failure reporting.

---

# 217. Resource Limits

External input should have limits:

- text length;
- upload size;
- document pages;
- batch size.

Limits must be configuration/documented.

---

# 218. Timeout Budgets

User-facing orchestration should have a total latency budget.

Nested adapter timeouts should not exceed it uncontrollably.

---

# 219. Localization Engineering

Use a centralized i18n framework.

Do not concatenate translated fragments.

Prefer full translation strings.

---

# 220. Clinical Localization

Clinical/safety strings should carry review metadata/version separately from generic i18n where needed.

---

# 221. Accessibility Testing

Core patient journeys should include:

- automated accessibility checks where possible;
- manual keyboard review;
- screen-reader-oriented semantic review.

Automated tools are not sufficient alone.

---

# 222. Browser Support

Supported browsers will be defined later.

Avoid unnecessary APIs that prevent common modern browser compatibility.

---

# 223. PWA Engineering

PWA caching must not cache sensitive API responses by default.

Service-worker strategy should focus on:

- app shell;
- public assets;
- approved static fallback.

---

# 224. Client Storage

Do not store sensitive health data in:

- localStorage;
- sessionStorage;

without explicit design approval.

Prefer server-side state and short-lived memory.

---

# 225. Cookies

Authentication cookies, if used, should use:

- Secure;
- HttpOnly;
- SameSite appropriate to flow.

---

# 226. CORS

CORS must use explicit allowed origins.

Do not use `*` with credentials in production.

---

# 227. CSP

Production frontend should implement Content Security Policy appropriate to integrations.

Avoid uncontrolled inline script dependencies.

---

# 228. CSRF

If cookie-based auth is used for state-changing requests, CSRF protections must be explicitly designed.

---

# 229. SSRF

Backend URL-fetching features must not fetch arbitrary user URLs without restrictions.

This matters for:

- documents;
- webhooks;
- future external imports.

---

# 230. Webhook Security

Inbound webhooks require:

- signature;
- timestamp;
- replay protection;
- idempotency;
- schema validation.

---

# 231. Outbound Webhook Security

Outbound webhooks should:

- send minimum payload;
- sign payload;
- use TLS;
- retry safely.

---

# 232. API Rate Limits

Anonymous and compute-heavy endpoints need stricter rate limiting.

Admin/clinician APIs also require abuse protection.

---

# 233. Security Headers

Frontend/API should apply appropriate headers:

- HSTS in production;
- CSP;
- X-Content-Type-Options;
- frame protections;
- referrer policy.

Exact headers depend on deployment.

---

# 234. Audit Logging

Audit entries should include:

- actor;
- action;
- resource;
- timestamp;
- outcome;
- request/correlation ID.

Avoid full clinical payloads.

---

# 235. Admin Actions

High-impact admin actions may require:

- confirmation;
- reason;
- maker-checker approval;
- audit.

---

# 236. Policy Change Safety

Codex must not make clinical policy "data configurable" in a way that lets ordinary admins bypass clinical governance.

Role separation matters.

---

# 237. Feature Flag Safety

Feature flags need:

- default;
- environment scope;
- owner;
- reason;
- expiry/review date for temporary flags.

Avoid permanent flag debt.

---

# 238. Experimental Features

Experimental user-facing features should show appropriate status internally and remain disabled in production unless explicitly approved.

---

# 239. Mock vs Production Config

Production must fail startup or disable the feature if a required real adapter is missing.

Never silently use `MockProvider` in production.

---

# 240. Startup Validation

Application startup should validate critical configuration:

- database;
- security settings;
- environment;
- required integrations for enabled features.

---

# 241. Configuration Errors

Misconfiguration should produce clear actionable errors.

Do not continue with unsafe defaults.

---

# 242. Health Startup

Readiness should remain false until critical migrations/configuration are valid.

---

# 243. Migration Compatibility

Application deployment and migrations should support safe ordering.

Avoid code that requires a destructive migration before any old instance can stop.

---

# 244. Zero-Downtime Goal

Production migration practices should aim for compatible staged deployment when the project reaches production.

Not all MVP changes require full zero-downtime complexity.

---

# 245. Data Backfills

Large backfills should run separately from schema migration when needed.

Do not lock tables for long periods unnecessarily.

---

# 246. Database Transactions

Use transactions for multi-write invariants.

Example referral:

```text
verify consent
create referral
write audit/outbox
COMMIT
```

---

# 247. External Calls Inside Transactions

Avoid long network calls while holding DB transactions open.

Pattern:

1. create pending state;
2. commit;
3. perform external call;
4. update status.

---

# 248. Eventual Consistency UI

If a workflow is asynchronous, UI should expose processing state instead of pretending instant completion.

---

# 249. User-Facing Status

Use clear statuses:

```text
Processing
Needs review
Completed
Failed
```

Avoid internal technical jargon.

---

# 250. Research Code Review

Research code may iterate faster but still requires:

- reproducibility;
- data leakage review;
- license/source tracking;
- no production coupling.

---

# 251. Dataset Files

Large datasets SHOULD NOT be committed directly to Git unless intentionally small fixtures.

Use dataset references/storage.

---

# 252. Model Files

Large model artifacts SHOULD NOT be stored in Git.

Use model/artifact storage.

---

# 253. Binary Artifacts

Avoid committing generated binaries, logs, exports, local DB files, caches.

Configure `.gitignore`.

---

# 254. Temporary Files

Temporary processing files should be:

- isolated;
- cleaned up;
- not trusted;
- securely handled.

---

# 255. OCR Temporary Images

Derived images containing medical data require retention/cleanup consistent with original documents.

---

# 256. Data Export Files

Generated exports should have:

- expiration;
- authorized access;
- audit;
- cleanup.

---

# 257. Search Index Privacy

Search/vector indexes containing sensitive data need:

- authorization;
- deletion propagation;
- retention;
- isolation.

---

# 258. Development Error Pages

Detailed error pages may be enabled locally.

Production must not expose stack traces/configuration.

---

# 259. Debug Flags

Debug must default off outside local development.

---

# 260. Naming External Adapters

Adapter classes should identify provider.

Example:

```text
PaddleOCRAdapter
```

Domain ports should identify capability.

Example:

```text
OCRPort
```

---

# 261. Naming Domain Services

Name services by domain responsibility.

Prefer:

```text
ReferralService
```

over:

```text
Manager
Helper
Utils
```

Avoid generic `helpers.py` dumping grounds.

---

# 262. Utility Modules

A utility should be:

- stateless;
- generic;
- narrow.

If utility starts knowing business concepts, move it to the domain/module.

---

# 263. Constants

Module-specific constants live with module.

Global constants are rare.

Clinical thresholds are not ordinary constants.

---

# 264. Serialization Boundaries

Serialize at:

- API;
- events;
- external adapters;
- persistence where needed.

Keep domain code operating on typed objects.

---

# 265. Transaction IDs / Request IDs

Do not expose internal DB transaction concepts to clients.

Request IDs are suitable for support/tracing.

---

# 266. Public Messages vs Internal Messages

Error response message:

```text
"Document processing failed. Please try again."
```

Internal log:

```text
error_code=OCR_PROVIDER_TIMEOUT provider=paddleocr
```

Do not expose provider/internal details unnecessarily.

---

# 267. Clinical User Messaging

Clinical/safety user messages must use approved copy where required.

Codex should not improvise safety language.

---

# 268. Internationalization Keys

Do not use English sentence as translation key.

Prefer:

```text
mentalHealth.crisis.callNow
```

---

# 269. Feature-Owned Translations

Feature modules own normal translations.

Central localization infrastructure aggregates them.

---

# 270. API Documentation

Every public endpoint should have:

- summary;
- auth requirement;
- request schema;
- response schema;
- errors.

FastAPI OpenAPI metadata should be meaningful.

---

# 271. Module Documentation

Each major module SHOULD eventually have a README containing:

- purpose;
- public capabilities;
- data ownership;
- dependencies;
- events;
- important invariants.

---

# 272. ADR Requirement

Create an ADR before:

- adding a new backend framework;
- adding microservice;
- changing DB;
- changing event transport;
- changing tenancy model;
- replacing API style globally;
- introducing a new architecture pattern.

---

# 273. ADR Status

Use:

```text
PROPOSED
ACCEPTED
SUPERSEDED
REJECTED
```

---

# 274. Code Ownership and Approval

Clinical policy changes require clinical review.

Security-sensitive changes require security review where available.

Architecture changes require architecture decision.

One developer may play multiple roles during prototype development, but review categories should remain conceptually explicit.

---

# 275. Release Versioning

Application release versioning may use semantic versioning.

Example:

```text
0.1.0
```

Policy/model/content versions remain independent.

---

# 276. Changelog

A changelog SHOULD track user/operations-visible changes as the project matures.

Do not expose sensitive internal incident details publicly.

---

# 277. Deprecation Warnings

Deprecation should be visible to developers/consumers before removal where feasible.

---

# 278. Code Freeze for Safety Evaluation

Before major clinical pilot evaluation, freeze:

- policy version;
- prompt version;
- model version;
- resource configuration;
- relevant code commit.

This supports reproducibility.

---

# 279. Performance Testing

Performance tests should focus on realistic bottlenecks:

- concurrent intake;
- document upload;
- OCR queue;
- provider search;
- API latency.

QML training performance is a research benchmark, not normal request-load target.

---

# 280. Load Test Data

Use synthetic data.

Never load-test production with copied patient data.

---

# 281. Privacy in Metrics

Metrics should not include:

- patient names;
- free-text query;
- phone;
- email;
- document content.

---

# 282. Metrics Naming

Use consistent names.

Suggested style:

```text
swasthyasetu_http_requests_total
swasthyasetu_llm_failures_total
```

Final convention follows monitoring stack.

---

# 283. Metrics Units

Include units in names where convention expects it:

```text
request_duration_seconds
```

---

# 284. Alert Fatigue

Do not alert on every recoverable error.

Alert on:

- sustained failure;
- safety impact;
- resource invalidity;
- infrastructure outage.

---

# 285. Incident Severity

Later incident plan should define severity classes.

Safety incidents and availability incidents may have different escalation.

---

# 286. Post-Incident Engineering

After a meaningful incident:

- root cause;
- corrective action;
- regression test;
- documentation;
- ownership.

---

# 287. Feature Removal

Deleting a feature requires:

- contract consumer check;
- data retention/migration;
- feature flag cleanup;
- route/UI removal;
- dependency cleanup;
- docs update.

---

# 288. Unused Dependency Cleanup

Remove dependencies no longer used.

Do not accumulate abandoned packages.

---

# 289. Database Column Cleanup

Do not remove old columns until:

- code no longer reads/writes;
- backfill complete;
- rollback period considered.

---

# 290. Experimental Code

Experimental code belongs in clearly scoped research/feature modules.

Do not scatter commented experiments into production code.

---

# 291. Prototype vs Production

Prototype shortcuts must be explicitly marked.

Examples:

```text
prototype-only mock directory
sandbox FHIR integration
synthetic data
```

Do not let a demo shortcut silently become production architecture.

---

# 292. Codex Prompt Alignment

Every implementation prompt should reference:

- exact phase;
- requirement IDs;
- architecture modules;
- affected docs;
- acceptance criteria;
- commands to run.

---

# 293. Codex Scope Control

Prompts should include:

```text
IN SCOPE
OUT OF SCOPE
```

This is mandatory for significant phases.

---

# 294. Codex Repository Audit

Before coding, Codex should report briefly:

- current branch;
- relevant folders;
- existing implementation;
- tests;
- migrations;
- conflicts with requested phase.

Then implement.

---

# 295. Codex Diff Audit

After coding, Codex should inspect:

```text
git status
git diff --stat
git diff
```

or equivalent.

It must verify no unrelated modifications were introduced.

---

# 296. Codex Command Execution

Codex should execute commands rather than merely instruct the user to run them when its environment permits.

---

# 297. Codex Timeouts

If long-running tests cannot complete, Codex should report:

- which command;
- how far it got;
- what remains unverified.

Do not state "all tests pass" unless they did.

---

# 298. Codex Generated Migrations

Autogenerated migrations must be manually inspected by Codex.

Verify:

- unexpected drops;
- type changes;
- indexes;
- constraints.

---

# 299. Codex Dependency Changes

If Codex adds a dependency, final report must list:

```text
dependency
version
purpose
```

---

# 300. Codex Architecture Deviation

If implementation requires deviation:

1. stop if material;
2. describe conflict;
3. propose ADR/change;
4. wait for approval if high-impact.

Do not silently improvise.

---

# 301. Codex Safety Blocker

If the task requires an undefined clinical threshold/rule:

```text
STATUS: BLOCKED — CLINICAL POLICY REQUIRED
```

Codex may scaffold interfaces/tests using placeholders clearly marked non-production, but must not invent authoritative clinical behavior.

---

# 302. Codex External Credential Blocker

If credentials are missing:

- implement adapter;
- use mock/sandbox when specified;
- add env config;
- add tests;
- report real integration unverified.

Do not hard-code dummy secret into production config.

---

# 303. Codex Dataset Blocker

If final dataset is undecided:

- implement generic dataset interface/framework;
- use approved synthetic/sample dataset for tests;
- do not select a medical dataset silently.

---

# 304. Codex Provider Directory Blocker

If real provider data source is undecided:

- implement registry schema/service;
- use clearly synthetic seed data;
- do not scrape/invent production contacts.

---

# 305. Codex Self-Care Content Blocker

If approved self-care content is unavailable:

- implement engine/schema/workflow;
- use synthetic/non-clinical fixtures;
- do not invent patient-facing remedy content.

---

# 306. Codex Mental Health Content Blocker

If clinician-approved thresholds/copy are unavailable:

- implement policy framework;
- use marked test fixtures;
- preserve fallback architecture;
- do not ship invented production thresholds.

---

# 307. Quality Priority Order

When trade-offs arise:

```text
1. Safety
2. Correctness
3. Privacy/Security
4. Architecture integrity
5. Testability
6. Maintainability
7. Accessibility
8. Performance
9. Developer convenience
10. Cosmetic elegance
```

This does not mean performance/UX are unimportant; it defines conflict resolution.

---

# 308. Prohibited Engineering Shortcuts

Never intentionally use:

- hard-coded secrets;
- unrestricted `eval`;
- unsafe deserialization;
- shell commands built from user input;
- disabled TLS verification in production;
- wildcard CORS with credentials;
- global auth bypass;
- direct raw AI output as clinical truth;
- silent exception swallowing;
- tests that depend on production data;
- unversioned safety policy changes.

---

# 309. Engineering Review Before Phase Completion

Before declaring a phase done:

```text
[ ] requirements mapped
[ ] architecture respected
[ ] code formatted
[ ] lint passes
[ ] typecheck passes
[ ] tests pass
[ ] migrations checked
[ ] security reviewed
[ ] logs reviewed
[ ] docs updated
[ ] git diff inspected
[ ] known limitations reported
```

---

# 310. Standard Phase Result Status

Use one of:

```text
COMPLETE
PARTIAL
BLOCKED
FAILED
```

Do not use vague "mostly done".

---

# 311. COMPLETE

Only when:

- acceptance criteria met;
- required checks pass;
- no unresolved blocker.

---

# 312. PARTIAL

Use when:

- meaningful implementation exists;
- some acceptance criteria remain;
- continuation is clear.

---

# 313. BLOCKED

Use when:

- missing policy;
- missing credential;
- unresolved architecture decision;
- external dependency unavailable;
- unsafe to guess.

---

# 314. FAILED

Use when:

- implementation did not reach usable state;
- verification failed materially.

Failure is preferable to falsely claiming success.

---

# 315. Engineering Standards Change Control

Changes to this document require:

- reason;
- affected modules;
- migration implications;
- tooling implications;
- Codex prompt updates if relevant.

Material architecture changes should additionally create/update an ADR.

---

# 316. Minimum Engineering Baseline Before Feature Work

Before major feature implementation begins, the repository should have:

```text
[ ] Python project
[ ] TypeScript/Next.js project(s)
[ ] formatting
[ ] linting
[ ] type checking
[ ] test framework
[ ] PostgreSQL
[ ] migrations
[ ] Docker local stack
[ ] typed settings
[ ] structured logging
[ ] request IDs
[ ] base error handling
[ ] module structure
[ ] CI skeleton
```

---

# 317. Recommended Initial Tooling Decisions

The repository foundation phase should strongly consider:

## Python

- `ruff`
- `mypy` or `pyright`
- `pytest`
- `pytest-asyncio`
- `httpx`
- `coverage`

## Backend

- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- async PostgreSQL driver

## Frontend

- ESLint
- TypeScript
- testing library
- Playwright for E2E

Exact versions belong in lockfiles.

---

# 318. Formatting Ownership

Formatting rules belong to tools, not personal preference.

Codex should not repeatedly debate formatting.

---

# 319. Linter Exceptions

If an exception is needed:

- narrowest scope;
- explanatory comment when non-obvious.

Avoid file-wide ignores.

---

# 320. Type Ignore Rules

`# type: ignore` should include a specific error code where supported and a reason if non-obvious.

Do not use it as routine workaround.

---

# 321. Security Ignore Rules

Do not suppress a security scanner finding without documenting:

- false positive or accepted risk;
- reason;
- scope;
- owner.

---

# 322. Test Skips

A skipped test must have a reason.

No silent skip for unstable code.

---

# 323. Flaky Tests

Flaky tests must be fixed or isolated with explicit tracking.

Repeated reruns are not a solution.

---

# 324. Dependency Injection in Tests

Use dependency injection to swap:

- adapters;
- time;
- repositories;
- external services.

Avoid global monkeypatching when cleaner seams exist.

---

# 325. Repository Test Boundaries

Each module should have tests located consistently.

Suggested:

```text
modules/<module>/tests/
```

plus cross-module:

```text
tests/integration/
tests/e2e/
tests/safety/
tests/contracts/
```

Final repository structure document will freeze layout.

---

# 326. CI Test Database

CI integration tests should use an isolated PostgreSQL instance.

Do not use SQLite to emulate PostgreSQL-specific behavior for critical integration tests.

---

# 327. Migration CI

CI should test:

```text
empty DB -> upgrade head
```

and later optionally:

```text
previous release -> upgrade head
```

---

# 328. Seed Migration Separation

Do not mix production schema migrations with large demo seed data.

Seed scripts are separate.

---

# 329. User-Visible Copy

Ordinary UI copy may be changed through product/UX review.

Clinical/safety copy follows stricter governance.

---

# 330. External API Contract Fixtures

For external providers, store sanitized/synthetic fixtures for:

- success;
- validation failure;
- timeout;
- rate limit;
- malformed response.

---

# 331. Integration Sandbox Tests

Sandbox tests should be opt-in in local/CI where credentials exist.

Normal tests must not require internet/vendor account.

---

# 332. No Internet Dependency for Core Test Suite

Core unit/integration tests should run offline except containerized local dependencies.

---

# 333. Retry Testability

Retry/backoff code should support injected sleep/clock to avoid slow tests.

---

# 334. Cancellation

Long-running async operations/jobs should respect cancellation where practical.

---

# 335. Graceful Shutdown

API/worker should:

- stop accepting new work;
- finish/abort safely;
- close DB connections;
- flush telemetry.

---

# 336. Database Connection Pool

Pool settings should be configurable.

Avoid hard-coded oversized pools.

---

# 337. Request Size Limits

Backend/proxy should enforce sensible request limits.

Document uploads may use separate larger limits.

---

# 338. Streaming Uploads

Large file uploads should avoid loading entire files into memory where possible.

---

# 339. Content Hashes

Documents/model artifacts may use checksums for:

- duplicate detection;
- integrity;
- versioning.

---

# 340. Data Normalization

Normalize values only through explicit functions.

Preserve original source representation where clinically useful.

---

# 341. Units and Numbers

Never compare measurement numbers without considering units.

Use typed value/unit structures.

---

# 342. Decimal Precision

Use decimal or domain-appropriate numeric type for values where float precision is unsuitable.

---

# 343. Money

If payments are introduced, never use binary floating point for currency.

---

# 344. Locale Formatting

Display formatting should be locale-aware.

Persistence should use canonical representations.

---

# 345. Phone Numbers

Provider/contact numbers should be stored in normalized form plus display form if needed.

Do not assume one national format if future international support emerges.

---

# 346. URLs

External URLs should be validated/normalized.

Provider-supplied links should be treated as untrusted external destinations.

---

# 347. Rich Text

Avoid unrestricted rich HTML in admin-managed medical content.

Prefer structured/Markdown-like safe subset.

---

# 348. File Names

User-visible original filename may be stored as metadata if allowed.

Object storage key must be generated independently.

---

# 349. Data Export Encoding

Use UTF-8 unless an external standard requires otherwise.

---

# 350. CSV Exports

Guard against spreadsheet formula injection when exporting user-controlled text.

---

# 351. JSON Encoding

Use ISO 8601 for timestamps.

Use stable enums/field names.

---

# 352. Schema Evolution Tests

When contract changes, add tests demonstrating old/new behavior or migration.

---

# 353. Feature Dependencies

A module should explicitly declare required capabilities.

Do not discover dependencies via implicit import side effects.

---

# 354. Circular Dependencies

Circular module dependencies are prohibited.

Resolve through:

- orchestration layer;
- events;
- extracting shared abstraction;
- rethinking ownership.

---

# 355. Import Rules

A module may import another module's public contracts.

It may not import internal infrastructure/repository classes.

---

# 356. Shared Kernel Growth

Every addition to shared kernel should answer:

> Is this truly generic across domains?

If not, keep it module-local.

---

# 357. Utility Dependency Direction

Shared utility code must not import feature modules.

---

# 358. Event Consumer Failure

A failed non-critical consumer should not rollback the original transaction after outbox commit.

It should retry independently.

---

# 359. Critical Synchronous Dependency

If a decision truly requires another module synchronously, call its public application interface.

Do not use event bus for everything.

---

# 360. Eventual Consistency Communication

UI should handle brief delays in projections.

Do not hide async state behind fake synchronous success.

---

# 361. Event Schema Compatibility

Consumers should tolerate additive fields where possible.

Breaking event changes require version bump.

---

# 362. API Schema Compatibility

Do not change optional -> required fields casually.

Version/migration required if clients may break.

---

# 363. Pagination Stability

If cursor pagination is chosen later, ordering must be deterministic.

---

# 364. Sorting

Public list APIs should document sortable fields.

Never pass arbitrary DB column names from user input.

---

# 365. Filtering

Validate filters against allowlist.

---

# 366. Search Query Limits

Search input should have length/complexity limits.

---

# 367. Research Resource Limits

Training/QML jobs need quotas/timeouts so a user cannot exhaust infrastructure accidentally.

---

# 368. QML Hardware Costs

Real quantum hardware use must be explicitly enabled.

Simulator is default unless phase specifies otherwise.

---

# 369. LLM Costs

AI gateway should expose usage metrics where provider supports them.

Do not include sensitive prompt text in cost telemetry.

---

# 370. Health Data in External AI

External AI requests must follow configured data-handling policy.

Where possible:

- remove identity;
- limit context;
- use contractual privacy settings.

---

# 371. Provider Data Updates

Provider/resource updates should preserve:

- previous version;
- updater;
- verification date;
- source.

---

# 372. Maker-Checker

Safety-critical admin-managed content SHOULD support maker-checker approval as the platform matures.

Initial prototype may use version-controlled approvals.

---

# 373. Feature Documentation Template

Every new module README should eventually include:

```text
Purpose
Requirements
Owned Data
Public Capabilities
Consumed Capabilities
API
Events
Permissions
Feature Flags
Failure Modes
Metrics
Tests
Safety/Privacy Notes
```

---

# 374. Adapter Documentation Template

Each adapter should document:

```text
Provider
Capability
Authentication
Timeout
Retry
Rate Limit
Data Sent
Errors
Fallback
Sandbox/Mock
```

---

# 375. Policy Documentation Template

Each policy should document:

```text
Policy ID
Version
Owner
Inputs
Outputs
Reason Codes
Hard Overrides
Ambiguity Behavior
Fallback
Approval
Test Suite
```

---

# 376. Model Documentation Template

Each model should document:

```text
Task
Dataset
Features
Target
Split
Metrics
Calibration
Limitations
Subgroups
Artifact
Version
Approval
```

---

# 377. PR Checklist for Codex

Codex final report must support reviewer verification:

```text
[ ] scope understood
[ ] requirements cited
[ ] tests run
[ ] no silent architecture changes
[ ] migration noted
[ ] new dependencies noted
[ ] security/safety impact noted
[ ] known limitations noted
```

---

# 378. Engineering Standards Enforcement

These standards should gradually become executable via:

- linters;
- type checkers;
- import-boundary tests;
- architecture tests;
- CI checks;
- schema tests;
- migration tests.

Written rules should become automated whenever cost-effective.

---

# 379. Exceptions

An exception to these standards requires:

- reason;
- scope;
- impact;
- duration if temporary.

Repeated exceptions suggest the standard or architecture needs revision.

---

# 380. Final Engineering Invariants

Every implementation must preserve:

```text
1. Strong typing at important boundaries.
2. Thin transport layers.
3. Domain logic outside routes/controllers.
4. Module-owned data.
5. No direct cross-module writes.
6. External providers behind adapters.
7. Deterministic safety logic.
8. No unvalidated AI output in decision logic.
9. Provenance for AI-derived clinical facts.
10. Explicit migrations for schema changes.
11. Structured, privacy-safe logs.
12. Tests delivered with features.
13. Honest degraded modes.
14. No invented clinical policy.
15. No invented provider/remedy information.
16. No fake success when verification fails.
17. Codex must inspect, implement, test, and audit each phase.
```

---

# 381. Next Foundation Document

After this Engineering Standards document, create:

```text
34_MASTER_IMPLEMENTATION_PLAN.md
```

The implementation plan will convert the master specification, PRD, architecture, and engineering standards into a phase-by-phase build sequence with:

- requirement IDs;
- prerequisites;
- exact scope;
- deliverables;
- files/directories;
- data changes;
- APIs;
- tests;
- commands;
- acceptance criteria;
- definition of done.

No major production implementation should begin before that plan is complete.


---

# R3 Dependency Profile Standards

## ENG-R3-001 — Keep runtime profiles narrow

The repository SHOULD maintain separate dependency groups/environments for:

```text
backend-core
document-ai
language-ai
rag
ml-research
qml-research
ops
dev
```

Do not create one global Python environment containing every AI/research framework.

## ENG-R3-002 — Research is not patient runtime

MLflow, Optuna, PennyLane, Qiskit Machine Learning, Promptfoo and comparable research tooling MUST NOT become transitive requirements of the normal clinical API unless a later accepted ADR explicitly changes that.

## ENG-R3-003 — Benchmark-gated providers

An implemented OCR/ASR/TTS/embedding adapter MUST NOT be described as production-approved until the project benchmark and acceptance criteria pass.

## ENG-R3-004 — Direct LLM adapter first

`LLMProvider` is mandatory.

A separately deployed LLM gateway is not mandatory.

Do not add LiteLLM Proxy without an explicit phase/ADR.

## ENG-R3-005 — No executable model upload

Production endpoints MUST NOT deserialize arbitrary pickle, joblib, dill or cloudpickle artifacts supplied by users.

Approved model artifacts originate from controlled training/registry/storage.

## ENG-R3-006 — ONNX parity

An ONNX model is deployable only after prediction/schema/threshold parity testing against the approved native model.

## ENG-R3-007 — Default Compose stays minimal

Early local development should not require every pilot/research service.

Phase-specific Compose profiles/overrides SHOULD introduce optional infrastructure.

## ENG-R3-008 — External framework telemetry

Any dependency capable of vendor telemetry must be reviewed and configured before protected deployment.

Generic observability MUST NOT capture PHI by default.
