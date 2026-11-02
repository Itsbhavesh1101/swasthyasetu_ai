# P23-A Core-Journey Negative E2E Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add real full-stack synthetic evidence for P7 consent-withdrawal and cross-session IDOR
denial, with only the smallest fail-closed correction for any verified authorization defect.

**Architecture:** Extend the existing patient Playwright suite with two focused journeys over the current Chromium → Next.js BFF → FastAPI → PostgreSQL topology. Reuse existing onboarding and session-cookie helpers; production code changes are allowed only if a test reveals a verified boundary defect.

**Tech Stack:** Playwright 1.64, TypeScript 5.9, Next.js 16.4, FastAPI, PostgreSQL 16, Docker Compose.

**Spec:** `docs/superpowers/specs/2026-11-02-p23a-core-journey-negative-e2e-design.md`

## Global Constraints

- Repository-owned synthetic values only; no patient, clinical, provider, or external data.
- No blocked P8+ module activation and no clinical, accessibility, performance, recovery, pilot, or release claim.
- No dependency, lockfile, schema, migration, API, feature-flag, or runtime-registration change.
- P23 remains `PARTIAL`; all live `AC-P23-*` and product acceptance remain unverified.

## Review Focus

- A second valid session requests another session's intake: no protected value or existence detail is exposed.
- Consent is withdrawn after a draft is created: subsequent read fails with `CONSENT_REQUIRED` and no draft content.
- A denied cross-session read must not affect the owner's session or silently grant fresh consent;
  the requesting BFF may clear its own cookies under the existing invalid-credential policy.
- Browser contexts and cookies must remain isolated throughout the IDOR test.
- CI retries must not depend on shared identifiers or test execution order.

---

### Task 1: Add bounded negative full-stack journeys and record evidence

**Files:**

- Modify: `tests/e2e/patient.spec.ts`
- Create: `docs/implementation/P23_A_CORE_JOURNEY_NEGATIVE_E2E.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**

- Consumes: existing `completeOnboarding(page)`, patient session cookies, intake BFF routes, exact
  session/consent backend enforcement, and the existing Playwright CI topology
- Produces: two deterministic full-stack negative journeys, one fail-closed existence-oracle
  regression test, and a truthful bounded evidence record

- [ ] **Step 1: Add consent-withdrawal and cross-session denial tests**

Assert exact safe error codes/statuses, bounded unavailable UI, absence of synthetic draft content,
continued validity of the correct session, and explicit browser-context isolation.

- [ ] **Step 2: Run the focused Playwright tests**

Run the patient project against real FastAPI/PostgreSQL and confirm both tests pass. If a verified
boundary defect appears, add the smallest test-driven application fix within the existing P7 scope.

- [ ] **Step 3: Record the bounded evidence**

Document the exact topology, cases, limitations, and unchanged P23 acceptance status; update the
tracker without changing any live acceptance criterion to PASS.

- [ ] **Step 4: Run complete verification**

Run backend/frontend quality gates, all Playwright journeys, Compose validation, migration checks,
`git diff --check`, and the six remote CI jobs on the exact feature SHA.

- [ ] **Step 5: Review, commit, push, merge, and verify main**

Perform a fresh whole-branch review. Fix Important/Critical findings with regression evidence. Merge
only after all six PR jobs pass; then verify all six jobs on the exact main merge SHA.
