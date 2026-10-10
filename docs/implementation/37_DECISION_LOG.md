# SwasthyaSetu AI
## 37 — Decision Log

**Document ID:** `SSAI-DEC-037`  
**Filename:** `37_DECISION_LOG.md`  
**Status:** P0 / Architecture & Product Decision Register  
**Version:** `1.0.0-draft`

---

# 1. Purpose

This log records accepted high-impact decisions so future Codex prompts do not silently revisit or contradict them.

Statuses:

```text
PROPOSED
ACCEPTED
SUPERSEDED
REJECTED
```

Material architecture decisions may also receive standalone ADR files under `docs/adr/`.

---

# 2. ADR-001 — Modular Monolith First

**Status:** ACCEPTED

## Context

The platform has many logical domains but does not yet justify operational complexity from many microservices.

## Decision

Use one FastAPI modular-monolith backend initially, with strong bounded-context boundaries.

## Consequences

- simpler local development;
- easier transactions;
- easier Codex navigation;
- modules must remain extractable;
- no casual cross-module ORM access.

---

# 3. ADR-002 — Ports and Adapters for External Systems

**Status:** ACCEPTED

## Decision

LLM, OCR, speech, translation, notifications, storage, FHIR, ABDM, model inference, and quantum execution are accessed through ports/adapters.

## Consequences

Vendor SDKs stay out of domain/application logic and can be replaced.

---

# 4. ADR-003 — Deterministic Safety Authority

**Status:** ACCEPTED

## Decision

Safety-critical physical and mental-health routing is deterministic and versioned.

LLM output may contribute structured signals but is not the final safety authority.

## Consequences

- reason codes required;
- policy versions required;
- regression tests required;
- model/LLM output cannot downgrade hard overrides.

---

# 5. ADR-004 — FHIR Is an Interoperability Boundary

**Status:** ACCEPTED

## Decision

SwasthyaSetu maintains an internal domain model optimized for product workflows and maps it to FHIR at the interoperability boundary.

## Consequences

- internal domain is not forced to mirror FHIR;
- mapping/validation layer is required;
- FHIR vendor/server may change behind adapter.

---

# 6. ADR-005 — Research/QML Isolation

**Status:** ACCEPTED

## Decision

Classical ML and QML research are isolated from production clinical authority.

## Consequences

- research models do not auto-promote;
- experiment artifacts require registry/approval;
- research failure does not break patient intake;
- QML cannot override safety.

---

# 7. ADR-006 — Typed Domain Events + Transactional Outbox

**Status:** ACCEPTED

## Decision

Use versioned domain/integration events and a transactional outbox for asynchronous reactions.

## Consequences

- handlers must support idempotency where needed;
- event transport can later move to Redis Streams/NATS/RabbitMQ/Kafka;
- business modules do not depend on broker implementation.

---

# 8. ADR-007 — Compile-Time Feature Registration

**Status:** ACCEPTED

## Decision

Use explicit feature/module registration at build/runtime initialization rather than arbitrary untrusted runtime code plugins.

## Consequences

- architecture remains extensible;
- new features still require deployment;
- lower security/operational complexity.

---

# 9. ADR-008 — PostgreSQL as Transactional Source of Truth

**Status:** ACCEPTED

## Decision

PostgreSQL stores authoritative transactional application state.

Redis, pgvector, caches, and search indexes are secondary/derived.

## Consequences

Critical consent, referral, safety, and clinical truth must not exist only in Redis/vector storage.

---

# 10. ADR-009 — Object Storage for Binary Medical Documents

**Status:** ACCEPTED

## Decision

Original medical files and large derived binary assets use object storage. PostgreSQL stores metadata, references, hashes, state, and retention metadata.

## Consequences

Deletion/retention must coordinate DB and object storage.

---

# 11. ADR-010 — Clinical Provenance Is First-Class

**Status:** ACCEPTED

## Decision

AI-extracted or imported clinical facts retain source/provenance and verification state.

## Consequences

The system must distinguish:

- patient-reported;
- OCR-extracted;
- imported;
- model-inferred;
- clinician-confirmed;
- rejected/superseded.

---

# 12. ADR-011 — Three Separate Web Applications

**Status:** ACCEPTED

## Decision

Use separate patient, clinician, and admin Next.js applications in one monorepo.

## Consequences

- clearer authorization/UX boundaries;
- shared UI/contracts remain reusable;
- deployments may later differ independently.

---

# 13. ADR-012 — Shared Longitudinal Patient Context

**Status:** ACCEPTED

## Decision

Patient longitudinal context is a shared platform capability rather than duplicated per feature.

## Consequences

OCR, intake, self-care, FHIR, clinician views, and model input consume stable patient context interfaces.

---

# 14. ADR-013 — No Universal Health Score

**Status:** ACCEPTED

## Decision

Do not collapse physical safety, mental-health risk, self-care eligibility, model risk, or provider availability into one opaque universal score.

