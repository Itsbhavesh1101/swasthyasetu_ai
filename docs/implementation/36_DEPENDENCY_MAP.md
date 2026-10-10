# SwasthyaSetu AI — Final R3 Dependency Map

**Document ID:** `SSAI-DEP-036-R3`  
**Status:** Accepted implementation dependency baseline  
**Version:** `1.0.0-r3`  
**Date:** 2026-10-10

---

# 1. Purpose

This map defines:

- phase dependencies;
- module dependencies;
- infrastructure activation dependencies;
- research/runtime separation;
- dependency classification;
- concrete R3 technology status.

No phase becomes eligible merely because its number is next.

---

# 2. Phase graph

```text
P0 Governance / repository foundation
 |
P1 Repository + tooling foundation
 |
P2 Shared Platform Kernel
 |
P3 Persistence / migrations / events / jobs / adapter foundation
 |
P4 Identity / pseudonymous session / consent
 |
P5 Longitudinal patient + encounter
 |
P6 Frontend shell + typed API
 |
P7 Structured clinical intake
 |
P8 LLM extraction/orchestration boundary
 |
P9 Deterministic physical safety
 |
P10 Clinician dashboard + provenance
 |
P11 Document AI / OCR
 |
P12 Speech / language
 |
P13 Provider directory / resources / referrals
 |
P14 MannSetu mental-health module
 |
P15 Self-care / Ayurveda
 |
P16 FHIR
 |
P17 ABDM
 |
P18 Classical ML research
 |
P19 QML research
 |
P20 Unified orchestration
 |
P21 Admin / governance
 |
P22 Security / privacy / resilience
 |
P23 E2E / accessibility / performance
 |
P24 Pilot readiness
```

New sub-phases may be inserted with dependency/safety review.

---

# 3. Foundation technology dependencies

## P0–P3 allowed baseline

```text
Python 3.12+
FastAPI
Pydantic v2
SQLAlchemy 2.x
Alembic
PostgreSQL
httpx-style async client
pytest
Ruff
typing
Docker/Compose
```

No AI model runtime is a prerequisite.

---

# 4. Module graph

```text
identity
  |
sessions
  |
consent
  |
patients <---- provenance
  |
encounters
  |
clinical_intake ---> ai_orchestration ---> LLMProvider
  |
  +--> safety
  |
  +--> summaries
  |
  +--> documents ---> OCRPort / DocumentParserPort
  |
  +--> language ---> ASR / TTS / Translation / LID / Xlit ports

mental_health
  |
  +--> structured signal extraction
  +--> deterministic policy
  +--> resources
  +--> referrals

self_care
  |
  +--> safety
  +--> patient context
  +--> approved knowledge retrieval
  +--> escalation

providers ---> referrals
resources ---> referrals

interoperability
  |
  +--> FHIR mapper
  +--> FHIRProvider/HAPI sidecar
  +--> ABDMProvider

model_governance
  |
  +--> ModelInferencePort

research_ml
  |
  +--> MLflow
  +--> Optuna
  +--> SHAP

research_qml
  |
  +--> PennyLane
  +--> Qiskit ML
```

---

# 5. Core product dependency rule

Product modules may depend on:

```text
domain contracts
application capabilities
public read models
typed events
ports
```

They may not depend directly on vendor SDK internals.

---

# 6. Identity dependency

Pseudonymous session:

```text
SwasthyaSetu-owned
```

Authenticated clinician/admin:

```text
OIDC port
 -> Keycloak preferred target when phase activates
```

Provider selection is not a prerequisite for pseudonymous functionality.

---

# 7. Consent dependency

Required before:

```text
referral sharing
ABDM exchange
research export
external AI processing when policy requires consent
caregiver/future sharing
```

Consent failure blocks the side effect, not the entire unrelated product.

---

# 8. Patient-context dependency

Longitudinal patient context is consumed by:

```text
intake
clinician dashboard
self-care
FHIR mapping
risk model input
document reconciliation
```

