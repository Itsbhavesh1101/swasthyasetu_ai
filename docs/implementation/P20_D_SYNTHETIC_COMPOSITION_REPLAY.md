# P20-D Synthetic Composition-Replay Preflight

**Status:** Bounded detached engineering-synthetic preflight implemented; P20 remains **PARTIAL**

**Baseline:** `origin/main @ 19b64409f2e69f97700fc55079869d434e0862c0`

**Branch:** `phase/p20-d-synthetic-composition-replay`

## 1. Governance decision

The P20 readiness review does not authorize a live cross-module journey, patient or clinical data,
clinical precedence, action execution, or runtime activation. This unit therefore replays only the
detached symbolic artifacts already produced by the bounded P20-A/B/C engineering preflights. It
is an offline consistency proof, not the live P20-D end-to-end acceptance slice.

## 2. Implemented engineering subset

- an immutable, versioned replay artifact bound to an exact validated P20-C reconciliation;
- deterministic re-composition of P20-A symbolic candidates against the exact reconciled request;
- preservation of exact candidate-to-evidence identity, version, hash, channel, and reason binding;
- explicit abstention when structural evidence is unavailable or no candidate is supplied;
- reconstruction validators and content-free fingerprints that expose reconciliation or replay
  drift, including mutation after construction;
- UTC normalization, chronology validation, and protected-environment denial before artifact or
  candidate inspection; and
- adversarial tests for request/evidence drift, replay/version/chronology drift, unavailable
  evidence, direct construction, forced mutation, immutability, and runtime/API isolation.

The replay outcome is limited to `PRESERVED` or `ABSTAINED`. Preserved means only that a synthetic
symbolic candidate retains its exact structural evidence binding. It does not mean clinically
approved, safe, recommended, authorized, executable, or suitable for a patient.

## 3. Deliberately absent

- patient, subject, session, encounter, consent, identity, actor, institution, diagnosis,
  recommendation, narrative, document, provider, model, or raw payload data;
- imports from live domain services, repositories, policies, registries, or adapters;
- clinical precedence, scoring, ranking, suppression policy, recommendation, authorization, or
  execution;
- database, ORM, cache, retrieval, search, RAG, vector, API, event, job, worker, network, or
  external access;
- persistence, migration, module/capability registration, feature flag, telemetry, UI, or runtime
  wiring;
- dependency or lockfile changes; and
- live P20-B patient integration, live P20-C retrieval, live P20-D cross-module E2E behavior,
  pilot, or production activation.

## 4. Security and failure behavior

Staging, pilot, and production deny before reconciliation or candidate inspection. Reconciliation
artifacts are reconstructed before use, and their stored fingerprint must match the reconstruction.
Every replay reconstructs the decision and binds it to the exact request and referenced evidence.
Malformed types, non-UTC-aware chronology, identity drift, unavailable-state inconsistency, and
forced mutation fail closed with stable content-free codes. No partial replay artifact is returned.

## 5. Acceptance status

This is bounded offline evidence for deterministic structural composition replay only. It is not a
patient journey, real module integration, clinical decision, authorization check, data retrieval,
availability proof, live E2E validation, approval, or release evidence. P20 remains **PARTIAL**.
Every live `AC-P20-001..010` and product-level `AC-PROD-001..014` outcome remains **NOT VERIFIED**.
Any real patient context, source adapter, clinical policy, journey, API/UI, persistence, or runtime
activation remains subject to the unresolved decisions in `P20_READINESS_GATE_REVIEW.md`.

Next action: independently review this bounded offline replay. Do not add a real module adapter,
patient journey, clinical precedence, data access, action execution, UI, persistence, or activation
until the recorded P20 readiness prerequisites genuinely exist.
