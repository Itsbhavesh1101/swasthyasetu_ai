# P14-A - Synthetic Mental-Health Signal Schema Foundation

**Status:** complete bounded engineering subset; live P14 processing and routing remain blocked and
unapproved

**Baseline:** merged main at `3451b85b2e95500993e6d36f4f43cc35f5a7a5f8`

## Implemented

- Immutable engineering-only artifact, extraction-request, observation, result, and failure
  contracts.
- Four fixed nonmedical toy signal tokens with explicit present/absent/unknown/uncertain/
  contradictory mechanics and no assigned meaning.
- Strict exact-field parsing, canonical UTC validation, deterministic ordering, abstention rules,
  artifact/version/hash binding, deadline validation, forced-mutation revalidation, and content-free
  errors.
- Detached provider-neutral extractor protocol with no implementation or runtime registration.

## Deliberately absent

No narrative, patient/session identity, clinical signal, score/confidence, screening instrument,
prompt, provider/model adapter, language backstop, route, policy, crisis resource/copy, consent,
referral, API, persistence, migration, job/event, dependency, UI, feature flag, or runtime behavior.

## Governance truth

This implements only P14 Readiness §§2.1 and 2.3's separately authorized nonmedical synthetic
contract/parser mechanics. It grants no clinical meaning or authority and satisfies no live P14
acceptance criterion. `FR-MH-001..020` and `AC-P14-001..013` remain live-not-verified.
