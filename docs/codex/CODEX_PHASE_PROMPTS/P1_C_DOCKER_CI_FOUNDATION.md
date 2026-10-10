# Codex Phase Prompt — P1-C Docker, Local PostgreSQL, CI & Quality Gates

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P1-C`
**Phase unit:** P1-C — Docker / local PostgreSQL / CI / quality-gate foundation
**Base branch:** `main`
**Expected base commit:** `d79a9a9dd9a82764380c9706801d8a3f59de03ea`
**Implementation branch:** `phase/p1-c-docker-ci-foundation`
**Scope:** P1 infrastructure/tooling completion only
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

# 0. Mission

Complete the remaining P1 Repository + Tooling Foundation work without pulling P2/P3 or later product infrastructure forward.

P1-A established the FastAPI backend foundation.

P1-B established:

```text
three Next.js App Router applications
strict TypeScript
Tailwind
shared UI
Vitest / Testing Library
Playwright test skeleton
pnpm workspace
```

P1-C must now establish the minimum reproducible local and CI environment needed to close P1:

```text
Docker backend foundation
Docker Compose local PostgreSQL
canonical Node runtime alignment
cross-platform quality-gate entry points
GitHub Actions baseline CI
real Playwright Chromium execution
Gitleaks secret scanning
Trivy source/image scanning
P1 final acceptance audit
```

Do not implement application persistence yet.

Do not create database tables.

Do not add SQLAlchemy or Alembic unless the canonical documents explicitly override the current phase ordering.

Do not add Redis/Valkey, object-storage services, Keycloak, HAPI FHIR, MLflow, OpenBao, NATS, Kafka, RabbitMQ, OCR, speech, LLM, QML, or other future infrastructure.

---

# 1. Repository State Verification

Before editing, run from repository root:

```text
git rev-parse --show-toplevel
git branch --show-current
git status --short
git rev-parse HEAD
git remote -v
git log --oneline --decorate -5
```

Required starting state:

```text
branch: main
HEAD: d79a9a9dd9a82764380c9706801d8a3f59de03ea
working tree: clean
```

Verify that this commit is the merged P1-B baseline and contains:

```text
backend/pyproject.toml
backend/uv.lock

package.json
pnpm-lock.yaml
pnpm-workspace.yaml

apps/patient-web/
apps/clinician-web/
apps/admin-web/
packages/ui/

tests/e2e/playwright.config.ts

docs/codex/CODEX_PHASE_PROMPTS/P1_A_REPOSITORY_BACKEND_TOOLING.md
docs/codex/CODEX_PHASE_PROMPTS/P1_B_FRONTEND_WORKSPACES.md
```

If `main` has advanced only through user-approved documentation or merge metadata, inspect the change and use the actual clean main head, but report the deviation.

If unrelated code changes are present:

```text
STATUS: BLOCKED
```

Do not overwrite them.

---

# 2. Create the Phase Branch

After preflight succeeds:

```text
git switch -c phase/p1-c-docker-ci-foundation
```

If the branch already exists:

1. inspect its head;
2. compare it to `main`;
3. do not reset/delete user work;
4. continue only if it is clearly the intended P1-C branch.

Never implement directly on `main`.

---

# 3. Required Reading

Read before implementation:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
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

docs/research/infrastructure/INFRA_SECURITY_TECH_EVALUATION.md

docs/codex/CODEX_PHASE_PROMPTS/P1_A_REPOSITORY_BACKEND_TOOLING.md
docs/codex/CODEX_PHASE_PROMPTS/P1_B_FRONTEND_WORKSPACES.md
```

If a lower-priority P1 document suggests optional Redis/object-store placeholders, R3 governs the implementation decision:

```text
no default Valkey/Redis in early local development
no SeaweedFS in first default Compose
no MinIO as new default
```

P1-C therefore uses PostgreSQL only as persistent infrastructure.

---

# 4. Canonical P1 Acceptance Targets

P1-C directly closes:

```text
AC-P1-010 — Local PostgreSQL starts through documented development environment
AC-P1-011 — CI workflow executes baseline quality gates
```

P1-C must also re-evaluate **all** P1 criteria before marking overall P1 complete:

```text
AC-P1-001
AC-P1-002
AC-P1-003
AC-P1-004
AC-P1-005
AC-P1-006
AC-P1-007
AC-P1-008
AC-P1-009
AC-P1-010
AC-P1-011
AC-P1-012
```

