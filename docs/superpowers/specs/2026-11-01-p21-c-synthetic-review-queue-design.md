# P21-C Synthetic Review Queue Design

## Intent

Provide a detached engineering-only proof for a bounded, content-free review queue without creating
clinical review authority. The proof lets later work reason about immutable queue snapshots,
deterministic ordering, stale/source-unavailable states, and adversarial input handling while all live
P10 and P21 gates remain closed.

## Goals

- Define immutable synthetic queue-item and queue-snapshot contracts with strict closed vocabularies.
- Accept only machine-shaped `syn_review_*` identities, engineering versions, SHA-256 digests, and
  timezone-aware timestamps normalized to UTC.
- Build snapshots deterministically from at most 16 items, reject duplicate identities and semantic
  aliases, and detect direct-constructor or post-construction drift.
- Reject `STAGING`, `PILOT`, and `PRODUCTION` before inspecting queue inputs.
- Keep errors content-free and prove the module is neither registered nor exposed through an API.

## Non-goals and anti-goals

There is no patient/encounter/source content, clinician identity, assignment, MFA ceremony, clinical
disposition, confirmation, rejection, correction, triage, policy, audit event, persistence,
migration, API, UI, event/job, feature flag, dependency, or runtime activation. A queue item is an
unverified engineering candidate, never evidence that a person may view or act on a clinical object.

## Approaches considered

1. **Live P10/P21 clinical queue:** rejected because trusted identity, assignment, lawful access,
   provenance review, lifecycle, audit, and retention approvals remain 0/9.
2. **Test-only UI fixture:** safe but duplicates P21-B and proves no backend contract invariants.
3. **Detached content-free backend contracts and pure builder:** selected because it advances the
   next architectural boundary without creating a route, data read, action, or authority claim.

## Contract shape

`SyntheticReviewQueueItem` carries only a synthetic item/object identity, closed item kind and state,
engineering version/hash, and creation time. `SyntheticReviewQueueSnapshot` carries a synthetic
snapshot identity, generation time, a canonical tuple of reconstructed items, a fingerprint, and
fixed `ENGINEERING_ONLY` / `ENGINEERING_SYNTHETIC` / `UNVERIFIED` labels.

`build_synthetic_review_queue` checks the environment first, then reconstructs and orders the tuple,
rejects duplicate IDs and semantic aliases, verifies chronology, and creates the snapshot. Snapshot
validation reconstructs all nested items so forced mutation cannot bypass invariants.

## Verification

Unit and adversarial tests cover immutability, UTC normalization, strict enums and identifiers,
canonical fingerprints/order, duplicate/alias rejection, capacity and chronology, drift, protected
environment short-circuiting, content-free errors, forbidden fields/methods, and runtime isolation.
