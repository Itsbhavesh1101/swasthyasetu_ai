# P20-B Synthetic Module-Evidence Boundary Preflight

**Status:** Bounded detached engineering-synthetic preflight implemented; P20 remains **PARTIAL**

**Baseline:** `origin/main @ 0ef98fcc3e1e6ef7d6d56124694cfd606bd55ede`

**Branch:** `phase/p20-b-synthetic-module-adapter-contracts`

## 1. Governance decision

The P20 readiness review still blocks live patient integration, broader longitudinal reads, clinical
composition, source-module activation, and cross-module disclosure. P19 also has no approved real
benchmark. This unit therefore implements only a content-free structural port preflight. It cannot
retrieve patient data, evaluate evidence, rank or select an action, create authority, or satisfy the
live P20-B patient-integration slice.

## 2. Implemented engineering subset

- an immutable synthetic source descriptor bound to a closed channel, engineering version, and
  SHA-256 fingerprint;
- an immutable query that binds an exact P20-A request fingerprint and exact evidence identity,
  version, hash, availability, source descriptor, channel, and UTC request time;
- an immutable receipt that must echo every query identity and cannot carry arbitrary payload;
- a provider-neutral structural inspection port;
- a fail-closed gateway limited to `LOCAL` and `TEST` environments;
- a deterministic test-only adapter that echoes structural metadata without retrieval or
  interpretation; and
- adversarial tests for mutation, drift, chronology, source failure, channel mismatch, missing
  evidence, protected environments, unavailable evidence, and privacy-sensitive field absence.

`PRESENT_UNVERIFIED` remains an engineering fixture state. It does not mean clinically available,
approved, current, safe, authorized, or eligible for display.

## 3. Deliberately absent

- patient, subject, session, encounter, actor, institution, consent, narrative, symptom, diagnosis,
  recommendation, provider, remedy, clinical policy, or raw payload fields;
- imports from P4/P5/P7/P8/P9/P10/P11/P13/P14/P15/P16/P17/P18/P19 source domains;
- data access, retrieval, cross-module ORM access, persistence, migration, event, job, or worker;
- candidate creation, precedence, suppression, ranking, selection, authorization, or execution;
- FastAPI routes, module/capability registration, feature flags, telemetry, UI, or runtime wiring;
- network access, external egress, dependency or lockfile changes; and
- live P20-B patient integration, P20-C retrieval, P20-D E2E, pilot, or production behavior.

## 4. Security and failure behavior

Protected environments fail before the request or source is inspected. The gateway reconstructs the
P20-A request, source descriptor, query, and receipt at each boundary. A source/channel mismatch,
missing evidence reference, identity/version/hash/availability drift, invalid UTC chronology, or
malformed receipt fails closed. Unexpected adapter exceptions become a stable content-free
`SOURCE_FAILURE` and never expose exception text.

## 5. Acceptance status

This is bounded architecture evidence toward a typed source boundary only. It is not a live module
adapter and does not prove patient integration, consent, authorization, provenance, clinical
precedence, availability, or resilience. P20 remains **PARTIAL**. Every live `AC-P20-001..010` and
product-level `AC-PROD-001..014` outcome remains **NOT VERIFIED**. Any real source read, patient
journey, clinical composition, UI, persistence, or activation still requires the unresolved
accountable decisions recorded in `P20_READINESS_GATE_REVIEW.md`.
