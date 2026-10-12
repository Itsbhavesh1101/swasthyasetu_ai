# Codex Phase Prompt — P6-C Accessibility + PWA Baseline

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P6-C`
**Phase unit:** P6-C — Accessibility + PWA Baseline
**Base branch:** `main`
**Expected base commit:** `b361511cbcf25e6834cc56daeb78bfc32d52e94d`
**Implementation branch:** `phase/p6-c-accessibility-pwa-baseline`
**Commit message:** `feat: complete P6 accessibility and PWA baseline`

## Mission

Complete P6 from the merged P6-A/P6-B baseline.

Current state:

```text
P5 = COMPLETE
P6-A = COMPLETE
P6-B = COMPLETE
P6-C = NEXT
P6 overall = PARTIAL
AC-P6-001..008 = PASS
Alembic head = p5b_0006
```

Implement only the final P6 accessibility and privacy-safe PWA baseline.

P6-C owns:
- WCAG 2.2 AA-oriented accessibility baseline;
- keyboard/focus/reflow/contrast regression coverage;
- screen-reader semantics review;
- touch-target verification;
- urgent-help prominence regression;
- PWA web app manifest;
- installable metadata/icons;
- root-scope service-worker registration;
- strict privacy-safe offline fallback;
- explicit safe static-only cache policy;
- PWA/browser-storage security regression tests;
- P6 final acceptance/documentation.

Do NOT implement:
- clinical intake;
- backend encounter creation;
- new session/consent behavior;
- new consent purposes/scopes;
- login/authentication;
- documents/OCR/results/referrals/providers;
- mental-health/safety logic;
- audio/TTS/ASR;
- push notifications;
- background sync;
- offline submission/clinical data/mutation queues;
- FHIR/ABDM;
- backend APIs;
- database migrations;
- new dependencies.

Stop after P6-C. Do not merge.

## 1. Preflight

Expected:

```text
branch: main
HEAD: b361511cbcf25e6834cc56daeb78bfc32d52e94d
working tree: clean
P6-A: COMPLETE
P6-B: COMPLETE
P6: PARTIAL
Alembic head: p5b_0006
```

Create:

```text
git switch -c phase/p6-c-accessibility-pwa-baseline
```

## 2. Required Reading

Read:
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
docs/codex/CODEX_PHASE_PROMPTS/P6_A_PATIENT_WEB_SHELL.md
docs/codex/CODEX_PHASE_PROMPTS/P6_B_ONBOARDING_SESSION_CONSENT.md
```

Inspect:
```text
apps/patient-web/**
packages/ui/**
tests/e2e/**
.github/workflows/ci.yml
package.json
pnpm-lock.yaml
```

Canonical requirements:
```text
NFR-ACCESS-001..007
NFR-UX-001
NFR-UX-004
NFR-UX-006
AC-P6-001..008
```

Do not claim independent WCAG certification. Implement the engineering baseline.

`NFR-ACCESS-006` does not authorize ad-hoc browser speech. No governed audio workflow exists yet, so keep audio guidance deferred to P12.

## 3. Preserve P6-B Security Boundary

Preserve exactly:
```text
same-origin Next.js BFF
SWASTHYASETU_BACKEND_URL server-only
HttpOnly transient session cookies
SameSite=Strict
no bearer in browser JavaScript
no bearer in URLs/logs/JSON
GENERAL_PRODUCT_USE
scope ["clinical_intake"]
notice_version privacy-v1
real FastAPI + PostgreSQL Playwright journey
```

Do not redesign this.

## 4. Dependency Boundary

Expected:
```text
NO new npm dependencies
NO package.json changes
NO pnpm-lock.yaml changes
NO backend dependency changes
```

Do not add:
```text
next-pwa
workbox
axe-core
@axe-core/playwright
Lighthouse packages
service-worker libraries
accessibility frameworks
```

Use only existing stack/platform APIs.

## 5. PWA Baseline

Recommended structure:
```text
apps/patient-web/
  app/
    manifest.ts
    offline/page.tsx
  components/
    pwa-registration.tsx
  public/
    sw.js
    icons/
      icon-192.png
      icon-512.png
      icon-maskable-512.png
```

Equivalent repository-consistent layout is acceptable.

Required:
```text
manifest
name
short_name
description
start_url "/"
scope "/"
display "standalone"
theme/background colors
lang
192 icon
512 icon
maskable icon
root-scope service worker
generic offline fallback
```

No third-party PWA package.

## 6. Manifest

Implement with `app/manifest.ts` or equivalent.

Recommended:
```text
name: SwasthyaSetu Patient
short_name: SwasthyaSetu
start_url: /
scope: /
display: standalone
lang: en
```

Use patient-shell theme colors.

