# P23-A Synthetic Journey Evidence Design

## Intent

Create the smallest safe P23-A engineering foundation that makes future end-to-end evidence explicit
and tamper-evident without executing or approving any blocked cross-module journey. The foundation is
for engineers preparing synthetic validation metadata; it is not a patient workflow, clinical oracle,
accessibility audit, performance run, recovery drill, or release gate.

## Goals

- Represent all 18 canonical P23 journeys as a closed, versioned inventory.
- Distinguish the existing bounded P7 technical path from journeys that remain unapproved and blocked.
- Bind a synthetic observation to an exact journey definition, build SHA, configuration hash, fixture
  hash, oracle hash, and UTC capture time.
- Produce only `EVIDENCE_CONSISTENT` or `ABSTAINED`; never `PASS`, approval, or release authority.
- Reject protected environments before reading caller-controlled journey data.
- Fail closed on drift, aliases, duplicate inventory entries, malformed input, or chronology errors.

## Non-goals and anti-goals

- No Playwright journey expansion, patient or clinical data, browser/API/database execution, network,
  external integration, load measurement, accessibility certification, or resilience exercise.
- No persistence, migration, API, UI, event, job, dependency, feature flag, module registration, or
  runtime activation.
- No invented clinical, privacy, identity, accessibility, performance, operational, or human approval.
- No claim that P23, P23-A, any `AC-P23-*`, or any product-level outcome is complete.

## Constraints

- The P23 readiness review remains authoritative: live cross-module journeys and their oracles are
  blocked. This unit may only provide detached engineering-synthetic mechanics.
- P7 manual text/touch remains the only bounded technical path; even it is not a production clinical
  acceptance result.
- P8-C/P9-C Stage 3 and all recorded P10-P24 governance restrictions remain unchanged.
- Errors must be stable and content-free. All contracts are immutable and reconstruct nested inputs.
- `LOCAL` and `TEST` are the only permitted environments.

## Approaches considered

### 1. Expand Playwright across the 18 journeys

Rejected. Seventeen journeys lack approved runtime, data, and independent oracles. Tests would either
fabricate authority or encode false success.

### 2. Documentation-only P23 inventory

Rejected as the implementation path. The readiness documents already inventory the gaps; another
prose-only artifact would not provide executable integrity checks.

### 3. Detached synthetic journey-evidence contracts and evaluator

Selected. A pure, unregistered `app.validation` package can validate metadata integrity and abstention
behavior while making no external call and granting no authority. It advances test infrastructure
without crossing governance boundaries.

## Architecture

`backend/app/validation/contracts.py` owns strict enums, immutable journey definitions, observations,
receipts, manifests, canonical fingerprints, UTC normalization, and snapshot reconstruction.

`backend/app/validation/evidence.py` owns two pure operations:

1. build an exact 18-entry canonical manifest from detached definitions; and
2. evaluate one synthetic observation against one definition, returning consistent metadata only for
   the bounded technical state and otherwise abstaining.

Blocked definitions short-circuit before inspecting an observation. Protected environments
short-circuit before inspecting any caller-controlled definition or collection. Receipts embed
reconstructed definition/observation snapshots so direct constructors cannot forge digest-only
evidence.

The package is intentionally outside the module registry and exposes no execute, run, approve,
publish, persist, search, export, or release surface.

## Contract model

- `SyntheticJourneyId`: the exact 18 canonical master-plan journey identifiers.
- `SyntheticJourneyReadiness`: `BOUNDED_P7_TECHNICAL_ONLY` or `BLOCKED_UNAPPROVED`.
- `SyntheticObservationState`: `METADATA_RECORDED` only; it is deliberately not a pass state.
- `SyntheticEvidenceDisposition`: `EVIDENCE_CONSISTENT` or `ABSTAINED`.
- `SyntheticEvidenceReason`: exact metadata match, blocked journey, or scope mismatch.
- `SyntheticJourneyDefinition`: exact engineering version/hashes/readiness and UTC creation time.
- `SyntheticJourneyObservation`: exact build/config/fixture/oracle metadata and UTC capture time.
- `SyntheticJourneyEvidenceReceipt`: reconstructs inputs and derives the only valid disposition.
- `SyntheticJourneyManifest`: contains exactly one definition for every canonical journey, sorted by
  identifier, with a deterministic fingerprint.

## Verification

Test-first coverage will include direct construction, forced mutation, wrong enum types, malformed
hash/version/SHA values, naive/non-UTC time, chronology, duplicate and missing inventory, canonical
ordering, blocked short-circuit behavior, protected-environment short circuiting, scope drift,
receipt forgery, deterministic replay, content-free failures, package isolation, and absence of
authority/execution surfaces. Full backend, frontend, Docker/PostgreSQL, Playwright-list, and remote
six-job CI gates remain required before integration.

## Governance outcome

This unit records engineering mechanics only. P23 remains `PARTIAL`; all `AC-P23-001..012` remain
`LIVE NOT VERIFIED`. Future live P23-A still requires the accountable journey inventory, fixture
rights, independent oracles, identity/consent/privacy scope, runtime approvals, and exact-SHA evidence
specified by `P23_READINESS_GATE_REVIEW.md`.
