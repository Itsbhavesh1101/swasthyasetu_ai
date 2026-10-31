# P20-A Synthetic Care-Composition Contract Foundation

**Status:** Bounded detached engineering-synthetic subset implemented; P20 remains **PARTIAL**

**Baseline:** `origin/main @ 3051d88c8b874db42ed8b18e27acb2b271a21fba`

**Branch:** `phase/p20-a-synthetic-care-composition-contracts`

## 1. Governance decision

The P20 specification permits no live composer while clinical precedence, identity/institution
scope, consent purposes, source authority, provider truth, self-care eligibility, and production
release decisions remain unresolved. This unit therefore implements only a data-free contract
kernel. It cannot evaluate, recommend, rank, authorize, disclose, or execute a care action.

## 2. Implemented engineering subset

- closed engineering-only authority, classification, verification, evidence-channel, availability,
  action, reason and disposition vocabularies;
- immutable evidence references containing only synthetic IDs, versions, hashes and UTC chronology;
- immutable requests binding an exact synthetic snapshot and canonically ordered evidence set;
- immutable symbolic candidates bound to an exact evidence channel, identity, version and hash;
- deterministic request fingerprints independent of input ordering;
- a pure detached function that denies protected environments, reconstructs inputs, abstains on any
  unavailable evidence, validates exact references, and otherwise preserves every candidate;
- fail-closed duplicate identity, channel and semantic-candidate guards; and
- adversarial direct-constructor, mutation, drift, ordering, chronology, privacy and runtime-boundary
  tests.

`PRESENT_UNVERIFIED` means only that a synthetic structural fixture is available. It never means
safe, approved, authorized, clinically valid, or eligible for display.

## 3. Deliberately absent

- patient, subject, session, encounter, actor, institution or consent identifiers;
- narrative, clinical content, symptoms, diagnoses, policy thresholds, provider contacts or advice;
- P9/P14/P15 evaluation, action priority, candidate suppression, universal score or clinical route;
- data access, cross-module adapter, ORM import, persistence, migration, event, job or worker;
- FastAPI route, module/capability registration, feature flag, telemetry, network or external egress;
- patient/clinician/admin UI, P20-B journey, P20-C retrieval, P20-D E2E or runtime activation; and
- any live `AC-P20-001..010` or `AC-PROD-001..014` acceptance claim.

## 4. Security and failure behavior

Staging, pilot and production deny before fixture or clock inspection. Boundary reconstruction
detects forced mutation. Missing, stale, unknown, blocked, unavailable, unevaluated or pending-review
evidence causes whole-request abstention before candidates are inspected. Candidate aliases and any
evidence ID/version/hash/channel drift fail with a closed content-free error code. Available
synthetic candidates are all preserved in canonical order; none is selected, ranked, suppressed or
executed.

## 5. Acceptance status

This is bounded architecture evidence toward typed, versioned composition mechanics only. P20 is
**PARTIAL**. Every live `AC-P20-001..010` and product-level `AC-PROD-001..014` outcome remains
**NOT VERIFIED**. P20-B/C/D, P21, P23, pilot and release remain blocked by their recorded upstream
and accountable decisions.
