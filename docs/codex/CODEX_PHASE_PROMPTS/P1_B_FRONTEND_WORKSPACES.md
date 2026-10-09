# Codex Phase Prompt — P1-B Frontend Workspaces & Shared Frontend Tooling

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P1-B`
**Phase unit:** P1-B — Frontend workspaces + shared tooling
**Base branch:** `main`
**Expected base commit:** `1d299b7f4e7f95d634e5e4745b2d020b69a87b01` or a direct documentation-only descendant
**Implementation branch:** `phase/p1-b-frontend-foundation`
**Scope:** Frontend foundation only
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

# 0. Mission

Implement the P1-B frontend foundation for SwasthyaSetu AI.

Create three independent Next.js web applications in the existing monorepo:

```text
apps/patient-web
apps/clinician-web
apps/admin-web
```

and the minimum shared frontend tooling/design-system foundation required by the canonical P1 plan.

This phase does **not** implement product features, clinical workflows, authentication, API integrations, backend changes, Docker/CI, databases, AI, FHIR, ABDM, or external services.

The result must be a reproducible, strictly typed frontend workspace in which all three applications:

```text
install
lint
typecheck
test
build
```

successfully.

---

# 1. Preflight — Mandatory Before Editing

From the repository root, run:

```text
git rev-parse --show-toplevel
git branch --show-current
git status --short
git rev-parse HEAD
git remote -v
```

The working tree must be clean before phase implementation, except for this phase-prompt file if the user placed it locally immediately before execution.

Verify the base contains:

```text
backend/pyproject.toml
backend/uv.lock
backend/app/main.py
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
docs/codex/CODEX_PHASE_PROMPTS/P1_A_REPOSITORY_BACKEND_TOOLING.md
```

Verify the P1-A baseline commit is in history:

```text
1d299b7f4e7f95d634e5e4745b2d020b69a87b01
```

If the current branch is `main`, the tree is clean, and the baseline commit is in history, create/switch to:

```text
phase/p1-b-frontend-foundation
```

Do **not** implement P1-B directly on `main`.

If the branch already exists locally, inspect it before using it.

If the working tree has unrelated user changes, do not overwrite them. Report and stop if they materially conflict.

---

# 2. Required Reading

Read before editing:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
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

docs/codex/CODEX_PHASE_PROMPTS/P1_A_REPOSITORY_BACKEND_TOOLING.md
```

Relevant canonical P1-B requirements come from the repository documents, not from assumptions in this prompt.

If this prompt conflicts materially with a higher-priority canonical document, follow the canonical document and report the conflict.

---

# 3. P1-B Acceptance Targets

P1-B primarily advances these canonical P1 criteria:

```text
AC-P1-001  Monorepo structure
AC-P1-004  Patient, clinician, and admin frontend projects build successfully
AC-P1-005  Strict TypeScript is enabled
AC-P1-009  Frontend lint/type checks pass
AC-P1-012  No premature business/clinical features
```

Also satisfy applicable global criteria:

```text
scope
architecture
engineering standards
tests
types
lint/format
security
documentation
honest verification
diff audit
```

Do not mark all of P1 complete because P1-C still owns Docker/CI/local PostgreSQL quality-gate work.

---

# 4. Package-Manager Decision

The repository currently has a Python package-manager decision (`uv`) but no accepted frontend workspace manager.

Use **one** frontend package manager for the entire JS/TS workspace.

Preferred for this monorepo:

```text
pnpm
```

because the repository contains three Next.js applications plus shared workspace packages.

Before using it:

```text
node --version
pnpm --version
```

If pnpm is unavailable but Corepack can provide it safely, enable/use Corepack.

Do not install multiple competing frontend package managers.

Do not keep:

```text
package-lock.json
yarn.lock
bun.lock
```

alongside the pnpm lockfile.

Record the package-manager decision as the next ADR only if no existing accepted decision already covers it.

The ADR should record:

```text
package manager
exact version used/pinned
workspace approach
why it fits the monorepo
consequences
```

Do not make unrelated architecture decisions in the same ADR.

---

# 5. Dependency Version Policy

Use **stable, non-canary, non-beta, non-RC** releases compatible with one another at implementation time.

Do not blindly reproduce old version numbers from historical project notes.

Lock the actual resolved dependency graph.

The final report must list the important resolved versions for:

```text
Node.js
pnpm
Next.js
React
React DOM
TypeScript
Tailwind CSS
ESLint
frontend unit-test runner
Playwright
```

