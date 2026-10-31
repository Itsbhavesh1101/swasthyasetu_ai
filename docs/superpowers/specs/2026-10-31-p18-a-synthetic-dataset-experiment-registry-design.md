# P18-A Synthetic Dataset and Experiment Registry Design

## Intent

Create the smallest offline engineering foundation for P18-A without selecting a medical task,
accessing a dataset, training a model, recording a metric, or activating inference. The purpose is
to prove strict identity, provenance, reproducibility-metadata, version pinning, and isolation
mechanics that later approved research work can build on.

## Goals

- Define immutable, content-free synthetic dataset and experiment records.
- Validate exact identity, hashes, versions, UTC chronology, status, and authority on construction
  and again at trust boundaries.
- Resolve records only by explicit ID and version from immutable in-memory snapshots.
- Bind an experiment record to the exact dataset fingerprint it references.
- Deny staging, pilot, and production before inspecting supplied fixtures.
- Keep the isolated research tree covered by the normal CI quality gate.

## Non-goals and anti-goals

No real or sample biomedical dataset, download, file/network/database access, clinical task, label,
feature, split, preprocessing, training, estimator, metric, threshold, model artifact, model card,
MLflow service, dependency, API, worker, runtime module registration, inference, P19 code, approval,
or acceptance claim is in scope. A registry entry must never imply admission for a real benchmark,
validation, pilot, or production.

## Constraints

- Use the existing `/ml` research boundary, outside the patient API package.
- Use Python standard library only; dependency and lock files remain unchanged.
- Represent only closed ALPHA/BETA/GAMMA/DELTA identities and engineering-only enum values.
- Every error is a stable content-free code.
- Records are frozen, slot-based dataclasses and registries snapshot caller-owned input.
- Only LOCAL and TEST environments may construct registries.
- P18 remains PARTIAL and `AC-P18-001..010` remain LIVE NOT VERIFIED.

## Approaches considered

1. **Production backend module.** Easy to test, but it blurs the accepted research/patient-runtime
   boundary and makes later research dependencies easier to leak into the API closure. Rejected.
2. **New dependency-managed research environment.** Strong isolation, but P18-A needs no external
   package and a second lock/profile would be unjustified infrastructure. Rejected for this unit.
3. **Standard-library package under `/ml`, verified by existing backend dev tooling.** Preserves the
   repository's research boundary without adding dependencies while making lint, typing, tests, and
   import-isolation checks mandatory in CI. Selected.

## Design

`ml/research/contracts.py` owns strict enums, errors, dataset/experiment records, reconstruction
validators, and canonical SHA-256 fingerprints. Dataset records contain only closed synthetic
source/license/classification/status tokens plus opaque hashes. Experiment records remain explicitly
not executed and unapproved; they bind code, lock, configuration, and exact dataset fingerprints but
contain no outputs, metrics, or artifacts.

`ml/research/registry.py` owns immutable dataset and experiment registries. Constructors validate
the environment first, then accept exact tuples, reconstruct records, reject duplicates, enforce a
small entry bound, and expose only version-pinned resolution. Experiment registry construction
fails if the referenced dataset identity or fingerprint is absent or mismatched.

`ml/tests` uses the standard library test framework. Tests cover direct construction, forced
mutation, UTC normalization, unknown/duplicate/oversized entries, hostile inputs, protected
environment short-circuiting, fingerprint mismatch, caller mutation, deterministic fingerprints,
content-free errors, and the absence of research imports from `backend/app`.

`scripts/quality_gate.py` runs Ruff, formatting, strict mypy, unittest, and compile checks for `/ml`
using the already locked backend development toolchain. It does not add a research runtime
dependency to the backend.

## Governance result

This unit is a separately bounded synthetic engineering authorization only. It creates no human or
clinical approval, resolves none of the P18 readiness gates, and supplies no evidence for a real
benchmark. P18-B through P18-E and all P19 work remain outside scope.
