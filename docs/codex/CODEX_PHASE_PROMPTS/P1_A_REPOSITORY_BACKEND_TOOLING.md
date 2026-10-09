# Codex Phase Prompt — P1-A Repository & Backend Engineering Foundation

**Project:** SwasthyaSetu AI  
**Prompt ID:** `SSAI-CODEX-P1-A`  
**Scope:** Repository preflight + backend engineering foundation only  
**Implementation mode:** Strict / minimal / architecture-preserving  
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

## 0. Mission

You are implementing the first real engineering unit of SwasthyaSetu AI.

Your task is to establish a clean, tested Python/FastAPI backend foundation **without pulling forward later clinical, persistence, AI, interoperability, identity-provider, storage-provider, or infrastructure work**.

This repository contains extensive architecture, governance, clinical-safety, research, and technology-selection documents. Treat them as authoritative constraints.

Do not "improve" the project by adding extra infrastructure.

Do not implement future features.

Do not invent unresolved clinical or integration decisions.

---

# 1. Stop Conditions Before Any Edit

Before changing a file, perform a repository preflight.

From the repository root, verify that the following canonical documents exist:

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

docs/source_material/README.md
docs/source_material/SOURCE_MANIFEST.md
```

Also verify that the source-material directories exist:

```text
docs/source_material/sih/
docs/source_material/mannsetu/
```

If any R3 governance file or the source-material governance structure is missing:

1. do **not** begin implementation;
2. do **not** invent replacements;
3. report:

```text
STATUS: BLOCKED
REASON: REQUIRED GOVERNANCE/SOURCE-MATERIAL FILES MISSING
```

4. list the exact missing paths;
5. stop.

The contents under `docs/source_material/` are immutable primary references.

Do not edit them.

---

# 2. Read Order and Precedence

Read the following before implementation.

## Tier 1 — permanent project constraints

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
```

## Tier 2 — architecture and engineering constraints

```text
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/29_ENGINEERING_STANDARDS.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_ARCHITECTURE_RECONCILIATION.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
```

## Tier 3 — implementation sequencing and acceptance

```text
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
```

## Tier 4 — contracts needed for foundation compatibility

```text
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
```

Do not implement the domain/database specifications in this phase.

Read them only to avoid creating a foundation that conflicts with later work.

If documents conflict:

1. apply the precedence rules documented by the project;
2. do not silently choose;
3. report the conflict;
4. stop if the conflict changes P1-A implementation materially.

---

# 3. Repository Audit Before Editing

Before edits, print/report:

```text
git branch --show-current
git status --short
git rev-parse --show-toplevel
```

Then inspect:

```text
repository tree
existing Python/build configuration
existing package-manager files
existing Docker files
existing CI files
backend/app contents
root .gitignore
root .editorconfig
README.md
```

Check for accidental nested repositories:

```text
find/search for nested .git directories
```

On Windows-compatible environments, use an equivalent command if needed.

Do not delete user changes.

If the working tree contains unrelated uncommitted user changes:

- preserve them;
- do not overwrite them;
- report them in the final summary.

---

# 4. Determine Exact P1-A Acceptance Scope

Before coding, extract the exact P1/P1-A-relevant acceptance criteria from:

```text
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
```

Create a short internal implementation checklist mapping each planned change to the relevant acceptance criterion.

Do not invent acceptance IDs.

If the canonical documents describe P1 differently from this prompt, follow the canonical documents and report the deviation.

This prompt intentionally limits implementation to the **backend engineering foundation**.

Do not mark all of P1 complete unless every canonical P1 acceptance criterion has actually passed.

---

# 5. Allowed P1-A Technology

Use only technology permitted by the R3 core foundation.

Expected backend foundation:

```text
Python 3.12+
FastAPI
Pydantic v2
pydantic-settings
Uvicorn
pytest
pytest-asyncio / async HTTP test support as needed
Ruff
mypy or the typing tool mandated by engineering standards
httpx only if needed by tests/application boundary
```

Add another dependency only if:

1. an authoritative document requires it;
2. it belongs to the correct R3 dependency class;
3. you document why it is needed.

Do not add dependencies simply because they may be useful later.

If the engineering standards mandate a specific package manager, use it.

If no package manager is prescribed, prefer a modern reproducible `pyproject.toml`-based workflow and generate the appropriate lockfile. Do not introduce multiple competing Python package managers.

---

