# P17-B Zero-Egress Synthetic Test Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a deterministic, test-only adapter for the opaque P17-A boundary without introducing official ABDM semantics, network access, runtime activation, or live acceptance claims.

**Architecture:** Keep all adapter implementation under `backend/tests/abdm_support`. The adapter snapshots an exact fingerprint-to-scenario mapping after a protected-environment check, revalidates every P17-A request before fixture lookup, constructs only existing content-free P17-A results, and validates the exact request/result binding before return. Production contracts remain unchanged.

**Tech Stack:** Python 3.12, frozen dataclasses/enums already in P17-A, pytest, Ruff, mypy.

---

### Task 1: Deterministic adapter and adversarial tests

**Files:**
- Create: `backend/tests/abdm_support/__init__.py`
- Create: `backend/tests/abdm_support/mock_adapter.py`
- Create: `backend/tests/test_synthetic_abdm_mock_adapter.py`

1. Write failing tests for exact accepted/rejected/unavailable scenarios, unknown requests, deterministic replay, snapshot isolation, request revalidation, clock normalization, malformed fixture entries, port conformance, and denial in staging/pilot/production before hostile fixtures or clocks are read.
2. Run the focused test file and confirm failure because the adapter module is absent.
3. Implement `MockABDMScenario` and `DeterministicMockABDMAdapter` with strict mapping snapshots, stable content-free errors, zero I/O imports, request fingerprint lookup, UTC result construction, and exact result validation.
4. Run the focused tests, Ruff and mypy; fix only failures within this scope.

### Task 2: Scope and acceptance documentation

**Files:**
- Create: `docs/implementation/P17_B_ZERO_EGRESS_SYNTHETIC_ADAPTER.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

1. Record the exact base SHA, test-only implementation, negative scope and live acceptance truth.
2. State explicitly that no official sandbox exists and `FR-ABDM-001..007` / `AC-P17-001..007` remain live-not-verified.
3. Update the P17 tracker note and append the next numbered evidence section without changing other phase status.

### Task 3: Full verification and integration

1. Run backend format, lint, mypy, complete pytest, compile/import smoke and Alembic-head checks.
2. Run unchanged frontend format, lint, typecheck, unit tests, builds and Playwright discovery.
3. Validate Compose configuration and `git diff --check`; review the complete diff for scope leakage.
4. Commit one clean feature commit, push, open a PR, and require all six CI jobs on the exact feature SHA.
5. Merge only after all six jobs pass, then require all six main-branch CI jobs on the merge SHA.

## Review Focus

- Protected environments must fail before fixture or clock access.
- Forced mutation of a P17-A request must fail before fixture lookup.
- Fixture mappings must be detached from caller mutation.
- Unknown fingerprints must fail closed without leaking identifiers.
- Non-UTC aware clocks must normalize to UTC; naive clocks must be rejected.
- The test adapter must contain no network, file, database, environment-variable, credential, endpoint, callback or official ABDM behavior.
