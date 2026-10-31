# P20-A Synthetic Care-Composition Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a detached engineering-synthetic contract kernel that binds exact evidence and
candidate metadata and can only preserve all candidates or abstain.

**Architecture:** A new unregistered `care_orchestration` package contains strict immutable
contracts and one pure composition function. It imports no upstream domain implementation, accesses
no data, applies no clinical precedence, and exposes no runtime surface.

**Tech Stack:** Python 3.12+, frozen/slotted dataclasses, `StrEnum`, hashlib/JSON canonicalization,
pytest, Ruff, mypy.

**Spec:**
`docs/superpowers/specs/2026-11-01-p20-a-synthetic-care-composition-contracts-design.md`

## Global Constraints

- Engineering-synthetic, nonclinical, unverified metadata only.
- No patient/subject/session/encounter/actor/institution identifiers or narrative payloads.
- No ranking, suppression, promotion, policy evaluation, clinical precedence, or source mutation.
- No route, registration, persistence, migration, event, job, flag, network, UI, dependency, or
  protected-environment activation.
- Every failure uses a closed content-free error code.
- Alembic head remains `p7a_0007`.

## Review Focus

- Forced mutation after construction must be caught by boundary reconstruction.
- An unavailable evidence item must short-circuit before hostile candidate inspection.
- Candidate evidence ID/version/hash/channel drift must fail closed.
- Input ordering must not change fingerprints or decision ordering.
- Protected-environment denial must happen before fixture or clock inspection.

---

### Task 1: Immutable synthetic composition contracts

**Files:**

- Create: `backend/app/modules/care_orchestration/__init__.py`
- Create: `backend/app/modules/care_orchestration/contracts.py`
- Create: `backend/tests/test_care_composition_contracts.py`

**Interfaces:**

- Produces: `CompositionContractError`, `CompositionCode`, `EvidenceChannel`,
  `EvidenceAvailability`, `SyntheticActionCode`, `CompositionDisposition`, `CompositionReason`,
  `SyntheticEvidenceReference`, `SyntheticCompositionRequest`, `SyntheticActionCandidate`, and
  `SyntheticCompositionDecision`.
- Produces: snapshot helpers and canonical fingerprints consumed only by Task 2.

- [ ] **Step 1: Write failing constructor, immutability, UTC, duplicate, chronology, canonical-order,
      and privacy-safe error tests.**
- [ ] **Step 2: Run `pytest tests/test_care_composition_contracts.py -q`; expect import failure.**
- [ ] **Step 3: Implement strict enums, helpers, and frozen/slotted dataclasses with exact-type
      validation and reconstruction.**
- [ ] **Step 4: Run focused tests; expect all Task 1 tests to pass.**

### Task 2: Fail-closed detached composition

**Files:**

- Create: `backend/app/modules/care_orchestration/composition.py`
- Create: `backend/tests/test_care_composition.py`
- Modify: `backend/app/modules/care_orchestration/__init__.py`

**Interfaces:**

- Consumes: Task 1 contract types and snapshot/fingerprint helpers.
- Produces:
  `compose_synthetic_candidates(request, candidates, *, evaluated_at, environment) -> SyntheticCompositionDecision`.

- [ ] **Step 1: Write failing tests for protected-environment short circuiting, unavailable-evidence
      abstention, empty-candidate abstention, exact reference validation, all-candidate preservation,
      deterministic replay, forced mutation, chronology, and absent ranking/suppression behavior.**
- [ ] **Step 2: Run both focused files; expect missing composition API failures.**
- [ ] **Step 3: Implement the pure function: deny protected environments first; reconstruct inputs;
      abstain before candidate inspection when evidence is not available; otherwise validate exact
      references and preserve every candidate in canonical order.**
- [ ] **Step 4: Run both focused files; expect all focused tests to pass.**

### Task 3: Boundary and evidence documentation

**Files:**

- Create: `backend/tests/test_care_composition_boundaries.py`
- Create: `docs/implementation/P20_A_SYNTHETIC_CARE_COMPOSITION_CONTRACTS.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**

- Consumes: public Task 1/2 surfaces.
- Produces: static boundary proof and an honest P20 PARTIAL tracker record.

- [ ] **Step 1: Write failing architecture tests proving no module registration, route, persistence,
      migration, upstream module import, execution method, or approval/activation surface.**
- [ ] **Step 2: Run the boundary test and verify the expected failure before the package boundary is
      finalized.**
- [ ] **Step 3: Finalize exports and add implementation evidence/tracker updates without claiming
      live P20 acceptance.**
- [ ] **Step 4: Run focused P20 tests, full backend quality/tests, frontend gates, migration checks,
      Docker/PostgreSQL, Playwright, Gitleaks, Trivy, and diff/privacy audits.**
- [ ] **Step 5: Commit, push, open a PR, verify all six CI jobs on the exact SHA, merge only when green,
      and verify all six jobs on the merge SHA.**

