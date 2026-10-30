# P22-C Retention/Purge Engineering Foundation Plan

**Goal:** Add safe provider-neutral purge and restore-reconciliation mechanics without inventing
retention policy or activating deletion.

**Spec:** `docs/superpowers/specs/2026-10-30-p22c-retention-foundation-design.md`

## Constraints

- Synthetic data only.
- No real store adapter, schema, migration, endpoint, job, worker, scheduler, outbox, or startup hook.
- No retention duration, legal conclusion, hold decision, provider decision, or approval.
- No dependency or lockfile change.
- Preserve all P8-C/P9-C/P10/P11 and P22 governance restrictions.

## Task 1 — immutable contracts

- Create strict retention/purge policy, authorization, target, plan, receipt, result, tombstone, and
  restore-decision contracts.
- Add direct-constructor and adversarial tests for types, UTC normalization, duplicate targets,
  blocked decisions, and privacy-safe representations.

## Task 2 — explicit coordinator and telemetry

- Add the provider-neutral idempotent adapter protocol.
- Implement a manually invoked coordinator with exact adapter registration, fail-closed
  authorization, honest partial failure, generic errors, and no exception leakage.
- Add bounded OpenTelemetry counters with no identifiers or locators.
- Prove complete, already-absent, missing-adapter, exception, malformed-receipt, and retry behavior.

## Task 3 — restore reconciliation and documentation

- Add deterministic tombstone-versus-restored-generation reconciliation.
- Prove old generations are reblocked and unmatched/newer generations require review.
- Update the P22 implementation report, progress tracker, and backend operator documentation.
- Run backend/frontend quality, PostgreSQL, Docker, Playwright, Gitleaks, Trivy, and exact-SHA CI.
- Open a PR without merging and keep live acceptance explicitly unverified.
