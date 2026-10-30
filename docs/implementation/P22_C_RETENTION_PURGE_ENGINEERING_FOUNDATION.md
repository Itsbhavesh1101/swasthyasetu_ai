# P22-C Retention/Purge — Synthetic Engineering Foundation

**Status:** Bounded synthetic engineering subset implemented; P22 remains **PARTIAL**

**Baseline:** `origin/main @ 2b473606c34775851d5a51aebe9d548bec5a3e1b`

**Branch:** `phase/p22-c-retention-controls`

## 1. Governance decision

Canonical privacy and readiness documents do not authorize retention durations, legal-hold
precedence, real-store deletion, backup/provider deletion, or operational ownership. This unit does
not infer those decisions. It implements mechanics that accept an already evaluated authorization;
it does not evaluate law, consent, records policy, or retention schedules.

## 2. Implemented engineering subset

- immutable machine-readable policy and version references;
- explicit `AUTHORIZED`, `BLOCKED_BY_HOLD`, and `NOT_AUTHORIZED` decisions;
- opaque, versioned database/object/search/cache/backup target contracts;
- immutable plans that reject duplicate target identities;
- a provider-neutral, idempotent `PurgeTargetAdapter` protocol;
- a manually invoked coordinator with explicit adapter registration;
- fail-closed blocked plans and missing-adapter behavior;
- generic target-failure receipts with honest failed/partial aggregate status and no locator or
  exception leakage;
- bounded OpenTelemetry target/failure counters without identifiers;
- content-free tombstones and deterministic restore-resurrection reconciliation; and
- direct-constructor, privacy, failure, retry, telemetry, and restore adversarial tests.

## 3. Deliberately absent

- retention durations, lawful/governance basis, legal-hold adjudication, or user-facing promises;
- patient/session/consent/encounter/intake deletion;
- PostgreSQL/object/search/cache/backup/provider adapters;
- database schema or Alembic migration;
- APIs, UI, jobs, workers, schedules, outbox events, or FastAPI activation;
- backup mutation, provider deletion, restore automation, or exactly-once claims; and
- production alerts, runbooks, responder ownership, or live execution evidence.

## 4. Security and privacy behavior

Unauthorized or held plans never call an adapter. Timestamps normalize to UTC. Target locators,
subjects, plan IDs, target IDs, and exception strings do not enter representations or metrics.
Adapter receipts must match the exact requested target. Any target failure prevents the aggregate
run from appearing complete. Telemetry observation is best-effort after each irreversible adapter
result; observer failure cannot relabel or retry completed deletion work, and the returned receipt
remains the authoritative execution result. A restored generation covered by a tombstone is classified
`REBLOCK_AND_REPURGE`; newer or unmatched data remains `REVIEW_REQUIRED` rather than becoming live.

## 5. Acceptance status

This is synthetic engineering evidence only. `PRIV-003`, `PRIV-004`, `AC-P22-007`, and
`AC-P22-008` remain **LIVE NOT VERIFIED**. A production workflow still requires an authoritative
per-data-class schedule, hold and audit-preservation rules, real store/backup/provider adapters,
durable state, operational alert ownership, recovery/reconciliation drills, and independent review.
No pilot, production release, real-patient purge, or deletion promise is authorized.