Do not claim offline clinical, diagnostic, or emergency-response capability.

## 7. Icons

Provide deterministic project-owned icons:
```text
192x192
512x512
maskable 512x512
```

No external download/stock image.

Keep branding simple and non-clinical-authority implying.

## 8. Service Worker — Privacy First

Implement `/public/sw.js`.

No Workbox.

Allowed cache examples:
```text
/offline
manifest
PWA icons
other explicitly enumerated non-sensitive public assets
/_next/static/* only if clearly safe
```

Never cache:
```text
/api/**
/api/onboarding/**
session/consent responses
POST/PUT/PATCH/DELETE
Authorization-bearing requests
patient/clinical API payloads
dynamic user JSON
backend responses
stateful page HTML
```

No broad "cache every GET" rule.

## 9. Navigation Strategy

Normal page navigation:
```text
NETWORK ONLY
```

On genuine network failure only:
```text
return cached generic /offline page
```

Never serve stale `/consent`, `/encounter`, session status, or user-specific state.

Never claim session validity while offline.

## 10. Offline Page

Add `/offline`.

Generic text must make clear:
```text
You appear to be offline.
Session and consent status cannot be confirmed without a connection.
Clinical workflows are unavailable offline.
Urgent-help information here is not a substitute for emergency services.
```

Provide accessible retry/home action.

No offline forms or queued mutations.

## 11. Safe Cache Policy

Use versioned cache name, e.g.:
```text
swasthyasetu-patient-shell-v1
```

Install:
```text
pre-cache only explicit approved generic resources
```

Use credential-omitted pre-cache requests where practical.

Activate:
```text
delete obsolete SwasthyaSetu patient-shell caches
```

Fetch rules:
```text
ignore non-GET
ignore /api/**
ignore non-http(s)
navigation -> network; offline fallback only on failure
approved static assets -> cache-first or stale-while-revalidate
everything else -> network
```

Never inspect/log cookies or tokens.

## 12. Service Worker Delivery

Ensure `/sw.js` supports update checks.

Recommended:
```text
Cache-Control: no-cache
Service-Worker-Allowed: /
```

Narrowly scope any Next config headers.

## 13. Registration

Register through a minimal client component.

Requirements:
```text
feature detect
browser-only
root scope
non-blocking
safe failure
no sensitive logging
no forced reload loop
```

No install-prompt UX required.

## 14. Browser Storage Boundary

P6-C may use Cache API only for explicitly safe PWA shell assets.

Still prohibited:
```text
localStorage
sessionStorage
IndexedDB app/user persistence
Cache API for API/user data
persistent consent
persistent health data
persistent session metadata
persistent bearer/token
```

P6-B HttpOnly cookies remain session-only and are not copied elsewhere.

## 15. Offline Session/Consent

Offline:
```text
do not infer ACTIVE session
do not infer GRANTED consent
do not create session
do not grant/revoke consent
do not close session
do not queue/replay mutations
```

No background sync.

## 16. Accessibility Audit

Review:
```text
/
/start
/language
/consent
/encounter
/documents
/results
/urgent-help
/referrals
/offline
```

Audit/fix:
```text
landmarks
single logical h1
heading hierarchy
native link/button semantics
accessible names
form labels
fieldset/legend
status/alert semantics
disabled semantics
focus visibility/order
keyboard operation
touch targets
contrast
reflow
reduced motion
forced colors
language attributes
urgent-help prominence
```

No unrelated redesign.

## 17. Screen Reader Semantics

Verify:
```text
main landmark
labelled nav
native labels
language fieldset/legend
explicit consent label
decorative marks aria-hidden
loading status semantics
meaningful page titles
Hindi content lang="hi"
```

Avoid unnecessary ARIA.

## 18. Focus / Keyboard

Preserve skip link.

Requirements:
```text
visible focus
logical tab order
no trap
disabled controls skipped
client-side transitions do not strand focus
errors discoverable
```

Test keyboard-only:
```text
Home -> Start
Start -> Language
select language
Continue -> Consent
toggle consent
Agree and continue
Encounter readiness
End private session
Urgent help
```

## 19. Reflow

Test:
```text
320x800
390x844
desktop
```

Require:
```text
no horizontal page scroll
no clipped actions
urgent help visible
no overlaps
forms usable
```

## 20. Touch Targets

Keep current ~44x44 CSS px baseline.

Verify representative:
```text
Urgent help
Get started / Continue
language radio cards
consent checkbox/control
Agree and continue
Withdraw consent
End private session
Try again
```

Use Playwright geometry assertions.

## 21. Contrast

Add deterministic test-only contrast checks.

At minimum:
```text
main text on canvas/surface
muted text on surface
primary button text/background
critical button text/background
focus indicator against surrounding background
disabled state where applicable
```