Do not perform unrelated dependency experimentation.

---

# 6. Workspace Structure

Use the existing repository structure.

Expected high-level result:

```text
swasthyasetu-ai/
├── package.json
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
│
├── apps/
│   ├── patient-web/
│   ├── clinician-web/
│   └── admin-web/
│
├── packages/
│   ├── contracts/
│   └── ui/
│
└── tests/
    └── e2e/
```

Do not add a new top-level directory.

Do not create empty architecture ceremony that is not needed by P1-B.

---

# 7. Root Frontend Workspace

Create the minimum root workspace configuration needed to operate all three apps consistently.

The root JS package must be:

```text
private
```

Provide scripts or equivalent workspace commands for at least:

```text
frontend:lint
frontend:typecheck
frontend:test
frontend:build
frontend:format-check
```

Names may differ if canonical tooling conventions require another pattern, but there must be one documented way to run each quality gate from the repository root.

Scripts must work on Windows/PowerShell and normal CI shells.

Avoid shell syntax that only works on bash when a package-manager workspace command can do the job.

---

# 8. Three Next.js Applications

Create:

```text
apps/patient-web
apps/clinician-web
apps/admin-web
```

Each must be an independent Next.js App Router application.

Each application must have:

```text
TypeScript
strict mode
Tailwind CSS
ESLint
build script
typecheck script
test script
accessible root page
route-level loading UI
route-level error UI
```

Do not implement actual healthcare workflows.

Do not create fake dashboards that look production-ready.

Foundation pages should be intentionally minimal and clearly identify the application surface.

Acceptable examples:

```text
SwasthyaSetu Patient
SwasthyaSetu Clinician
SwasthyaSetu Admin
```

with neutral foundation text.

Do not display:

```text
real patient data
real provider data
medical advice
risk scores
crisis copy
Ayurvedic remedies
clinical thresholds
fake analytics presented as real
```

---

# 9. Server and Client Component Discipline

Default to server components.

Use `"use client"` only where Next.js requires it, such as route-level error handling/reset behavior or interactive tested UI.

Do not mark root layouts/page trees as client components without a reason.

---

# 10. Shared UI Package

Turn:

```text
packages/ui/
```

into the initial shared UI package.

Use a project-owned package name such as:

```text
@swasthyasetu/ui
```

unless an existing canonical package naming convention says otherwise.

The package should provide only minimal, genuinely shared primitives needed by the three foundation applications.

Good initial candidates:

```text
AppShell
LoadingState
ErrorState
EmptyState
Button/Link-style primitive only if actually used
basic design tokens / CSS variables
```

Do not build a large component library.

Do not add a heavy third-party design system in P1-B.

Do not add:

```text
Material UI
Ant Design
Chakra
shadcn-generated component catalog
Bootstrap
```

unless explicitly authorized by a later decision.

Prefer semantic HTML and project-owned minimal styling.

---

# 11. Accessibility Requirements

Foundation UI must already establish good defaults.

Verify:

```text
semantic main/header/nav structure where applicable
keyboard-accessible controls
visible focus states
accessible headings
accessible labels for interactive controls
reasonable contrast
no severity meaning encoded solely through color
```

Do not create clickable non-semantic `<div>` controls.

If route error UI provides a retry action, it must be a real button.

---

# 12. Shared Visual Foundation

Create only enough styling to establish consistency across all three applications.

Shared design tokens may include:

```text
font families
spacing scale
surface/background
text colors
border/focus tokens
radius
```

Do not define clinical risk/severity colors in P1-B.

Clinical severity semantics belong to later governed UI specifications.

---

# 13. Loading / Error / Empty States

Provide reusable typed components for normal application-state rendering.

At least loading and error states must be wired into each app's App Router foundation.

The components must not expose raw exception stack traces to end users.

Developer diagnostics may remain in console/build tooling where appropriate, but UI text must be generic.

---

# 14. Frontend Unit-Test Tooling

Select one modern test runner compatible with the chosen Next.js/React stack.

A lightweight expected choice is:

```text
Vitest
```

with React Testing Library if component rendering tests need it.

Do not install multiple unit-test runners.

At minimum test:

```text
each app has a renderable foundation page/component
shared UI loading/error behavior
basic accessibility-oriented semantics
```

Tests must be deterministic and network-free.

Do not snapshot entire pages as the primary assertion.

---

# 15. Playwright Skeleton

P1 master plan requires a Playwright skeleton.

Add the minimum project-owned E2E foundation under the existing testing structure.

Preferred location:

