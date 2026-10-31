# P14-C - Synthetic Policy-Routing Mechanics

**Status:** complete bounded engineering subset; live mental-health policy and routing remain blocked
and unapproved

**Baseline:** merged main at `9244864dc79be72fd8d0db53b0d381af1bf47a88`

## Implemented

- Immutable engineering-only rule, policy artifact, evaluation, policy reference, and decision
  contracts using closed nonmedical toy symbols.
- Exact policy-content hashing across identity, lifecycle, state, and ordered rule content.
- Exact evidence and decision binding with source-sensitive fingerprints and canonical UTC time.
- Pure deterministic precedence mechanics: synthetic override, clarification, then standard.
- Explicit synthetic degraded results for absent, invalid, future, expired, suspended, unmatched,
  disagreeing, and equal-precedence-conflicting policy/evidence states.
- Hard denial in staging, pilot, and production before policy or evidence is read.
- A single executable toy rule mapping isolated under backend test support.

## Deliberately absent

No `ROUTE_A/B/C` meanings, clinical signals, high-risk criteria, score, threshold, questionnaire,
language lexicon, narrative or patient data, model route authority, crisis disposition, resource,
referral, consent behavior, API, persistence, migration, event/job, dependency, UI, feature flag,
module registration, or runtime activation.

## Governance truth

This implements only the P14 Readiness section 2.4 separately permitted toy symbolic ordering and
fail-closed mechanics. It is not a mental-health policy, cannot execute in protected environments,
and grants no clinical authority. `FR-MH-001..020` and `AC-P14-001..013` remain live-not-verified.
