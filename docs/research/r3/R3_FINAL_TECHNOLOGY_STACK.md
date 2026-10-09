# SwasthyaSetu AI — R3 Final Technology Stack & Adoption Matrix

**Document ID:** `SSAI-R3-TECH-001`  
**Status:** Architecture-reconciled technology decision baseline  
**Version:** `1.0.0-r3`  
**Date:** 2026-10-10  
**Supersedes:** scattered technology recommendations in R2-A through R2-E where this document gives a more specific adoption status.

---

# 1. Purpose

R1/R2 research intentionally evaluated more technologies than SwasthyaSetu should actually deploy.

R3 converts that research into one coherent implementation baseline for Codex.

The goal is not to select the maximum number of "best" tools. The goal is to select the **smallest coherent set of technologies that preserves safety, replaceability, research reproducibility, and future expansion**.

This document distinguishes:

```text
CORE / ADOPT NOW
    required or expected in the near-term implementation baseline

PORT NOW / PROVIDER LATER
    interface is implemented now; concrete external product activates only in its phase

BENCHMARK-GATED
    preferred candidates exist but final provider cannot be chosen honestly until project-specific benchmark

RESEARCH-ONLY
    allowed in isolated research environments; must not leak into patient runtime

PILOT/PRODUCTION LATER
    valid target technology but must not be added to default development stack yet

FUTURE
    architecture-compatible but not justified now

REJECTED AS DEFAULT
    should not become the standard implementation choice
```

---

# 2. Final Architecture Principle

SwasthyaSetu remains:

```text
Next.js feature applications
          |
       REST /api/v1
          |
FastAPI modular monolith
          |
application/domain modules
          |
typed ports and capabilities
          |
replaceable adapters
          |
PostgreSQL + object storage
          |
outbox + workers
```

External AI, FHIR, speech, OCR, storage, identity, notifications, model serving and quantum systems stay behind project-owned contracts.

No R3 decision changes the fundamental safety boundary:

```text
AI/model output
     |
validation
     |
deterministic policy
     |
governed action
     |
human clinical authority where applicable
```

---

# 3. Core Product Stack — ADOPT

| Layer | Final R3 selection | Status | Notes |
|---|---|---|---|
| Backend language | Python 3.12+ | CORE | Exact patch version pinned in lock/runtime image |
| Web API | FastAPI | CORE | Modular monolith transport layer |
| Validation/contracts | Pydantic v2 | CORE | API + boundary schemas; not a substitute for all domain behavior |
| ORM | SQLAlchemy 2.x | CORE | Explicit repositories and module ownership |
| Migrations | Alembic | CORE | Every persistent schema change |
| Primary DB | PostgreSQL | CORE | Clinical transactional source of truth |
| Vector extension | pgvector | ACTIVATE WHEN RAG EXISTS | Same PostgreSQL architecture; not required before RAG |
| HTTP client | async-capable `httpx`-style client | CORE | External service adapters |
| Frontend framework | Next.js + React | CORE | Patient, clinician, admin applications |
| Frontend language | TypeScript strict mode | CORE | Typed API boundaries |
| UI utility CSS | Tailwind CSS | CORE | Design implementation |
| Local container tooling | Docker + Docker Compose | CORE | No Kubernetes requirement |
| CI | GitHub Actions or equivalent | CORE | Lint/type/test/security gates |
| Observability contract | OpenTelemetry | CORE CONTRACT | Instrumentation/API standard |
| Metrics backend | Prometheus | PILOT/SELF-HOSTED | Add when deployment needs central metrics |
| Ops dashboard | Grafana | OPTIONAL | App must not depend on it |
| IaC | Terraform/OpenTofu | LATER | Only when real infrastructure resources exist |

---

# 4. Architectural Style — FINAL

## 4.1 Modular monolith first

SwasthyaSetu will **not** start as dozens of microservices.

One deployable FastAPI application owns the product modules, with separate workers when long-running jobs require them.

