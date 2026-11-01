# P23-B Synthetic Accessibility Evidence Implementation Plan

## Goal

Add a detached, immutable, synthetic-only accessibility evidence catalog without performing or
claiming an accessibility audit.

## Constraints

- No browser/tool audit, patient data, clinical copy review, WCAG claim, finding severity, approval,
  persistence, API/UI, dependency, CI, migration, network, or runtime activation.
- Only `LOCAL` and `TEST` environments are permitted.
- Every record remains engineering-only, synthetic, unverified, and human-review-required.
- Results can only be metadata-consistent or abstained; never pass, approved, certified, or released.

## Task 1: Contract tests and immutable model

- Add failing tests for the exact eight-area inventory, strict machine fields, UTC normalization,
  immutable snapshots, direct-constructor consistency, manifest invariants, and private reprs.
- Implement `backend/app/validation/accessibility.py` and package exports.
- Run focused tests to green.

## Task 2: Pure manifest and evaluator boundaries

- Add failing tests for deterministic canonical construction, drift abstention, protected-environment
  no-inspection rejection, hostile input, and runtime isolation.
- Implement the pure builder/evaluator with environment checks first.
- Run the complete validation package tests.

## Task 3: Boundary record and verification

- Add a P23-B implementation boundary document and truthful tracker entry.
- Run backend and frontend quality gates, formatting, migration drift, Docker/PostgreSQL and browser
  regression through the standard local/remote gates.
- Review the whole branch, fix important findings with regression tests, then push, open a PR, verify
  all six exact-SHA jobs, merge, and verify all six jobs on `main`.
