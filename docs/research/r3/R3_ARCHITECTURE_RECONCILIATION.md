# SwasthyaSetu AI — R3 Architecture Reconciliation

**Document ID:** `SSAI-R3-ARCH-001`  
**Status:** Accepted architecture reconciliation  
**Version:** `1.0.0-r3`  
**Date:** 2026-10-10

---

# 1. Purpose

R2-A through R2-E produced detailed domain-specific technology research.

R3 reconciles those findings with:

- `00_PROJECT_MASTER_SPEC.md`
- `01_PRODUCT_REQUIREMENTS.md`
- `02_SYSTEM_ARCHITECTURE.md`
- `03_REPOSITORY_STRUCTURE.md`
- `04_DOMAIN_MODEL.md`
- `05_DATABASE_SCHEMA.md`
- `06_API_CONTRACTS.md`
- `29_ENGINEERING_STANDARDS.md`
- `34_MASTER_IMPLEMENTATION_PLAN.md`
- `36_DEPENDENCY_MAP.md`
- the R2-A/R2-B/R2-C/R2-D/R2-E research documents

The objective is to remove contradictions before Codex implementation.

---

# 2. R3 architecture result

No major rewrite is required.

The existing architecture was fundamentally correct:

```text
modular monolith
ports/adapters
PostgreSQL source of truth
deterministic safety
research isolation
feature flags
domain events
outbox/workers
replaceable external providers
```

R3 mainly tightens **when and how concrete external technologies are allowed to appear**.

---

# 3. Reconciled system topology

```text
┌───────────────────────────────────────────────────────────────┐
│                       Client Applications                     │
│  Patient PWA        Clinician Web        Admin Web/Kiosk     │
│  Next.js / React / TypeScript                              │
└──────────────────────────────┬────────────────────────────────┘
                               │ HTTPS
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                   FastAPI Modular Monolith                    │
│                                                               │
│ identity/sessions/consent                                    │
│ patients/encounters/provenance                               │
│ clinical intake/summaries                                    │
│ deterministic safety                                         │
│ mental health                                                 │
│ documents                                                     │
│ providers/resources/referrals                                │
│ self-care                                                     │
│ interoperability                                              │
│ model governance / inference boundary                        │
│ audit / feature management                                   │
└──────────────┬──────────────────────────────┬─────────────────┘
               │                              │
               ▼                              ▼
      PostgreSQL + pgvector          Background Worker(s)
      canonical product data         durable jobs when needed
               │                              │
               ├──────────────┐               │
               ▼              ▼               ▼
       ObjectStoragePort    Outbox      Long-running adapters
               │                          OCR / language / sync
               ▼
     local dev filesystem
     self-hosted/cloud S3 adapter later

External boundaries:
    LLMProvider
    OCRPort
    SpeechToTextPort
    TextToSpeechPort
    TranslationPort
    FHIRProvider
    ABDMProvider
    NotificationProvider
    ModelInferencePort
    QuantumBackendPort (research)
```

---

# 4. Architecture clarification: AI Gateway

The phrase `AI Gateway` previously risked being interpreted as a mandatory network service.

R3 resolves this.

The default architecture is:

```text
Task-specific AI application service
        |
AI orchestration / governance layer
        |
LLMProvider
        |
direct provider adapter
```

The orchestration layer centralizes:

```text
timeouts
bounded retries
approved model configuration
schema validation
request metadata
cost/usage metadata
privacy controls
provenance
```

It is initially **inside the FastAPI application boundary**.

A network gateway such as LiteLLM Proxy becomes optional infrastructure only when real multi-provider operational complexity justifies it.

---

# 5. Architecture clarification: external AI is optional to safety

The deterministic safety path must not wait for:

```text
LLM gateway
ML model
QML
RAG
OCR
speech
```

where an equivalent structured/manual signal already exists.

If optional AI fails, the product should move toward:

```text
manual input
clarification
safe fallback
human review
```

not fabricate success.

---

# 6. Architecture clarification: jobs

Early architecture mentioned generic Redis queues.

R3 selects this order:

```text
InProcessJobDispatcher
        |
        | when durability required
        v
PostgreSQL-native durable job adapter
(Procrastinate preferred spike target)
        |
        | only if requirements outgrow it
        v
Celery or later service messaging
```

The transactional outbox remains separate and canonical for reliable event publication.

---

# 7. Architecture clarification: cache

Cache is not a prerequisite.

If introduced:

```text
Valkey
```

is the preferred Redis-compatible direction.

The application must remain correct after cache loss.

---

# 8. Architecture clarification: object storage

Object storage is mandatory as a **port**, not as an infrastructure service in the first phase.

Stages:

```text
local/test:
    local controlled adapter

document/pilot phase:
    S3-compatible implementation
    SeaweedFS preferred self-hosted candidate

cloud deployment:
    provider-specific S3-like adapter
```