Target WCAG AA for normal text.

If token fails, fix token; do not weaken test.

No dependency.

## 22. Reduced Motion / Forced Colors

Preserve and test:
```text
prefers-reduced-motion
forced-colors
```

Critical controls must remain identifiable:
```text
Urgent help
primary actions
focus
agreement controls
language choices
disabled controls
```

## 23. Urgent Help

Regression-critical:
```text
visible
not hidden in menu
keyboard reachable
visually distinct
mobile visible
forced-colors identifiable
```

No invented numbers/providers/resources.

## 24. Audio Guidance

Do NOT implement browser speech/TTS.

Document:
```text
NFR-ACCESS-006 applies to configured audio workflows.
No governed audio workflow exists in P6.
P12 owns speech/language activation.
```

## 25. Language Accessibility

Preserve:
```text
Hindi strings use lang="hi"
root stays lang="en" unless whole page is translated
no claim of full translated experience
```

## 26. Error / Degraded States

Review:
```text
backend unavailable
no session
no consent
consent withdrawn
session close failure
unexpected error
offline
```

Require:
```text
plain language
safe alert/status semantics
accessible retry
urgent help remains available
```

## 27. PWA Unit/Static Tests

Prove:
```text
manifest required fields
root start_url/scope
standalone display
icons declared and exist
service worker exists
cache allowlist explicit
/api/ bypass explicit
mutations not cached
navigation uses network + offline fallback
old cache cleanup
offline page generic
```

## 28. Browser Storage Source Audit

Update P6-B source audit precisely.

Required:
```text
no localStorage
no sessionStorage
no IndexedDB app persistence
no /api caching
no onboarding-response caching
no bearer copied to browser-readable storage
```

Cache API is allowed only inside service worker for safe generic shell.

## 29. Playwright Accessibility

Add/extend:
```text
landmarks
one h1 per route
skip link
keyboard onboarding
visible focus
urgent help
390px no overflow
320px no overflow
>=44px representative controls
offline page readability
```

No flaky screenshot testing.

## 30. Playwright PWA

On Chromium loopback secure context, verify:
```text
manifest route valid
service worker registers
service worker reaches ready/activated
root scope
safe shell cache exists
cached URLs only approved generic resources
no /api URL in Cache Storage
no /consent or /encounter navigation HTML in cache
```

Never print cookie/token values.

## 31. Offline Fallback E2E

After SW ready:
```text
load online
simulate offline
navigate normally
generic offline fallback appears
restore online
```

Offline page must state that session/consent cannot be confirmed and clinical workflows are unavailable.

## 32. P6-B Regression E2E

Preserve real FastAPI + PostgreSQL tests:
```text
session create
HttpOnly cookie properties
consent grant
consent revoke
session close
no bearer in document.cookie
no localStorage/sessionStorage
```

Also prove Cache Storage contains no API/session/consent payloads.

## 33. CI