Potential extraction targets later:

```text
document AI
speech/language inference
FHIR sidecar
model inference
QML/research jobs
notification delivery
```

Extraction requires a measured reason:

```text
scaling
runtime isolation
security boundary
deployment cadence
team ownership
GPU/CPU requirements
```

---

# 5. Data Stack

## 5.1 PostgreSQL

**ADOPT.**

PostgreSQL holds:

```text
patient/encounter structured data
consent
provenance
provider/resource metadata
referrals
policy/model governance metadata
audit metadata
job/outbox metadata where applicable
```

PostgreSQL remains authoritative even if caches/queues/vector search disappear.

## 5.2 pgvector

**ADOPT WHEN RAG/semantic retrieval is introduced.**

Do not enable vector tables merely because pgvector is available.

Uses:

```text
approved knowledge retrieval
patient document semantic retrieval
future embedding-backed search
```

Not authoritative for:

```text
clinical facts
provider truth
consent
safety policy
```

## 5.3 Cache

**Valkey — OPTIONAL, ACTIVATE ONLY WITH A REAL EPHEMERAL USE CASE.**

Examples:

```text
rate limits
short-lived cache
temporary distributed coordination
non-authoritative session acceleration
```

Never:

```text
canonical clinical record
only copy of referral state
only copy of safety decision
```

No default Valkey service is required for early local development.

---

# 6. Object Storage

## 6.1 Contract

**SwasthyaSetu `ObjectStoragePort` — ADOPT NOW.**

## 6.2 Local development

Use a controlled local filesystem adapter for early development/tests where appropriate.

## 6.3 Self-hosted pilot target

**SeaweedFS — preferred candidate, activation later.**

Do not put SeaweedFS into the first repository scaffold or default Compose merely because R2-D preferred it.

Before activation:

```text
S3 compatibility spike
encryption configuration
private bucket policy
signed URL behavior
lifecycle/retention
backup/restore
malware/quarantine workflow
metrics
```

## 6.4 MinIO

**REJECTED AS NEW DEFAULT** for this project based on the researched 2026 upstream posture and license/maintenance considerations.

Existing deployments could still be integrated behind `ObjectStoragePort` if an institution already uses it.

---

# 7. Identity & Authentication

## 7.1 Pseudonymous sessions

**SwasthyaSetu-owned session model — ADOPT.**

Required for:

```text
zero-login first contact
kiosk
MannSetu pseudonymous experience
```

Do not force an IdP account for those flows.

## 7.2 Authenticated IdP

**Keycloak — preferred target, technical spike before activation.**

R3 does not require Keycloak during P0/P1 repository work.

When authenticated clinician/admin/patient identity is introduced, run a focused spike and then pin the selected IdP.

Alternatives remain:

```text
authentik
ZITADEL
deployment-managed OIDC provider
```

SwasthyaSetu owns resource authorization regardless of IdP.

---

# 8. Secrets

## 8.1 Contract

**`SecretProvider` / deployment configuration abstraction — ADOPT.**

## 8.2 Local development

Environment-based development secrets are acceptable with `.env` excluded from Git.

## 8.3 Self-hosted production

**OpenBao — preferred only when production requirements justify a dedicated secret manager.**

Do not require every developer to run OpenBao.

Cloud-managed secret stores may implement the same boundary.

---

# 9. Background Jobs & Reliable Events

## 9.1 Domain-event reliability

**PostgreSQL transactional outbox — ADOPT.**

It couples state change and event recording in one transaction.

## 9.2 Early development

**In-process job dispatcher — permitted for deterministic local/test scaffolding.**

It must not pretend to provide durable delivery.

## 9.3 Initial durable worker target

**Procrastinate — preferred PostgreSQL-native candidate; implementation spike required in async-processing phase.**

Reason:

```text
uses PostgreSQL
avoids immediate Redis dependency
fits modular-monolith operational model
```

## 9.4 Fallback