No feature maintains a competing patient-history JSON silo.

---

# 9. Safety dependency

```text
validated structured inputs
 + approved policy version
 -> deterministic safety decision
```

Safety does not depend on:

```text
QML
RAG
provider directory
MLflow
OCR availability
```

---

# 10. LLM dependency

Consumers:

```text
intake extraction
mental-health signal extraction
summary drafting
document entity extraction
approved knowledge explanation
```

Default runtime dependency:

```text
LLMProvider -> direct provider adapter
```

LiteLLM Proxy is not a hard dependency.

---

# 11. Document dependency

P11 depends on:

```text
patient/encounter
ObjectStoragePort
JobDispatcher
provenance
clinician/manual review path
```

Concrete OCR provider is benchmark-gated.

---

# 12. Object storage dependency

Phase ordering:

```text
port + local adapter
    |
document phase
    |
S3-compatible implementation
    |
SeaweedFS self-hosted candidate if selected
```

PostgreSQL remains authoritative metadata.

---

# 13. Job dependency

Phase ordering:

```text
JobDispatcher port
    |
InProcess adapter for local/test
    |
PostgreSQL durable queue spike
    |
Procrastinate preferred
    |
Celery fallback only if needed
```

Valkey is not a prerequisite.

---

# 14. Language dependency

P12 requires:

```text
speech/language ports
language metadata
fallback UI
```

Candidate adapters:

```text
faster-whisper
IndicConformer
IndicTrans2
IndicLID
IndicXlit
BHASHINI
```

Final ASR/TTS selection depends on benchmark.

---

# 15. Provider/referral dependency

Provider discovery depends on:

```text
verified provider registry
governed specialty routing
```

Referral depends on:

```text
consent
minimal payload
provider/resource record
lifecycle state
```

LLM is not provider truth.

---

# 16. Mental health dependency

Depends on:

```text
structured signals
lexicon/backstop
deterministic policy
verified resources
referral workflow
```

LLM extraction can fail while crisis fallback still works.

---

# 17. Self-care dependency

Hard order:

```text
patient context
 -> physical safety
 -> self-care eligibility
 -> contraindications
 -> approved knowledge retrieval
 -> supportive guidance
```

RAG/LLM is downstream of authorization.

---

# 18. Retrieval/RAG dependency

RAG activates only after an approved use case exists.

```text
PostgreSQL
 -> pgvector
 -> EmbeddingProvider
 -> approved corpus
 -> metadata/authorization filters
 -> RetrievalService
 -> optional RerankerProvider
```

No LangChain/LlamaIndex dependency is implied.

---

# 19. FHIR dependency

P16 depends on:

```text
stable internal domain
provenance
consent representation
mapping spec
```

Runtime:

```text
FHIRProvider
 -> HAPI FHIR sidecar/conformance
```

FHIR remains an interoperability projection.

---

# 20. ABDM dependency

P17 depends on:

```text
P16 FHIR
approved ABDM flow specification
consent semantics
sandbox
ABDMProvider
```

ABDM is not required for core patient intake.

---

# 21. Classical ML research dependency

P18 depends on:

```text
approved dataset
dataset manifest
split specification
evaluation protocol
research artifact store
experiment tracker
```

Typical research tools:

```text
scikit-learn
XGBoost/PyTorch when justified
MLflow
Optuna
SHAP
```

This profile is isolated from clinical writes.

---

# 22. Production model inference dependency

A patient/clinician risk output requires:

```text
approved model version
artifact hash
feature schema
calibration
threshold
approval scope
ModelInferencePort
```

MLflow registry state alone is insufficient.

---

# 23. ONNX dependency

ONNX Runtime activates only for a model whose export passes:

```text
prediction parity
probability parity
threshold/risk-band parity
schema checks
known-answer tests
telemetry configuration
```

---

# 24. QML dependency

P19 depends on P18.

```text
same approved dataset
same split
classical baseline
quantum experiment spec
```

Research runtimes:

```text
PennyLane primary
Qiskit Machine Learning secondary
```