```text
tests/e2e/
```

or another location explicitly required by canonical docs.

The P1-B objective is to establish:

```text
Playwright dependency
configuration
documented command
minimal foundation/smoke test structure
```

Do not build real clinical E2E journeys.

If running browser tests would require browser installation that is intentionally deferred to P1-C/CI, validate configuration with an appropriate command such as test discovery/listing and report that full browser execution is deferred.

Do not claim Playwright passed if browsers were not installed/executed.

---

# 16. Typed API Access Boundary

P1-B should establish a location/convention for centralized typed API access but should **not** invent backend domain endpoints.

Do not scatter raw fetch calls in the foundation pages.

If no API call is required, no runtime API client dependency is required yet.

Do not generate fake clinical API schemas.

`packages/contracts/` may remain a placeholder if OpenAPI client generation is assigned to a later phase.

Do not generate contracts just to fill the directory.

---

# 17. Frontend Environment Variables

Do not add secrets.

Do not add speculative environment settings.

If a public API base URL variable is required for workspace foundation, use a clearly public setting such as:

```text
NEXT_PUBLIC_API_BASE_URL
```

only if the current implementation actually consumes it.

Remember that any `NEXT_PUBLIC_*` value is exposed to browsers.

Do not place server credentials there.

---

# 18. Telemetry / Analytics

Do not add:

```text
Google Analytics
PostHog
Sentry
Datadog RUM
Mixpanel
Hotjar
session replay
```

during P1-B.

Do not add patient/user analytics.

Framework build telemetry must not become a hidden patient-data path; document any framework telemetry control needed for protected CI/deployment, but do not overbuild the observability phase.

---

# 19. No Authentication Yet

Do not add:

```text
NextAuth/Auth.js
Keycloak SDK
OIDC client
JWT parsing
login pages
fake role guards
```

Identity belongs to later phases.

The patient/clinician/admin applications are separate surfaces, but P1-B does not implement access control.

---

# 20. No Backend Scope Creep

P1-A backend should remain functionally unchanged unless a tiny non-behavioral change is required to support monorepo tooling.

Do not:

```text
change health contracts
change error contracts
add database
add CORS "for later"
add auth
add API endpoints
add WebSockets
add OpenAPI generation tooling
```

If frontend foundation needs backend behavior that does not exist, stop and report instead of inventing it.

---

# 21. No Docker / CI Yet

P1-C owns:

```text
local Docker Compose
PostgreSQL local service
CI workflows
quality-gate orchestration
```

P1-B may provide commands that P1-C will call, but must not implement P1-C.

Leave `.github/workflows/` unchanged except for preserving existing placeholders.

Do not add a Dockerfile or Compose configuration in P1-B.

---

# 22. P1-A Provenance Reconciliation

Do **not** rewrite the historical P1-A execution record to pretend Git existed when Codex executed it.

The P1-A record correctly states that `.git` metadata was unavailable during its original execution.

However, append a small provenance note to `docs/implementation/38_PROGRESS_TRACKER.md` recording that after P1-A execution the repository was initialized/pushed with baseline:

```text
branch: main
commit: 1d299b7f4e7f95d634e5e4745b2d020b69a87b01
```

This is an audit-history clarification, not a change to P1-A status.

---

# 23. P1-B Phase Prompt Traceability

Ensure this phase prompt is retained at:

```text
docs/codex/CODEX_PHASE_PROMPTS/P1_B_FRONTEND_WORKSPACES.md
```

Do not delete P1-A's prompt.

Once a real prompt file exists in the directory, obsolete `.gitkeep` may be removed if empty-placeholder tracking is no longer needed.

---

# 24. Documentation

Update only documentation affected by P1-B.

Expected:

```text
README.md
REPOSITORY_TREE.txt
frontend-specific developer README(s) if useful
docs/implementation/38_PROGRESS_TRACKER.md
docs/implementation/37_DECISION_LOG.md only for real decisions
```

Document:

```text
Node requirement
frontend package-manager requirement
install command
run each app
lint
typecheck
unit tests
build
Playwright discovery/run instructions
workspace package structure
```

Do not write future product-feature documentation.

---

# 25. Progress Tracking

Only after verification succeeds, update `38_PROGRESS_TRACKER.md`.

Record P1-B as:

```text
COMPLETE
```

only if all P1-B-targeted mandatory criteria pass.

Overall P1 must remain:

```text
PARTIAL
```

until P1-C and all remaining P1 acceptance criteria are verified.

Record exact:

