# P18-D Synthetic Candidate Metadata and Model Cards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build immutable, synthetic-only candidate metadata and model-card mechanics that bind an
exact P18-C baseline to a reproducibly recomputed P18-B locked-test evaluation.

**Architecture:** A new isolated research module owns closed model-card and candidate contracts,
evidence-bound builders, canonical fingerprints, and an immutable exact-lookup registry. It composes
existing P18-B/C validators and prediction/evaluation functions and never enters the backend runtime.

**Tech Stack:** Python 3.12 standard library, frozen slot dataclasses, `unittest`/pytest.

**Spec:** `docs/superpowers/specs/2026-11-01-p18-d-synthetic-candidate-model-cards-design.md`

## Global Constraints

- Synthetic, non-medical fixtures only; only `LOCAL` and `TEST` environments are permitted.
- Every card and candidate remains `TEST_ONLY_UNAPPROVED` with `ENGINEERING_ONLY` authority.
- No new dependency, artifact, serialization, persistence, migration, API, UI, worker, service,
  backend import, runtime inference, P18-E, or P19 behavior.
- No free-form purpose, limitation, metric, or model-card narrative.
- All failures are stable and content-free; all nested trust-boundary values are reconstructed.
- All live `FR-ML-001..017` and `AC-P18-001..010` outcomes remain NOT VERIFIED.

## Review Focus

- A valid-looking evaluation from a different model must not be attributed to the candidate.
- A direct constructor or forced mutation must not bypass model/card/count/fingerprint consistency.
- Duplicate candidate identities or aliases for the same model/card must fail closed.
- Protected environments must reject before hostile caller collections are inspected.
- Naive timestamps and unbounded/free-form metadata must not enter registry records.

---

### Task 1: Evidence-bound model cards

**Files:**
- Create: `ml/research/candidates.py`
- Modify: `ml/research/pipeline.py`
- Test: `ml/tests/test_candidates.py`

**Interfaces:**
- Consumes: P18-B/C validators, fingerprints, `predict_synthetic_baseline`, and
  `evaluate_synthetic_labels`.
- Produces: `SyntheticModelCard`, `build_synthetic_model_card`,
  `validate_synthetic_model_card`, and `synthetic_model_card_fingerprint`.

- [ ] **Step 1: Write failing card contract and evidence-binding tests**

Cover deterministic construction, exact recomputation, mismatched evaluation/model/split rejection,
closed limitations, UTC handling, direct construction, forced mutation, content-free errors, and
protected-environment short circuiting.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `python -m pytest ml/tests/test_candidates.py -q`
Expected: collection fails because `ml.research.candidates` does not exist.

- [ ] **Step 3: Implement minimal card contracts and public evaluation validator**

Add reconstructing validators, canonical fingerprints, fixed closed metadata, and recomputation of
the locked-test evaluation before card issuance.

- [ ] **Step 4: Run focused and research tests and verify GREEN**

Run: `python -m pytest ml/tests/test_candidates.py ml/tests/test_baselines.py ml/tests/test_pipeline.py -q`
Expected: all pass.

### Task 2: Candidate records and immutable registry

**Files:**
- Modify: `ml/research/candidates.py`
- Modify: `ml/tests/test_candidates.py`

**Interfaces:**
- Consumes: validated `SyntheticBaselineModel` and `SyntheticModelCard` snapshots.
- Produces: `SyntheticModelCandidate`, `build_synthetic_model_candidate`,
  `SyntheticCandidateRegistry`, exact `resolve`, and canonical fingerprints.

- [ ] **Step 1: Write failing candidate and registry tests**

Cover deterministic binding, exact lookup, unknown/duplicate identity, model/card alias rejection,
bounded capacity, immutable snapshots, forbidden promotion/activation/serialization surfaces, and
protected-environment rejection.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `python -m pytest ml/tests/test_candidates.py -q`
Expected: failures for missing candidate and registry interfaces.

- [ ] **Step 3: Implement minimal candidate and registry mechanics**

Use exact identity maps and reconstructed immutable snapshots; expose no mutating registration or
lifecycle transition method.

- [ ] **Step 4: Run the complete research suite and verify GREEN**

Run: `python -m pytest ml/tests -q`
Expected: all pass.

### Task 3: Phase evidence and full verification

**Files:**
- Create: `docs/implementation/P18_D_SYNTHETIC_CANDIDATE_MODEL_CARDS.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**
- Consumes: verified Task 1-2 behavior and canonical P18 governance documents.
- Produces: truthful P18-D scope, acceptance status, and next-action record.

- [ ] **Step 1: Document implemented mechanics and explicit negative scope**

Record P18 as PARTIAL, all live P18 criteria as NOT VERIFIED, P19 as blocked, and no runtime or
artifact authority.

- [ ] **Step 2: Run repository quality, security, boundary, and diff checks**

Run the full backend/research gate, frontend gate, Compose validation, migration check, architecture
searches, forbidden dependency/serialization searches, and `git diff --check`.
Expected: all applicable checks pass with unchanged dependency locks and Alembic head.

- [ ] **Step 3: Review the complete branch against the design and canonical documents**

Expected: no Important/Critical finding remains and every scope statement matches executable code.

- [ ] **Step 4: Commit, push, open PR, and verify all six CI jobs on the exact SHA**

Expected: Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL,
Playwright Chromium, and Security scans all pass before merge.
