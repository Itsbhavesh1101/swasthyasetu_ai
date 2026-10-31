# P13-E - Synthetic Referral Presentation Test Foundation

**Status:** complete bounded test-only engineering subset; live P13 patient/admin UI remains
blocked and unapproved

**Baseline:** merged main at `ced4839c220cd598f1f3c65052828d7fdb4bd36e`

## Implemented

- Vitest-only patient previews for unavailable, unknown, and simulated-failure referral states.
- Vitest-only admin warnings for unavailable, unverified, stale, and revoked synthetic sources.
- Closed state vocabularies with runtime fail-closed defaults.
- Accessible status semantics, explicit engineering-only labels, no-action rendering, and tests that
  prevent production imports or optimistic success/delivery/source-authority claims.

## Deliberately absent

No production component or route changed. There is no provider/resource/contact/source evidence,
referral record, consent, moderation action, API/BFF, network, browser storage, persistence,
migration, dependency, feature flag, or runtime activation.

## Governance truth

This implements only the P13 Gate 7 and Admin Readiness §2.6 allowance for static synthetic
unavailable/degraded/source-warning component tests. It does not approve product copy, roles,
identity, source truth, accessibility, referral status, or release. Every live P13 requirement and
`AC-P13-001..011` remains live-not-verified.