Keep exactly six jobs:
```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Do not add a seventh.

Keep current Playwright real backend/PostgreSQL setup.

All six must pass.

## 34. Backend / Migration Boundary

Expected unchanged:
```text
backend/app/**
backend/migrations/**
backend/pyproject.toml
backend/uv.lock
deployments/local/compose.yaml
infra/docker/backend.Dockerfile
```

Alembic:
```text
p5b_0006
```

## 35. Frontend Dependency Boundary

Expected unchanged:
```text
package.json
pnpm-lock.yaml
apps/patient-web/package.json
```

`apps/patient-web/next.config.ts` may change only for narrow service-worker delivery headers.

## 36. No Sensitive PWA Persistence

Merge blocker if any of these occur:
```text
API response cached
BFF response cached
session/consent JSON cached
clinical data cached
token cached
mutation queue stored
background sync added
```

## 37. Documentation

Update only relevant:
```text
README.md
docs/frontend/README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P6_C_ACCESSIBILITY_PWA_BASELINE.md
```

Document:
```text
manifest
service-worker registration
cache allowlist
offline fallback
network-only stateful behavior
no offline clinical/session/consent capability
accessibility evidence
audio guidance deferred
```

## 38. Verification

Run:
```text
pnpm install --frozen-lockfile
pnpm frontend:format-check
pnpm frontend:lint
pnpm frontend:typecheck
pnpm frontend:test
pnpm frontend:build
pnpm e2e:list
```

Real E2E:
```text
start PostgreSQL
uv sync --locked --dev
alembic upgrade head
start backend
SWASTHYASETU_BACKEND_URL=http://127.0.0.1:8000
pnpm e2e:test
```

Also run backend regression and Alembic drift.

Audit:
```text
git diff --check
lockfiles unchanged
backend unchanged
migrations unchanged
Alembic p5b_0006
no sensitive browser storage
no API cache entries
no background sync/push
no speech/TTS
```

## 39. Final Acceptance

After successful P6-C:
```text
AC-P6-001 PASS
AC-P6-002 PASS
AC-P6-003 PASS
AC-P6-004 PASS
AC-P6-005 PASS
AC-P6-006 PASS
AC-P6-007 PASS
AC-P6-008 PASS

P6-A = COMPLETE
P6-B = COMPLETE
P6-C = COMPLETE
P6 = COMPLETE
```

Also verify phase exit criteria:
```text
patient shell usable
session/consent connected
accessibility primitives established
feature architecture established
PWA shell baseline established
no sensitive localStorage by default
```

Do not implement P7.

## 40. P7 Readiness Warning

Current tracker states P7 requires missing specs including:
```text
07_CLINICAL_INTAKE_SPEC.md
22_UX_AND_USER_FLOWS.md
23_PATIENT_APP_SPEC.md
```

Do not begin P7.

Report missing prerequisites before P7-A.

## 41. Progress Tracker

Before CI:
```text
P6-C = PARTIAL — REMOTE CI VERIFICATION PENDING
P6 = PARTIAL
```

After all six jobs pass:
```text
P6-C = COMPLETE
P6 = COMPLETE
next = resolve/create P7 prerequisite specs before P7-A
```

## 42. Commit / Push

```text
git add <P6-C files only>
git commit -m "feat: complete P6 accessibility and PWA baseline"
git push -u origin phase/p6-c-accessibility-pwa-baseline
```

Do not merge.

## 43. Final Report

Return only:
```text
STATUS
BRANCH / GIT
ACCESSIBILITY BASELINE
KEYBOARD / FOCUS
REFLOW / TOUCH TARGETS
CONTRAST / HIGH CONTRAST
URGENT HELP
PWA MANIFEST
SERVICE WORKER
OFFLINE FALLBACK
CACHE PRIVACY
BROWSER STORAGE
P6-B REGRESSION
BACKEND / MIGRATION STATUS
DEPENDENCIES
TESTS
REAL E2E
VERIFICATION
CI
P6 FINAL ACCEPTANCE
DEVIATIONS
BLOCKERS / OPEN DECISIONS
P7 READINESS
PROGRESS TRACKER
MERGE
RECOMMENDED NEXT ACTION
```

`MERGE PERFORMED: NO`

Recommended next:
```text
Complete/approve P7 prerequisite specifications before P7-A.
```

## Success Definition

P6-C is complete only when:
- valid patient PWA manifest and required icons exist;
- root-scope project-owned service worker registers;
- only explicit generic/static shell resources enter Cache Storage;
- `/api/**` and onboarding responses are never cached;
- navigations are network-only with generic offline fallback;
- offline mode never claims session/consent validity;
- no offline mutation queue/background sync exists;
- no health/session/consent/token data enters localStorage/sessionStorage/IndexedDB/Cache Storage;
- P6-B HttpOnly security remains intact;
- all P6 routes have sound semantic/accessibility structure;
- keyboard onboarding remains fully operable;
- focus remains visible/logical;
- 320px/390px reflow passes;
- representative controls preserve >=44px target;
- intended color pairs pass AA contrast;
- reduced-motion/forced-colors remain usable;
- urgent help remains prominent;
- audio is not falsely activated;
- real Playwright verifies PWA cache privacy and P6-B regression against FastAPI/PostgreSQL;
- no backend/schema/migration/dependency drift occurs;
- Alembic remains `p5b_0006`;
- all six CI jobs pass;
- AC-P6-001..008 remain PASS;
- P6-C = COMPLETE;
- P6 = COMPLETE;
- P7 = NOT STARTED;
- branch is pushed, not merged.

Stop after P6-C.

## Implementation Record

```text
Executed: 2026-10-12
Branch: phase/p6-c-accessibility-pwa-baseline
Base: b361511cbcf25e6834cc56daeb78bfc32d52e94d
Scope: accessibility engineering baseline, manifest/icons, root service worker, generic offline fallback, explicit safe-shell cache, and real browser privacy regression.
Cache: /offline, /manifest.webmanifest, and project-owned icons only; API/mutations/stateful navigation bypassed.
Browser persistence: no localStorage/sessionStorage/IndexedDB app persistence; Cache API restricted to approved generic shell resources.
Audio: deferred to P12; no browser speech/TTS.
Dependencies/backend/schema/migrations: unchanged
Alembic head: p5b_0006
AC-P6-001..008: PASS locally
P6-C: PARTIAL — REMOTE CI VERIFICATION PENDING
P6 overall: PARTIAL
Next: complete/approve P7 prerequisite specifications before P7-A
```