# 6. Explicitly Forbidden in P1-A

Do **not** add or implement:

```text
clinical business logic
physical red-flag rules
mental-health routing
self-care/Ayurveda rules
provider-routing rules
real provider records
real resource/hotline data
FHIR resources or HAPI runtime
ABDM flows
Keycloak
authentik
SeaweedFS
MinIO
Valkey/Redis
NATS
RabbitMQ
Kafka
OpenBao
Infisical
MLflow
PaddleOCR
Tesseract
IndicConformer
faster-whisper
IndicTrans2
IndicLID
IndicXlit
BHASHINI
LiteLLM Proxy
LangChain
LlamaIndex
Haystack
Sentence Transformers
pgvector schema
SQLAlchemy models
Alembic migrations
database repositories
Celery
Procrastinate durable queue
PennyLane
Qiskit
Optuna
SHAP
ONNX Runtime
BentoML
KServe
Triton
vLLM
Kubernetes
Terraform resources
```

Some of these are approved future technologies.

They are still forbidden in P1-A because their phases have not activated.

Do not clone upstream GitHub repositories into the project.

If you somehow need upstream source inspection for a foundation dependency, use a temporary ignored location such as:

```text
.external/
upstream/
.tmp/upstream/
```

and do not commit it.

---

# 7. Required Backend Foundation

Implement the smallest clean backend that satisfies the canonical P1-A acceptance criteria.

At minimum, unless the canonical acceptance criteria say otherwise, establish:

```text
backend/
├── pyproject.toml
├── README.md                         if useful/consistent with repo docs
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   └── ...
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── ...
└── tests/
    └── foundation tests
```

Do not mechanically create files just to match this example.

Respect `docs/03_REPOSITORY_STRUCTURE.md`.

If the canonical repository structure places tests differently, follow it.

---

# 8. FastAPI Application Construction

Use an application factory unless project standards explicitly choose another pattern.

Preferred conceptual pattern:

```python
def create_app(settings: Settings | None = None) -> FastAPI:
    ...
```

and expose:

```python
app = create_app()
```

from a predictable module for Uvicorn.

The application factory must support deterministic testing without process-global mutation.

Do not put domain logic into `main.py`.

---

# 9. API Versioning

Establish the `/api/v1` routing boundary according to:

```text
docs/06_API_CONTRACTS.md
```

Do not create domain endpoints yet.

The v1 router can initially be empty or contain only foundation endpoints if the API contract explicitly places them there.

---

# 10. Health Endpoints

Implement the canonical health endpoints from `06_API_CONTRACTS.md`.

Expected paths from the current architecture are:

```text
GET /health/live
GET /health/ready
```

Confirm them from the canonical API contract before implementation.

## Liveness

Liveness answers:

```text
is the application process alive and able to serve?
```

It must not depend on optional external services.

## Readiness

At P1-A there may be no database or external runtime dependency yet.

Do not invent fake database/provider checks.

Readiness should reflect only dependencies that actually exist in this phase.

Use a stable typed response.

Do not expose secrets, environment dumps, host internals, package inventories, or sensitive diagnostics.

---

# 11. Settings / Configuration

Create a typed settings model using the configuration library permitted by engineering standards.

Use explicit environment handling.

Recommended concepts:

```text
application name
environment
debug
API v1 prefix
log level
```

Only add settings needed by current foundation behavior.

Do not add dozens of speculative future settings.

Production-safe defaults:

```text
debug = false
```

No real secrets.

---

# 12. Environment File

Create/update a safe example environment file in the canonical location if required.

It may contain:

```text
variable names
safe local defaults
dummy non-secret values
```

It must not contain:

```text
real passwords
API keys
ABDM credentials
LLM secrets
database production credentials
```

Ensure real `.env` files remain ignored.

---

# 13. Error Foundation

Read `docs/06_API_CONTRACTS.md` and `docs/29_ENGINEERING_STANDARDS.md`.

If P1 acceptance requires the common API error envelope, implement only the minimal project-level foundation now.

Do not invent domain error types for modules that are not implemented.

A future domain module should be able to translate a typed application error into the documented HTTP envelope without leaking stack traces.

If the acceptance criteria defer this to a later phase, do not pull it forward.

---

# 14. Correlation / Request IDs

If required by the canonical P1 criteria or engineering standards, implement minimal request correlation middleware.

Requirements:

