# Patient Profile Tile Wizard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add database-backed mobile number and self-reported blood group, a non-real Aadhaar demonstration reference, a first-login one-question tile wizard, and an honest optional health-record setup checklist.

**Architecture:** Extend the existing patient-demographics aggregate and table rather than creating parallel profile or checklist state. The authenticated patient API and same-origin BFF remain the only read/write path. Initial setup is a client-side in-memory wizard that performs one final optimistic-concurrency update; completed profiles retain the existing full edit form.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, Alembic, PostgreSQL, Next.js 16, React 19, TypeScript, Vitest, Testing Library, Playwright.

**Spec:** `docs/superpowers/specs/2026-11-08-patient-profile-contact-blood-checklist-design.md`

## Global Constraints

- Accept mobile numbers only in E.164 form: `+` followed by 7–15 digits, first digit 1–9.
- Accept blood group only as `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, or `UNKNOWN`.
- Accept the identity demonstration value only as `DEMO-AADHAAR-` followed by four digits; reject all 12-digit values.
- Never describe the demonstration reference as real Aadhaar, verified identity, authentication, or ABDM linkage.
- Do not add phone login, OTP, recovery, notifications, a checklist table, dependencies, browser storage, or partial-profile persistence.
- Existing profiles and rows must migrate without fabricated values.
- All private values remain behind authenticated same-origin BFF routes and `no-store` responses.

## Review Focus

- Existing profile rows containing null new columns must still load and remain editable; Task 2 adds a migration round-trip and legacy-row test.
- Unicode digits, spaces, punctuation, overlong values, and plausible 12-digit government identifiers must fail closed; Tasks 1 and 3 add boundary tests.
- Back/Next/Skip and refresh must not duplicate submissions or persist partial values; Task 4 adds interaction and storage tests.
- A concurrent profile update during the wizard's final save must preserve the existing 409 conflict path; Tasks 3 and 4 add conflict tests.
- Dashboard setup actions must never display completed checkmarks or percentages without authoritative evidence; Task 5 adds negative UI assertions.

---

### Task 1: Domain contracts and validation

**Files:**
- Modify: `backend/app/modules/patients/domain.py`
- Modify: `backend/tests/test_patient_domain.py`

**Interfaces:**
- Produces: `BloodGroup(StrEnum)` and `PatientDemographics.mobile_number: str | None`, `blood_group: BloodGroup | None`, `demo_aadhaar_reference: str | None`.
- Validation: E.164 regex `^\+[1-9][0-9]{6,14}$`; demo regex `^DEMO-AADHAAR-[0-9]{4}$`.

- [ ] **Step 1: Write failing direct-constructor tests**

Add tests covering every blood-group member, valid minimum/maximum E.164 values, valid demo reference, whitespace, Unicode digits, punctuation, short/long mobile values, arbitrary blood group, real-looking 12-digit input, and lowercase demo prefixes.

- [ ] **Step 2: Run domain tests and verify failure**

Run: `cd backend; uv run pytest tests/test_patient_domain.py -q`

Expected: FAIL because the three fields and `BloodGroup` do not exist.

- [ ] **Step 3: Implement the immutable domain fields and closed enum**

Export `BloodGroup` through `backend/app/modules/patients/public.py`; validate exact ASCII formats in `PatientDemographics.__post_init__` without normalizing malformed input.

- [ ] **Step 4: Run domain tests**

Run: `cd backend; uv run pytest tests/test_patient_domain.py -q`

Expected: PASS.

- [ ] **Step 5: Commit domain changes**

Commit message: `Add patient contact and demo identity domain fields`

### Task 2: PostgreSQL persistence and migration

**Files:**
- Create: `backend/migrations/versions/0010_patient_contact_blood_demo_identity.py`
- Modify: `backend/app/modules/patients/infrastructure.py`
- Modify: `backend/migrations/env.py` only if metadata registration requires it
- Modify: `backend/tests/integration/test_postgres_p5_persistence.py`
- Modify: `backend/tests/test_persistence.py`
- Modify: `backend/tests/test_p5_domain_boundaries.py`

**Interfaces:**
- Consumes: Task 1 `BloodGroup` and demographic fields.
- Produces: nullable `patient_demographics.mobile_number VARCHAR(16)`, `blood_group VARCHAR(7)`, and `demo_aadhaar_reference VARCHAR(17)` with named format/check constraints and complete mapper round-trip support.

- [ ] **Step 1: Write failing ORM metadata and PostgreSQL round-trip tests**

Assert exact column types/nullability, closed blood-group database constraint, ASCII-format constraints, legacy null-row loading, valid round trip, invalid direct SQL rejection, downgrade removal, and upgrade restoration.

- [ ] **Step 2: Run focused persistence tests and verify failure**

Run: `cd backend; uv run pytest tests/test_persistence.py tests/test_p5_domain_boundaries.py -q`

With the configured test database, run: `cd backend; uv run pytest tests/integration/test_postgres_p5_persistence.py -q -m postgres`

Expected: FAIL because columns and mapper fields are absent.

- [ ] **Step 3: Add migration and mapper fields**

Set `down_revision` to the current `0009` revision, keep one Alembic head, map `blood_group` back to `BloodGroup`, and preserve nulls for pre-existing profiles.

- [ ] **Step 4: Verify migration and persistence**

Run: `cd backend; uv run alembic -c alembic.ini heads`

Expected: exactly one `0010` head.

Run the focused unit and PostgreSQL commands from Step 2; expected PASS.

- [ ] **Step 5: Commit persistence changes**

Commit message: `Persist patient contact and profile identity details`

### Task 3: Authenticated API and BFF boundary

**Files:**
- Modify: `backend/app/modules/patients/api.py`
- Modify: `backend/tests/patients/test_profile_update.py`
- Modify: `backend/tests/integration/test_patient_account_http_postgres.py`
- Modify: `apps/patient-web/lib/patient/contracts.ts`
- Modify: `apps/patient-web/lib/patient/server.ts`
- Modify: `apps/patient-web/tests/patient-profile-bff.test.ts`

**Interfaces:**
- Consumes: Task 1 domain types and Task 2 persisted columns.
- Produces: snake-case backend request/response fields and camel-case BFF fields `mobileNumber`, `bloodGroup`, and `demoAadhaarReference` within authenticated profile demographics.

- [ ] **Step 1: Write failing API and BFF tests**

Test authenticated read/update round trips, all invalid formats, forbidden extra keys, anonymous access, cross-subject isolation, no-store behavior, safe error minimization, and unchanged 409 optimistic-concurrency handling.

- [ ] **Step 2: Run focused API/BFF tests and verify failure**

Run: `cd backend; uv run pytest tests/patients/test_profile_update.py tests/integration/test_patient_account_http_postgres.py -q`

Run: `pnpm --filter @swasthyasetu/patient-web test -- patient-profile-bff.test.ts`

Expected: FAIL on absent fields/guards.

- [ ] **Step 3: Extend Pydantic contracts, serializers, TypeScript types, and runtime guards**

Keep backend and BFF allowlists exact. Do not return the fields from account/session endpoints or place them in logs.

- [ ] **Step 4: Run focused API/BFF tests**

Run the commands from Step 2; expected PASS.

- [ ] **Step 5: Commit boundary changes**

Commit message: `Expose protected patient profile detail fields`

### Task 4: First-login floating-tile wizard and completed-profile editor

**Files:**
- Create: `apps/patient-web/components/profile-setup-wizard.tsx`
- Create: `apps/patient-web/components/profile-fields.tsx`
- Modify: `apps/patient-web/components/profile-form.tsx`
- Modify: `apps/patient-web/app/globals.css`
- Modify: `apps/patient-web/tests/patient-profile-ui.test.tsx`
- Modify: `apps/patient-web/tests/accessibility.test.tsx`

**Interfaces:**
- Consumes: Task 3 `PatientProfile`, `PatientProfileSubmission`, and `/api/patient/profile`.
- Produces: `ProfileSetupWizard` for incomplete profiles and shared field definitions used by the ordinary completed-profile editor.

- [ ] **Step 1: Write failing wizard and editor tests**

Test the 13-step sequence, one field tile at a time, progress text, age/BMI support text, required validation, optional Skip, Back value preservation, Enter behavior, review editing, exactly one final POST, duplicate-submit prevention, conflict message, successful dashboard navigation, no local/session storage, real 12-digit rejection, and full-form editing after completion.

- [ ] **Step 2: Run UI tests and verify failure**

Run: `pnpm --filter @swasthyasetu/patient-web test -- patient-profile-ui.test.tsx accessibility.test.tsx`

Expected: FAIL because the wizard and new fields are absent.

- [ ] **Step 3: Extract shared profile-field metadata and implement wizard state**

Keep unsaved values only in React state. Use semantic form controls, focus the tile heading on step change, expose progress via `aria-live`, provide Back/Next/Skip, and submit only from final review.

- [ ] **Step 4: Style the floating tile and responsive states**

Use the existing indigo palette, visible focus states, reduced-motion support, 320px no-overflow behavior, and no background navigation on first-time setup.

- [ ] **Step 5: Run UI, accessibility, lint, and type checks**

Run the Step 2 tests, then `pnpm --filter @swasthyasetu/patient-web lint` and `pnpm --filter @swasthyasetu/patient-web typecheck`; expected PASS.

- [ ] **Step 6: Commit wizard changes**

Commit message: `Add first-login patient profile tile wizard`

### Task 5: Optional dashboard setup checklist

**Files:**
- Modify: `apps/patient-web/components/dashboard-overview.tsx`
- Modify: `apps/patient-web/tests/dashboard-overview.test.tsx` or the existing dashboard test file
- Modify: `tests/e2e/patient-account-history.spec.ts`

**Interfaces:**
- Consumes: existing authenticated dashboard, `/profile`, `/history`, `/documents`, and `/encounter` destinations.
- Produces: a “Complete your health record” action section with links for profile, conditions, medicines, allergies, procedures, documents, and guided intake.

- [ ] **Step 1: Write failing dashboard and browser tests**

Assert every destination is reachable, tasks are described as optional actions, and no checkmark, completed claim, or percentage appears.

- [ ] **Step 2: Run focused tests and verify failure**

Run: `pnpm --filter @swasthyasetu/patient-web test -- dashboard-overview`

Expected: FAIL because the checklist is absent.

- [ ] **Step 3: Implement the action checklist using existing UI primitives**

Use links only; do not create checklist persistence or query additional private data.

- [ ] **Step 4: Run focused frontend and Playwright tests**

Run the focused unit command and the relevant patient Playwright project; expected PASS.

- [ ] **Step 5: Commit checklist changes**

Commit message: `Guide optional patient health record setup`

### Task 6: Full verification, migration of local demo, and handoff

**Files:**
- Modify: `docs/DEMO_GUIDE.md`
- Modify: `README.md` only if the onboarding walkthrough requires a concise update

**Interfaces:**
- Consumes: Tasks 1–5.
- Produces: verified branch, migrated local demo, documentation, and review-ready PR.

- [ ] **Step 1: Update demo documentation**

Document E.164 mobile format, self-reported blood group, synthetic-only `DEMO-AADHAAR-0000` style reference, prohibition on real identifiers, tile flow, and optional dashboard actions.

- [ ] **Step 2: Run complete backend quality and non-PostgreSQL tests**

Run the repository's backend formatting, lint, type, and test commands from CI; expected PASS.

- [ ] **Step 3: Run clean PostgreSQL migration and integration tests**

Upgrade a clean database to head, run Alembic `current` and `check`, execute all PostgreSQL-marked tests, downgrade/upgrade the new revision, and confirm one head; expected PASS.

- [ ] **Step 4: Run complete frontend and browser checks**

Run `pnpm frontend:format-check`, `pnpm frontend:lint`, `pnpm frontend:typecheck`, `pnpm frontend:test`, `pnpm frontend:build`, and `pnpm e2e:test`; expected PASS.

- [ ] **Step 5: Run Docker, privacy, and security verification**

Validate Compose, rebuild/migrate/health-check the backend, run repository security scans, search for real-looking Aadhaar fixtures and accidental mobile logging, and run `git diff --check`; expected PASS with no real identifier fixture.

- [ ] **Step 6: Apply migration to the preserved local demo and visually verify**

Restart only SwasthyaSetu services, apply Alembic head, verify registration → tile wizard → dashboard checklist at desktop and 320px widths, and preserve existing database/document volumes.

- [ ] **Step 7: Request whole-branch review and fix verified findings**

Review domain/API/privacy boundaries, migration reversibility, wizard accessibility, and honest checklist semantics before push.

- [ ] **Step 8: Commit documentation and final fixes**

Commit message: `Document and verify patient profile onboarding`

- [ ] **Step 9: Push, open PR, verify all six CI jobs, and merge after success**

Confirm the CI run targets the exact final SHA and all six required jobs succeed before merging.
