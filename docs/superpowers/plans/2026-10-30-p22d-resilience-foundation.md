# P22-D Kill-Switch and Resilience Engineering Foundation Plan

**Goal:** Add safe-off process-local optional dependency controls and synthetic failure evidence
without activating optional features or inventing production governance.

**Spec:** `docs/superpowers/specs/2026-10-30-p22d-resilience-foundation-design.md`

## Constraints

- Synthetic data and adapters only.
- No endpoint, UI, schema, migration, job, worker, scheduler, outbox, deployment control, or startup
  registration.
- No production provider, external request, clinical rule, content, resource, or activation.
- No dependency or lockfile change.
- Feature flags and switches remain distinct from authorization and clinical policy.
- Preserve all P8-C, P9-C, P10, P11, P22, P23 and P24 restrictions.

## Task 1 — strict control and outcome contracts

- Define a closed optional capability inventory, safe switch states/reasons, retry/deadline policy,
  dependency failure classification, and honest outcomes.
- Add direct-constructor, UTC, default-off, representation, and invalid-state tests.

## Task 2 — one-way switchboard and bounded executor

- Implement a thread-safe process-local switchboard with no reset/re-enable operation.
- Implement bounded optional execution with total/per-attempt deadlines and idempotent transient
  retries only.
- Prove zero-call disabled behavior, idempotent trip, in-flight late-result rejection, cancellation,
  generic failures, nil-result rejection, and observer-failure isolation.

## Task 3 — privacy-safe telemetry and regression evidence

- Add counters with exact closed attribute allowlists and no identifiers/content.
- Prove every optional capability is disabled by default and caller-owned fallback remains usable.
- Prove the package is absent from runtime module registration.
- Update the implementation report, progress tracker, and backend operator documentation.
- Run backend/frontend quality, PostgreSQL, Docker, Playwright, Gitleaks, Trivy, and exact-SHA CI.
- Open a PR without merging; keep live P22 resilience acceptance explicitly unverified.
