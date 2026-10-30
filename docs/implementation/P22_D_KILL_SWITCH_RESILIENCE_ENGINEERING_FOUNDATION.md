# P22-D Kill-Switch/Resilience — Synthetic Engineering Foundation

**Status:** Bounded synthetic engineering subset implemented; P22 remains **PARTIAL**

**Baseline:** `origin/main @ 7dc45bf11285e7c061211436f804d4e5f8f5c2dd`

**Branch:** `phase/p22-d-resilience-controls`

## 1. Governance decision

Canonical documents require resilient optional dependencies but leave production inventory,
activation and switch authority, fleet topology, operational ownership, reset ceremony, monitoring,
recovery objectives, and drills unresolved. This unit does not infer those decisions. Switch state
does not replace actor/object authorization, purpose-specific consent, clinical policy, resource
verification, or production enablement.

## 2. Implemented engineering subset

- closed optional capability inventory for LLM, OCR, speech, referral, FHIR, ABDM, self-care, QML,
  resource-directory, language-path, and policy-version controls;
- immutable switch, retry/deadline, dependency-failure, and outcome contracts;
- fail-safe disabled-by-default process-local switchboard;
- idempotent one-way trip with no reset path;
- in-flight post-call switch recheck and late-result rejection;
- bounded per-attempt and total deadlines;
- transient retry only for explicitly idempotent operations;
- honest generic degradation without payload/exception leakage;
- bounded identifier-free OpenTelemetry counters; and
- direct-constructor, concurrency, retry, timeout, cancellation, privacy and telemetry tests.

## 3. Deliberately absent

- FastAPI/module/capability registration or any runtime wiring;
- production enablement, provider/network call, external integration, clinical decision or content;
- distributed/durable switch state, API/UI, database/migration, job/worker, scheduler, event/outbox,
  configuration reload, deployment controller, automatic circuit breaker, or reset/re-enable path;
- cancellation or reversal of an already-started external side effect; no side-effecting integration
  is wired, and production adapters still require cancellation, idempotency/reconciliation, and
  in-flight incident rules;
- alerting destination, on-call owner, switch authority, SLO/RTO/RPO, incident runbook or drill; and
- any claim that feature flags or switches confer authorization or policy approval.

## 4. Security and resilience behavior

Every capability is disabled by default and makes zero calls. Explicit synthetic availability is a
composition input only, not approval. A trip is first-write-wins, UTC-normalized, observer-failure
tolerant and irreversible for that process. Work that completes after a concurrent trip is
discarded. Cancellation propagates. Non-idempotent work cannot retry; retries and backoff stay
inside the total deadline. Returned outcomes and telemetry expose only closed capability/state/
reason/failure values. Core/manual fallback remains caller-owned and cannot be fabricated here.

## 5. Acceptance status

This is synthetic engineering evidence only. `AC-P22-009`, `AC-P22-010`, and live acceptance for
`NFR-RES-001..007` remain **LIVE NOT VERIFIED**. Production acceptance still requires an approved
capability/owner matrix, authoritative distributed controls, authenticated and audited operations,
monitoring/alerts, re-enable governance, actual dependency/provider outage exercises, partial
deployment and rollback drills, recovery objectives, and independent review. P22-E/P23/P24, pilot,
and release remain outside this unit.