```text
random/non-PHI identifier
accept/reject inbound value according to documented policy
return correlation identifier in response where specified
available to structured logs
```

Never derive correlation ID from:

```text
patient ID
encounter ID
email
phone
ABHA
```

If not required in P1-A, defer it rather than overbuilding.

---

# 15. Logging

Use the smallest logging implementation consistent with engineering standards.

Requirements:

```text
no request-body logging by default
no Authorization header
no secrets
no PHI fields
stable logger configuration
environment-appropriate log level
```

Do not introduce a third-party logging framework unless the project standards require it.

Do not add a centralized log backend in P1-A.

---

# 16. OpenTelemetry

R3 makes OpenTelemetry the observability contract, not necessarily a P1-A deployed service.

If canonical P1 acceptance explicitly requires basic OTel instrumentation, implement the minimal instrumentation boundary.

Otherwise:

- do not add Collector;
- do not add Prometheus;
- do not add Grafana;
- leave the code cleanly extensible for the observability phase.

---

# 17. Python Quality Configuration

Configure the backend toolchain according to `29_ENGINEERING_STANDARDS.md`.

Expected categories:

```text
Ruff lint
Ruff format/check
static typing
pytest
async test support
coverage reporting if required
```

Do not invent arbitrary coverage percentages unless standards/acceptance criteria define them.

Keep configuration in `pyproject.toml` where appropriate.

---

# 18. Type Quality

The implemented foundation must pass the configured type checker.

Avoid:

```text
Any everywhere
type: ignore without explanation
untyped public functions
dict[str, Any] for stable API responses
```

Prefer typed response models/contracts.

---

# 19. Tests Required

At minimum, subject to canonical P1 acceptance:

## Application construction

Verify:

```text
create_app() succeeds
expected title/version/config are set
```

## Liveness

Verify:

```text
GET /health/live
expected status code
expected schema
```

## Readiness

Verify:

```text
GET /health/ready
expected status code
expected schema
```

## API version boundary

Verify that the v1 router is mounted at the expected prefix.

## Settings

Verify:

```text
safe defaults
environment override
invalid value handling
```

## Error behavior

If error foundation is implemented, test the documented envelope and confirm internal stack traces are not returned.

## Import/boot smoke

Application package imports cleanly in a fresh process/test environment.

Do not write tests for unimplemented clinical behavior.

---

# 20. No Fake Clinical Data

Do not create development fixtures claiming to be:

```text
real doctor
verified hospital
real hotline
approved Ayurvedic remedy
approved red-flag threshold
approved mental-health threshold
approved disease model
```

Synthetic technical values are fine when clearly marked synthetic.

---

# 21. Docker

Read P1 acceptance criteria.

If P1-A explicitly requires backend containerization:

implement a minimal backend Dockerfile consistent with engineering standards.

Requirements:

```text
Python 3.12-compatible
non-root where practical
no secrets
reproducible dependency installation
small/appropriate base image
health behavior documented
```

Do not add PostgreSQL or the full Compose ecosystem simply because Docker is used.

If P1-A does not require Docker, defer it to its designated subphase.

---

# 22. Database Boundary

P1-A must not implement the database schema.

Do not create:

```text
SQLAlchemy clinical models
Alembic migrations
repository implementations
database engine/session management
pgvector tables
```

unless the canonical implementation plan explicitly assigns some minimal DB bootstrap to P1-A.

If canonical docs assign persistence to P2, keep it in P2.

---

# 23. Shared Kernel Boundary

Do not prematurely implement broad shared abstractions.

Only create a shared utility/type if:

1. current foundation needs it;
2. more than one current component needs it;
3. its semantics are stable.

Avoid:

```text
shared/utils/helpers.py
```

becoming a dumping ground.

---

# 24. Module Directories

Existing `.gitkeep` module directories are intentional placeholders.

Do not replace all of them with empty Python packages during P1-A.

Create package files only where runtime/import behavior currently requires them.

Do not imply a module is implemented merely by adding boilerplate files.

---

# 25. Frontend

P1-A is backend foundation only.

Do not scaffold the three Next.js applications unless the canonical P1-A acceptance criteria explicitly include frontend tooling.

If frontend setup belongs to a later P1 subunit, leave:

```text
apps/patient-web
apps/clinician-web
apps/admin-web
```

untouched except for documentation required by this phase.

---

# 26. CI

Do not implement the full CI pipeline unless P1-A explicitly owns it.

