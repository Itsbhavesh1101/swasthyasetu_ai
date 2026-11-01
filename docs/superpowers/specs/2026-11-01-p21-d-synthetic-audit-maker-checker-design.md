# P21-D Synthetic Audit and Maker-Checker Design

## Intent

Provide detached engineering-only proof for content-free separation-of-duty checks and immutable
audit snapshots without creating an approver, approval workflow, audit store, or audit viewer. The
proof lets later work reason about exact-revision binding, self-review rejection, deterministic
evidence snapshots, and adversarial input handling while every live P21 gate remains closed.

## Goals

- Define immutable synthetic proposal, checker-submission, independence-receipt, and audit-snapshot
  contracts with strict closed vocabularies.
- Accept only machine-shaped `syn_governance_*` identities, engineering versions, SHA-256 digests,
  and timezone-aware timestamps normalized to UTC.
- Evaluate maker/checker independence without returning an approval, publication, activation, or
  execution decision.
- Bind every receipt to the exact proposal revision, checker submission, institution, source, and
  purpose; self-review and scope drift abstain deterministically.
- Build canonical audit snapshots from at most 16 receipts, rejecting duplicate identities,
  semantic aliases, chronology violations, and forced mutation.
- Reject `STAGING`, `PILOT`, and `PRODUCTION` before inspecting supplied evidence.

## Non-goals and anti-goals

There is no real actor, role, MFA ceremony, reviewer appointment, policy/content/model/source
authority, approval/rejection, publish/activate/rollback action, patient or clinical content, audit
event schema, audit-of-audit, retention, legal hold, tamper-evident store, persistence, migration,
API, BFF, UI, search/export, event/job, feature flag, dependency, or runtime activation. An
independence-confirmed receipt proves only that two closed synthetic actor identifiers differ and
that the submitted metadata matches; it never authorizes a change.

## Approaches considered

1. **Live audit store and maker-checker workflow:** rejected because identity, event, access,
   retention, integrity, source-domain authority, and approval-policy decisions remain blocked.
2. **Audit viewer UI fixture:** rejected because P21-B already proves test-only presentation states
   and a viewer would imply an unavailable authorization and data source.
3. **Detached content-free contracts and pure evaluators:** selected because it exercises the P21-D
   invariants without creating authority, storage, routes, or data access.

## Contract shape

`SyntheticGovernanceProposal` binds a synthetic proposal/maker/object identity, exact engineering
revision and hash, synthetic institution/source/purpose scope, closed change kind, and creation time.
`SyntheticCheckerSubmission` binds a distinct synthetic checker and the exact proposal metadata it
claims to inspect. Both carry canonical fingerprints.

`evaluate_synthetic_maker_checker` reconstructs both inputs, validates chronology, and returns a
`SyntheticMakerCheckerReceipt`. Exact scope plus a distinct actor produces
`INDEPENDENCE_CONFIRMED`; self-review or any metadata mismatch produces `ABSTAINED` with a closed,
content-free reason. Neither disposition means approved.

`SyntheticGovernanceAuditSnapshot` contains only reconstructed receipts in canonical order and a
fingerprint. `build_synthetic_governance_audit_snapshot` checks the environment first, bounds input,
orders receipts, and rejects duplicate check identities or multiple receipts aliasing the same
proposal revision.

## Verification

Unit and adversarial tests cover immutability, UTC normalization, strict identities/enums,
fingerprints, direct-constructor and forced-mutation drift, self-review, exact-scope mismatch,
chronology, deterministic ordering, duplicate/alias rejection, capacity, protected-environment
short-circuiting, content-free errors, forbidden action/search/export surfaces, and continued
non-registration/no-route isolation.
