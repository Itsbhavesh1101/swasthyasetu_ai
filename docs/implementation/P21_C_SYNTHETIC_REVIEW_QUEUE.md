# P21-C Synthetic Review Queue Foundation

## Status

`PARTIAL - BOUNDED DETACHED ENGINEERING-SYNTHETIC SUBSET`

P21 remains partial. `AC-P21-006` remains live and unverified because this increment creates neither
a clinical review queue nor any authority to view or act on clinical information.

## Implemented boundary

- Immutable synthetic queue-item and queue-snapshot contracts use strict closed item kinds/states,
  machine-shaped identities, engineering versions, SHA-256 digests, bounded tuples, and canonical
  fingerprints.
- A pure builder reconstructs inputs, canonicalizes ordering, rejects duplicate item identities and
  semantic aliases, normalizes aware clocks to UTC, and enforces snapshot chronology.
- `STAGING`, `PILOT`, and `PRODUCTION` fail before any queue input, identifier, or clock is inspected.
- Direct-constructor and forced-mutation paths are revalidated with stable content-free errors.
- The module remains detached: it is absent from the module registry and exposes no route or action.

## Explicit exclusions

There is no patient, encounter, clinician, reviewer, assignment, institution/source authority,
clinical value, narrative, source content, confirmation, rejection, correction, supersession,
triage, policy, consent decision, audit event/store, persistence, migration, API/BFF, UI, event/job,
feature flag, dependency, network, or runtime registration/activation.

## Acceptance truth and next action

The snapshot is an unverified content-free engineering candidate list. It is not a clinical work
queue, trusted assignment, lawful access decision, reviewer disposition, source-access grant, audit
record, or production artifact. P10 live remains 0/9 approved. `FR-ADMIN-001..010`,
`FR-AUDIT-001..007`, and `AC-P21-001..008` remain `LIVE NOT VERIFIED`.

Any live P21-C work requires separately approved clinician identity/assignment, institution and
object scope, lawful purpose/consent, source/provenance access, fact/summary lifecycle and
concurrency rules, minimized audit/retention, API/UI privacy, and independent clinical/security
review.