## Consequences

Each decision channel remains explainable and independently governed.

---

# 15. ADR-014 — Self-Care Uses Approved Knowledge

**Status:** ACCEPTED

## Decision

Patient-facing self-care/Ayurveda/gharelu guidance is retrieval-based from approved/versioned content.

## Consequences

LLM may explain approved content but cannot invent treatments/remedies.

---

# 16. ADR-015 — Provider Truth Comes from Registry/Validated Integration

**Status:** ACCEPTED

## Decision

Doctor/resource contacts come only from verified registry or validated external data source.

## Consequences

No LLM-generated provider contact information.

---

# 17. ADR-016 — Specialty/Service Routing Before Provider Selection

**Status:** ACCEPTED

## Decision

Map patient context to care category/specialty before selecting specific providers.

## Consequences

Individual provider selection remains transparent and registry-backed.

---

# 18. ADR-017 — Classical Baseline Before QML

**Status:** ACCEPTED

## Decision

Every QML disease-risk task requires a reproducible classical benchmark using comparable data split and metrics.

## Consequences

No fair QML claim without baseline discipline.

---

# 19. ADR-018 — No Quantum Advantage Claim by Default

**Status:** ACCEPTED

## Decision

The product/research report must not claim quantum advantage unless reproducible benchmark evidence supports it.

---

# 20. ADR-019 — Background Jobs for Long-Running Work

**Status:** ACCEPTED

## Decision

OCR, document processing, notifications, referral retries, large FHIR sync, ML/QML training, and similar long work use worker/job abstractions rather than blocking request handlers.

---

# 21. ADR-020 — Feature Flags for Staged/Risky Features

**Status:** ACCEPTED

## Decision

Experimental/high-risk optional features should support controlled activation.

## Consequences

- risky defaults off;
- feature flag is not authorization;
- mandatory safety control cannot be disabled while dependent risky feature remains active.

---

# 22. ADR-021 — Internal Contracts Are Typed

**Status:** ACCEPTED

## Decision

Pydantic/typed Python contracts, OpenAPI, typed TypeScript clients, and versioned event schemas are used at important boundaries.

---

# 23. ADR-022 — No Real Clinical Policy Invented During Scaffolding

**Status:** ACCEPTED

## Decision

Engineering may scaffold safety/policy engines with synthetic fixtures, but real patient-facing policy waits for appropriate approval.

---

# 24. ADR-023 — No Real Provider/Remedy Fabrication in Development

**Status:** ACCEPTED

## Decision

Development may use clearly synthetic provider and self-care fixtures. Synthetic data must never appear as verified production truth.

---

# 25. ADR-024 — New Features Are Insertable Into Roadmap

**Status:** ACCEPTED

## Decision

The phase sequence is disciplined but not immutable. New features can be inserted after requirement/dependency/safety review.

## Consequences

Update PRD, dependency map, implementation plan, acceptance criteria, and progress tracker before implementation.

---

# 26. ADR-025 — No Premature Full Multi-Tenancy

**Status:** ACCEPTED

## Decision

Do not implement a full tenancy model until deployment requirements are clearer.

## Consequences

Avoid hard-coded single-institution assumptions; retain institution/context fields where appropriate.

---

# 27. ADR-026 — No Arbitrary Runtime Plugin System

**Status:** ACCEPTED

## Decision

Extensibility uses bounded modules/capabilities and compile-time registration, not arbitrary dynamic code loading.

---

# 28. ADR-027 — Core Safety Paths Must Degrade Independently of Optional AI

**Status:** ACCEPTED

## Decision

Crisis resources, deterministic safety, manual intake, and core navigation must survive failures of optional LLM/OCR/speech/QML components where applicable.

---

# 29. ADR-028 — Raw Chat Is Not the Authoritative Clinical Record

**Status:** ACCEPTED

## Decision

Structured validated facts and explicitly governed records are authoritative application state.

Conversation is an interaction source, not the only clinical data model.

---

# 30. ADR-029 — Clinical Corrections Preserve History

**Status:** ACCEPTED

## Decision

Clinician corrections/rejections do not silently erase original AI extraction provenance.

---

# 31. ADR-030 — New Top-Level Repository Directories Require Justification

**Status:** ACCEPTED

## Decision

Ordinary feature work fits existing top-level concerns. Material top-level architecture additions require review/ADR.

---

# 32. Decision Template

Future entries should use:

```text
ADR-XXX
Title
Status
Context
Decision
Alternatives
Consequences
Migration/Rollback
```

---

# 33. Change Rule

Do not edit an accepted historical decision to make it appear it was always different.

If a decision changes:

- mark old ADR `SUPERSEDED`;
- create a new ADR;
- describe migration.


---

# R3 Technology Reconciliation Decisions

# ADR-031 — AI Gateway Means Project-Owned Orchestration by Default

**Status:** ACCEPTED

