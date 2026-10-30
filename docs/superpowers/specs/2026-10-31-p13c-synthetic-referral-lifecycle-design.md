# P13-C Synthetic Referral Lifecycle Design

## Intent

Add pure engineering mechanics for referral status, optimistic versioning, explicit transition
policy injection, and idempotent replay without deciding any live transition, consent, destination,
payload, delivery, or correction rule.

## Canonical reconciliation

The canonical domain model defines the closed status vocabulary, while the P13 policy labels its
proposed transition matrix unapproved. Therefore this unit exposes the status names but bundles no
default or production transition policy. A caller must supply an immutable, versioned, synthetic
policy fixture. The engine applies only an exact pair present in that fixture; the fixture is not a
clinical, privacy, operational, or release decision.

## Constraints

- No patient, session, encounter, actor, institution, destination, consent, payload, reason,
  priority, contact, transcript, external reference, adapter, webhook, notification, or delivery.
- No persistence, migration, API, outbox, event, job, worker, feature flag, dependency, or runtime
  registration.
- No bundled transition graph, terminal-state semantics, correction workflow, expiry clock, retry,
  or side-effect claim.
- Every identifier is reserved synthetic data; authority is permanently engineering-only,
  engineering-synthetic, and unverified.

## Design

`app.modules.referrals.domain` owns frozen, slotted referral, transition-pair, policy, command,
receipt, and application contracts. Constructors validate strict types, bounds, chronology,
reserved identifiers, UTC timestamps, policy artifact identity, version adjacency, nested forced
mutation, and consistent direct construction.

`apply_synthetic_transition` is pure. It revalidates all inputs, requires the referral identity,
expected version, source state, chronology, and exact policy pair, then returns a new aggregate and
immutable receipt. It performs no side effect. Receipt history is bounded and referral-scoped.
An exact repeated idempotency key and command fingerprint is a no-op against state at or beyond the
recorded result; a reused key with different intent fails as a conflict. Replay never rolls state
back and never claims exactly-once delivery.

## Non-goals and acceptance

This does not satisfy live referral acceptance or authorize sharing. Acceptance is focused
adversarial coverage, full regression, unchanged schema/dependencies/runtime, and exact-SHA CI.
`FR-REF-001..013` and `AC-P13-006..010` remain live-not-verified.
