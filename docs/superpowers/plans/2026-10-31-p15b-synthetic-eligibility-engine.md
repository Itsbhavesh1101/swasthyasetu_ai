# P15-B Synthetic Eligibility Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a detached fail-closed P15-B eligibility evaluator using only closed engineering fixtures.

**Architecture:** Immutable contracts bind evaluation, P9 safety provenance, P15-A knowledge, a compile-time synthetic policy, and the resulting placeholder references. A pure evaluator denies protected environments and applies safety, completeness, exclusion, then match ordering without runtime registration.

**Tech Stack:** Python 3.12, frozen dataclasses, enums, hashlib, pytest, Ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-10-31-p15b-synthetic-eligibility-engine-design.md`

## Global Constraints

- Engineering-only nonmedical tokens; no real remedy, source, clinical rule, threshold, or patient data.
- No persistence, migration, API, UI, dependency, feature flag, registry, or runtime activation.
- `Environment.STAGING`, `PILOT`, and `PRODUCTION` must fail before evaluation.
- Live FR-SELF and AC-P15 criteria remain unverified.

## Review Focus

- A forged positive safety result must block rather than create a candidate.
- Missing, conflicting, or mutated context must clarify/block and never match.
- Exclusion predicates must win over include predicates independent of order.
- Any policy/pack/evaluation/safety drift must invalidate the result binding.
- No unapproved fixture or protected environment may yield a candidate.

---

### Task 1: Immutable synthetic eligibility contracts and policy fixture

**Files:**
- Create: `backend/app/modules/self_care/eligibility.py`
- Create: `backend/app/modules/self_care/synthetic_eligibility.py`
- Create: `backend/tests/test_synthetic_self_care_eligibility.py`

**Interfaces:**
- Consumes: `SafetyDecision`, `SyntheticKnowledgePack`, `Environment`.
- Produces: `SyntheticEligibilityEvaluation`, `SyntheticEligibilityPolicy`,
  `SyntheticEligibilityResult`, `validate_synthetic_eligibility_result`, and
  `SYNTHETIC_ELIGIBILITY_POLICY`.

- [ ] Write direct-constructor tests for closed tokens, bounds, ordering, UTC normalization, hashes,
  policy state, and forced mutation.
- [ ] Run the focused file and verify RED because the eligibility module does not exist.
- [ ] Implement the minimal immutable contracts, canonical fingerprints, and compile-time fixture.
- [ ] Run the focused file and verify GREEN.
- [ ] Run Ruff and project-wide mypy.

### Task 2: Deterministic fail-closed evaluator and drift validation

**Files:**
- Modify: `backend/app/modules/self_care/eligibility.py`
- Modify: `backend/tests/test_synthetic_self_care_eligibility.py`

**Interfaces:**
- Consumes: exact evaluation, safety decision, knowledge pack, synthetic policy, environment.
- Produces: `SyntheticEligibilityEngine.evaluate(...) -> SyntheticEligibilityResult` and exact
  cross-artifact validation.

- [ ] Add tests for protected-environment denial, exact safety provenance, no-downgrade blocking,
  missing/conflicting context, exclusion precedence, deterministic candidates, unavailable or
  invalid policy, and all four drift classes.
- [ ] Run the focused file and verify RED because the evaluator is absent.
- [ ] Implement the pure evaluator in the specified ordering with content-free failure codes.
- [ ] Run the focused file and verify GREEN.
- [ ] Run the full backend quality gate.

### Task 3: Scope evidence and project verification

**Files:**
- Create: `docs/implementation/P15_B_SYNTHETIC_ELIGIBILITY_ENGINE.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**
- Consumes: completed P15-B implementation and test evidence.
- Produces: precise bounded-scope status without any live approval claim.

- [ ] Record the detached synthetic scope, exclusions, test evidence, and remaining blockers.
- [ ] Verify no runtime import/registration, dependency, migration, API, frontend, or infrastructure
  changes exist.
- [ ] Run backend and frontend quality gates, Compose validation, `git diff --check`, and security CI.
- [ ] Commit, push, open a PR, verify all six exact-SHA CI jobs, merge, and verify main CI.
