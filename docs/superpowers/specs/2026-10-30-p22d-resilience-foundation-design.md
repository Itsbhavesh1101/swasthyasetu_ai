# P22-D Kill-Switch and Resilience Engineering Foundation Design

## Decision boundary

Canonical P22 documents require independent safe-off controls, bounded dependency behavior, honest
degradation, and preservation of core intake. They also record that the production capability
inventory, activation authorities, operational owners, deployment topology, durable control plane,
clinical-policy rollback authority, monitoring, recovery targets, and disaster exercises remain
unapproved or absent. This increment therefore supplies only process-local provider-neutral
mechanics and synthetic evidence. It grants no activation or clinical authority.

## Goals

- Keep every optional capability disabled by default.
- Represent the canonical optional dependency and high-risk capability classes as a closed enum.
- Permit an explicitly composed synthetic capability to be disabled through a one-way switch.
- Recheck switch state after in-flight work so a late result cannot bypass a concurrent trip.
- Bound each attempt and total execution time.
- Retry only adapter-classified transient work that is explicitly idempotent.
- Return closed success or degraded outcomes without raw payload or exception leakage.
- Expose identifier-free switch and dependency telemetry.
- Preserve fallback ownership in the calling domain rather than inventing clinical/user content.

## Non-goals

- A production or distributed kill-switch service, endpoint, UI, database table, migration, worker,
  scheduler, outbox event, deployment controller, or automatic startup registration.
- Cancellation or reversal of an already-started external side effect; no side-effecting integration
  is wired to this foundation, and production adapters require their own cancellation,
  idempotency/reconciliation, and in-flight incident rules.
- Enabling LLM, OCR, speech, referral, FHIR, ABDM, self-care, QML, provider, language, or policy
  behavior.
- Treating a feature flag, switch state, test, CI run, or Codex decision as authorization, clinical
  approval, policy approval, or production enablement.
- Choosing switch owners, response times, SLO/RTO/RPO, escalation policy, reset/re-enable ceremony,
  or patient-facing degraded copy.
- Claiming `AC-P22-009`, `AC-P22-010`, `NFR-RES-001..007`, P23, P24, or pilot acceptance.

## Architecture

`app.resilience` contains immutable contracts, `OptionalCapabilitySwitchboard`,
`OptionalDependencyExecutor`, and bounded OpenTelemetry counters. The switchboard starts every
capability disabled unless an embedding composition explicitly provides a synthetic availability
set. It supports idempotent one-way trips and deliberately exposes no reset. It is not registered in
the application module/capability registries.

The executor refuses disabled/tripped capabilities without calling the dependency. For an available
synthetic capability, it applies per-attempt and total deadlines, retries only transient idempotent
work within a maximum budget, propagates task cancellation, converts raw failures to closed codes,
rejects a missing result, and rechecks the switch before returning success. It returns no fallback
content; core/manual paths remain owned by their existing modules.

## Security and resilience invariants

- Disabled-by-default and tripped capabilities make zero dependency calls.
- A trip is one-way and first-write-wins within the process.
- A naive trip clock is rejected before switch mutation; aware clocks normalize to UTC.
- A switch tripped during an in-flight operation discards the late result.
- Non-idempotent work cannot have a retry budget.
- Total deadline includes attempts and retry delay.
- Cancellation is never converted into apparent success or an ordinary dependency failure.
- Dependency payloads, raw exceptions, identifiers, and incident text never enter results/metrics.
- Observer failure cannot prevent a trip or relabel the returned dependency outcome.

## Acceptance boundary

This is bounded synthetic engineering evidence only. Real deployment controls, independent owner
authority, live provider/integration failure exercises, monitoring/alerts, re-enable governance,
durable fleet propagation, partial-deploy/rollback tests, and disaster recovery remain outstanding.
P22 remains `PARTIAL`; `AC-P22-009/010` and `NFR-RES-001..007` remain live acceptance not verified.