```text
branch
base commit
implementation commit if one is created
commands
test/build results
remaining criteria
```

---

# 26. Decision Log

If pnpm becomes the official frontend package manager, record an accepted ADR using the next available ADR number.

Do not alter prior accepted ADR history.

A package-manager ADR should not decide unrelated frontend architecture.

If no new architectural/tooling decision is necessary, do not create an ADR merely for activity logging.

---

# 27. Required Verification

Run from the appropriate workspace/root locations.

At minimum verify:

```text
package-manager lockfile consistency
workspace install from lock
frontend lint for all 3 apps/shared package
frontend TypeScript check for all 3 apps/shared package
frontend unit tests
frontend production build for patient-web
frontend production build for clinician-web
frontend production build for admin-web
Playwright config/test discovery
backend P1-A regression checks
git diff --check
git status --short
```

For backend regression, run from `backend/`:

```text
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

P1-B must not break P1-A.

---

# 28. Clean Install Verification

Where practical, verify the frontend can be restored from committed manifests and lockfile rather than relying on stale `node_modules`.

Do not commit:

```text
node_modules/
.next/
coverage/
playwright-report/
test-results/
```

The existing `.gitignore` must continue to protect them.

---

# 29. Git Diff Audit

Before completion:

```text
git diff --check
git status --short
git diff --stat
```

Inspect all changed files.

Confirm:

```text
no backend behavior scope creep
no clinical feature
no authentication
no database
no Docker/CI
no secrets
no analytics
no vendored dependency source
no generated build output committed
```

---

# 30. Commit and Push Policy

For this phase, after all required checks pass:

1. stage only P1-B-related changes;
2. commit on:

```text
phase/p1-b-frontend-foundation
```

3. use a clear commit message such as:

```text
feat: establish P1-B frontend workspace foundation
```

4. push that branch to `origin`;
5. do **not** merge into `main`;
6. do **not** force-push;
7. do **not** delete the branch.

If implementation is `PARTIAL`, `BLOCKED`, or `FAILED`, do not create a misleading "complete" commit message. You may commit a coherent partial state only if explicitly justified in the final report.

Do not create or merge a pull request unless the user explicitly asks.

---

# 31. Final Report Format

Return these sections exactly.

## STATUS

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
base commit
implementation branch
final commit SHA
push result
final git status
```

## SCOPE IMPLEMENTED

Describe only P1-B work.

## FILES CHANGED

Group:

```text
root workspace
patient app
clinician app
admin app
shared UI
tests
docs
```

## DEPENDENCIES ADDED

For each important dependency:

```text
name
resolved version
classification
reason
license
workspace scope
```

## ACCEPTANCE CRITERIA

Map the canonical applicable criteria to:

```text
PASS
FAIL
BLOCKED
NOT APPLICABLE
NOT VERIFIED
```

Do not invent acceptance IDs.

## VERIFICATION

Report every command and result, including failed attempts and corrected reruns.

Explicitly show results for:

```text
install/lock
lint
typecheck
tests
3 production builds
Playwright validation
backend regression
git diff --check
```

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
No clinical/business feature invented: YES/NO
No authentication pulled forward: YES/NO
No persistence pulled forward: YES/NO
No Docker/CI pulled forward: YES/NO
No third-party repo vendored: YES/NO
No secret or real patient data committed: YES/NO
P1-A backend behavior preserved: YES/NO
Research/AI dependencies absent from frontend runtime: YES/NO
```

## DEVIATIONS

List deviations and reasons.

## BLOCKERS / OPEN DECISIONS

Only real remaining issues.

## PROGRESS TRACKER

State exactly how P1-B and overall P1 were recorded.

## RECOMMENDED NEXT UNIT

Expected:

```text
P1-C — Docker / local PostgreSQL / CI / quality-gate foundation
```

unless canonical state reveals a blocker.

Do not implement P1-C.

---

# 32. Success Definition

P1-B is complete when:

- all three Next.js applications exist;
- all three build in production mode;
- strict TypeScript is enabled;
- frontend lint passes;
- frontend type checking passes;
- frontend unit tests pass;
- a minimal shared UI package exists and is actually consumed;
- loading/error foundations are accessible;
- Playwright foundation exists honestly;
- dependency installation is lockfile-reproducible;
- P1-A backend checks still pass;
- no product/clinical/auth/database/infrastructure scope has leaked in;
- changes are committed and pushed only to the P1-B feature branch;
- overall P1 remains partial until P1-C.

Implement only that.
