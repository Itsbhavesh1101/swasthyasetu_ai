# P23-C Synthetic Performance Planning Foundation

## Status

`PARTIAL — BOUNDED DETACHED ENGINEERING-SYNTHETIC NO-RUN FOUNDATION ONLY`

This unit defines strict metadata for proposed future performance experiments. It does not execute a
performance or load test, establish a baseline, or verify `AC-P23-010` or `NFR-PERF-001..006`.

## Implemented boundary

The unregistered `app.validation` package contains the exact five P23 targets: API latency, LLM
latency, document queue, provider search, and database query hotspots. Each immutable plan binds an
engineering version, build SHA, configuration hash, synthetic-workload hash, fixture-provenance
hash, measurement-method hash, isolation/cleanup-plan hash, analysis-plan hash, and UTC creation
time.

Every plan and manifest is permanently labelled `ENGINEERING_ONLY`, `ENGINEERING_SYNTHETIC`,
`UNVERIFIED`, `NOT_EXECUTED`, and `HUMAN_APPROVAL_REQUIRED`. The deterministic manifest requires one
canonically ordered plan per target and rejects missing, duplicate, aliased, malformed, stale, or
forcibly mutated values. Staging, pilot, and production reject before plan input is inspected.

## Explicitly absent

- No experiment execution, load generation, request, browser action, database query, queue or model
  operation, external endpoint, or network traffic.
- No concurrency, duration, repetition, warmup, sample size, percentile, throughput, error rate,
  availability, SLO, budget, threshold, baseline, comparison, regression, result, or pass state.
- No telemetry exporter, dashboard, query, alert, evidence sink, screenshot, recording, or raw
  sensitive data.
- No persistence, migration, API/BFF/UI, event/job, dependency, CI configuration, feature flag,
  module registration, runtime activation, deployment, pilot, or release behavior.

## Outstanding decisions

Before any P23-C experiment, accountable product, clinical operations, SRE/performance, database,
privacy/security, accessibility, observability, and owning-module reviewers must approve the exact
objective, environment, data classification, synthetic workload, fixture rights, method, warmup,
repetitions, concurrency, clocks, metrics, uncertainty/outlier handling, cleanup, evidence retention,
third-party restrictions, thresholds, and review criteria.

`AC-P23-010`, `NFR-PERF-001..006`, all other live P23 criteria, and product acceptance remain
unverified. P23-D, P24, pilot, and release are outside this unit.