Database stores canonical document metadata and ownership.

---

# 9. Architecture clarification: identity

Two identity concepts remain separate:

```text
pseudonymous session
authenticated identity
```

Pseudonymous sessions are product-native.

Authenticated identity can later use OIDC/Keycloak or another approved IdP.

Authorization remains SwasthyaSetu-owned.

---

# 10. Document AI architecture

```text
Document upload
   |
security validation
   |
ObjectStoragePort
   |
Document record
   |
JobDispatcher
   |
DocumentParserPort / OCRPort
   |
raw OCR/layout result
   |
medical entity extraction
   |
validation + confidence
   |
provenance
   |
clinician review / longitudinal timeline
```

PaddleOCR/Docling/etc. are adapter implementations, not document-domain dependencies.

No OCR output becomes confirmed clinical truth merely because OCR confidence is high.

---

# 11. Language architecture

```text
audio/text
   |
language detection / explicit user language
   |
ASR if audio
   |
transliteration/normalization if needed
   |
translation only when required
   |
preserve original wording
   |
structured clinical extraction
```

Language processing components are separable.

Example:

```text
IndicConformer may win ASR
IndicTrans2 may remain translation
BHASHINI may provide TTS
```

There is no requirement that one provider win every language capability.

---

# 12. FHIR architecture

```text
Internal Domain
    |
FHIR Mapper
    |
FHIR Validation/Conformance Boundary
    |
HAPI FHIR sidecar
    |
External FHIR / ABDM adapter
```

HAPI is not the main database.

Internal domain state stays canonical.

The sidecar can be:

```text
validator-only
validator + private projection repository
```

depending on phase requirements.

---

# 13. ABDM architecture

ABDM sits behind:

```text
ABDMProvider
```

and consumes approved FHIR mappings.

The product remains useful without ABDM connectivity.

ABDM sandbox failures must not corrupt clinical product state.

---

# 14. Retrieval architecture

R3 selects simple retrieval first.

```text
Approved content / authorized patient documents
      |
chunking
      |
EmbeddingProvider
      |
pgvector
      |
hard metadata/authorization filters
      |
retrieval
      |
optional reranking
      |
provenance/citations
      |
LLM explanation/synthesis if allowed
```

Important:

```text
authorization filter precedes private semantic search scope
```

No global cross-patient nearest-neighbor search followed by post-filtering.

---

# 15. No general agent runtime

The product does not require a universal agent loop.

Most clinical workflows are explicit state machines/use cases.

Therefore no core dependency on:

```text
LangChain agent
LlamaIndex agent
generic autonomous tool agent
```

If a later module truly needs an orchestration library, it remains an adapter/local implementation choice.

---

# 16. Classical ML architecture

```text
Research Dataset
   |
approved preprocessing
   |
frozen split
   |
training
   |
MLflow experiment metadata
   |
validation/calibration
   |
model artifact
   |
SwasthyaSetu governance approval
   |
ModelInferencePort
   |
risk-support output
```

No model artifact can bypass the approval layer by being marked "production" in MLflow.

---

# 17. Model artifact architecture

```text
trusted training pipeline
   |
artifact
   |
SHA-256
   |
private artifact storage
   |
model registry metadata
   |
SwasthyaSetu approval
   |
loader verifies hash/runtime/schema
   |
inference
```

Preferred deployable formats:

```text
ONNX
skops for compatible sklearn
trusted framework-native format
```

Arbitrary executable model uploads are prohibited.

---

# 18. QML architecture

```text
ml/qml research workspace
      |
same approved dataset/split
      |
classical baseline       quantum branch
      |                       |
      +------------+----------+
                   |
             common evaluation
```

QML has no dependency edge into:

```text
physical safety
mental-health crisis routing
referrals
patient intake availability
```

The product can operate if every QML dependency is removed.

---

# 19. Model serving architecture

Default:

```text
ModelInferencePort
    -> in-process/worker runtime
```

Extraction sequence if justified:

```text
in-process
   -> dedicated service
   -> BentoML
   -> Kubernetes/KServe or Triton only at scale
```

This prevents a full serving platform from becoming a prerequisite for one tabular classifier.

---

# 20. Deployment profiles

## 20.1 Local developer profile

Minimum:

```text
patient/clinician/admin frontends as needed
FastAPI
PostgreSQL
```

Optional test fakes/local filesystem.

Not required:

```text
Keycloak
SeaweedFS
Valkey
OpenBao
Prometheus
MLflow
HAPI
PaddleOCR
Qiskit
```

## 20.2 Integration profile

Add only components needed by current integration tests:

```text
worker
HAPI sidecar
selected OCR adapter
selected language adapter
```

## 20.3 Research profile

Separate:

```text
MLflow
Optuna
SHAP
PennyLane
Qiskit Machine Learning
research artifact storage
```