And applicable global criteria:

```text
AC-G-001 through AC-G-014
```

Use the exact vocabulary from `35_PHASE_ACCEPTANCE_CRITERIA.md`:

```text
PASS
FAIL
BLOCKED
NOT APPLICABLE
NOT VERIFIED
```

Do not invent criterion IDs.

---

# 5. Important Phase Boundary

P1-C provides infrastructure **availability**, not persistence implementation.

Allowed:

```text
PostgreSQL container
PostgreSQL health check
psql/pg_isready connectivity verification
synthetic database credentials for local development
backend container
backend liveness test
CI service container
Docker build
quality scripts
GitHub Actions
secret/dependency/image scanning
```

Forbidden:

```text
SQLAlchemy
Alembic
PostgreSQL Python driver
database session code
ORM models
tables
migrations
repositories
pgvector
outbox tables
job tables
application database readiness dependency
```

Those belong to later phases.

Do not modify `/health/ready` to require PostgreSQL yet because the application does not consume PostgreSQL in P1.

---

# 6. Local Infrastructure Principle

Default local infrastructure must remain deliberately small.

Expected local infrastructure:

```text
PostgreSQL
backend container (for Docker smoke/testing)
```

Frontend applications may continue to run through pnpm during development.

Do not add frontend production Dockerfiles unless a canonical P1 requirement clearly requires them.

Do not add:

```text
Redis
Valkey
NATS
Kafka
RabbitMQ
SeaweedFS
MinIO
OpenBao
Keycloak
HAPI FHIR
Prometheus
Grafana
OTel Collector
MLflow
vLLM
Kubernetes
```

---

# 7. Canonical Node Runtime

P1-B verified the frontend using:

```text
Node.js 24.18.1
```

but the root project currently permits a broader `>=20.9.0` range and uses Node 26 type declarations.

P1-C must define one canonical frontend runtime line for:

```text
local development guidance
CI
future containers
TypeScript Node types
```

Use **Node.js 24 LTS** for P1-C unless authoritative project documents or the installed stable tooling reveal a concrete incompatibility.

Prefer an exact patch version for the repository runtime marker.

Expected:

```text
24.18.1
```

if still available/valid in the environment.

Align:

```text
package.json engines
Node version marker (.node-version or equivalent)
@types/node major
GitHub Actions setup-node version
documentation
```

Do not move to Node 26 merely because type definitions exist.

Do not downgrade Next.js/React unless compatibility testing requires it.

If a different Node 24 patch is selected:

1. explain why;
2. use the same selected patch consistently;
3. record it in the final report.

---

# 8. Frontend Package Manager

Preserve ADR-042:

```text
pnpm 9.15.4
```

Do not add npm/Yarn/Bun lockfiles.

Use Corepack or an equivalent reproducible mechanism in CI.

Do not silently change pnpm major version.

---

# 9. Backend Python Runtime

Preserve:

```text
Python >= 3.12
uv
```

For the backend container, use a supported Python 3.12 official image.

Prefer:

```text
python:3.12-slim
```

with an exact patch tag and/or digest when practical.

Do not switch the project to Python 3.13+ in P1-C.

Do not add a second dependency manager.

---

# 10. Backend Dockerfile

Create the backend Docker build in the existing infrastructure area.

Preferred path:

```text
infra/docker/backend.Dockerfile
```

unless `03_REPOSITORY_STRUCTURE.md` requires another existing location.

Requirements:

```text
Python 3.12
uv-based locked install
backend/uv.lock respected
production dependencies only
non-root runtime user
no development/test dependencies in runtime image
no source-material copying
no secrets baked into image
no .env copied
predictable WORKDIR
Uvicorn entrypoint
bind 0.0.0.0
container port documented
```

Use BuildKit/cache patterns only if they remain understandable and portable.

The image must successfully start:

```text
app.main:app
```

and serve:

```text
GET /health/live
GET /health/ready
```

Do not install curl solely for the health check if Python can perform a lightweight check without expanding the image.

---

# 11. Docker Ignore

Create a project-appropriate `.dockerignore`.

It should prevent unnecessary or sensitive material from entering Docker build contexts.

Include as relevant:

```text
.git
.github
.env
.env.*
!.env.example only if genuinely required
node_modules
.next
coverage
playwright-report
test-results
.venv
__pycache__
pytest/mypy/ruff caches
mlruns
wandb
data/private
data/local
artifacts
models weight files
docs/source_material if backend runtime does not need it
temporary upstream repositories
```