QML is not a prerequisite for any core safety/navigation module.

---

# 25. Observability dependency

Application code can adopt OTel instrumentation without requiring:

```text
Prometheus
Grafana
Loki
```

backends to exist locally.

Pilot can add:

```text
OTel Collector
Prometheus
Grafana
```

---

# 26. Cache dependency

Valkey classification:

```text
OPTIONAL
```

A module adding Valkey must document:

```text
what is cached
TTL
fallback behavior
why DB/local cache is insufficient
```

---

# 27. Secrets dependency

SecretProvider/config exists before OpenBao.

OpenBao activates only in protected self-hosted deployments that need it.

---

# 28. Infrastructure activation map

| Capability | Earliest justified phase | R3 target |
|---|---|---|
| PostgreSQL | P1/P2 | ADOPT |
| Docker Compose | P0/P1 | ADOPT |
| OTel instrumentation | P1+ | ADOPT CONTRACT |
| Durable jobs | P3/P11 | Procrastinate spike |
| Object store | P11 | SeaweedFS candidate / cloud S3 adapter |
| IdP | P4/P10/P21 | Keycloak spike |
| pgvector | P15 or approved retrieval phase | ADOPT WHEN NEEDED |
| HAPI FHIR | P16 | ADOPT SIDE-CAR |
| MLflow | P18 | RESEARCH |
| PennyLane/Qiskit | P19 | RESEARCH |
| Prometheus/Grafana | P22/P24 | PILOT |
| Valkey | any justified phase | OPTIONAL |
| OpenBao | P22/P24 | OPTIONAL PROTECTED DEPLOYMENT |
| NATS | post-extraction/scaling | FUTURE |
| KServe/Triton | model fleet scale | FUTURE |
| vLLM | self-hosted LLM decision | FUTURE |

---

# 29. Dependency profiles

```text
backend-core
document-ai
language-ai
rag
ml-research
qml-research
ops
dev
```

Frontend workspaces maintain their own scoped JS dependencies.

No profile is automatically included in another except where explicitly documented.

---

# 30. Failure dependency matrix

| Dependency class | Expected failure semantics |
|---|---|
| HARD | clear service failure; never fabricated success |
| SOFT | degraded workflow/manual fallback |
| OPTIONAL | feature unavailable; unrelated flows continue |
| RESEARCH_ONLY | no patient-runtime effect |
| DEV_TEST_ONLY | no production dependency |
| OPS_ONLY | app can run even if dashboard/backend unavailable |

---

# 31. R3 technology dependency classification

## HARD / core

```text
FastAPI
Pydantic
SQLAlchemy
Alembic
PostgreSQL
frontend core
```

## SOFT capability

```text
LLM
OCR
ASR/TTS
translation
RAG
provider APIs
notifications
FHIR/ABDM connectivity
model inference
```

## OPTIONAL

```text
Valkey
Prometheus
Grafana
SeaweedFS in local dev
LiteLLM Proxy
```

## RESEARCH_ONLY

```text
MLflow
Optuna
PennyLane
Qiskit ML
Promptfoo
```

---

# 32. New dependency review checklist

```text
[ ] R3 status known
[ ] phase allows it
[ ] port/adapter exists or is created
[ ] runtime profile chosen
[ ] version pinned
[ ] license checked
[ ] model/data license checked if applicable
[ ] security reviewed
[ ] egress/telemetry reviewed
[ ] failure behavior implemented
[ ] tests added
[ ] docs/decision log updated
```

---

# 33. Dependency anti-patterns

Forbidden:

```text
one global requirements file with every model framework
research packages imported by clinical safety module
cross-module ORM access
global Redis as hidden truth
LLM framework owning clinical routing
HAPI owning internal clinical domain
vector DB authorizing patient access
production loading arbitrary Python model files
```

---

# 34. Final rule

The dependency graph is designed so that **removing an optional AI provider, research tool, cache, metrics backend or quantum runtime does not invalidate the clinical core**.
