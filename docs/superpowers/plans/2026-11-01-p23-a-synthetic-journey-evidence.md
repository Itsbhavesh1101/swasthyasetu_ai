# P23-A Synthetic Journey Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a detached, immutable, synthetic-only P23-A journey inventory and evidence-consistency foundation without executing or approving any live journey.

**Architecture:** A new unregistered `app.validation` package separates strict immutable contracts from pure manifest/evidence mechanics. Protected environments and blocked journeys short-circuit before caller-controlled evidence is inspected; all returned states remain engineering-only and unverified.

**Tech Stack:** Python 3.12, frozen/slotted dataclasses, `StrEnum`, SHA-256 canonical fingerprints, pytest, Ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-11-01-p23-a-synthetic-journey-evidence-design.md`

## Global Constraints

- No live E2E execution, patient/clinical data, clinical oracle, accessibility certification, load measurement, recovery drill, network, or external call.
- No persistence, migration, API/UI, event/job, dependency, feature flag, module registration, or runtime activation.
- Only `LOCAL` and `TEST` environments are permitted; protected environments reject before input inspection.
- Results never use `PASS`, approval, promotion, release, or production-authority semantics.
- P23 and all `AC-P23-001..012` remain partial/live-not-verified.

## Review Focus

- A blocked journey supplied a hostile observation: evaluator must abstain without reading it.
- A protected environment supplied hostile definitions: builder/evaluator must reject before reading them.
- A direct constructor combines valid fingerprints with mismatched nested evidence: reconstruction must reject it.
- The 18-entry manifest contains aliases, a missing journey, or duplicate IDs: construction must fail closed.
- An aware non-UTC clock or a naive clock is supplied: aware values normalize to UTC; naive values reject.

---

### Task 1: Strict synthetic journey evidence contracts

**Files:**

- Create: `backend/app/validation/__init__.py`
- Create: `backend/app/validation/contracts.py`
- Test: `backend/tests/test_synthetic_journey_evidence_contracts.py`

**Interfaces:**

- Consumes: canonical 18-journey list in `docs/34_MASTER_IMPLEMENTATION_PLAN.md`
- Produces: strict journey enums, `SyntheticJourneyDefinition`, `SyntheticJourneyObservation`, `SyntheticJourneyEvidenceReceipt`, `SyntheticJourneyManifest`, snapshot helpers, and stable contract errors

- [ ] **Step 1: Write failing contract tests**

Cover exact inventory, strict type/value validation, immutable snapshots, direct-constructor consistency,
UTC behavior, deterministic fingerprints, manifest completeness/uniqueness/order, and content-free errors.

- [ ] **Step 2: Run the tests and verify RED**

Run: `python -m uv run pytest tests/test_synthetic_journey_evidence_contracts.py -q`
Expected: collection fails because `app.validation` does not exist.

- [ ] **Step 3: Implement minimal immutable contracts**

Implement the exported types and snapshot reconstruction in `contracts.py`; re-export the public surface
from `__init__.py` without registering the package.

- [ ] **Step 4: Run the tests and verify GREEN**

Run: `python -m uv run pytest tests/test_synthetic_journey_evidence_contracts.py -q`
Expected: all contract tests pass.

- [ ] **Step 5: Commit**

Commit message: `feat(validation): add synthetic journey evidence contracts`

### Task 2: Pure manifest and evidence mechanics

**Files:**

- Create: `backend/app/validation/evidence.py`
- Modify: `backend/app/validation/__init__.py`
- Test: `backend/tests/test_synthetic_journey_evidence.py`
- Test: `backend/tests/test_synthetic_journey_evidence_boundaries.py`

**Interfaces:**

- Consumes: Task 1 contract/snapshot interfaces and `app.config.Environment`
- Produces: `build_synthetic_journey_manifest(...)` and `evaluate_synthetic_journey_evidence(...)`

- [ ] **Step 1: Write failing behavior and boundary tests**

Cover canonical construction, deterministic replay, exact-match consistency, scope mismatch abstention,
blocked no-inspection abstention, protected-environment no-inspection rejection, capacity/completeness,
content-free failures, import/route isolation, and absence of execution/authority surfaces.

- [ ] **Step 2: Run the tests and verify RED**

Run: `python -m uv run pytest tests/test_synthetic_journey_evidence.py tests/test_synthetic_journey_evidence_boundaries.py -q`
Expected: collection fails because the mechanics are absent.

- [ ] **Step 3: Implement minimal pure mechanics**

Implement exact manifest construction and evidence evaluation. Check environment first; for blocked
definitions return an abstention receipt with no observation before observation access.

- [ ] **Step 4: Run focused and related tests**

Run: `python -m uv run pytest tests/test_synthetic_journey_evidence*.py -q`
Expected: all P23-A tests pass.

- [ ] **Step 5: Commit**

Commit message: `feat(validation): evaluate synthetic journey evidence`

### Task 3: Boundary documentation, tracker, and complete verification

**Files:**

- Create: `docs/implementation/P23_A_SYNTHETIC_JOURNEY_EVIDENCE.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**

- Consumes: verified implementation/test results from Tasks 1-2
- Produces: exact bounded-scope record and truthful P23 status

- [ ] **Step 1: Document the implemented boundary and unresolved gates**

Record scope, non-goals, test evidence, no runtime activation, and every remaining P23 approval blocker.
Append a minimal tracker entry with P23 `PARTIAL` and all live acceptance unverified.

- [ ] **Step 2: Run complete local verification**

Run backend and frontend quality gates, `git diff --check`, migration-head verification, focused privacy/
boundary audits, Docker/PostgreSQL checks where available, and list the Playwright suite.

- [ ] **Step 3: Perform whole-branch review and fix important findings with RED-to-GREEN tests**

Review contract invariants, input-order determinism, hostile direct constructors, protected-environment
short circuiting, error privacy, and runtime isolation.

- [ ] **Step 4: Commit**

Commit message: `docs(validation): record synthetic P23-A boundary`

- [ ] **Step 5: Push, open PR, verify all six PR CI jobs, merge, and verify all six main CI jobs**

Only merge after the exact feature SHA passes all six required jobs. Delete the merged remote feature
branch after the exact merge SHA passes all six main jobs.