Do not accidentally exclude files required for the selected build context.

---

# 12. Local PostgreSQL Version

PostgreSQL is the canonical transactional source of truth, but P1-C is not implementing persistence.

Use a stable supported PostgreSQL major for local/CI foundation.

Prefer:

```text
PostgreSQL 16
```

for the initial baseline unless the canonical docs already select another supported major.

Use an official PostgreSQL image.

Prefer an exact stable image tag/digest rather than an unqualified mutable `latest`.

Do not enable pgvector in P1-C.

Do not install extensions.

Record the selected image/tag/digest in documentation.

---

# 13. Docker Compose Location

Use the existing deployment structure.

Preferred:

```text
deployments/local/compose.yaml
deployments/local/.env.example
deployments/local/README.md
```

or the closest canonical equivalent.

Do not add a new top-level directory.

Compose should remain understandable and minimal.

---

# 14. PostgreSQL Compose Service

The PostgreSQL service should provide:

```text
official PostgreSQL image
named volume
explicit database name
explicit non-production development user
password supplied through environment
healthcheck using pg_isready
restart behavior appropriate for local development
port mapping configurable or documented
```

Use a clear local database name, for example:

```text
swasthyasetu
```

No production credentials.

Do not commit a real password.

A committed `.env.example` may show a clearly fake local-only value.

The real `.env` must remain Git-ignored.

Avoid `trust` authentication.

---

# 15. Backend Compose Service

It is acceptable and preferred for the local Compose file to include a backend service using the P1-C Dockerfile.

The backend service must:

```text
start after/alongside local infrastructure cleanly
serve port 8000 or documented configurable port
use no production secrets
not pretend to use PostgreSQL before P3
not require PostgreSQL for /health/ready in P1
```

If `depends_on` PostgreSQL is added for convenience, do not interpret it as a database integration.

The backend should still be capable of starting independently where appropriate.

---

# 16. Compose Profiles / Minimal Default

Do not turn `docker compose up` into a large platform.

A good result is:

```text
postgres
backend
```

with no other services.

If profiles improve developer ergonomics without needless complexity, they may be used.

Do not add placeholder services for future systems.

---

# 17. Local PostgreSQL Verification

P1-C must prove the database is actually available.

Required local verification:

```text
docker compose config
docker compose pull postgres
docker compose up -d postgres
docker compose ps
PostgreSQL health becomes healthy
pg_isready succeeds
psql SELECT 1 succeeds
docker compose down -v
```

Use the project's actual Compose path/options.

Do not claim AC-P1-010 passes based only on YAML syntax.

The service must actually start.

---

# 18. Backend Docker Verification

Required:

```text
docker build ...
container starts
GET /health/live -> expected 200 response
GET /health/ready -> expected 200 response
container exits/cleans up successfully
```

Also run:

```text
docker image inspect
```

or equivalent to verify:

```text
non-root User
expected exposed/listening port
```

Do not expose secrets in image history.

Where practical inspect:

```text
docker history --no-trunc
```

for accidental secrets/large artifacts.

---

# 19. Root Quality-Gate Interface

Create a simple, cross-platform way to execute baseline project checks.

Avoid a Bash-only workflow because the primary developer environment includes Windows.

Preferred options:

```text
Python script under scripts/
plus existing pnpm/uv commands
```

