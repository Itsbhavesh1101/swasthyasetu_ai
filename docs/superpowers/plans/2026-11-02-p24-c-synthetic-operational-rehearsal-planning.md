# P24-C Synthetic Operational Rehearsal Planning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an immutable, detached P24-C metadata contract for proposed synthetic operational rehearsals without executing or approving any drill.

**Architecture:** Add one unregistered pure-contract module under `app.validation`, mirroring the strict P24-A/P24-B boundary while owning a distinct P24 operational-rehearsal vocabulary. The builder fails closed outside local/test, canonicalizes an exact eight-scenario inventory, and exposes no result or operational action.

**Tech Stack:** Python 3.12 dataclasses, `StrEnum`, standard-library hashing/JSON/datetime, pytest, existing FastAPI module-registry smoke boundary.

**Spec:** `docs/superpowers/specs/2026-11-02-p24-c-synthetic-operational-rehearsal-planning-design.md`

## Global Constraints

- Implement P24-C planning integrity only; do not execute a rehearsal or record evidence/results.
- Preserve all P8-C, P9-C, P10, P11, P22, P23, and P24 governance restrictions.
- Add no dependencies, persistence, migration, API, UI, event, job, feature flag, infrastructure, or CI change.
- Permit only `LOCAL` and `TEST`; reject `STAGING`, `PILOT`, and `PRODUCTION` before caller input inspection.
- Keep every P24 and product-level acceptance criterion unverified.

## Review Focus

- Hostile or overflowing timezone implementations must return only `INVALID_TYPE` without leaking supplied content.
- A manifest with exact cardinality but duplicate/missing scenarios must fail deterministically.
- Forced mutation of every plan or manifest boundary must be detected by snapshot reconstruction.
- Build/config drift between nested plans and the manifest must be rejected.
- No public execution, result, approval, evidence, deployment, or release authority may appear.

---

### Task 1: Strict release-rehearsal contracts

**Files:**

- Create: `backend/app/validation/release_rehearsal.py`
- Create: `backend/tests/test_synthetic_release_rehearsal_planning.py`

**Interfaces:**

- Consumes: `app.config.Environment` and standard-library immutable value types.
- Produces: `SyntheticReleaseRehearsalPlan`, `SyntheticReleaseRehearsalManifest`, snapshot helpers, and `build_synthetic_release_rehearsal_manifest(...)`.

- [ ] **Step 1: Write failing inventory and authority tests**

Define the exact eight-scenario enum, fixed authority labels, immutable plan behavior, and strict constructor expectations in tests before the module exists.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `py -m uv run pytest tests/test_synthetic_release_rehearsal_planning.py -q`

Expected: collection fails because `app.validation.release_rehearsal` does not exist.

- [ ] **Step 3: Implement minimal plan value objects**

Create strict enums, stable contract errors, machine grammar helpers, aware-UTC normalization, immutable plan construction, full fingerprint binding, and plan snapshots.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `py -m uv run pytest tests/test_synthetic_release_rehearsal_planning.py -q`

Expected: current plan tests pass.

- [ ] **Step 5: Add failing manifest, hostile-input, and isolation tests**

Cover canonical ordering, exact inventory, duplicates, build/config drift, chronology, hostile timezone values, protected-environment short circuiting, snapshot drift, content-free errors, prohibited authority, and absent runtime registration.

- [ ] **Step 6: Implement minimal manifest and builder behavior**

Add manifest construction, full fingerprint binding, snapshots, environment-first validation, exact-cardinality validation, canonical sorting, and exports local to the module.

- [ ] **Step 7: Run the focused test and verify GREEN**

Run: `py -m uv run pytest tests/test_synthetic_release_rehearsal_planning.py -q`

Expected: all P24-C tests pass.

- [ ] **Step 8: Commit**

```text
git add backend/app/validation/release_rehearsal.py backend/tests/test_synthetic_release_rehearsal_planning.py
git commit -m "feat(validation): add synthetic release rehearsal planning"
```

### Task 2: Public package surface and phase documentation

**Files:**

- Modify: `backend/app/validation/__init__.py`
- Create: `docs/implementation/P24_C_SYNTHETIC_OPERATIONAL_REHEARSAL_PLANNING.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**

- Consumes: Task 1's complete public contract.
- Produces: explicit package exports and an honest P24-C progress record.

- [ ] **Step 1: Write failing package-export and public-isolation tests**

Import every intended symbol through `app.validation`; verify no execution/result/approval surface and no FastAPI module or route registration.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `py -m uv run pytest tests/test_synthetic_release_rehearsal_planning.py -q`

Expected: imports fail until package exports are added.

- [ ] **Step 3: Add explicit exports**

Update only `app.validation.__init__` and `__all__`; do not register a runtime module.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `py -m uv run pytest tests/test_synthetic_release_rehearsal_planning.py -q`

Expected: all P24-C tests pass.

- [ ] **Step 5: Document bounded status**

Record exact scope, absent behavior, verification boundary, blockers, and that all live P24/product acceptance remains unverified. Add tracker section 110 without changing earlier history.

- [ ] **Step 6: Commit**

```text
git add backend/app/validation/__init__.py docs/implementation/P24_C_SYNTHETIC_OPERATIONAL_REHEARSAL_PLANNING.md docs/implementation/38_PROGRESS_TRACKER.md docs/superpowers/specs/2026-11-02-p24-c-synthetic-operational-rehearsal-planning-design.md docs/superpowers/plans/2026-11-02-p24-c-synthetic-operational-rehearsal-planning.md
git commit -m "docs(implementation): record P24-C rehearsal planning boundary"
```

### Task 3: Regression, security, and release-boundary verification

**Files:**

- Verify only; modify production/test files only through a RED-GREEN fix for a confirmed defect.

**Interfaces:**

- Consumes: Tasks 1 and 2.
- Produces: exact verification evidence for review and integration.

- [ ] **Step 1: Run focused and adjacent P23/P24 tests**

Run: `py -m uv run pytest tests/test_synthetic_recovery_planning.py tests/test_synthetic_release_evidence_planning.py tests/test_synthetic_release_safety_planning.py tests/test_synthetic_release_rehearsal_planning.py -q`

- [ ] **Step 2: Run backend quality and full test gates**

Run Ruff check/format, mypy, compileall, import smoke, Alembic single-head check, and `py -m uv run pytest -q`.

- [ ] **Step 3: Run unchanged frontend/ML/security/infrastructure gates**

Run the repository's locked frontend quality/build/test commands, ML test/type gates, `git diff --check`, Docker Compose validation/health where available, and local Gitleaks/Trivy checks where installed. Remote CI remains the authority for all six canonical jobs.

- [ ] **Step 4: Audit the final diff and request whole-branch review**

Compare the full branch against its merge base, verify only planned files changed, and obtain one fresh-context code review focused on the Review Focus list.

- [ ] **Step 5: Apply at most one Critical/Important RED-GREEN fix pass**

Defer Minor findings explicitly; rerun the full relevant suite after any required fix.

- [ ] **Step 6: Commit verified fixes, push, open PR, and merge only after exact-SHA CI**

Verify all six PR CI jobs, merge, then verify all six `main` jobs on the merge SHA before deleting the remote feature branch.
