# P13-E Synthetic Referral Presentation Design

## Intent

Prove safe, accessible static rendering mechanics for unavailable referral states and synthetic
source warnings without exposing any surface in production.

## Boundary reconciliation

P13 Gate 7 remains blocked because identity, source truth, copy, roles, privacy, accessibility, and
release decisions are unresolved. The gate and Admin Readiness §2.6 permit only separately scoped
static synthetic unavailable/degraded/source-warning component tests. Therefore all fixtures live
under app test-support directories and production code cannot import them.

## Design and constraints

- Patient states are closed to `UNAVAILABLE`, `UNKNOWN`, and `FAILED`.
- Admin warnings are closed to `SOURCE_UNAVAILABLE`, `SOURCE_UNVERIFIED`, `SOURCE_STALE`, and
  `SOURCE_REVOKED`.
- Unknown runtime values degrade to unavailable.
- Fixed engineering labels never claim source authority, referral creation, delivery, or success.
- Fixtures expose no links, actions, identifiers, contacts, evidence, free text, network, storage,
  API, provider, consent, or moderation behavior.
- No production route, component, dependency, schema, or runtime integration changes.

## Acceptance

Focused and full regression tests must prove accessibility semantics, fail-closed rendering,
test-only isolation, absence of sensitive/actionable content, unchanged production builds, and
exact-SHA CI. All live P13 acceptance remains unverified.