Example conceptual interface:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
python scripts/quality_gate.py all
```

The exact interface may differ.

Requirements:

```text
cross-platform
fails fast or clearly aggregates failures
prints commands being executed
propagates non-zero exit codes
does not hide output
does not install dependencies implicitly unless documented
```

Do not add a heavy task-runner dependency merely for orchestration.

---

# 20. Backend Quality Gate

The backend quality gate must cover at least:

```text
uv lock --check
uv sync --locked --dev or equivalent install verification
ruff check .
ruff format --check .
mypy
pytest
python compile/import smoke
```

Use existing P1-A commands.

Do not alter backend semantics merely to satisfy the script.

---

# 21. Frontend Quality Gate

The frontend quality gate must cover at least:

```text
pnpm install --frozen-lockfile or install validation
frontend:format-check
frontend:lint
frontend:typecheck
frontend:test
frontend:build
e2e:list
```

Full browser E2E execution may be a separate CI job because it installs Chromium.

Do not run `pnpm install` redundantly inside every workspace.

---

# 22. Playwright — Real Browser Execution

P1-B only verified discovery.

P1-C must execute all three smoke tests with Chromium in a browser-capable environment.

In CI:

```text
install Playwright Chromium with required OS dependencies
run pnpm e2e:test
```

The existing Playwright configuration should start:

```text
patient-web
clinician-web
admin-web
```

on their documented local ports.

All three smoke tests must actually navigate and pass.

If local browser execution is possible, run it locally too.

At minimum, actual GitHub Actions execution must verify it before P1 is marked complete.

---

# 23. GitHub Actions Workflow

Create baseline CI under:

```text
.github/workflows/
```

Use one understandable workflow, or a very small number of clearly separated workflows.

Preferred name:

```text
ci.yml
```

Trigger at least on:

```text
pull_request
push to main
```

It may also run on phase branches.

Do not add deployment workflows in P1-C.

---

# 24. CI Concurrency

Configure CI concurrency to avoid wasting runs on superseded commits where appropriate.

Example concept:

```text
group by workflow + ref
cancel in progress for non-main updates
```

Do not cancel important main verification incorrectly.

---

# 25. CI Backend Job

The backend CI job should:

```text
checkout
setup Python 3.12 exact/minor baseline
setup uv
sync from lock
run Ruff
run format check
run mypy
run pytest
run compile/import smoke
```

Do not use an unlocked pip install.

Use repository lock state.

---

# 26. CI Frontend Job

The frontend CI job should:

```text
checkout
setup canonical Node 24 runtime
enable pinned pnpm 9.15.4
pnpm install --frozen-lockfile
format check
lint
typecheck
unit tests
build all three applications
```

Use package-manager caching only if it is simple and safe.

Do not cache `.next` in a way that can hide broken builds.

---

# 27. CI PostgreSQL / Compose Job

CI must verify the local PostgreSQL development environment.

Acceptable approaches:

```text
Docker Compose invocation on GitHub-hosted Linux runner
```

or a CI PostgreSQL service plus a separate Compose validation.

Because AC-P1-010 refers to the documented local development environment, prefer verifying the actual Compose file.

Required:

```text
docker compose config
docker compose up -d postgres
wait until healthy
pg_isready
SELECT 1
docker compose down -v
```

Cleanup should run even after verification failure where practical.

---

# 28. CI Backend Docker Job

Build the backend Docker image.

Verify:

```text
image builds
container starts
/health/live works
/health/ready works
```

This can be combined with the Docker/PostgreSQL job if that keeps CI understandable.

Do not push an image to a registry in P1-C.

---

# 29. CI Playwright Job

Use the same canonical Node/pnpm setup.

Install Chromium:

```text
pnpm exec playwright install --with-deps chromium
```

or the supported equivalent for the pinned Playwright version.

Run:

```text
pnpm e2e:test
```

All 3 applications must be tested.

Upload Playwright artifacts only on failure if useful.

Do not upload screenshots/traces containing sensitive patient data in later phases without privacy policy; current P1-B pages are synthetic foundation pages.

---

# 30. Gitleaks

R3 adopts Gitleaks for CI secret scanning.

Add Gitleaks in CI as `OPS_ONLY`.

Requirements:

```text
scan repository history/current change as supported
fail on detected committed secrets
do not add allowlist patterns that broadly suppress findings
do not commit a real secret to test it
```

If a configuration file is necessary, keep it minimal.

Use a pinned/traceable Gitleaks version or action.

Record the exact version/reference in final report.

---

# 31. Trivy

R3 adopts Trivy for CI security scanning.

Use it in P1-C as `OPS_ONLY`.

At minimum perform:

```text
filesystem/dependency scan
backend Docker image scan
```

A practical initial failure policy is:

```text
HIGH/CRITICAL vulnerabilities
```

with a clear documented policy.

Do not silently ignore all vulnerabilities.

If an upstream vulnerability causes a legitimate false-positive/accepted-risk blocker:

1. report it;
2. do not create a broad ignore;
3. leave P1-C `PARTIAL` or `BLOCKED` if the mandatory gate cannot pass;
4. recommend a narrow reviewed resolution.

Do not add Trivy to Python/Node application runtime dependencies.

---

# 32. GitHub Action Supply-Chain Hygiene

Prefer official or well-established actions.

Pin third-party actions to immutable commit SHAs where practical, with a comment indicating the corresponding release/tag.

Do not use arbitrary unreviewed GitHub Actions.

At minimum review the actions selected for:

```text
checkout
Python setup / uv setup
Node setup
Gitleaks
Trivy
artifact upload if used
```

If an action must remain on a major tag due maintainability constraints, document the choice.

---

# 33. CI Permissions

Use least-privilege workflow permissions.

For a validation-only CI workflow, expected baseline:

```text
contents: read
```

Add other permissions only when required.

Do not grant:

```text
contents: write
packages: write
id-token: write
```

without a real requirement.

---

# 34. CI Environment / Secrets

P1-C CI should not require production secrets.

Use synthetic local PostgreSQL credentials through job environment variables.

Do not create repository secrets merely for local CI database startup.

No:

```text
LLM keys
ABDM credentials
cloud credentials
auth secrets
provider credentials
```

---

# 35. Node / Type Definition Alignment

Fix the P1-B runtime/type mismatch.

Expected changes:

```text
Node runtime pinned to Node 24 line
@types/node aligned to Node 24
package.json engines narrowed appropriately
runtime version file added
CI uses same runtime
docs use same runtime
```

After alignment rerun:

```text
pnpm install --frozen-lockfile
frontend typecheck
unit tests
all builds
Playwright
```

Do not change app behavior.

---

# 36. No Application Analytics

Do not add:

```text
Sentry
Datadog
Google Analytics
PostHog
Mixpanel
Hotjar
session replay
```

P1-C is operational CI/container tooling only.

---

# 37. No OpenTelemetry Deployment Yet

OpenTelemetry is the architectural observability contract.

Do not deploy:

```text
OTel Collector
Prometheus
Grafana
Loki
Tempo
Jaeger
```

during P1-C.

Those activate in later observability/deployment phases.

---

# 38. No Object Storage Yet

Do not add SeaweedFS.

Do not add MinIO.

Do not add S3 emulator placeholders.

The current product has no document persistence implementation yet.

---

# 39. No Cache / Broker Yet

Do not add:

```text
Redis
Valkey
NATS
Kafka
RabbitMQ
```

even though older P1 wording mentioned an optional placeholder.

R3 explicitly defers these without a real use case.

---

# 40. No Durable Job Backend Yet

Do not add:

```text
Procrastinate
Celery
Dramatiq
Taskiq
```

P1-C does not implement background work.

---

# 41. No SQLAlchemy/Alembic Yet

P1-C creates PostgreSQL availability only.

Do not prematurely implement P3 persistence.

No:

```text
SQLAlchemy
Alembic
asyncpg
psycopg
database.py
session factory
Base ORM
migration folder
```

unless a canonical phase specification has materially changed since this prompt.

---

# 42. Environment Files

Keep environment examples safe.

Expected:

```text
deployments/local/.env.example
```

or equivalent.

Do not commit:

```text
deployments/local/.env
backend/.env
```

Ensure root `.gitignore` covers real environment files.

If the general `.env.*` ignore pattern accidentally hides `.env.example`, preserve the explicit allow rule.

---

# 43. Local Documentation

Document local container use.

Expected content:

```text
prerequisites
copy local env example
start PostgreSQL
verify PostgreSQL
start backend container
health URLs
stop environment
remove local volume intentionally
common Windows PowerShell commands
```

Do not include production deployment guidance.

---

# 44. Root README

Update the root README only as needed.

After successful P1-C and verified CI:

```text
P1 Repository + Tooling Foundation COMPLETE
P2 is next
```

If remote CI is not yet verified:

```text
P1-C implementation complete locally; remote CI verification pending
P1 remains PARTIAL
```

Do not claim completion early.

---

# 45. Repository Tree

Update:

```text
REPOSITORY_TREE.txt
```

to reflect real files.

Do not list ignored build outputs.

---

# 46. Decision Log

Create a new ADR only for a durable new project decision.

Likely decisions worth recording if not already covered:

```text
ADR-043 — canonical Node 24 runtime baseline
ADR-044 — PostgreSQL 16 local/CI baseline
```

However, avoid unnecessary ADR fragmentation.

A single coherent infrastructure-runtime baseline ADR may be acceptable if it clearly records:

```text
Node runtime
PostgreSQL major
Docker/Compose local baseline
```

Do not alter historical ADRs.

Do not record implementation details as architecture decisions if they are easily reversible.

---

# 47. Progress Tracker — Before Remote CI

Do not mark P1/P1-C `COMPLETE` merely because workflow YAML exists.

The workflow must actually run.

If implementation and all local verification pass, but remote GitHub Actions has not been observed:

```text
P1-C: PARTIAL — REMOTE CI VERIFICATION PENDING
P1: PARTIAL
```

Record:

```text
branch
base commit
implementation commit
local verification
remote CI pending
```

---

# 48. Progress Tracker — After Remote CI

Only if the P1-C branch GitHub Actions run is actually green for all mandatory jobs may you record:

```text
P1-C: COMPLETE
P1: COMPLETE
```

Then record all 12 P1 criteria as evaluated.

If tooling cannot query the CI result from the environment, leave status `PARTIAL` and report exactly what remains.

Do not fabricate a passing CI run.

---

# 49. GitHub CLI / Remote CI Verification

After pushing the branch, if authenticated GitHub CLI is available:

```text
gh --version
gh run list --branch phase/p1-c-docker-ci-foundation
gh run watch <run-id> --exit-status
```

Equivalent safe commands are acceptable.

If `gh` is unavailable or unauthenticated:

```text
REMOTE CI: NOT VERIFIED
```

Do not block implementation work, but do not mark final P1 complete.

The user/ChatGPT reviewer will verify the actual GitHub run.

---

# 50. Local Verification — Existing Backend

From `backend/` run at least:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
```

