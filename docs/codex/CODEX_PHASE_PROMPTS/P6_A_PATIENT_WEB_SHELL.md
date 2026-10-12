# Codex Phase Prompt — P6-A Patient Web Design System / App Shell

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P6-A`
**Phase unit:** P6-A — Patient Web Design System / App Shell
**Base branch:** `main`
**Expected base commit:** `f8634bea8876ea800b06527c4328c0c24873a661`
**Implementation branch:** `phase/p6-a-patient-web-shell`
**Commit message:** `feat: establish P6-A patient web shell`

## Mission

Start P6 from the merged P5-complete baseline.

Current state:

```text
P5 = COMPLETE
P6-A = NEXT
P6-B = NOT STARTED
P6-C = NOT STARTED
Alembic head = p5b_0006
```

Implement only the patient-facing design-system/app-shell foundation.

P6-A owns:

- patient application shell;
- responsive layout foundation;
- patient-facing visual tokens;
- accessible reusable controls;
- persistent urgent-help entry-point architecture;
- route-shell architecture for planned patient screens;
- honest disabled/not-yet-available states;
- loading/error/empty state refinement;
- keyboard/focus primitives;
- patient-web unit + Playwright shell tests.

Do NOT implement:

- session/backend onboarding integration;
- consent/backend integration;
- working language persistence/selection flow;
- authenticated patient continuity flow;
- PWA manifest/service worker/installability/offline caching;
- clinical intake;
- documents/OCR;
- results/referrals/provider directory;
- safety or mental-health engines;
- AI/FHIR/ABDM;
- backend APIs or database changes.

P6-B owns onboarding/session/consent integration.
P6-C owns the full accessibility + PWA baseline.

Do not merge.

## 1. Preflight

Expected:

```text
branch: main
HEAD: f8634bea8876ea800b06527c4328c0c24873a661
working tree: clean
Alembic head: p5b_0006
P5: COMPLETE
```

Create:

```text
git switch -c phase/p6-a-patient-web-shell
```

## 2. Required Reading

Read before coding:

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
```

Inspect:

```text
apps/patient-web/**
packages/ui/**
tests/e2e/**
package.json
pnpm-workspace.yaml
eslint.config.mjs
prettier.config.mjs
```

Read exact:

```text
NFR-ACCESS-001..007
NFR-UX-001
NFR-UX-004
NFR-UX-006
AC-P6-001..008
```

If an identifier is missing/contradictory, report specification drift; do not invent requirements.

## 3. Preserve Existing Stack

Use the current stack only:

```text
Next.js 16.4.0
React 19.3.0
TypeScript 5.9.3 strict
Tailwind CSS 4.3.3
Vitest 5.0.3
Testing Library
Playwright 1.64.0
pnpm workspace
```

Build forward from the existing patient foundation and shared UI.

## 4. Dependency Boundary

Expected:

```text
NO new dependencies
NO lockfile changes
```

Do not add component frameworks, icon libraries, state managers, form libraries, accessibility packages, PWA packages, or analytics SDKs.

## 5. Patient App Shell

Implement a patient-specific shell, preferably under:

```text
apps/patient-web/components/
```

Provide:

- brand/header;
- main landmark;
- skip-to-content;
- responsive content container;
- patient navigation architecture;
- persistent urgent-help entry point;
- footer/help context;
- route/page title support.

Do not put patient-specific emergency behavior into generic shared `AppShell` if it would affect clinician/admin apps.

Shared generic primitives may live in `packages/ui`, but preserve backward compatibility.

## 6. Visual / UI Primitives

Establish maintainable tokens and states for:

- canvas/surface/text/muted/border;
- primary/secondary/critical actions;
- focus indicator;
- status banners;
- spacing/radius/touch target/content width;
- hover/focus/disabled;
- reduced motion;
- high-contrast readable presentation.

Create/refine only reusable primitives needed by the shell, such as:

- Button / ActionLink;
- PageHeader;
- Panel/Card;
- StatusBanner;
- LoadingState;
- ErrorState;
- EmptyState;
- DisabledState/UnavailableState.

Use semantic HTML, accessible names, visible focus, native disabled semantics, and large touch targets.

## 7. Urgent Help — Critical

Implement a persistent, visually prominent urgent-help action on applicable patient shell screens.

Route:

```text
/urgent-help
```

Requirements:

- keyboard reachable;
- clearly labelled;
- not hidden inside a menu;
- visually distinct;
- usable on mobile;
- present in shell architecture.

The route is only a safe P6-A shell.

Do NOT invent:

