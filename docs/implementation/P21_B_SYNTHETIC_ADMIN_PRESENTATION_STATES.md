# P21-B Synthetic Admin Presentation States

## Status

`PARTIAL - BOUNDED TEST-ONLY ENGINEERING-SYNTHETIC SUBSET`

P21 remains partial. This increment adds no production admin component, route, API, BFF, identity,
data access, action, or authority. All live `FR-ADMIN-*`, `FR-AUDIT-*`, and `AC-P21-*` outcomes
remain unverified.

## Implemented test boundary

- A Vitest-only projection accepts closed `LOCAL`/`TEST` environments and six synthetic states:
  identity unavailable, MFA required, scope denied, synthetic contract match, stale snapshot, and
  pending human review.
- Unknown and protected environments fail unavailable before the state is inspected.
- Unknown state values fail unavailable.
- The synthetic-match copy states explicitly that runtime access is not granted.
- The preview exposes an accessible live status and contains no interactive control.
- Tests prove the fixture has no actor, object, institution, source, contact, credential, token,
  network, browser-storage, or cookie surface.
- Tests scan production admin-web sources and prove neither fixture nor projection is imported.

## Explicit exclusions

There is no live admin page or navigation, authenticated session, real MFA, role or grant,
authoritative backend response, provider/resource/patient/clinical data, source warning, moderation,
audit viewer, clinical queue, maker-checker workflow, persistence, migration, API/BFF, network call,
browser storage, feature activation, pilot, or production behavior.

## Acceptance truth and next action

Static synthetic presentation evidence does not satisfy admin accessibility, identity,
authorization, source governance, audit, clinical review, or release acceptance. P21-C/D and every
live P21 capability remain blocked by the accountable decisions recorded in Spec 25 and the P21
readiness reconciliation. Any production component, route, BFF, or data/action surface requires a
separately bounded unit with authoritative backend and governance inputs.
