# P23-A Synthetic Journey Evidence Foundation

## Status

`PARTIAL — BOUNDED DETACHED ENGINEERING-SYNTHETIC P23-A FOUNDATION ONLY`

P23 remains `PARTIAL`. All `AC-P23-001..012` remain `LIVE NOT VERIFIED`. This increment does not
constitute an E2E result, clinical validation, accessibility review, performance baseline,
reliability exercise, observability acceptance, pilot decision, or release authorization.

## Baseline and branch

- Baseline: exact merged `origin/main @ d834ea891dcef4ade87d4d4792db961ef0def4c4`
- Branch: `phase/p23-a-synthetic-journey-evidence`
- Worktree: isolated from the user's existing checkout

## Implemented engineering boundary

The detached `app.validation` package provides:

- a closed enumeration of the 18 journeys listed in the canonical master implementation plan;
- immutable, slotted definitions, observations, evidence receipts, and manifests;
- exact engineering version, SHA-256, Git SHA, authority, classification, verification, and UTC
  validation;
- canonical fingerprints and snapshot reconstruction to detect forged or mutated inputs;
- an exact 18-entry manifest that permits only structured intake as
  `BOUNDED_P7_TECHNICAL_ONLY` and marks the other 17 journeys `BLOCKED_UNAPPROVED`;
- a pure evidence evaluator that returns only `EVIDENCE_CONSISTENT` or `ABSTAINED`, never `PASS`;
- no-inspection abstention for blocked journeys;
- protected-environment denial before caller-controlled definitions or observations are inspected;
- content-free stable errors and representations that do not echo evidence hashes.

## Isolation and prohibited authority

The package is not registered in the module registry and exposes no FastAPI route. It has no
execute, run, approve, promote, publish, release, persist, search, or export surface.

This increment adds no patient or clinical content, browser/API/database journey, clinical oracle,
network access, external integration, accessibility certification, load measurement, resilience
drill, persistence, migration, dependency, event, job, UI, feature flag, or runtime activation.

## Verification boundary

Focused tests cover:

- exact 18-journey inventory and canonical ordering;
- strict enum, identifier, version, hash, Git SHA, and time validation;
- aware non-UTC normalization and naive-clock rejection;
- immutable/direct-constructor invariants and forced-mutation detection;
- missing, duplicate, aliased, or wrong-readiness manifest entries;
- deterministic replay and input-order independence;
- exact metadata consistency and scope-drift abstention;
- blocked observation no-inspection behavior;
- protected-environment no-inspection behavior;
- stable content-free failures and hidden evidence representations;
- absence of execution/approval fields, route exposure, and module registration.

The complete repository quality, database, Docker, browser-list, security, and remote CI gates are
required on the final SHA before integration.

Local verification on the feature tree recorded:

- 49 focused P23-A tests passed;
- 1,994 backend tests passed and 101 PostgreSQL-gated tests skipped in the non-database gate;
- 92 isolated ML tests passed;
- 201 frontend tests passed, all three production web builds passed, and 13 Playwright journeys were
  discovered without adding a P23 browser journey;
- Ruff, formatting, mypy, compilation, import smoke, lock checks, Alembic single-head
  `p7a_0007`, documentation formatting, and `git diff --check` passed.

The local Docker Linux daemon was unavailable, so PostgreSQL integration, Docker health, Playwright
execution, Gitleaks, and image/configuration scanning must pass in the six-job remote CI run on the
exact final SHA before merge. This limitation is not treated as local evidence or waived acceptance.

## Acceptance truth and outstanding decisions

This foundation validates only synthetic metadata consistency. It does not validate the patient,
clinical, operational, accessibility, performance, or recovery outcome represented by a journey.
Even `STRUCTURED_CLINICAL_INTAKE` remains bounded P7 technical evidence rather than an approved
production clinical journey.

Before live P23-A work, accountable owners must still approve and provide:

- exact 18-journey applicability for an intended population, institution, and environment;
- owning-module runtime approvals and exact build/config/policy/source versions;
- lawful synthetic fixture rights, privacy classification, retention, and deletion rules;
- authoritative action and abstention oracles with independent reviewer ownership;
- identity, assignment, consent, and cross-subject access boundaries;
- browser/API/PostgreSQL consistency design and privacy-safe evidence capture;
- clinical/safety, accessibility/language, security/AppSec, SRE, product, domain, and independent QA
  decisions recorded by accountable humans.

P23-B accessibility, P23-C performance/load, P23-D resilience/recovery, P24, pilot, and release work
remain outside this increment.
