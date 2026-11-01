# P21-C Synthetic Review Queue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build immutable, deterministic, content-free P21-C synthetic review queue contracts without live clinical authority or runtime activation.

**Architecture:** Add one focused contract module under the existing detached `admin_governance` package and one pure builder module. Export the bounded API from the package while retaining the existing non-registration and no-route boundary.

**Tech Stack:** Python 3.12, frozen/slotted dataclasses, `StrEnum`, SHA-256 canonical JSON fingerprints, pytest, Ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-11-01-p21-c-synthetic-review-queue-design.md`

## Global Constraints

- Local/test engineering-synthetic inputs only; protected environments fail before input inspection.
- Maximum 16 queue items; tuple-only collections; strict closed types and machine-shaped values.
- No patient/clinical content, identity/assignment, review action, persistence, API/UI, dependency, registration, or activation.
- P10 live remains 0/9 approved and P21 remains PARTIAL.

## Review Focus

- Hostile getters or forged dataclass mutation must fail with stable content-free errors.
- Duplicate IDs and different IDs aliasing one semantic object revision must both be rejected.
- Naive clocks, non-UTC aware clocks, and pre-item snapshot clocks must behave deliberately.
- Protected environments must reject before touching hostile queue inputs or clocks.
- The snapshot must expose no confirm/reject/correct/assign/authorize/execute surface.

---

### Task 1: Strict queue contracts

**Files:**
- Create: `backend/app/modules/admin_governance/review_queue_contracts.py`
- Test: `backend/tests/test_admin_review_queue_contracts.py`

**Interfaces:**
- Produces: `ReviewQueueContractCode`, `ReviewQueueContractError`, `SyntheticReviewItemKind`, `SyntheticReviewItemState`, `SyntheticReviewQueueItem`, `SyntheticReviewQueueSnapshot`, `snapshot_review_queue_item`, and `snapshot_review_queue`.

- [ ] Write constructor, normalization, immutability, fingerprint, drift, strict-value, forbidden-field, and content-free-error tests.
- [ ] Run the focused test and confirm import failure because the contract module is absent.
- [ ] Implement the minimal strict frozen contracts and snapshot reconstruction helpers.
- [ ] Run the focused test and confirm all contract tests pass.

### Task 2: Deterministic fail-closed builder

**Files:**
- Create: `backend/app/modules/admin_governance/review_queue.py`
- Modify: `backend/app/modules/admin_governance/__init__.py`
- Test: `backend/tests/test_admin_review_queue_projection.py`
- Test: `backend/tests/test_admin_review_queue_boundaries.py`

**Interfaces:**
- Consumes: Task 1 contracts.
- Produces: `build_synthetic_review_queue(items: tuple[SyntheticReviewQueueItem, ...], *, snapshot_id: str, generated_at: datetime, environment: Environment) -> SyntheticReviewQueueSnapshot`.

- [ ] Write deterministic ordering, duplicate/alias, capacity, chronology, protected-environment, forced-mutation, no-route, and no-action-surface tests.
- [ ] Run focused tests and confirm failure because the builder/export is absent.
- [ ] Implement environment-first rejection, reconstruction, ordering, uniqueness, chronology, and snapshot construction.
- [ ] Run all P21-C and existing P21-A tests and confirm they pass.

### Task 3: Scope documentation and full verification

**Files:**
- Create: `docs/implementation/P21_C_SYNTHETIC_REVIEW_QUEUE.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**
- Records bounded implementation truth; creates no runtime interface.

- [ ] Record exact baseline, implemented invariants, exclusions, acceptance truth, and P21 PARTIAL status.
- [ ] Run backend/frontend quality gates, migration-head check, diff/scope/privacy checks, and complete self-review.
- [ ] Commit, push, open a PR, verify all six CI jobs on the exact SHA, merge after success, and verify all six jobs on merged `main`.