The initial AI gateway is an in-process SwasthyaSetu orchestration boundary over `LLMProvider`. A separately deployed LiteLLM/other gateway is conditional future infrastructure.

# ADR-032 — Research Tooling Is Isolated From Patient Runtime

**Status:** ACCEPTED

MLflow, Optuna, PennyLane, Qiskit Machine Learning and comparable research tooling live in separate dependency/runtime profiles and do not become transitive dependencies of the clinical API.

# ADR-033 — SwasthyaSetu Owns Model Approval

**Status:** ACCEPTED

MLflow registry state does not equal clinical approval. SwasthyaSetu governance records own pilot/production approval, calibration, thresholds, suspension and retirement.

# ADR-034 — Simple RAG Before General Agent Frameworks

**Status:** ACCEPTED

Default retrieval is project-owned `RetrievalService` + `EmbeddingProvider` + PostgreSQL/pgvector + optional reranker. LangChain/LlamaIndex are not core dependencies.

# ADR-035 — HAPI FHIR Is an Interoperability Sidecar

**Status:** ACCEPTED

HAPI FHIR is the preferred conformance/validation sidecar behind `FHIRProvider`; internal SwasthyaSetu domain/PostgreSQL remains canonical.

# ADR-036 — Benchmark-Gated OCR and Speech Providers

**Status:** ACCEPTED

PaddleOCR, IndicConformer and other concrete OCR/speech models may have adapters before final selection, but production approval requires project benchmark evidence.

# ADR-037 — PostgreSQL-Native Async Infrastructure First

**Status:** ACCEPTED

Use PostgreSQL outbox for reliable events and evaluate a PostgreSQL-native durable job backend before introducing a cache/broker dependency.

# ADR-038 — Dependency Profiles Are Architectural Boundaries

**Status:** ACCEPTED

Core, document AI, language AI, RAG, ML research, QML research, operations and development dependencies should remain separable.

# ADR-039 — Trusted, Hashed Model Artifacts Only

**Status:** ACCEPTED

Production model inference loads only approved immutable artifacts with hashes and schemas. Arbitrary executable serialized model uploads are prohibited.

# ADR-040 — Heavy Infrastructure Is Phase-Activated

**Status:** ACCEPTED

Keycloak, SeaweedFS, OpenBao, Valkey, HAPI FHIR, MLflow, Prometheus/Grafana, large AI runtimes and model-serving platforms are not default local-stack dependencies simply because they are approved candidates.

# ADR-041 — uv Manages the Backend Python Environment

**Status:** ACCEPTED

## Context

The engineering standards require one reproducible Python package-management workflow with a
lockfile, development dependencies, and simple local commands. No package manager was previously
selected.

## Decision

Use `uv` with `backend/pyproject.toml`, PEP 735 dependency groups, and `backend/uv.lock` for the
backend environment. The backend is an application project rather than a distributable package.

## Consequences

- backend installs use one lockfile and `uv sync --locked --dev`;
- runtime and development dependencies remain separately declared;
- Python 3.12+ is enforced by project metadata;
- no second Python package manager or competing requirements file is maintained.

---

# ADR-042 — pnpm Manages the Frontend Workspace

**Status:** ACCEPTED

## Context

P1-B introduces three Next.js applications and a shared UI package. The repository had no accepted
JavaScript workspace manager, and maintaining separate dependency graphs would weaken reproducibility
and shared-tooling consistency.

## Decision

Use pnpm `9.15.4`, pinned through the root `packageManager` field, with a single
`pnpm-workspace.yaml` covering `apps/*` and `packages/*` and one root `pnpm-lock.yaml`.

## Consequences

- frontend dependencies install through one reproducible lockfile;
- root commands run consistent lint, format, type, test, and build gates across workspaces;
- applications remain independently runnable and buildable;
- no npm, Yarn, or Bun lockfile is maintained alongside pnpm.

---

# ADR-043 — P1 Infrastructure Runtime Baseline

**Status:** ACCEPTED

## Context

P1-C requires reproducible local and CI runtimes without activating deferred production
infrastructure. The frontend also needs one Node runtime that matches its type declarations.

## Decision

- use Node.js `24.18.1` and matching Node 24 type declarations for frontend tooling;
- use PostgreSQL `16.12` as the local and CI database baseline;
- use Docker Compose for the P1 local stack, limited to PostgreSQL and the backend API;
- build the backend from the official Python `3.12.15-alpine3.23` image, pinned by digest, and use
  the operating-system package state contained in that immutable image without build-time upgrades;
- treat Gitleaks and Trivy as CI/operations tools only, not application dependencies.

## Consequences

- local and CI runtime versions are explicit and traceable;
- PostgreSQL readiness is demonstrated without pulling persistence implementation into P1;
- the backend runs as a non-root user from production-only locked dependencies;
- Redis/Valkey, object storage, identity, observability stacks, and other phase-gated services remain
  deferred;
- image builds require access to the pinned image registries and Alpine package repositories.