Run the existing import smoke.

All must remain green.

---

# 51. Local Verification — Existing Frontend

From repository root:

```text
pnpm install --frozen-lockfile
pnpm frontend:format-check
pnpm frontend:lint
pnpm frontend:typecheck
pnpm frontend:test
pnpm frontend:build
pnpm e2e:list
```

Then install Chromium if not already installed and run:

```text
pnpm e2e:test
```

If full local Playwright cannot run because the OS/browser dependency environment is unavailable, report it honestly and rely on the browser-enabled CI job before completion.

---

# 52. Local Verification — Docker

Run:

```text
docker version
docker compose version
docker compose -f <compose-file> config
docker compose -f <compose-file> up -d postgres
docker compose -f <compose-file> ps
```

Wait for PostgreSQL health.

Then verify:

```text
pg_isready
SELECT 1
```

Build the backend image and start it.

Probe:

```text
/health/live
/health/ready
```

Then cleanly stop/remove test containers.

Use `down -v` only when it is safe for this new synthetic P1 environment.

Do not delete unrelated Docker volumes.

---

# 53. Docker Resource Naming

Use project-specific names/labels so local development does not collide with unrelated containers.

Avoid broad cleanup commands such as:

```text
docker system prune -a
docker volume prune
```

Never delete unrelated user Docker resources.

