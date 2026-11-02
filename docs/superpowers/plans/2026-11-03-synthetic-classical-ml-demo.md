# Synthetic Classical ML Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an offline deterministic command that demonstrates the existing P18 synthetic classical-ML mechanics without entering product runtime or making a clinical claim.

**Architecture:** A new `ml.research.demo` module composes the existing P18-A through P18-D contracts over one fixed non-medical in-memory fixture and returns a strictly validated content-free receipt. The same module provides a canonical JSON CLI; production backend and frontend code remain unchanged.

**Tech Stack:** Python 3.12 standard library, existing `ml.research` contracts, `unittest`, existing backend `uv` quality gate.

**Spec:** `docs/superpowers/specs/2026-11-03-synthetic-classical-ml-demo-design.md`

## Global Constraints

- Keep all executable code under `/ml`; `backend/app` must not import `ml`.
- Accept only `ResearchEnvironment.LOCAL` and `ResearchEnvironment.TEST`.
- Use fixed synthetic non-medical rows and symbolic classes only.
- Preserve `ENGINEERING_ONLY`, `TEST_ONLY_UNAPPROVED`, and `NO_PERFORMANCE_OR_CLINICAL_CLAIM`.
- Add no dependency, persistence, migration, API, UI, network, artifact, activation, P18-E, or P19 behavior.
- Do not claim any live `FR-ML-*` or `AC-P18-*` criterion is satisfied.

## Review Focus

- A protected environment must be rejected before fixture construction or processing.
- The receipt must not allow forged approval, activation, claim, count, or provenance values.
- Training labels and preprocessor fitting must remain confined to the training partition.
- Locked-test expected/predicted membership must be exact and non-degenerate.
- CLI output must remain deterministic, content-free, machine-readable, and non-zero on failure.

---

### Task 1: Deterministic research replay and receipt

**Files:**
- Create: `ml/research/demo.py`
- Create: `ml/tests/test_demo.py`

**Interfaces:**
- Consumes: existing P18 registry, pipeline, baseline, card, and candidate APIs.
- Produces: `SyntheticClassicalDemoReceipt`, `validate_synthetic_classical_demo_receipt(value)`, and `run_synthetic_classical_demo(environment)`.

- [ ] **Step 1: Write failing replay tests**

Add tests proving deterministic replay, exact local/test states, partition/count consistency,
64-character provenance fingerprints, candidate registry resolution, direct-constructor rejection,
forced-mutation rejection, and protected-environment failure.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `backend/.venv/Scripts/python.exe -m unittest ml.tests.test_demo -v`

Expected: import failure because `ml.research.demo` does not exist.

- [ ] **Step 3: Implement the minimal replay**

Implement the immutable strict receipt and the fixed in-memory P18-A-D composition. Validate the
environment before calling the private fixture builder. Derive the dataset hashes from the fixed
fixture and expose no feature values or row-level labels in the receipt.

- [ ] **Step 4: Run focused and research tests**

Run: `backend/.venv/Scripts/python.exe -m unittest ml.tests.test_demo -v`

Expected: PASS.

Run: `backend/.venv/Scripts/python.exe -m unittest discover -s ml/tests -t . -v`

Expected: all research tests PASS.

- [ ] **Step 5: Commit**

Commit message: `feat(ml): add synthetic classical replay`

### Task 2: Canonical CLI and governance handoff

**Files:**
- Modify: `ml/research/demo.py`
- Modify: `ml/tests/test_demo.py`
- Modify: `ml/README.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**
- Consumes: Task 1's validated receipt and replay function.
- Produces: `python -m ml.research.demo --environment LOCAL|TEST` canonical JSON command.

- [ ] **Step 1: Write failing subprocess tests**

Add tests proving a `TEST` invocation exits zero with a strict canonical JSON object and a
`PRODUCTION` invocation exits non-zero with only `PROTECTED_ENVIRONMENT` in a content-free error
object.

- [ ] **Step 2: Run the CLI tests and verify RED**

Run: `backend/.venv/Scripts/python.exe -m unittest ml.tests.test_demo -v`

Expected: FAIL because the CLI entrypoint is absent.

- [ ] **Step 3: Implement the CLI and documentation**

Add strict environment parsing, canonical sorted JSON, stable content-free failure handling, README
usage/boundaries, and a new college-demo Wave 9 tracker entry that leaves canonical P18 partial and
all live acceptance unverified.

- [ ] **Step 4: Run focused and full quality gates**

Run: `backend/.venv/Scripts/python.exe -m unittest ml.tests.test_demo -v`

Expected: PASS.

Run: `python scripts/quality_gate.py backend`

Expected: full backend/research gate PASS with Alembic head unchanged at `p7a_0007`.

- [ ] **Step 5: Commit**

Commit message: `docs(ml): document synthetic classical demo`