**Celery — mature fallback if project requirements exceed Procrastinate's fit.**

## 9.5 NATS / Kafka / RabbitMQ

**DEFER.**

No distributed broker until service extraction or event volume justifies it.

---

# 10. Logging, Metrics & Audit

## 10.1 OpenTelemetry

**ADOPT.**

Use OTel APIs/semantic context as the observability contract.

## 10.2 OTel Collector

**Preferred deployment distribution when centralized telemetry is introduced.**

## 10.3 Prometheus

**ADOPT for self-hosted pilot metrics.**

No PHI in labels.

## 10.4 Grafana

**OPTIONAL operations UI.**

## 10.5 Loki

**DEFER.**

Start with structured logs. Add a dedicated log backend only after operational need.

## 10.6 Audit

Audit is a separate product/governance data stream, not an OTel log substitute.

---

# 11. Security Tooling

| Capability | Selection | R3 status |
|---|---|---|
| Source/container/config/SBOM scanning | Trivy | ADOPT IN CI |
| Secret scanning | Gitleaks | ADOPT IN CI |
| Python lint | Ruff | ADOPT |
| Python typing | mypy or approved equivalent | ADOPT |
| Python tests | pytest + pytest-asyncio | ADOPT |
| Frontend lint/type/test | strict TS + project test tooling | ADOPT |
| Dependency pinning | lockfiles | MANDATORY |
| Container pinning | image tags + digests for protected environments | MANDATORY |

---

# 12. OCR / Document Intelligence

## 12.1 Architectural decision

**Implement `OCRPort` and document-processing contracts first.**

The repository must not couple document domain logic to one OCR framework.

## 12.2 Preferred baseline candidate

```text
PaddleOCR 3.x family
PP-OCRv5 / appropriate language models
PPStructureV3 for structured pages
```

**Status: BENCHMARK-GATED PRODUCTION PROVIDER.**

## 12.3 Hard-document candidate

**PaddleOCR-VL — benchmark candidate.**

## 12.4 Native parsing/normalization

**Docling — adopt/consider behind `DocumentParserPort`.**

Use it for document structure/normalization where the integration benchmark supports it.

## 12.5 Challengers

```text
Surya
docTR
Tesseract
RapidOCR
```

Tesseract remains a useful transparent baseline/fallback, not the default complex medical-document engine.

## 12.6 Final rule

R3 **does not falsely declare a production OCR winner before the medical-document benchmark**.

Codex may scaffold adapters, fixtures, worker jobs and benchmark harnesses. It must not label a provider "production approved" until benchmark acceptance is recorded.

---

# 13. Indian Language / Speech

## 13.1 Port-first architecture

Adopt project-owned interfaces:

```text
SpeechToTextPort
TextToSpeechPort
TranslationPort
LanguageDetectionPort
TransliterationPort
```

## 13.2 ASR

**faster-whisper — baseline/fallback candidate.**

**IndicConformer — preferred India-specialized challenger, benchmark-gated.**

The final language-by-language ASR provider remains benchmark-dependent.

## 13.3 Translation

**IndicTrans2 — preferred local translation implementation behind `TranslationPort`, benchmark required for medical semantics.**

## 13.4 Language ID

**IndicLID — adopt/consider behind adapter.**

It helps routing; it is not safety authority.

## 13.5 Transliteration

**IndicXlit — adopt/consider behind adapter.**

Named entities, medicines and clinical terms need preservation tests.

## 13.6 BHASHINI

**Optional external/pilot provider.**

Never make core product safety dependent on external hosted availability.

## 13.7 TTS

**BENCHMARK-GATED.**

IndicF5 is a modern local candidate. BHASHINI is a strong hosted candidate.

Patient voice cloning is not part of the default product.

---

# 14. Generative AI / LLM

## 14.1 Stable project boundary

**`LLMProvider` — ADOPT.**

Task-specific services:

