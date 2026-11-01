# P21-A Synthetic Admin Authorization Contracts

## Status

`PARTIAL — BOUNDED DETACHED ENGINEERING-SYNTHETIC SUBSET ONLY`

P21 remains partial. Every live `FR-ADMIN-*`, `FR-AUDIT-*`, and `AC-P21-*` outcome remains
unverified. This increment records no human approval and creates no administrator or runtime
authorization.

## Implemented boundary

- Immutable content-free request, grant, and decision contracts use a closed synthetic namespace.
- Exact action, actor, object, object version/hash, institution, source, and purpose binding is
  required.
- MFA is mandatory for a synthetic match; absent MFA abstains before grant inspection.
- Grant validity uses normalized UTC instants and half-open intervals.
- Duplicate IDs, overlapping semantic aliases, forced mutation, malformed types, and snapshot drift
  fail closed with stable content-free codes.
- Staging, pilot, and production environments are rejected before input inspection.
- A match is explicitly `MATCHED_SYNTHETIC_CONTRACT`; it is not runtime permission or approval.

## Explicit exclusions

There is no production identity provider, role/permission policy, credential, MFA ceremony,
institution/source assignment, provider/resource or patient data, clinical action, human approval,
maker-checker workflow, audit event/store, persistence, migration, API, UI, event, job, dependency,
module registration, feature activation, or protected-environment execution.

P21-B/C/D, P13-E, and all real admin, clinical-review, governance, audit, export, referral,
provider/resource, policy, model, content, feature-flag, pilot, and production behavior remain out of
scope and blocked by their recorded accountable decisions.

## Verification intent

Tests cover direct constructors, exact types, opaque identifiers, canonical fingerprints, UTC
normalization, chronology, every scope dimension, missing/future/expired grants, MFA, duplicates,
overlapping aliases, input ordering, forced mutation, protected environments, nonenumerating
abstention, absent routes/registration, and absent authorization/execution surfaces.

## Acceptance truth and next action

This is bounded engineering evidence only. It does not satisfy `FR-ADMIN-001..010`,
`FR-AUDIT-001..007`, or `AC-P21-001..008`. Accountable identity/institution, security, privacy,
source, clinical, audit/data, accessibility, operations, and release decisions remain outstanding.
Any runtime adapter, real role grant, API/BFF/UI, persistence, audit, clinical queue, or
maker-checker work requires a separately bounded unit and all applicable authority.
