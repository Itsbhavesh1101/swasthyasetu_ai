# P21-D Synthetic Audit and Maker-Checker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build immutable, deterministic, content-free P21-D separation-of-duty and audit-snapshot mechanics without live governance authority or runtime activation.

**Architecture:** Add one focused contract module under the existing detached `admin_governance` package and one pure mechanics module. Export the bounded API from the package while preserving non-registration and the absence of routes, persistence, search, and executable actions.

**Tech Stack:** Python 3.12, frozen/slotted dataclasses, `StrEnum`, SHA-256 canonical JSON fingerprints, pytest, Ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-11-01-p21-d-synthetic-audit-maker-checker-design.md`

## Global Constraints

- Local/test engineering-synthetic inputs only; protected environments fail before input inspection.
- At most 16 audit receipts; tuple-only collections; strict closed types and machine-shaped values.
- An independence receipt is never an approval, publication, activation, or execution decision.
- No patient/clinical content, real identity/authority, persistence, API/UI, search/export, dependency, registration, or activation.
- P21 remains PARTIAL and `FR-ADMIN-*`, `FR-AUDIT-*`, and `AC-P21-*` remain live unverified.

## Review Focus

- A maker checking their own proposal must abstain without creating an approval-like result.
- A distinct checker with stale or mismatched object/scope metadata must also abstain.
- Direct constructors and forced mutation must not bypass receipt/snapshot consistency.
- Duplicate check identities and aliased receipts for one proposal revision must be rejected.
- Protected environments must reject before touching hostile proposals, submissions, receipts, or clocks.

---

### Task 1: Strict governance evidence contracts

**Files:**

- Create: `backend/app/modules/admin_governance/governance_evidence_contracts.py`
- Test: `backend/tests/test_admin_governance_evidence_contracts.py`

**Interfaces:**

- Produces: `GovernanceEvidenceContractCode`, `GovernanceEvidenceContractError`, `SyntheticGovernanceChangeKind`, `SyntheticIndependenceDisposition`, `SyntheticIndependenceReason`, `SyntheticGovernanceProposal`, `SyntheticCheckerSubmission`, `SyntheticMakerCheckerReceipt`, `SyntheticGovernanceAuditSnapshot`, and reconstruction helpers.

- [ ] Write constructor, normalization, immutability, fingerprint, strict-value, consistency, drift, chronology, duplicate/alias, and content-free-error tests.
- [ ] Run the focused test and confirm import failure because the contracts are absent.
- [ ] Implement the minimal strict frozen contracts and reconstruction helpers.
- [ ] Run the focused test and confirm all contract tests pass.

### Task 2: Fail-closed independence evaluator and audit builder

**Files:**

- Create: `backend/app/modules/admin_governance/governance_evidence.py`
- Modify: `backend/app/modules/admin_governance/__init__.py`
- Test: `backend/tests/test_admin_governance_evidence.py`
- Test: `backend/tests/test_admin_governance_evidence_boundaries.py`

**Interfaces:**

- Consumes: Task 1 contracts.
- Produces: `evaluate_synthetic_maker_checker(proposal, submission, *, evaluated_at, environment) -> SyntheticMakerCheckerReceipt` and `build_synthetic_governance_audit_snapshot(receipts, *, snapshot_id, generated_at, environment) -> SyntheticGovernanceAuditSnapshot`.

- [ ] Write exact-match, self-review, scope-drift, chronology, deterministic-ordering, duplicate/alias, capacity, protected-environment, forced-mutation, no-route, and forbidden-surface tests.
- [ ] Run focused tests and confirm failure because the mechanics and exports are absent.
- [ ] Implement environment-first rejection, reconstruction, closed abstention, canonical ordering, uniqueness, and snapshot construction.
- [ ] Run all P21 tests and confirm they pass.

### Task 3: Scope documentation and full verification

**Files:**

- Create: `docs/implementation/P21_D_SYNTHETIC_AUDIT_MAKER_CHECKER.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**

- Records bounded implementation truth; creates no runtime interface.

- [ ] Record the exact baseline, invariants, exclusions, acceptance truth, and P21 PARTIAL status.
- [ ] Run backend/frontend quality gates, migration-head check, diff/scope/privacy checks, and complete self-review.
- [ ] Commit, push, open a PR, verify all six CI jobs on the exact SHA, merge after success, and verify all six jobs on merged `main`.