```text
ClinicalIntakeExtractor
MentalHealthSignalExtractor
DocumentEntityExtractor
SummaryGenerator
TranslationAssistant where justified
KnowledgeExplanationGenerator
```

## 14.2 Default runtime topology

**Direct provider adapter first.**

Architecture:

```text
Domain/Application Task
       |
AI Orchestration Service
       |
LLMProvider
       |
Concrete Provider Adapter
```

"AI gateway" in SwasthyaSetu means a **project-owned orchestration/policy boundary**, not necessarily a separately deployed proxy.

## 14.3 LiteLLM SDK

**CONSIDER** if multiple direct provider adapters create unnecessary duplication.

## 14.4 LiteLLM Proxy/Gateway

**DEFER / CONDITIONAL.**

Only activate if we actually need:

```text
multi-provider central routing
central budgets/quotas
provider failover
shared virtual keys
centralized model governance across applications
```

Do not deploy it in MVP solely for abstraction.

## 14.5 Provider

Exact production LLM provider remains deployment/policy dependent and is not selected by R3.

Codex must not invent it.

---

# 15. RAG / Retrieval

## 15.1 Default architecture

Use a narrow project-owned:

```text
RetrievalService
    |
EmbeddingProvider
    |
PostgreSQL + pgvector
    |
optional RerankerProvider
```

## 15.2 Embeddings

**Sentence Transformers — preferred local embedding/reranking toolkit candidate.**

Every selected model requires:

```text
exact revision
model-specific license review
language benchmark
medical retrieval benchmark
remote-code review
```

## 15.3 LangChain

**NOT A CORE/DEFAULT DEPENDENCY.**

## 15.4 LlamaIndex

**NOT A CORE/DEFAULT DEPENDENCY.**

## 15.5 Haystack

**CONSIDER LATER** if genuinely complex RAG pipelines justify a framework.

Its use does not eliminate application responsibility for input validation, SSRF controls, prompt injection, and trusted pipeline definitions.

---

# 16. FHIR / ABDM

## 16.1 Source of truth

**Internal SwasthyaSetu domain/PostgreSQL remains canonical.**

FHIR is an interoperability representation.

## 16.2 Baseline

**FHIR R4 4.0.1** aligned with the ABDM interoperability work researched for this project.

## 16.3 HAPI FHIR

**ADOPT BEHIND `FHIRProvider` / sidecar boundary.**

Use for:

```text
validation
conformance
optional private FHIR projection repository
```

Do not move the whole product data model into HAPI.

Do not expose the HAPI starter defaults to production.

## 16.4 Remote FHIR client

**Project-owned httpx-based `FHIRRemoteClientPort` — preferred initial implementation.**

## 16.5 Medplum

**Architecture-pivot alternative, not default.**

## 16.6 Python FHIR type libraries

Do not use a library whose active major does not match the required R4 authority as the canonical conformance source.

## 16.7 ABDM

ABDM transport/flows remain a dedicated adapter and sandbox-validated phase.

Codex must not invent production ABHA flows.

---

# 17. Classical ML

## 17.1 Training

Use task-appropriate:

```text
scikit-learn
XGBoost
PyTorch
```

No novelty requirement overrides model suitability.

## 17.2 HPO

**Optuna — research-only standard when HPO is needed.**

## 17.3 Explainability

**SHAP — primary explanation toolkit for compatible models.**

Attribution is not causality.

## 17.4 Experiment tracking

**MLflow — ADOPT FOR RESEARCH.**

Separate tracking DB/artifact storage from clinical product data.

## 17.5 Governance

MLflow does **not** decide clinical approval.

SwasthyaSetu model-governance records decide:

```text
research validation
pilot approval
production approval
suspension
retirement
```

## 17.6 Persistence

Preferred order:

```text
ONNX if faithful
skops for compatible sklearn
trusted framework-native artifact
```

Arbitrary pickle/joblib/dill/cloudpickle upload is prohibited.

## 17.7 Inference

