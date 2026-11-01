# P24-C Synthetic Operational Rehearsal Planning Design

## Intent

Create a detached, engineering-synthetic contract that can describe proposed future P24 operational
rehearsals without executing a drill, deciding applicability, producing a result, or granting pilot
or release authority. This advances only the metadata-integrity foundation required before genuine
accountable owners can authorize nonproduction exercises.

## Goals

- Represent exactly the eight operational rehearsal scenarios named by the Master Implementation
  Plan: application rollback, policy rollback, model rollback, resource disable, incident
  escalation, backup/restore, purge failure, and provider outage.
- Bind each proposed plan to an exact engineering version, build, configuration, prerequisite,
  failure-injection, oracle, isolation/cleanup, privacy-canary, safe-off/rollback, evidence, and
  responsible-role description hash plus a UTC creation time.
- Produce one immutable, canonically ordered manifest for an exact build and proposed scope.
- Fail closed on malformed values, snapshot drift, incomplete or duplicate inventory, chronology
  errors, and protected environments using stable content-free error codes.
- Preserve all P24 blockers and keep every live acceptance criterion unverified.

## Non-goals and anti-goals

- No drill execution, process restart, deployment, rollback, backup, restore, purge, outage,
  escalation, failure injection, external call, or infrastructure mutation.
- No applicability decision, threshold, RTO/RPO, SLO, metric, result, pass/fail, evidence body,
  signature, waiver, release decision, pilot eligibility, or approval.
- No persistence, migration, API, UI, event, job, feature flag, module registration, dependency, CI
  configuration, production credential, patient data, or clinical behavior.
- No implication that a hash, complete inventory, green test, or plan is operational evidence.

## Constraints

- The package remains an unregistered pure contract under `backend/app/validation`.
- Builders permit only `LOCAL` and `TEST`; `STAGING`, `PILOT`, and `PRODUCTION` reject before any
  caller-controlled plan is inspected.
- Every plan and manifest is fixed to `ENGINEERING_ONLY`, `ENGINEERING_SYNTHETIC`, `UNVERIFIED`,
  `NOT_EXECUTED`, `NOT_ELIGIBLE`, `HUMAN_APPLICABILITY_AND_OPERATIONAL_APPROVAL_REQUIRED`, and
  release decision `NOT_RECORDED`.
- Scenario applicability remains `UNDECIDED`; the repository cannot decide whether an absent model,
  provider, backup design, or other component belongs in a future approved scope.
- All timestamps are aware and normalized to UTC. Hostile clock behavior becomes a stable
  content-free contract error.

## Approaches considered

### Execute synthetic nonproduction drills now

Rejected. The readiness review explicitly requires separate accountable authorization, exact
environment design, oracles, and owners before a drill. The repository lacks those approvals and
several required runtimes.

### Extend the P23 recovery-planning contract

Rejected. P23-D covers worker restart, duplicate event, retry, outbox recovery, and possible
projection rebuild. Reusing it would blur platform recovery validation with P24 release-candidate
rollback, backup, purge, escalation, and provider-outage governance.

### Add a separate P24-C release-rehearsal planning contract

Selected. It follows the existing detached validation pattern, preserves phase ownership, requires
no new dependency or infrastructure, and makes the absence of execution and authority explicit.

## Contract design

`SyntheticReleaseRehearsalScenario` is a closed enum with eight members. Each
`SyntheticReleaseRehearsalPlan` stores only machine-readable metadata and hashes. A
`SyntheticReleaseRehearsalManifest` contains exactly one plan per scenario, sorted by enum value,
all bound to the manifest build and configuration.

Snapshot helpers reconstruct inputs and compare fingerprints so forced mutation cannot cross the
boundary. The builder checks the environment first, validates exact cardinality before item
inspection, snapshots and sorts plans, then constructs the manifest.

## Failure behavior

All failures use `ReleaseRehearsalContractError` with a closed
`ReleaseRehearsalContractCode`. Messages contain only the code. Unknown types, malformed machine
values, invalid labels, unsafe clocks, and hostile timezone implementations never leak supplied
content.

## Verification

Tests exercise exact inventory, fixed authority labels, strict type and grammar rejection, UTC
normalization, hostile clocks, complete fingerprint binding, build/config consistency, duplicate,
missing and reordered inventory, chronology, protected-environment short circuiting, forced
mutation, content-free failures, lack of execution/result authority, and lack of runtime module or
route registration.

Passing tests prove only deterministic metadata integrity. `AC-P24-001..013` and
`AC-PROD-001..014` remain live/product-level unverified.
