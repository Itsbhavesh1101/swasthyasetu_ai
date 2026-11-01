# P23-C Synthetic Performance Planning Design

## Intent

Create a detached engineering-only schema for future performance experiment plans without running a
load test or recording any measurement. The implementation must make the current STOP state
machine-enforceable: no approved workload, environment, method, threshold, observability sink, or
human decision exists.

## Canonical inventory

The manifest contains exactly the five P23 measurement targets:

1. API latency;
2. LLM latency;
3. document queue;
4. provider search; and
5. database query hotspots.

Each plan binds only an engineering version, exact build/configuration, and hashes for a proposed
synthetic workload, fixture provenance, measurement method, isolation/cleanup plan, and analysis
plan. It contains no counts, durations, concurrency, percentiles, throughput, error budget, SLO,
threshold, baseline, result, or approval.

## Invariants

- Every plan is `ENGINEERING_ONLY`, `ENGINEERING_SYNTHETIC`, `UNVERIFIED`, `NOT_EXECUTED`, and
  `HUMAN_APPROVAL_REQUIRED`.
- Only `LOCAL` and `TEST` may build a manifest; staging, pilot, and production reject before input
  inspection.
- The manifest requires exactly one canonically ordered plan per target.
- Contracts are immutable, reconstruct nested inputs, normalize aware clocks to UTC, reject naive
  clocks, and use content-free errors.
- Fingerprints bind every machine field; hashes and nested plans are excluded from representations.

## Non-goals

No benchmark, request, browser action, database query, job, model call, queue operation, external
service, network traffic, telemetry export, threshold, comparison, report, persistence, API/UI,
migration, dependency, CI change, runtime registration, pilot, or release behavior.

## Governance outcome

This is planning integrity only. It does not establish a performance baseline or verify
`AC-P23-010` or `NFR-PERF-001..006`. Qualified product, clinical operations, SRE/performance,
database, privacy/security, accessibility, observability, and owning-module decisions remain
required before any run.
