# P18-A Synthetic Dataset and Experiment Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an isolated, immutable, content-free synthetic dataset and experiment registry foundation for P18-A.

**Architecture:** Put standard-library-only contracts and immutable registries under `/ml`, never the patient backend package. Extend the existing quality gate to check this research tree without adding dependencies or runtime imports.

**Tech Stack:** Python 3.12 standard library, unittest, Ruff, mypy, existing CI tooling.

**Spec:** `docs/superpowers/specs/2026-10-31-p18-a-synthetic-dataset-experiment-registry-design.md`

## Global Constraints

- Synthetic, non-medical, engineering-only tokens; no real dataset, task, label, feature, model, metric, or claim.
- No dependency, lockfile, service, persistence, migration, API, worker, feature flag, module registration, or runtime activation.
- Research code stays under `/ml`; `backend/app` must not import it.
- Registries are immutable, explicitly version-pinned, and denied outside LOCAL/TEST before fixture inspection.
- P18 remains PARTIAL; `FR-ML-001..017` and `AC-P18-001..010` remain LIVE NOT VERIFIED.

## Review Focus

- Forged or mutated dataclass instances must be reconstructed and rejected, never trusted by type alone.
- Protected environments with hostile fixtures must fail before fixtures are inspected.
- Duplicate identity/version pairs and experiment-to-dataset fingerprint drift must fail closed.
- Registry snapshots must not change when caller-owned containers or nested records are mutated.
- Patient/backend source must remain free of imports from the isolated research package.

---

### Task 1: Strict synthetic research contracts

**Files:**
- Create: `ml/__init__.py`
- Create: `ml/research/__init__.py`
- Create: `ml/research/contracts.py`
- Create: `ml/tests/test_contracts.py`

**Interfaces:**
- Produces: `SyntheticDatasetManifest`, `SyntheticExperimentRecord`, their closed enums, stable errors, validation functions, and fingerprint functions.

- [ ] Write contract tests first for valid construction, non-UTC normalization, naive time rejection, invalid types/values, direct-constructor invariants, forced mutation reconstruction, deterministic fingerprints, and content-free errors.
- [ ] Run `python -m unittest ml.tests.test_contracts -v`; verify failures are caused by the missing package.
- [ ] Implement frozen slot dataclasses with strict exact-type validation, closed symbolic identities, exact lowercase hashes, canonical UTC, and stable non-echoing error codes.
- [ ] Re-run the focused tests and verify they pass.

### Task 2: Immutable version-pinned registries

**Files:**
- Create: `ml/research/registry.py`
- Create: `ml/tests/test_registry.py`

**Interfaces:**
- Consumes: Task 1 validators and fingerprints.
- Produces: `SyntheticDatasetRegistry` and `SyntheticExperimentRegistry` with tuple snapshots, bounded construction, and exact `resolve` methods.

- [ ] Write registry tests first for exact resolution, unknown identity, duplicates, oversize input, caller mutation, forged records, dataset-fingerprint mismatch, and protected-environment short-circuiting with hostile input.
- [ ] Run `python -m unittest ml.tests.test_registry -v`; verify failures are caused by the missing registry module.
- [ ] Implement environment-first validation and immutable mapping snapshots; expose no mutation, promotion, latest-version, or execution method.
- [ ] Re-run the focused tests and verify they pass.

### Task 3: Enforced research isolation and documentation

**Files:**
- Create: `ml/tests/test_isolation.py`
- Modify: `scripts/quality_gate.py`
- Create: `docs/implementation/P18_A_SYNTHETIC_DATASET_EXPERIMENT_REGISTRY.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**
- Consumes: Tasks 1-2 research package and existing quality entry point.
- Produces: CI-enforced Ruff, formatting, strict mypy, unittest, compile, and backend-import isolation checks for `/ml`.

- [ ] Write an AST-based test first that fails if `backend/app` imports `ml` or `ml.research`.
- [ ] Extend the backend quality entry point with `/ml` lint, format, strict typing, tests, and compile checks using the existing locked toolchain.
- [ ] Document the exact base, bounded behavior, negative scope, unchanged dependencies/schema, and unverified live P18 criteria; keep P18 partial.
- [ ] Run focused research checks, the complete backend/frontend quality gates, Compose validation, Alembic-head verification, security/diff review, and confirm no dependency or migration drift.
- [ ] Commit once, push, open a PR, require all six CI jobs on the exact SHA, merge only when green, then require all six jobs on the merge SHA.