---

# 54. Docker Network Exposure

PostgreSQL is local development infrastructure.

Bind only as broadly as local tooling requires.

Prefer loopback/local development exposure where Compose allows it.

Do not expose PostgreSQL as a public service.

Backend development port should likewise be documented as local.

---

# 55. PostgreSQL Data Persistence

Use a named volume.

Document how to reset it intentionally.

Do not place PostgreSQL data directories inside the Git repository.

Do not commit database data.

---

# 56. CI Quality-Gate Independence

Jobs should be separated enough that failures identify the concern.

A useful baseline:

```text
backend
frontend
docker-postgres
playwright
security
```

Exact job structure may differ.

Avoid one giant 30-minute job when independent jobs can run in parallel.

Do not create dozens of micro-jobs.

---

# 57. CI Timeouts

Set reasonable job timeouts to avoid runaway credit/minute usage.

Do not use extremely large timeouts.

Playwright/browser job may need longer than lint.

Docker/PostgreSQL health wait must be bounded.

---

# 58. CI Failure Visibility

Do not swallow failures with:

```text
|| true
continue-on-error: true
```

for mandatory quality gates.

Optional diagnostic upload steps may use failure conditions appropriately.

Security gates intended as mandatory must fail the workflow when policy requires.

---

# 59. CI Generated Artifacts

Do not commit generated CI outputs.

Playwright reports/traces should remain ignored.

If uploading artifacts on failure:

```text
short retention
no secrets
no patient/clinical data
```

P1 data is synthetic.

---

# 60. CI Dependency Caches

Caching is optional.

If implemented:

```text
cache package-manager downloads, not arbitrary generated source
key by lockfile
avoid secret-containing paths
```

Correctness must not depend on cache hits.

---

# 61. Security Scan Scope

P1-C scans the current codebase and backend image.

Do not attempt to solve future clinical security architecture.

