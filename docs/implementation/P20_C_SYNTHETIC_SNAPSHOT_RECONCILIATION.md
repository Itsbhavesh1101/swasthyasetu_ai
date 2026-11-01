# P20-C Synthetic Snapshot-Reconciliation Preflight

**Status:** Bounded detached engineering-synthetic preflight implemented; P20 remains **PARTIAL**

**Baseline:** `origin/main @ 5db46ce4904caa039997ed7d4d3b225c967425cb`

**Branch:** `phase/p20-c-synthetic-snapshot-reconciliation`

## 1. Governance decision

The P20 readiness review does not authorize longitudinal retrieval, patient integration, broader
source access, clinical composition, or runtime activation. This unit therefore reconciles only the
content-free structural receipts introduced by P20-B against an exact P20-A synthetic request. It
does not read a record, evaluate a policy, infer availability, or satisfy live P20-C selective
longitudinal/retrieval use.

## 2. Implemented engineering subset

- an immutable, versioned reconciliation artifact bound to an exact P20-A request fingerprint;
- exact one-to-one receipt coverage for every synthetic evidence channel in the request;
- deterministic canonical ordering and fingerprinting independent of source-map order;
- reconstruction of each P20-B query and receipt to detect identity, descriptor, version, hash,
  availability, query-fingerprint, and UTC chronology drift;
- an explicit structural state distinguishing complete synthetic echoes from complete echoes that
  contain unavailable evidence;
- fail-closed exact source-set validation before any adapter call;
- protected-environment denial before request or source-map inspection; and
- adversarial tests for missing, duplicate and extra receipts, missing and extra sources, adapter
  failure, mutation, chronology, unavailable evidence, runtime isolation, and sensitive-field
  absence.

`STRUCTURALLY_COMPLETE` means only that every synthetic reference has an exact validated structural
echo. It does not mean the evidence is clinically complete, current, safe, approved, authorized, or
eligible for use. Unavailable evidence remains explicit and is never interpreted as negative.

## 3. Deliberately absent

- patient, longitudinal, clinical, document, provider, model, policy, consent, identity, actor,
  institution, narrative, symptom, diagnosis, recommendation, or raw payload data;
- imports from source-domain services or repositories;
- database, ORM, cache, search, RAG, vector, API, event, job, worker, network, or external access;
- freshness thresholds, clinical precedence, evidence weighting, universal scoring, candidate
  creation, suppression, ranking, selection, authorization, or execution;
- persistence, migration, module/capability registration, feature flags, telemetry, UI, or runtime
  wiring;
- dependency or lockfile changes; and
- live P20-B patient integration, live P20-C retrieval, P20-D E2E, pilot, or production behavior.

## 4. Security and failure behavior

Staging, pilot, and production deny before request or source inspection. Source keys must exactly
match the request channels before any call. A source failure yields no reconciliation artifact and
is reduced to the stable content-free `SOURCE_FAILURE` code. Every receipt is reconstructed from the
request, descriptor fingerprint, exact evidence reference, request time, and canonical query ID.
Any missing, duplicate, extra, drifted, malformed, or future-completed receipt fails closed.

## 5. Acceptance status

This is bounded contract evidence for deterministic structural reconciliation only. It is not
patient-context retrieval, authorization, consent evaluation, clinical integration, availability
proof, E2E validation, or release evidence. P20 remains **PARTIAL**. Every live
`AC-P20-001..010` and product-level `AC-PROD-001..014` outcome remains **NOT VERIFIED**. Any real
longitudinal read, source adapter, patient journey, clinical composition, UI, persistence, or
activation remains subject to the unresolved decisions in `P20_READINESS_GATE_REVIEW.md`.