**ONNX Runtime — preferred portable runtime when parity tests pass.**

Disable ONNX Runtime vendor telemetry in healthcare deployment profile unless explicitly approved.

---

# 18. Model Serving

## 18.1 Initial

In-process or isolated application worker behind `ModelInferencePort`.

## 18.2 First service-extraction candidate

**BentoML — optional when model runtime/scaling actually requires a separate service.**

## 18.3 Kubernetes fleet

**KServe — future.**

## 18.4 Specialized GPU inference

**Triton — future.**

## 18.5 Self-hosted LLMs

**vLLM — future candidate.**

Do not add these to the base stack before a real workload requires them.

---

# 19. Quantum ML

## 19.1 PennyLane

**PRIMARY QML research framework.**

Use simulator-first.

## 19.2 Qiskit Machine Learning

**SECONDARY QML comparison framework.**

Use for VQC, QSVC/quantum kernels, QNN experiments and Qiskit backend interoperability.

## 19.3 QML isolation

QML dependencies belong in a research profile/environment.

They must not become imports in:

```text
patient API
safety module
mental-health routing
referral logic
```

## 19.4 Quantum hardware

Optional only after reproducible simulator results and governance approval.

---

# 20. Dependency Profiles

R3 standardizes dependency placement conceptually.

Exact build-system syntax can be decided in the repository phase.

## 20.1 Backend core

```text
backend-core
```

Contains only dependencies required for normal API/domain operation.

## 20.2 Document AI

```text
document-ai
```

OCR/parser dependencies.

## 20.3 Language AI

```text
language-ai
```

ASR/translation/transliteration/TTS dependencies.

## 20.4 RAG

```text
rag
```

Embedding/reranking packages after RAG is introduced.

## 20.5 ML research

```text
ml-research
```

MLflow, Optuna, SHAP and training dependencies not required by patient API.

## 20.6 QML research

```text
qml-research
```

PennyLane, Qiskit and Qiskit Machine Learning.

## 20.7 Operations

```text
ops
```

deployment/observability integrations only as needed.

## 20.8 Development

```text
dev
```

test/lint/type/security tooling.

The project must avoid one enormous Python environment containing every research framework.

---

# 21. Final Adoption Matrix