Do not add runtime WAF, service mesh, SIEM, IDS, or secret manager.

---

# 62. P1 Final Acceptance Audit

Before declaring P1 complete, explicitly evaluate:

## AC-P1-001

Repository structure matches canonical spec.

## AC-P1-002

Backend installs reproducibly from `uv.lock`.

## AC-P1-003

FastAPI starts successfully.

## AC-P1-004

All three frontend applications build successfully.

## AC-P1-005

Strict TypeScript enabled.

## AC-P1-006

Backend lint configured and passing.

## AC-P1-007

Backend type checking configured and passing.

## AC-P1-008

Pytest configured and passing.

## AC-P1-009

Frontend lint/type checks passing.

## AC-P1-010

Documented local PostgreSQL Compose service actually starts and accepts a query.

## AC-P1-011

GitHub Actions baseline workflow actually executes and passes mandatory gates.

## AC-P1-012

No business/clinical feature implemented prematurely.

Every mandatory item must be `PASS`.

---

# 63. P1-C Tests

P1-C-specific evidence should include:

```text
Compose config parses
Postgres health check
Postgres SELECT 1
backend Docker image build
backend container health request
Node runtime/version assertion
CI workflow syntax/structure validation where practical
Gitleaks local/CI invocation
Trivy local/CI invocation where practical
Playwright actual browser tests
quality-gate script behavior
```

Do not invent clinical tests.

---

# 64. Workflow Syntax Validation

GitHub Actions itself is the final workflow validator.

If a local YAML/workflow linter is already available without adding a large dependency, it may be used.

Do not add a heavy application dependency solely to lint YAML.

Do not claim workflow validity until GitHub accepts/runs it.

---

# 65. Secret Scanning Before Push

Before committing:

```text
scan staged/current repository for obvious credentials
run Gitleaks locally if installed/available
```

If local Gitleaks cannot run, CI must run it.

Never paste detected secret values into the final report.

Report only file/path/type and remediation status.

---

# 66. Image Scanning Before Push

If Docker and Trivy are locally available:

```text
scan built backend image
```

If not, ensure the CI security job does it.

Do not mark the security scan PASS if it was not executed.

---

# 67. P1-C Prompt Traceability

Retain this prompt at:

```text
docs/codex/CODEX_PHASE_PROMPTS/P1_C_DOCKER_CI_FOUNDATION.md
```

Do not delete P1-A or P1-B prompts.

---

# 68. Documentation Updates

Expected P1-C documentation changes may include:

```text
README.md
REPOSITORY_TREE.txt
deployments/local/README.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
```

Only modify architecture/spec documents if implementation reveals an actual specification conflict.

Do not casually rewrite R3 decisions.

---

# 69. No Source-Material Changes

Do not modify:

```text
docs/source_material/**
```

Hash/check them if your normal governance workflow requires it.

If changed accidentally, restore them before completion.

---

# 70. Dependency Reporting

Any newly added tool/dependency must be classified.

Likely P1-C categories:

```text
Docker / Compose    developer/ops tooling
Gitleaks            OPS_ONLY
Trivy               OPS_ONLY
GitHub Actions      CI/ops
```

Do not add Gitleaks/Trivy to Python or Node runtime manifests unless a documented reason requires it.

For action-based tools, report:

```text
action/repository
version/tag/commit
purpose
permission requirements
```

---

# 71. Git Diff Audit

Before commit:

```text
git diff --check
git diff --stat
git status --short
```

Inspect every changed file.

Explicitly verify:

```text
no SQLAlchemy/Alembic
no database schema
no Redis/Valkey
no object store
no auth
no AI
no product/clinical feature
no production secret
no generated node_modules/.next/Playwright reports
no Docker data directory
no unrelated dependency upgrade
```

---

# 72. Commit Policy

Once the coherent P1-C implementation and local mandatory checks pass, commit on:

```text
phase/p1-c-docker-ci-foundation
```

Suggested message:

```text
feat: establish P1-C Docker and CI foundation
```

If tracker must remain `PARTIAL` pending remote CI, that is acceptable.

Push the branch.

Do not merge.

Do not force-push.

---

# 73. Remote CI Closure Commit

If remote CI is verified green after the implementation commit and the progress tracker was left partial:

1. update `38_PROGRESS_TRACKER.md`;
2. mark P1-C and P1 `COMPLETE`;
3. record CI run evidence;
4. commit with a focused message such as:

