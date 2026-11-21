# Masked Aadhaar Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the synthetic Aadhaar reference with a realistic exactly-12-digit entry flow that persists and returns only the final four digits.

**Architecture:** The browser and authenticated write request hold the complete number transiently. The backend Pydantic boundary uses `SecretStr`, extracts the suffix, and constructs a domain object containing only `aadhaar_last_four`; PostgreSQL and all read responses therefore cannot expose or reconstruct the complete number. A forward Alembic migration removes the old runtime column without rewriting historical migrations.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, Alembic, PostgreSQL, Next.js 16, React 19, TypeScript, Vitest, Playwright.

**Spec:** `docs/superpowers/specs/2026-11-08-masked-aadhaar-profile-design.md`

## Global Constraints

- Accept only `^[0-9]{12}$`; spaces, punctuation, letters, Unicode digits, short values, and long values fail closed.
- Persist and return only `aadhaar_last_four`, exactly four ASCII digits or null.
- Never log, render, persist, echo in errors, or return the complete number.
- Preserve an existing suffix when a completed-profile update supplies no replacement number.
- Do not add Aadhaar authentication, verification, checksum, OTP, UIDAI, ABHA linkage, lookup, deduplication, authorization, dependencies, or browser storage.
- Do not rewrite the already-applied `patient_details_0010` migration or historical plans/specifications.
- Remove Aadhaar-specific demo/synthetic wording from current runtime UI and current demo instructions; unrelated governance labels remain unchanged.

## Review Focus

- A completed-profile save with a blank replacement input must preserve the stored suffix; Task 2 adds a real API/PostgreSQL preservation test and Task 4 adds a UI submission test.
- Full digits must not escape through response serialization, repr, errors, logs, or review UI; Tasks 1, 2, 3, and 4 add negative assertions.
- Unicode digits and formatted values must fail at browser/BFF/backend boundaries; Tasks 2–4 add adversarial tests.
- Old demonstration values must not be reinterpreted as real Aadhaar suffixes during migration; Task 1 verifies existing-row null behavior.
- A concurrent profile update between preservation read and write must still return the existing 409 conflict; Task 2 retains the optimistic-concurrency test.

---

### Task 1: Domain contract and forward migration

**Files:**
- Modify: `backend/app/modules/patients/domain.py`
- Modify: `backend/app/modules/patients/infrastructure.py`
- Create: `backend/migrations/versions/0011_masked_aadhaar_last_four.py`
- Modify: `backend/tests/test_patient_domain.py`
- Modify: `backend/tests/test_p5_domain_boundaries.py`
- Modify: `backend/tests/integration/test_postgres_p5_persistence.py`

**Interfaces:**
- Produces: `PatientDemographics.aadhaar_last_four: str | None`, validated by `^[0-9]{4}$`.
- Produces: nullable `patient_demographics.aadhaar_last_four VARCHAR(4)` with named ASCII-digit constraint; removes runtime `demo_aadhaar_reference`.

- [ ] **Step 1: Write failing domain, metadata, migration, and PostgreSQL tests**

Assert valid suffixes, malformed/Unicode rejection, absence of the old ORM field, exact new column/constraint, no historical-value copy, persistence round trip, direct-SQL rejection, and downgrade/upgrade restoration.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `cd backend; uv run pytest tests/test_patient_domain.py tests/test_p5_domain_boundaries.py -q`

Run with PostgreSQL: `cd backend; uv run pytest tests/integration/test_postgres_p5_persistence.py -q -m postgres`

Expected: FAIL because the domain and schema still expose the synthetic reference.

- [ ] **Step 3: Implement the domain rename, mapper changes, and `patient_aadhaar_0011` migration**

The migration adds the nullable suffix, drops the old constraint/column without copying values, and reverses by restoring the old nullable column/constraint before dropping the suffix.

- [ ] **Step 4: Run focused tests and migration round trip**

Expected: focused tests PASS; one Alembic head; clean upgrade/current/check; downgrade to `patient_details_0010` restores the old column; re-upgrade restores only the suffix column.

- [ ] **Step 5: Commit**

Commit message: `Persist only masked Aadhaar profile suffix`

### Task 2: Transient backend write and preservation semantics

**Files:**
- Modify: `backend/app/modules/patients/api.py`
- Modify: `backend/tests/patients/test_profile_update.py`
- Modify: `backend/tests/integration/test_patient_accounts_postgres.py`

**Interfaces:**
- Consumes: Task 1 `aadhaar_last_four` domain field.
- Produces: write-only `DemographicsRequest.aadhaar_number: SecretStr | None`; read-only `DemographicsResponse.aadhaar_last_four: str | None`.
- Produces: a request-to-domain helper that extracts `get_secret_value()[-4:]` or preserves an existing suffix when the request value is null.

- [ ] **Step 1: Write failing API tests**

Assert exact 12-digit acceptance, suffix-only response, no complete digits in serialized response/repr/error, malformed and Unicode rejection, blank replacement preservation, valid replacement, anonymous/cross-subject denial, and unchanged 409 behavior.

- [ ] **Step 2: Run focused API tests and verify RED**

Run: `cd backend; uv run pytest tests/patients/test_profile_update.py tests/integration/test_patient_accounts_postgres.py -q`