| Technology | R3 classification |
|---|---|
| FastAPI | CORE / ADOPT |
| Pydantic v2 | CORE / ADOPT |
| SQLAlchemy 2.x | CORE / ADOPT |
| Alembic | CORE / ADOPT |
| PostgreSQL | CORE / ADOPT |
| pgvector | ACTIVATE WITH RAG |
| Next.js | CORE / ADOPT |
| React | CORE / ADOPT |
| TypeScript | CORE / ADOPT |
| Tailwind | CORE / ADOPT |
| Docker/Compose | CORE / ADOPT |
| OpenTelemetry | CORE CONTRACT |
| Prometheus | PILOT/SELF-HOSTED |
| Grafana | OPTIONAL |
| Loki | DEFER |
| Trivy | CI / ADOPT |
| Gitleaks | CI / ADOPT |
| Keycloak | PREFERRED IDP TARGET; SPIKE-GATED |
| SeaweedFS | PREFERRED SELF-HOSTED OBJECT STORE; ACTIVATION LATER |
| Procrastinate | PREFERRED DURABLE JOB TARGET; SPIKE-GATED |
| Celery | FALLBACK |
| Valkey | OPTIONAL WHEN NEEDED |
| NATS JetStream | FUTURE |
| OpenBao | PRODUCTION SELF-HOSTED OPTION |
| PaddleOCR | PREFERRED OCR BASELINE; BENCHMARK-GATED |
| Docling | DOCUMENT PARSER CANDIDATE / ADOPT-CONSIDER |
| Surya | OCR CHALLENGER |
| Tesseract | OCR BASELINE/FALLBACK |
| faster-whisper | ASR BASELINE/FALLBACK |
| IndicConformer | INDIA ASR CHALLENGER / BENCHMARK-GATED |
| IndicTrans2 | PREFERRED TRANSLATION CANDIDATE |
| IndicLID | LANGUAGE-ID CANDIDATE |
| IndicXlit | TRANSLITERATION CANDIDATE |
| BHASHINI | OPTIONAL PILOT EXTERNAL PROVIDER |
| HAPI FHIR | ADOPT BEHIND SIDE-CAR/ADAPTER |
| Medplum | ALTERNATIVE |
| LiteLLM SDK | CONSIDER |
| LiteLLM Proxy | DEFER |
| MLflow | RESEARCH / ADOPT |
| scikit-learn | ML / ADOPT |
| XGBoost | TASK-DEPENDENT |
| PyTorch | TASK-DEPENDENT |
| Optuna | RESEARCH / ADOPT-CONSIDER |
| SHAP | EXPLAINABILITY / ADOPT |
| skops | PREFERRED SKLEARN PERSISTENCE |
| ONNX Runtime | PREFERRED PORTABLE INFERENCE |
| Sentence Transformers | RAG MODEL TOOLKIT CANDIDATE |
| LangChain | NOT CORE |
| LlamaIndex | NOT CORE |
| Haystack | CONDITIONAL FUTURE |
| Promptfoo | OPTIONAL OFFLINE LLM EVAL |
| PennyLane | QML PRIMARY |
| Qiskit Machine Learning | QML SECONDARY |
| BentoML | FUTURE/CONDITIONAL MODEL SERVICE |
| KServe | FUTURE |
| Triton | FUTURE |
| vLLM | FUTURE |
| Evidently | FUTURE MODEL MONITORING |
| MinIO | REJECTED AS NEW DEFAULT |

---

# 22. Technologies Codex Must Not Add by Default

Without an explicit phase prompt, Codex must not add:

```text
Kubernetes
service mesh
Kafka
NATS
RabbitMQ
Valkey/Redis
Keycloak
OpenBao
SeaweedFS
LiteLLM Proxy
KServe
Triton
vLLM
LangChain
LlamaIndex
Haystack
MLflow to patient API runtime
PennyLane/Qiskit to patient API runtime
OCR heavyweight models
ASR/TTS heavyweight models
```

Research approval is not default-runtime permission.

---

# 23. Benchmark-Gated Decisions

These are intentionally unresolved at provider level:

```text
production OCR pipeline
ASR provider per language/noise profile
TTS provider
exact embedding model
exact production LLM provider/model
exact durable job backend until spike
exact IdP until identity spike
exact self-hosted object-store activation
```

Codex must implement the boundary and benchmark harness, not fabricate a result.

---

# 24. Explicit Reconciliation of Earlier Ambiguities

## "AI Gateway"

Earlier architecture used the term "central AI gateway."

R3 defines:

```text
AI Gateway = project-owned in-process orchestration boundary by default
```

It does **not** imply LiteLLM Proxy or another network service.

## Redis

Earlier architecture examples listed Redis.

R3 replaces this with:

```text
Valkey/Redis-compatible cache only if needed
```

and prefers PostgreSQL-native job/outbox designs first.

## MLflow

Earlier baseline listed MLflow as a general AI/ML tool.

R3 scopes it to:

```text
research tracking/registry
```

not patient runtime.

## QML

QML remains part of the product's research feature set but is not a runtime dependency for normal clinical workflows.

---

# 25. Final R3 Stack Statement

SwasthyaSetu will build its **product, safety, clinical context, consent, provenance, routing and governance logic itself**.

It will reuse mature technologies only through bounded interfaces.

The default implementation should stay small:

```text
Next.js / React / TypeScript
FastAPI / Pydantic
SQLAlchemy / Alembic
PostgreSQL
Docker
OpenTelemetry
project-owned ports/policies/tests
```

Everything else activates only when its phase and acceptance criteria require it.