- helpline numbers;
- doctor/hospital/counsellor contacts;
- crisis resources;
- clinical routing decisions.

If no verified resource registry exists, use honest generic wording and explicitly say verified resources are not configured in this build. Do not hard-code unverified phone numbers.

## 8. Planned Patient Routes

Establish honest route shells for:

```text
/
/start
/consent
/language
/encounter
/documents
/results
/urgent-help
/referrals
```

Expected intent:

- `/` usable landing shell;
- `/start` P6-B onboarding handoff;
- `/consent` unavailable until P6-B;
- `/language` unavailable until P6-B;
- `/encounter` unavailable until governed workflow;
- `/documents` unavailable until document phase;
- `/results` unavailable until real results exist;
- `/urgent-help` safe urgent-help shell;
- `/referrals` unavailable until referral phase.

Do not fabricate clinical data or backend success.

## 9. Landing Page

Replace the generic "Foundation ready" placeholder.

May contain:

- clear SwasthyaSetu identity;
- short product-safe description;
- "Get started" link to `/start`;
- prominent Urgent help action;
- privacy/respectful-use reassurance.

Do not claim diagnosis or unavailable services.

## 10. Navigation

Active primary navigation should include only operational shell destinations such as Home, Start, Urgent help.

Future features should be omitted from primary navigation or visibly unavailable/disabled.

## 11. Accessibility Foundation

Implement now:

- semantic landmarks;
- one logical h1/page;
- skip link;
- keyboard-operable actions;
- visible `:focus-visible`;
- touch targets about 44x44 CSS px where practical;
- accessible labels;
- appropriate `aria-live`;
- reduced-motion support;
- high contrast;
- meaningful disabled semantics.

P6-C performs the broader accessibility baseline.

## 12. Keyboard Verification

At minimum prove:

- Tab reaches skip link;
- skip link targets main content;
- Tab reaches Get started;
- Tab reaches Urgent help;
- no keyboard trap;
- disabled controls are not falsely actionable;
- focus visibly discernible.

## 13. Loading / Error / Unavailable States

Refine current states for:

- loading;
- unexpected error;
- feature unavailable;
- future workflow not enabled.

Rules:

- no raw exception messages;
- no stack traces;
- retry only when meaningful;
- accessible status/alert semantics;
- no fake success state.

Keep error logging content-free.

## 14. Browser Storage Boundary

Do not introduce storage of health/session/consent data.

No:

```text
localStorage
sessionStorage
IndexedDB
Cache API
service worker caches
persistent sensitive cookies
```

Add a source/regression audit proving P6-A introduces no sensitive browser persistence.

## 15. No Backend Integration Yet

Do not fetch:

```text
/api/v1/sessions
/api/v1/consents
/api/v1/patients
/api/v1/encounters
```

P6-B owns these connections.

P6-A must build/test without backend availability.

## 16. No Auth / Working Language Flow Yet

Do not invent login/signup/OTP/password/OIDC/account-linking UI.

`/language` may exist as a shell only. Do not persist language preference.

## 17. PWA Boundary

Do NOT implement:

- manifest;
- service worker;
- offline cache;
- install prompt;
- background sync;
- push notifications.

P6-C owns PWA baseline.

## 18. Shared UI Boundary

`packages/ui` is shared by patient, clinician, and admin apps.

Patient-specific:

- urgent-help placement;
- patient navigation;
- patient route labels;
- patient footer

should normally remain under `apps/patient-web`.

All three apps must continue to build/test.

## 19. Suggested Structure

A reasonable structure:

```text
apps/patient-web/
  app/
    page.tsx
    start/page.tsx
    consent/page.tsx
    language/page.tsx
    encounter/page.tsx
    documents/page.tsx
    results/page.tsx
    urgent-help/page.tsx
    referrals/page.tsx
    error.tsx
    loading.tsx
    layout.tsx
    globals.css
  components/
    patient-shell.tsx
    patient-header.tsx
    patient-navigation.tsx
    urgent-help-link.tsx
    route-unavailable.tsx
  tests/
    shell.test.tsx
    routes.test.tsx
    page.test.tsx
```

Adjust only if repository style warrants it.

## 20. Unit Tests

Add tests for:

- landing semantic structure;
- Get started target;
- persistent Urgent help link;
- urgent-help safe wording;
- no invented phone/contact data;
- unavailable route state;
- loading/error state;
- accessible names;
- disabled semantics;
- shared UI regressions.

## 21. Playwright

Extend patient E2E to prove:

