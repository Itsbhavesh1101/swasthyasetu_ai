# P22-C Retention/Purge Engineering Foundation Design

## Decision boundary

Canonical privacy documents deliberately leave retention durations, lawful/governance authority,
legal-hold precedence, backup deletion, provider deletion, and operational ownership unresolved.
This increment therefore does not create a schedule or delete any real application record. It
builds only provider-neutral mechanics that a future approved policy and store-specific adapters can
use.

## Goals

- Represent an externally evaluated purge authorization without deciding legal or records policy.
- Represent immutable, versioned purge plans and privacy-minimized targets.
- Execute authorized plans explicitly through compile-time supplied provider-neutral adapters.
- Fail closed when authorization or an adapter is unavailable.
- Keep multi-target partial failure honest and observable without exception or locator leakage.
- Make target operations idempotent and expose already-absent outcomes.
- Detect restored generations covered by a prior tombstone and require reblocking/repurge.
- Use only synthetic tests and no runtime activation.

## Non-goals

- Retention durations, lawful basis, consent interpretation, legal-hold adjudication, or user copy.
- Real patient deletion, PostgreSQL/object/search/cache/backup adapters, migrations, or schemas.
- A purge API, background worker, job registration, scheduler, outbox event, or FastAPI startup hook.
- Provider deletion, backup mutation, restore automation, or an exactly-once claim.
- Promotion of `PRIV-003/004` or `AC-P22-007/008` to live acceptance.

## Architecture

`app.retention` owns immutable contracts for policy references, externally resolved authorization,
targets, plans, receipts, run results, tombstones, and restore decisions. A `PurgeTargetAdapter`
protocol requires explicit, idempotent target deletion. `PurgeCoordinator` is invoked manually and
contains no scheduler. It refuses blocked plans, maps each closed target kind to an explicitly
provided adapter, converts adapter exceptions or malformed receipts into generic failures, and
returns an honest aggregate result.

`PurgeTelemetry` records bounded target-kind, outcome, and generic error-code attributes only. It
never records plan, subject, target, locator, or exception content. `RestoreReconciler` is
deterministic and text-blind: a restored target at or below a tombstoned generation is marked
`REBLOCK_AND_REPURGE`; unmatched or newer generations require review rather than automatic deletion.

## Security and privacy invariants

- A plan is executable only when its immutable authorization decision is `AUTHORIZED`.
- `BLOCKED_BY_HOLD` and `NOT_AUTHORIZED` never call adapters.
- Target locators and subject references are excluded from representations and telemetry.
- Every timestamp is timezone-aware and normalized to UTC.
- Duplicate target identities in one plan are rejected.
- An adapter receipt must match the exact requested target.
- Raw exception text never enters results, metrics, or logs.
- A failed target never makes the aggregate result appear complete.
- No restore candidate is automatically accepted as live data.

## Acceptance boundary

The unit provides synthetic engineering evidence for future P22-C implementation. It cannot prove
that a live retention workflow executed, that failure alerting has an accountable responder, or that
backup/provider deletion works. P22 remains `PARTIAL`; `PRIV-003/004` and `AC-P22-007/008` remain
`LIVE NOT VERIFIED`.
