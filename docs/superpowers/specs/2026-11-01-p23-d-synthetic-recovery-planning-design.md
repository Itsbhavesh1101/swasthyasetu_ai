# P23-D Synthetic Recovery Planning Design

## Intent

Create strict detached metadata contracts for future resilience/recovery drills without controlling
infrastructure or executing a drill. The schema covers the five canonical P23 reliability scenarios:
worker restart, duplicate event, retry, outbox recovery, and projection rebuild if applicable.

Projection rebuild remains `UNDECIDED`; the other scenarios remain `PROPOSED_UNAPPROVED`. Every plan
is engineering-only, synthetic, unverified, not executed, and human-approval-required.

## Model

Each plan binds an exact build/configuration plus hashes for a proposed failure-injection plan,
recovery oracle, isolation/cleanup plan, privacy-canary plan, and rollback plan. The canonical manifest
requires exactly one plan per scenario, reconstructs inputs, normalizes aware timestamps to UTC, and
rejects aliases, duplicates, drift, malformed values, invalid chronology, or forced mutation.

Only `LOCAL` and `TEST` may construct a manifest. Staging, pilot, and production reject before any
caller-controlled plan is inspected.

## Explicit non-goals

No worker/process/database restart, failure injection, event publication, retry/replay, outbox
dispatch, projection operation, lease, heartbeat, network partition, backup/restore, kill switch,
timeout/backoff, RTO/RPO, exactly-once claim, result, pass, persistence, API/UI, runtime registration,
dependency, CI, deployment, pilot, or release behavior.

## Governance outcome

This foundation proves planning integrity only. It does not verify `AC-P23-011`, `AC-P23-012`, or
`NFR-RES-001..007`. SRE/incident, data/application architecture, outbox/job, domain/clinical,
privacy/security, observability, infrastructure, and release decisions remain required before a
drill.
