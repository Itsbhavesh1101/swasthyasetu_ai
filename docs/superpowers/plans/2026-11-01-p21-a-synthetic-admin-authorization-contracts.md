# P21-A Synthetic Admin Authorization Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a detached, content-free synthetic admin authorization preflight that proves exact scope binding and fail-closed behavior without creating live authority.

**Architecture:** A strict immutable contract module owns validated engineering-only requests, grants, decisions, snapshots, and fingerprints. A pure evaluator rejects protected environments, reconstructs inputs, and returns only a synthetic match or abstention; it is never registered or exposed over HTTP.

**Tech Stack:** Python 3.12 dataclasses, enums, hashlib/json, pytest, Ruff, mypy

**Spec:** `docs/superpowers/specs/2026-11-01-p21-a-synthetic-admin-authorization-contracts-design.md`

## Global Constraints

- Engineering-synthetic, content-free, test/local only.
- No production roles, permissions, identity, MFA ceremony, patient/source/clinical data, or human approval.
- No API/UI, persistence/migration, events/jobs, dependencies, registration, or activation.
- Protected environments are rejected before request or grant inspection.
- Alembic head remains `p7a_0007`; all P21 live acceptance remains unverified.

## Review Focus

- Forced mutation of frozen requests or grants must be caught by boundary reconstruction.
- A match differing by one scope dimension or object version must abstain without enumeration detail.
- Duplicate semantic grants with different IDs must not create an ambiguous match.
- Naive and non-UTC clocks must be rejected or normalized consistently without widening validity.
- Protected environments must fail before malformed inputs are inspected.

---

### Task 1: Strict synthetic contracts

**Files:**
- Create: `backend/app/modules/admin_governance/__init__.py`
- Create: `backend/app/modules/admin_governance/contracts.py`
- Test: `backend/tests/test_admin_authorization_contracts.py`

**Interfaces:**
- Consumes: Python standard library only.
- Produces: immutable request, grant and decision contracts; closed enums; snapshot helpers.

- [ ] **Step 1: Write failing contract tests** for exact types, identifiers, UTC chronology, canonical fingerprints, duplicates, direct-constructor inconsistency, and forced mutation.
- [ ] **Step 2: Run tests and verify RED** due to the missing module.
- [ ] **Step 3: Implement the minimal strict contracts and exports.**
- [ ] **Step 4: Run focused tests, Ruff, and mypy and verify GREEN.**
- [ ] **Step 5: Commit** with `feat(admin): add synthetic authorization contracts`.

### Task 2: Fail-closed detached evaluator

**Files:**
- Create: `backend/app/modules/admin_governance/preflight.py`
- Modify: `backend/app/modules/admin_governance/__init__.py`
- Test: `backend/tests/test_admin_authorization_preflight.py`

**Interfaces:**
- Consumes: Task 1 snapshot helpers and contracts; `app.config.Environment`.
- Produces: `evaluate_synthetic_admin_preflight(request, grants, evaluated_at, environment)`.

- [ ] **Step 1: Write failing evaluator tests** for exact match, MFA denial, missing/stale/future/mismatched/ambiguous grants, canonical order, clocks, and protected environments.
- [ ] **Step 2: Run tests and verify RED** due to the missing evaluator.
- [ ] **Step 3: Implement the minimal pure evaluator.**
- [ ] **Step 4: Run both focused suites, Ruff, and mypy and verify GREEN.**
- [ ] **Step 5: Commit** with `feat(admin): evaluate synthetic authorization preflight`.

### Task 3: Boundary evidence and tracker

**Files:**
- Create: `backend/tests/test_admin_authorization_boundaries.py`
- Create: `docs/implementation/P21_A_SYNTHETIC_ADMIN_AUTHORIZATION_CONTRACTS.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**
- Consumes: Tasks 1 and 2 public surface.
- Produces: regression evidence that the module is detached and P21 remains partial.

- [ ] **Step 1: Write failing adversarial boundary tests** for mutation, semantic aliases, non-enumerating decisions, route/registry absence, and no approval/execution surface.
- [ ] **Step 2: Run tests and verify RED** on at least one uncovered invariant.
- [ ] **Step 3: Make the smallest contract/evaluator correction needed for GREEN.**
- [ ] **Step 4: Record scope, tests, non-claims, and blockers without changing live acceptance status.**
- [ ] **Step 5: Run focused and full repository verification.**
- [ ] **Step 6: Commit** with `test(admin): harden synthetic authorization boundary`.