```text
docs: close P1 after successful CI verification
```

5. push the same feature branch.

Do not amend/rewrite the implementation commit solely to add closure metadata.

---

# 74. If Remote CI Fails

Do not merge.

Inspect the failure.

Fix only the actual P1-C issue.

Re-run local relevant checks.

Commit the fix.

Push.

Wait for CI again.

Do not weaken tests/security gates simply to obtain green status.

---

# 75. Final Report Format

Return exactly these sections.

## STATUS

One of:

```text
COMPLETE
PARTIAL
BLOCKED
FAILED
```

`COMPLETE` requires remote mandatory CI verification.

## BRANCH / GIT

Report:

```text
base branch
base commit
implementation branch
implementation commit
closure commit if any
remote branch SHA
main SHA
working-tree state
```

## SCOPE IMPLEMENTED

Describe only P1-C work.

## FILES CHANGED

Group by:

```text
Docker
local deployment
quality scripts
GitHub Actions
frontend runtime alignment
documentation
```

## RUNTIME / INFRASTRUCTURE BASELINE

Report exact:

```text
Python image/tag/digest
Node version
pnpm version
PostgreSQL image/tag/digest
Docker version
Docker Compose version
Playwright version/browser
```

## DEPENDENCIES / OPS TOOLS ADDED

For each:

```text
name
version/reference
R3 classification
reason
license
runtime impact
```

## LOCAL POSTGRESQL VERIFICATION

Report:

```text
compose config
container status
health status
pg_isready
SELECT 1
cleanup
```

## DOCKER VERIFICATION

Report:

```text
backend image build
runtime user
container startup
/health/live
/health/ready
image scan
cleanup
```

## QUALITY-GATE VERIFICATION

Report every backend/frontend command and result.

## PLAYWRIGHT VERIFICATION

Report:

```text
browser installation
3 smoke tests discovered
3 smoke tests executed
pass/fail
```

## SECURITY VERIFICATION

Report:

```text
Gitleaks
Trivy filesystem/dependency
Trivy image
findings
```

Do not reveal secrets.

## CI VERIFICATION

Report:

```text
workflow file
GitHub run ID/URL if available
jobs
result per job
overall conclusion
```

If not remotely verified, explicitly:

```text
REMOTE CI: NOT VERIFIED
```

and status cannot be COMPLETE.

## P1 FINAL ACCEPTANCE

Map all:

```text
AC-P1-001
...
AC-P1-012
```

to the canonical status vocabulary.

## GLOBAL ACCEPTANCE

Report relevant AC-G criteria.

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
No persistence implementation pulled forward: YES/NO
No SQLAlchemy/Alembic added: YES/NO
No Redis/Valkey added: YES/NO
No object store added: YES/NO
No authentication added: YES/NO
No AI/ML/QML added: YES/NO
No clinical/business feature invented: YES/NO
No real secret committed: YES/NO
Source material unchanged: YES/NO
P1-A backend behavior preserved: YES/NO
P1-B frontend behavior preserved: YES/NO
```

## DEVIATIONS

List every deviation and reason.

## BLOCKERS / OPEN DECISIONS

Only genuine remaining issues.

## PROGRESS TRACKER

State exactly:

```text
P1-C status
overall P1 status
CI evidence status
next macro phase
```

## RECOMMENDED NEXT UNIT

If and only if P1 is complete:

```text
P2-A — Shared Platform Kernel primitives
```

Do not implement it.

If P1 remains partial, recommend the smallest closure/fix unit instead.

---

# 76. Success Definition

P1-C is successful only when:

- backend Docker image builds reproducibly;
- backend container runs as a non-root user;
- backend health endpoints work in container;
- local PostgreSQL Compose service starts;
- PostgreSQL becomes healthy;
- a real SQL `SELECT 1` succeeds;
- no persistence code was prematurely implemented;
- Node runtime is standardized and type definitions aligned;
- backend quality gates pass;
- frontend quality gates pass;
- all three frontend production builds pass;
- all three Playwright smoke tests execute in Chromium;
- Gitleaks runs successfully;
- Trivy filesystem/image scans satisfy the defined gate;
- GitHub Actions executes the baseline quality gates;
- all applicable P1 acceptance criteria pass;
- no future infrastructure or clinical/product feature leaked into P1;
- branch is pushed but not merged.

Only then may:

```text
P1-C = COMPLETE
P1 = COMPLETE
```

Proceed no further.
