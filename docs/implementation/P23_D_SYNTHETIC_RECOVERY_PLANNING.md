# P23-D Synthetic Recovery Planning Foundation

## Status

`PARTIAL — BOUNDED DETACHED ENGINEERING-SYNTHETIC NO-DRILL FOUNDATION ONLY`

This unit defines strict metadata for proposed future resilience/recovery drills. It does not execute
a drill or verify `AC-P23-011`, `AC-P23-012`, or `NFR-RES-001..007`.

## Implemented boundary

The unregistered `app.validation` package contains the exact five canonical scenarios: worker
restart, duplicate event, retry, outbox recovery, and projection rebuild if applicable. Projection
rebuild is explicitly `UNDECIDED`; the other four scenarios are `PROPOSED_UNAPPROVED`.

Each immutable plan binds an engineering version, exact build/configuration, and hashes for proposed
failure injection, recovery oracle, isolation/cleanup, privacy canary, and rollback plans. Every plan
and manifest remains `ENGINEERING_ONLY`, `ENGINEERING_SYNTHETIC`, `UNVERIFIED`, `NOT_EXECUTED`, and
`HUMAN_APPROVAL_REQUIRED`.

The deterministic manifest requires one canonically ordered plan per scenario and rejects missing,
duplicate, aliased, malformed, inapplicable, stale, or forcibly mutated values. Staging, pilot, and
production reject before caller-controlled plans are inspected.

## Explicitly absent

- No worker/process/database restart, failure injection, retry/replay, event publication, outbox
  dispatch, projection operation, network partition, backup/restore, or kill-switch action.
- No lease, heartbeat, timeout, backoff, RTO/RPO, exactly-once claim, recovery result, pass, or
  operational approval.
- No patient/clinical data, raw telemetry, dashboard, alert, screenshot, or recording.
- No persistence, migration, API/BFF/UI, event/job, dependency, CI configuration, feature flag,
  module registration, runtime activation, deployment, pilot, or release behavior.

## Outstanding decisions

Before any drill, accountable SRE/incident, data/application architecture, outbox/job, affected
domain/clinical, privacy/security, observability, infrastructure, and release reviewers must approve
the durability backend, applicability, claim/lease/idempotency semantics, retry/deadline/backoff,
ordering/late-result handling, cancellation/tombstones, recovery objectives, monitoring, kill-switch
authority, environment, evidence handling, rollback, and incident process.

All live P23 acceptance and product acceptance remain unverified. P24, pilot, and release remain
outside this unit.