- landing page loads;
- main heading visible;
- Get started reachable;
- Urgent help visible/reachable;
- urgent-help page loads;
- keyboard Tab reaches primary actions;
- skip link works;
- mobile viewport e.g. 390x844 has no horizontal overflow;
- urgent help remains visible/reachable on mobile.

Do not test session/consent journey yet.

## 22. CI / Regression

Keep exactly six CI jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

All must pass.

Expected no changes to:

```text
backend/app/**
backend/migrations/**
backend/pyproject.toml
backend/uv.lock
deployments/local/compose.yaml
infra/docker/backend.Dockerfile
```

Alembic head stays:

```text
p5b_0006
```

Expected unchanged:

```text
package.json
pnpm-lock.yaml
backend/pyproject.toml
backend/uv.lock
```

## 23. Acceptance Status

Do not automatically mark all P6 acceptance criteria PASS.

Expected minimum after P6-A:

```text
AC-P6-001 PASS
P6-A COMPLETE
P6 overall PARTIAL
```

AC-P6-004/005/006/007/008 may be marked PASS only if fully satisfied and tested.

Expected not complete before later units:

```text
AC-P6-002 session/consent journey
AC-P6-003 working language selection UI
```

Do not mark P6 complete.

## 24. Documentation

Update only relevant:

```text
README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P6_A_PATIENT_WEB_SHELL.md
```

Update patient/UI docs if they already exist.

## 25. Verification

Run:

```text
pnpm install --frozen-lockfile
pnpm frontend:format-check
pnpm frontend:lint
pnpm frontend:typecheck
pnpm frontend:test
pnpm frontend:build
pnpm e2e:list
pnpm e2e:test
```

Also run the existing backend/root regression gates required by CI.

Audit:

- no dependency drift;
- no migration/backend/Docker scope drift;
- no service worker/PWA work;
- no localStorage/sessionStorage/IndexedDB;
- `git diff --check`.

## 26. Commit / Push

```text
git add <P6-A files only>
git commit -m "feat: establish P6-A patient web shell"
git push -u origin phase/p6-a-patient-web-shell
```

Do not merge.

## 27. Final Report

Return only:

```text
STATUS
BRANCH / GIT
SCOPE IMPLEMENTED
PATIENT SHELL
ROUTES
URGENT HELP
ACCESSIBILITY FOUNDATION
BROWSER STORAGE
DEPENDENCIES
BACKEND / MIGRATION STATUS
TESTS
VERIFICATION
CI
P6 ACCEPTANCE STATUS
DEVIATIONS
BLOCKERS / OPEN DECISIONS
PROGRESS TRACKER
MERGE
RECOMMENDED NEXT UNIT
```

`MERGE PERFORMED: NO`

Recommended next:

```text
P6-B — Patient Onboarding / Session / Consent
```

## Success Definition

P6-A is complete only when:

- patient-web has a real responsive shell;
- reusable patient-facing UI/accessibility primitives exist;
- shared UI remains compatible with clinician/admin;
- planned patient routes have honest shells;
- urgent-help entry-point architecture is persistently visible and keyboard reachable;
- no unverified helpline/provider data is invented;
- loading/error/unavailable states are usable;
- focus remains visible;
- mobile shell has no horizontal overflow;
- no sensitive browser persistence is introduced;
- no backend/session/consent integration is pulled forward;
- no PWA/service-worker work is pulled forward;
- no backend/schema/migration/dependency drift occurs;
- all six CI jobs pass;
- P6-A is COMPLETE;
- P6 remains PARTIAL;
- branch is pushed and not merged.

Stop after P6-A.

## Implementation Record

```text
Executed: 2026-10-12
Branch: phase/p6-a-patient-web-shell
Base: f8634bea8876ea800b06527c4328c0c24873a661
Scope: patient-only responsive app shell, planned route shells, urgent-help architecture, accessible UI states, and patient unit/Playwright coverage.
Dependencies: unchanged
Backend/schema/migrations/Docker: unchanged
Alembic head: p5b_0006
P6-A: COMPLETE
P6 overall: PARTIAL
AC-P6-001: PASS
AC-P6-002: NOT YET IMPLEMENTED (P6-B)
AC-P6-003: NOT YET IMPLEMENTED (P6-B)
AC-P6-004: PASS
AC-P6-005: PARTIAL (shell keyboard path passes; connected onboarding remains P6-B)
AC-P6-006: PASS
AC-P6-007: PASS
AC-P6-008: PASS
Remote CI: PENDING
Next: P6-B — Patient Onboarding / Session / Consent
```