Expected: FAIL on missing write/read separation.

- [ ] **Step 3: Implement `SecretStr` input conversion and existing-suffix preservation**

Read the current self-scoped patient before update only to obtain the suffix. Let the existing expected timestamp reject a race. Never pass the complete number into the domain or persistence layer.

- [ ] **Step 4: Run focused API tests**

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `Protect Aadhaar input at the patient API boundary`

### Task 3: Same-origin BFF read/write separation

**Files:**
- Modify: `apps/patient-web/lib/patient/contracts.ts`
- Modify: `apps/patient-web/lib/patient/server.ts`
- Modify: `apps/patient-web/tests/patient-profile-bff.test.ts`

**Interfaces:**
- Produces: `PatientDemographics.aadhaarLastFour: string | null` for reads.
- Produces: `PatientDemographicsSubmission.aadhaarNumber: string | null` for writes.
- Maps `aadhaarNumber` to backend `aadhaar_number`; maps backend `aadhaar_last_four` to `aadhaarLastFour`.

- [ ] **Step 1: Write failing BFF tests**

Assert exact allowlists, accepted/generated 12 digits, short/long/formatted/Unicode rejection, suffix-only reads, no full-number response, blank replacement forwarding as null, no-store responses, minimized errors, origin validation, and anonymous denial.

- [ ] **Step 2: Run the BFF test and verify RED**

Run: `pnpm --filter @swasthyasetu/patient-web test -- patient-profile-bff.test.ts`

Expected: FAIL on old contract names and formats.

- [ ] **Step 3: Implement separate read and submission contracts plus exact runtime guards**

Use ASCII `[0-9]`; do not normalize formatted input into acceptance.

- [ ] **Step 4: Run the BFF test, lint, and typecheck**

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `Separate Aadhaar write input from masked profile reads`

### Task 4: Realistic masked patient UI

**Files:**
- Modify: `apps/patient-web/components/profile-fields.tsx`
- Modify: `apps/patient-web/components/profile-setup-wizard.tsx`
- Modify: `apps/patient-web/components/profile-form.tsx`
- Modify: `apps/patient-web/tests/patient-profile-ui.test.tsx`
- Modify: `tests/e2e/support/patient-account.ts`

**Interfaces:**
- Consumes: Task 3 `aadhaarNumber` write and `aadhaarLastFour` read fields.
- Produces: `maskedAadhaar(lastFour)` returning `•••• •••• 1234` or no display for null.
- Produces: required first-login numeric entry and optional blank replacement input for completed profiles.

- [ ] **Step 1: Write failing UI tests**

Generate 12-digit test values from shorter string fragments. Assert label/copy, exact validation, Unicode/format rejection, masked review with no full digits in DOM, single final submission, completed-profile masking, blank preservation submission, valid replacement, and absence of Aadhaar-specific demo/synthetic text.

- [ ] **Step 2: Run focused UI tests and verify RED**

Run: `pnpm --filter @swasthyasetu/patient-web test -- patient-profile-ui.test.tsx`

Expected: FAIL on old wording and contract.

- [ ] **Step 3: Implement transient input, masking, and replacement UI**

Use `inputMode="numeric"`, `maxLength={12}`, `pattern="[0-9]{12}"`, `autoComplete="off"`, content-free errors, and never render the complete number on review.

- [ ] **Step 4: Update the real browser helper and run UI/accessibility checks**

Expected: focused UI tests, patient suite, lint, typecheck, formatting, and Playwright discovery PASS.

- [ ] **Step 5: Commit**

Commit message: `Present Aadhaar input with masked profile display`

### Task 5: Documentation, privacy audit, and complete verification

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/DEMO_GUIDE.md`
- Modify: `README.md` only if current patient onboarding copy references the removed field

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: accurate migration assertions, current demo instructions, verified PR, and merged change after six green CI jobs.

- [ ] **Step 1: Update current CI schema assertions and demo instructions**

Document exactly-12-digit fictional college-demo input, last-four-only retention, masking, and non-verification without exposing a contiguous 12-digit fixture.

- [ ] **Step 2: Run complete backend and PostgreSQL verification**

Run the backend quality gate, clean migration/current/check, all PostgreSQL tests, and the new revision downgrade/upgrade. Expected: PASS.

- [ ] **Step 3: Run complete frontend and browser verification**

Run formatting, lint, typecheck, all frontend tests/builds, and all Playwright journeys against real FastAPI/PostgreSQL. Expected: PASS.

- [ ] **Step 4: Run privacy and security verification**

Search current runtime files for old field/copy, contiguous 12-digit Aadhaar fixtures, logging, browser persistence, full-number response keys, and unsafe database columns. Run Gitleaks, Trivy filesystem/image scans, Compose validation, and `git diff --check`. Expected: no finding.

- [ ] **Step 5: Visually verify first setup, masked review, completed editor, and 320px layout**

Expected: no full number rendered after entry, no Aadhaar demo wording, no overflow, and local PostgreSQL remains connected.

- [ ] **Step 6: Whole-branch review and one fix pass**

Review privacy boundaries, migration reversibility, concurrency preservation, response minimization, and UI masking against the spec.

- [ ] **Step 7: Commit, push, open PR, verify six jobs, and merge**

Commit message: `Verify masked Aadhaar profile handling`
