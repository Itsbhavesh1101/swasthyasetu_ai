# P20-A Synthetic Care-Composition Contracts Design

**Date:** 2026-11-01

**Status:** Bounded engineering design; not a clinical, policy, privacy, security, or release
approval

## Intent

Create the smallest useful P20-A foundation: immutable, content-free contracts that can describe a
detached synthetic composition attempt without accessing patient data, evaluating clinical rules,
ranking care actions, or activating an orchestrator.

This foundation exists to make future integration explicit and testable. It must not make the
currently blocked P20 patient journey appear implemented.

## Approaches considered

### Full care orchestrator

Rejected. A full composer would need approved physical- and mental-health precedence, consent and
authorization scope, self-care eligibility, provider truth, and real source versions. Those inputs
do not exist, and inventing them would violate the P20 readiness STOP conditions.

### Cross-module adapters over existing P9/P13/P14/P15 outputs

Rejected. The current outputs are engineering-synthetic and independently bounded. Adapting them
into a shared service would create implied authority and coupling without approved access or policy.

### Detached synthetic contract kernel

Selected. It proves type, identity, version, chronology, availability, provenance-reference,
snapshot-integrity, and non-interference mechanics with closed symbolic fixtures. It never ranks,
suppresses, promotes, or executes an action.

## Scope

Add an unregistered `care_orchestration` package containing:

- closed engineering-only authority, classification, environment, evidence-channel, availability,
  action, and disposition vocabularies;
- immutable evidence references carrying only synthetic IDs, versions, hashes, timestamps, and
  explicit availability;
- an immutable request that binds an exact synthetic snapshot and a bounded set of independently
  owned evidence references;
- immutable action candidates that bind exact evidence references and governing artifact versions;
- an immutable decision receipt that either preserves all valid independent candidates or abstains;
  and
- a pure composition function that reconstructs every input, denies protected environments before
  inspecting fixtures, fails closed on drift or invalid references, abstains on any non-available
  evidence, and otherwise preserves candidates in canonical order.

## Invariants

1. Every object is exact-type validated, frozen, slotted, and reconstructed at trust boundaries.
2. Only unmistakably synthetic machine values are accepted.
3. All aware timestamps normalize to UTC; naive timestamps are rejected.
4. Duplicate evidence channels, IDs, candidates, and references are rejected.
5. Candidate references must resolve to evidence in the exact request snapshot.
6. Candidate governing version/hash must match its referenced evidence.
7. Any `NOT_EVALUATED`, `UNKNOWN`, `STALE`, `UNAVAILABLE`, `BLOCKED`, or
   `PENDING_HUMAN_REVIEW` evidence causes whole-request abstention.
8. Available evidence does not mean safe, approved, or authorized; it only permits structural
   preservation of already supplied synthetic candidates.
9. The kernel never chooses between candidates, creates a candidate, collapses channels into a
   score, or claims clinical precedence.
10. Protected environments deny before reading fixtures or clocks.
11. Errors and representations expose only bounded codes/metadata, never payloads or arbitrary
    exception text.
12. No registration, route, API, persistence, migration, event, job, flag, telemetry, network, or
    dependency is added.

## Verification

Adversarial tests cover direct construction, forced mutation, exact-type attacks, duplicate and
unknown references, snapshot/version/hash drift, chronology, UTC normalization, unavailable states,
input-order determinism, candidate preservation, protected-environment short circuiting, privacy-safe
errors, absent runtime surfaces, and unchanged Alembic/dependency boundaries.

## Non-goals

No real subject/session/encounter/actor/institution identifiers; no raw narrative or clinical data;
no consent or authorization decision; no P9/P14/P15 policy evaluation; no provider recommendation;
no action ranking or precedence; no patient/clinician/admin UI; no P20-B/C/D; and no live
`AC-P20-001..010` or `AC-PROD-001..014` acceptance claim.

