# Synthetic Quantum Planning Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a deterministic offline command demonstrating P19 request validation and non-executable planning with no quantum runtime.

**Architecture:** Refactor the Wave 9 composer to expose one private exact-evidence bundle, then compose P19-A/B into a strict receipt and CLI under `/ml`.

**Tech Stack:** Python 3.12 standard library, existing `ml.research` and `ml.quantum` contracts, unittest.

**Spec:** `docs/superpowers/specs/2026-11-03-synthetic-quantum-plan-demo-design.md`

## Global Constraints

- LOCAL/TEST only; no product runtime import.
- No quantum dependency or execution, no selected experiment configuration, and no comparison claim.
- No API, UI, persistence, migration, network, artifact, patient data, P19-C/D/E, or acceptance claim.

## Review Focus

- Protected environments reject before the P18 fixture is built.
- Request, gateway receipt, plan, and P18 candidate/card fingerprints remain exactly bound.
- All configurable quantum fields remain explicitly unselected.
- Direct construction and forced mutation cannot forge execution, approval, or claim states.
- CLI output is canonical, content-free, and fails non-zero for protected environments.

### Task 1: Exact P18 bundle and P19 composition

- [ ] Write failing `ml/tests/test_quantum_demo.py` unit tests.
- [ ] Verify RED due to missing `ml.quantum.demo`.
- [ ] Refactor `ml.research.demo` to provide a private immutable exact-evidence bundle without changing its public receipt/CLI.
- [ ] Implement strict `ml.quantum.demo` composition and receipt.
- [ ] Run focused and all research tests; commit `feat(qml): add synthetic quantum planning replay`.

### Task 2: CLI and governance handoff

- [ ] Add failing success/protected-environment subprocess tests.
- [ ] Implement canonical CLI JSON and stable errors.
- [ ] Update `ml/README.md` and progress tracker Wave 10 entry.
- [ ] Run full backend and frontend gates; commit `docs(qml): document synthetic quantum planning demo`.