No production DB credentials.

## 20.4 Pilot profile

Potential:

```text
authenticated IdP
durable workers
object storage
OTel Collector
Prometheus
Grafana
FHIR sidecar
approved AI adapters
```

Every service remains private unless explicitly exposed.

---

# 21. Network trust zones

Conceptual:

```text
PUBLIC
  reverse proxy / web entry

APPLICATION
  Next.js servers
  FastAPI

PRIVATE DATA
  PostgreSQL
  object storage
  job backend
  FHIR sidecar

RESEARCH
  MLflow
  training workers
  QML
  research artifacts

EXTERNAL
  LLM provider
  BHASHINI
  ABDM
  provider/notification APIs
  optional QPU
```

Research zone does not receive unrestricted production credentials.

---

# 22. Database ownership remains unchanged

One PostgreSQL cluster can be used initially.

Logical ownership is still strict.

Modules do not directly mutate foreign tables.

Shared analytics/read models may combine data but do not own authoritative writes.

---

# 23. Cross-module interaction priority

Preferred order:

```text
1. public application capability
2. typed synchronous service call
3. typed domain/integration event
4. read model
5. external port
```

Forbidden:

```text
cross-module ORM mutation
vendor SDK use in domain module
hidden service locator
global mutable singleton
```

---

# 24. Feature flags

Experimental providers can be gated:

```text
ocr.paddle.enabled
speech.indicconformer.enabled
rag.enabled
model.<id>.enabled
qml.ui.enabled
```

Feature flags cannot disable required safety checks.

Unknown flag state for risky features defaults to off.

---

# 25. Failure isolation matrix

| Dependency | Failure behavior |
|---|---|
| LLM | manual/guided input, clarification, no fabricated extraction |
| OCR | manual upload review/manual entry |
| ASR | text/touch fallback |
| Translation | original-language display / supported fallback |
| TTS | text remains available |
| RAG | structured search/approved content unavailable message |
| Provider directory | no invented contacts |
| Notification | referral state retained; retry/manual contact |
| HAPI FHIR | core product continues; sync/conformance job fails visibly |
| ABDM | core product continues; integration marked unavailable |
| MLflow | research logging fails; patient app unaffected |
| classical risk model | risk output unavailable; safety route unchanged |
| QML | research job fails only |
| object store | document capability fails clearly; existing structured clinical data remains |
| cache | correctness preserved |
| metrics backend | application keeps working |

---

# 26. Codex dependency insertion rule

Before adding a third-party package/service, Codex must identify:

```text
R3 classification
phase
owned port/adapter
runtime profile
failure behavior
license/security status
tests
```

If it cannot map the dependency to an approved R3 entry, it must not add it silently.

---

# 27. Architecture changes caused by R3

Accepted changes:

1. "AI Gateway" becomes in-process orchestration by default.
2. LiteLLM network proxy is not the default.
3. Redis is no longer implied by jobs; Procrastinate is the preferred durable-job spike.
4. Valkey is optional cache only.
5. MLflow is explicitly isolated from patient runtime.
6. RAG defaults to pgvector + project-owned retrieval, not LangChain/LlamaIndex.
7. HAPI FHIR is explicitly a sidecar/conformance service.
8. QML dependencies remain research-profile-only.
9. OCR and speech providers stay benchmark-gated.
10. Heavy infrastructure is absent from default local Compose until its phase.

---

# 28. Architecture changes NOT caused by R3

R3 does not change:

```text
modular monolith
deterministic safety
patient longitudinal context
ports/adapters
module-owned persistence
API versioning
provenance
consent
human clinical authority
feature flags
transactional outbox
```

---

# 29. Service extraction triggers

A module may be split from the monolith only with evidence.

Examples:

```text
OCR worker requires incompatible GPU/CUDA image
speech runtime needs dedicated GPU autoscaling
FHIR sidecar already separate Java runtime
model inference requires independent deployment
notification service becomes high-throughput
```

Service extraction is not a prestige milestone.

---

# 30. R3 acceptance criteria

Architecture reconciliation is complete when:

```text
[ ] final technology matrix exists
[ ] 02_SYSTEM_ARCHITECTURE is reconciled
[ ] 29_ENGINEERING_STANDARDS reflects dependency-profile rules
[ ] 36_DEPENDENCY_MAP reflects concrete R3 statuses
[ ] decision log records R3 ADRs
[ ] Codex has dependency allow/deny rules
[ ] benchmark-gated providers are not falsely marked approved
[ ] research dependencies are isolated
[ ] default local stack remains minimal
```

---

# 31. Final R3 architecture statement

SwasthyaSetu is not a collection of external AI products.

It is a safety-governed healthcare application with a stable internal domain, where third-party technology implements replaceable capabilities behind explicit boundaries.