If CI belongs to a later P1 subunit:

- keep `.github/workflows/.gitkeep`;
- ensure commands are reproducible locally;
- document commands that later CI will execute.

---

# 27. README / Developer Instructions

Update documentation only enough to make the P1-A backend reproducible.

Document:

```text
required Python version
dependency installation
environment setup
run API
run tests
run lint
run formatting check
run typecheck
```

Do not write deployment instructions for infrastructure that does not exist.

---

# 28. Progress Tracker

Only after all implemented P1-A checks pass:

update:

```text
docs/implementation/38_PROGRESS_TRACKER.md
```

Record:

```text
P1-A status
date
implemented scope
verification commands
remaining P1 subunits
blockers/open decisions
```

Do **not** mark:

```text
P1 COMPLETE
```

unless every P1 acceptance criterion is actually complete.

Do not mark P2+ work complete.

---

# 29. Decision Log

Update:

```text
docs/implementation/37_DECISION_LOG.md
```

only if implementation requires a real architectural/tooling decision not already covered by the accepted architecture.

Do not create an ADR for trivial formatting choices.

Do not silently overturn R3.

---

# 30. Source Material

Do not modify:

```text
docs/source_material/**
```

Normal P1-A coding does not need to reread all source PDFs.

If a canonical specification appears materially inconsistent with a primary source:

report:

```text
SPECIFICATION DRIFT DETECTED
```

with:

```text
source document
relevant requirement
canonical spec
conflict/omission
recommended reconciliation
```

Do not change clinical/product behavior during P1-A to resolve such drift.

---

# 31. Verification Commands

Use commands compatible with the chosen project tooling.

At minimum run the equivalents of:

```text
dependency lock/install validation
ruff check
ruff format --check
static type check
pytest
Python import/compile smoke
git diff --check
git status --short
```

If Docker is introduced in this subphase, additionally verify the image builds and starts.

Do not claim a command passed if it was not executed.

Record exact command + result.

---

# 32. Diff Audit

After implementation:

1. inspect every changed file;
2. confirm no scope creep;
3. confirm no secrets;
4. confirm no clinical policy was invented;
5. confirm no future infrastructure was added;
6. confirm no generated caches/venvs/build artifacts are committed;
7. confirm no upstream repository was vendored;
8. run `git diff --check`;
9. inspect final `git status --short`.

---

# 33. Final Report Format

Return exactly these sections.

## STATUS

One of:

```text
COMPLETE
PARTIAL
BLOCKED
FAILED
```

## SCOPE IMPLEMENTED

Concise description of P1-A work actually completed.

## PREFLIGHT

Report:

```text
branch
initial working-tree state
required docs present/missing
R3/source-material governance check
```

## FILES CHANGED

List all changed/created/deleted files.

## DEPENDENCIES ADDED

For each dependency:

```text
name
version/range
R3 classification
reason
runtime profile
license if known from project metadata/research docs
```

If none:

```text
None
```

## ACCEPTANCE CRITERIA

Map each canonical P1-A criterion to:

```text
PASS
PARTIAL
BLOCKED
NOT IN P1-A
```

Do not invent criterion IDs.

## VERIFICATION

For every command:

```text
command
result
```

Include failures.

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
No clinical policy invented: YES/NO
No future infrastructure pulled forward: YES/NO
No third-party repo vendored: YES/NO
Research dependencies absent from core runtime: YES/NO
Source material unchanged: YES/NO
```

## DEVIATIONS

List any deviation from this prompt or canonical plan and why.

## BLOCKERS / OPEN DECISIONS

List only unresolved issues that genuinely remain.

Do not invent a decision just to fill this section.

## PROGRESS TRACKER

State exactly what you changed in `38_PROGRESS_TRACKER.md`.

## RECOMMENDED NEXT UNIT

Recommend the next smallest implementation unit based on the canonical implementation plan.

Do not implement it yet.

---

# 34. Success Definition

P1-A is successful when:

- the repository still reflects the documented modular architecture;
- the FastAPI backend has a reproducible engineering foundation;
- the application boots;
- canonical health endpoints work;
- configuration is typed and safe;
- lint/format/type/tests pass;
- no clinical/business logic has been invented;
- no database/domain work has been prematurely implemented;
- no heavy external infrastructure has been introduced;
- R3 dependency boundaries remain intact;
- a later P1/P2 implementation can build on the foundation without undoing it.

Implement only that.
