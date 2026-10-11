# SwasthyaSetu AI — Third-Party Component Register

**Document ID:** SSAI-OSS-002  
**Status:** Preliminary engineering shortlist  
**Review baseline:** 2026-10-09

> These decisions are based on repository/source/manifests/releases/issues/security/license inspection. High-impact components still require SwasthyaSetu-specific technical spikes.

| Subsystem | Candidate | Initial decision | SwasthyaSetu integration | Main reason | Main unresolved risk |
|---|---|---|---|---|---|
| OCR/document parsing | PaddlePaddle/PaddleOCR | **ADOPT BEHIND ADAPTER** | `OCRPort` worker | Mature multilingual document stack, active development, permissive license | Must prove performance on Indian medical scans and handwriting |
| OCR alternative | datalab-to/surya | **BENCHMARK BEFORE ADOPTION** | alternate `OCRPort` | Strong OCR/layout/table capability | Model-weight license needs separate suitability review |
| OCR alternative | mindee/doctr | **CONSIDER** | alternate `OCRPort` | Active tested PyTorch OCR library | Indic-language fit weaker than our main requirement |
| FHIR | hapifhir/hapi-fhir | **ADOPT BEHIND ADAPTER** | FHIR sidecar via `FHIRProvider` | Mature client/server/JPA/validation ecosystem | Operational Java surface and deployment hardening |
| FHIR platform alternative | medplum/medplum | **CONSIDER** | FHIR service adapter | Strong modern FHIR platform and security tooling | Overlaps too much with our own backend/product architecture |
| Indian translation | AI4Bharat/IndicTrans2 | **ADOPT BEHIND ADAPTER** | `TranslationPort` service | Direct support for scheduled Indian languages | Need reproducible modern inference packaging |
| Indian ASR | AI4Bharat/IndicConformerASR | **BENCHMARK BEFORE ADOPTION** | `SpeechToTextPort` | Exceptional India-language fit | Thin repo/runtime maturity and large multilingual model |
| Generic ASR | SYSTRAN/faster-whisper | **ADOPT AS BENCHMARK/FALLBACK** | secondary `SpeechToTextPort` | Mature tests/workflows and efficient Whisper inference | Must benchmark Hindi/Hinglish/noisy OPD accuracy |
| LLM abstraction | BerriAI/litellm | **ADOPT BEHIND ADAPTER** | internal implementation of `LLMProvider` | Very active multi-provider Python abstraction | Large/fast-moving dependency surface |
| Vector retrieval | pgvector/pgvector | **ADOPT WHEN NEEDED** | PostgreSQL extension | Excellent fit with chosen PostgreSQL stack | RAG should not be introduced before justified |
| ML lifecycle | mlflow/mlflow | **ADOPT** | research experiment/model tracking | Mature ML lifecycle, security process, active releases | Keep isolated from final clinical authority |
| QML primary | PennyLaneAI/pennylane | **ADOPT** | primary `QuantumBackend` research implementation | Strong hybrid-QML/plugin design | Pin plugin/JAX compatibility |
| QML secondary | qiskit-community/qiskit-machine-learning | **ADOPT AS SECONDARY BACKEND** | Qiskit `QuantumBackend` adapter | Direct VQC/QNN/quantum-kernel support | Qiskit API migrations need version discipline |
| Identity | keycloak/keycloak | **CONSIDER** | external OIDC IdP | Very mature OIDC/SAML ecosystem | Heavy operational footprint |
| Identity alternative | goauthentik/authentik | **CONSIDER** | external OIDC IdP | Modern IAM, strong adoption/security tooling | Upgrade complexity and license review |
| Object storage | seaweedfs/seaweedfs | **CONSIDER FOR SELF-HOSTED** | S3-compatible `ObjectStorageProvider` | Active self-hosted storage ecosystem | More infra than MVP may need |
| Full EHR | openmrs/openmrs-core | **REFERENCE / INTEGRATE ONLY** | future HIS/FHIR integration | Mature healthcare domain experience | Too much architecture/product overlap |
| Full EHR | openemr/openemr | **REFERENCE / INTEGRATE ONLY** | future HIS/FHIR integration | Mature EHR/practice-management project | PHP/GPL stack and major product overlap |
| Indian TTS | AI4Bharat/Indic-TTS | **BENCHMARK / CONSIDER** | `TextToSpeechPort` | India-language-specific models | Older project/deployment stack needs validation |

## Current preferred direction

```text
OCR                  PaddleOCR (+ Surya/docTR benchmark)
Translation          IndicTrans2
ASR                  IndicConformer vs faster-whisper benchmark
LLM provider layer   SwasthyaSetu LLMProvider with LiteLLM internally
FHIR                 HAPI FHIR sidecar
Vector retrieval     pgvector only when an approved RAG use case exists
ML tracking          MLflow
QML                  PennyLane primary + Qiskit ML secondary
Auth                 Keycloak vs Authentik technical spike
Object storage       provider-neutral S3 API; self-hosted option evaluated later
```

## Explicitly not authorized

This register does not authorize:

- replacing SwasthyaSetu with a full EHR;
- using public-repo clinical content as medical authority;
- generated provider/contact information;
- generated remedies;
- replacing deterministic safety with any OSS AI system.


---

## R2-A OCR research update — 2026-10-09

### New/updated decisions

| Component | R2-A status | Notes |
|---|---|---|
| PaddleOCR | **PRIMARY PRE-BENCHMARK CANDIDATE** | Use isolated worker behind `OCRPort`; Devanagari model is a major requirement fit. |
| PaddleOCR-VL | **PREFERRED HARD-PAGE FALLBACK CANDIDATE** | Apache-licensed official model; test handwriting and hallucination/omission behavior. |
| Docling | **DOCUMENT PARSER CANDIDATE** | Strong native PDF/Office/structure layer; keep outside clinical domain; sandbox untrusted parsing. |
| RapidOCR | **EDGE/CPU BENCHMARK CANDIDATE** | Portable PaddleOCR-family deployment via ONNX/OpenVINO/etc. |
| Surya | **SERIOUS BENCHMARK COMPETITOR** | Strong layout/handwriting capabilities, but model-weight license and open failure cases prevent default adoption. |
| docTR | **SECONDARY BASELINE** | Strong library quality, weaker multilingual/handwriting fit. |
| Tesseract | **BASELINE/FALLBACK** | Mature deterministic CPU OCR, not primary medical handwriting solution. |

### Architectural refinement

Create separate:

```text
DocumentParserPort
OCRPort
VLMDocumentParserPort
```

Medical entity extraction remains a downstream SwasthyaSetu-owned capability.


---

## R2-B Indian Language / Speech Research Update — 2026-10-09

| Capability | Component | R2-B decision | Notes |
|---|---|---|---|
| India-specialized ASR | AI4Bharat IndicConformer | **BENCHMARK BEFORE ADOPTION** | Excellent 22-language fit; deployment engineering is less mature and depends on AI4Bharat NeMo. |
| Mature local ASR | faster-whisper | **ADOPT AS BASELINE/FALLBACK CANDIDATE** | Strong package/CI/runtime; Hinglish Romanization is not solved by ASR alone. |
| Edge ASR | whisper.cpp | **BENCHMARK** | Excellent offline/edge portability; accuracy remains Whisper-family dependent. |
| Hosted ASR | BHASHINI | **OPTIONAL PILOT PROVIDER** | Strong India-language ecosystem; external processing and production terms require approval. |
| Translation | IndicTrans2 | **ADOPT BEHIND `TranslationPort`** | Strong 22-language fit; pin HF model/toolkit/Transformers revisions and benchmark medical semantics. |
| Language ID | IndicLID | **ADOPT/CONSIDER** | Native + Romanized Indian language classes; useful for Hinglish routing, not definitive safety authority. |
| Transliteration | IndicXlit | **ADOPT/CONSIDER** | Strong Roman/native-script coverage; named entities require protection/benchmarking. |
| Hosted language services | BHASHINI | **OPTIONAL PROVIDER** | ASR/translation/TTS/transliteration/LID service ecosystem; keep replaceable. |
| Modern local TTS | IndicF5 | **BENCHMARK BEFORE ADOPTION** | Strong Indian-language quality promise; reference-audio/voice-cloning governance and latency are concerns. |
| Legacy local TTS | Indic-TTS | **REFERENCE/BENCHMARK** | Research-proven 13-language system but older deployment stack. |
| Benchmark reference | Dhruva Evaluation Suite | **REFERENCE ONLY** | Useful WER/SacreBLEU/CER/load-test patterns, not our product runtime. |
| Speech dataset | IndicVoices | **APPROVED RESEARCH CANDIDATE SUBJECT TO REVISION MANIFEST** | CC BY 4.0; broad Indian spontaneous/conversational speech useful for evaluation subsets. |
| Romanized LID benchmark | Bhasha-Abhijnaanam | **RESEARCH DATASET CANDIDATE** | Useful for IndicLID validation; pin dataset revision/license. |

### R2-B architecture refinement

SwasthyaSetu will keep these separate:

```text
SpeechToTextPort
LanguageDetectionPort
TransliterationPort
TranslationPort
TextToSpeechPort
```

Hinglish is implemented as a pipeline of speech recognition, language/script analysis, selective transliteration and optional translation. Original patient wording remains preserved as source evidence.

### BHASHINI rule

BHASHINI is an external provider. Do not make it a mandatory platform dependency, and do not assume that research/PoC access implies unrestricted production/commercial authorization.

### Voice cloning rule

Patient voice cloning is **not part of the default product**. Any TTS model requiring reference audio must use an approved system voice asset unless a future explicitly governed feature is approved.


---

## R2-C FHIR / Interoperability Research Update — 2026-10-09

| Component | R2-C decision | Intended role | Notes |
|---|---|---|---|
| HAPI FHIR | **ADOPT BEHIND ADAPTER** | FHIR validation + optional private JPA sidecar | Strongest fit with custom SwasthyaSetu domain; R4/R4B/R5, IG validation, PostgreSQL support, active ecosystem. |
| HAPI JPA Server Starter | **REFERENCE CONFIG ONLY** | Starting point for sidecar | Explicitly not production-secure by default; hardening mandatory. |
| Medplum | **CONSIDER / ARCHITECTURE-PIVOT ALTERNATIVE** | Full FHIR CDR/platform | Strong auth/SMART/audit/Postgres/security; overlaps heavily with SwasthyaSetu backend/domain. |
| LinuxForHealth FHIR | **CONSIDER SECONDARY** | Alternate R4/R4B server | Strong modular server/validation; smaller community and no decisive benefit over HAPI discovered. |
| Microsoft FHIR Server | **CONSIDER IF AZURE SELECTED** | Azure-specific FHIR server | R4 continues; R4B support ended Jul 2026; Cosmos provider support ended Sep 2026; Azure-oriented. |
| Firely .NET SDK | **REFERENCE / TEST CLIENT** | .NET parsing/client/validation | Excellent SDK, but not our server and wrong runtime for FastAPI core. |
| Google FHIR/FhirProto | **REFERENCE ONLY** | Proto/analytics utilities | Useful technology, does not solve FHIR REST/ABDM server requirement. |
| `fhir.resources` current major | **REJECT AS ABDM R4 TYPE AUTHORITY** | Python model library | Current major omits R4 in favor of R5/R4B; conflicts with ABDM R4 requirement. |
| SMART `fhirclient` | **CONSIDER FOR SMART REMOTE CLIENT** | SMART OAuth / R4 client | Relevant only when SMART app/client integration is actually required. |
| `fhirpy` | **CONSIDER FOR SIMPLE REMOTE CLIENT** | async/sync FHIR REST client | Small client option; not validator/server. |
| Plain `httpx` | **PREFERRED INITIAL REMOTE CLIENT IMPLEMENTATION** | SwasthyaSetu-owned `FHIRRemoteClientPort` | Minimal dependency; easy to control auth, retries, telemetry and ABDM-specific behavior. |

### R2-C standards decision

Primary interoperability target:

```text
FHIR R4 4.0.1
```

because the current published ABDM implementation guide is R4-based.

R5 remains a future compatibility target.

### R2-C architecture decision

Do not use a FHIR server as the product source of truth.

Use:

```text
FHIRMapper               # SwasthyaSetu-owned
FHIRValidationPort       # HAPI candidate
FHIRRepositoryPort       # optional
FHIRRemoteClientPort     # httpx initially
```

### HAPI production rule

Never deploy the starter with defaults.

Mandatory review includes:

```text
security/auth
CORS
MCP disablement
test UI/OpenAPI exposure
database credentials
schema migration
audit
rate limits
network isolation
exact version/image pin
```

### ABDM package rule

Track published and preview implementation-guide packages separately.

A preview package must never silently replace the production conformance package.


---

## R2-D Infrastructure & Security Foundation Update — 2026-10-09

| Capability | Component | R2-D decision | Notes |
|---|---|---|---|
| Self-hosted IdP | Keycloak | **PREFERRED / BENCHMARK BEFORE FINAL ADOPTION** | Mature Apache-2.0 IdP; clinician/admin and future authenticated patient identity. |
| IdP alternative | authentik | **STRONG ALTERNATIVE** | Modern self-hosted UX and security posture; strict controls required for privileged expressions/blueprints/egress. |
| Multi-tenant IdP | ZITADEL | **CONSIDER** | Strong organization/multi-tenant model; AGPL main license and more platform than currently needed. |
| Composable IAM | Ory Kratos/Hydra | **REFERENCE / FUTURE** | Strong primitives, but more integration and login UX ownership. |
| Pseudonymous patient session | SwasthyaSetu-owned | **ADOPT** | Zero-login and kiosk/MannSetu sessions should not require an IdP account. |
| Object-storage abstraction | `ObjectStoragePort` | **ADOPT** | S3/provider-neutral boundary. |
| Self-hosted object store | SeaweedFS | **PREFERRED CANDIDATE** | Active Apache-2.0 S3 ecosystem with IAM/STS, encryption, audit, lifecycle and metrics. |
| MinIO | MinIO | **REJECT AS NEW DEFAULT** | Very popular but upstream repository is archived/read-only in the current 2026 snapshot; AGPL-3.0. |
| Object-store alternative | Garage | **CONSIDER** | Lightweight/resilient; AGPL-3.0 and smaller ecosystem. |
| Background jobs | Procrastinate | **PREFERRED INITIAL CANDIDATE** | PostgreSQL-native async queue; reduces infrastructure; maintainer bus-factor requires adapter/exit path. |
| Job fallback | Celery | **MATURE FALLBACK** | Huge ecosystem and broker flexibility; more operational complexity. |
| Job alternative | Dramatiq | **CONSIDER** | Solid implementation; no decisive advantage over primary choices. |
| Job alternative | Taskiq | **WATCH / CONSIDER** | Strong async/FastAPI fit; current package metadata still marks Alpha. |
| Reliable events | PostgreSQL outbox | **ADOPT** | Same-transaction state + event reliability. |
| Ephemeral cache | Valkey | **ADOPT WHEN NEEDED** | Permissive/community Redis-compatible option; never clinical source of truth. |
| Future distributed messaging | NATS JetStream | **APPROVED FUTURE CANDIDATE** | CNCF/Apache-2.0; only after actual service extraction. |
| Self-hosted secrets | OpenBao | **PREFERRED WHEN REQUIRED** | Dynamic secrets, leases, transit encryption; operationally non-trivial. |
| Secrets alternative | Infisical | **STRONG ALTERNATIVE** | Excellent DX, rotation/PKI/machine identity; confirm OSS/enterprise feature boundary. |
| Telemetry contract | OpenTelemetry | **ADOPT** | Vendor-neutral traces/metrics/logs. |
| Collector | OTel Collector Contrib | **PREFERRED INITIAL DISTRIBUTION** | Enable only components actually used. |
| Collector alternative | Grafana Alloy | **CONSIDER** | Good OTel/Prometheus/Grafana distribution; keep app OTLP-neutral. |
| Metrics backend | Prometheus | **ADOPT FOR SELF-HOSTED/PILOT** | Mature low-cardinality metrics stack. |
| Ops dashboard | Grafana | **ADOPT/CONSIDER** | Optional operations UI; app must not depend on Grafana APIs. |
| Log backend | Loki | **DEFER** | Structured logs first; add dedicated log backend only when needed. |
| Security scanner | Trivy | **ADOPT** | Source/image/config/SBOM security scanning. |
| Secret scanner | Gitleaks | **ADOPT** | Focused high-adoption scanner; re-evaluate maintenance periodically. |

### R2-D architecture rules

```text
IdP authenticates; SwasthyaSetu authorizes clinical resources.
Pseudonymous sessions remain a SwasthyaSetu capability.
Object bytes live outside PostgreSQL; PostgreSQL owns canonical metadata.
Queue/broker state is not clinical truth.
Valkey is ephemeral.
Reliable events use in-process dispatch + PostgreSQL outbox before an external bus.
NATS is a future extraction tool, not an MVP dependency.
Secrets are provider-neutral.
OpenTelemetry/OTLP is the telemetry contract.
Normal operational telemetry excludes PHI.
Audit records are distinct from operational observability.
```

### R2-D timing rule

Research approval does **not** mean "add this service to the default Compose stack".

A provider is introduced only in the implementation phase that actually needs the capability.


---

## R2-E AI / ML / QML Runtime & Model-Governance Update — 2026-10-09

| Capability | Project | R2-E decision | Notes |
|---|---|---|---|
| LLM provider boundary | SwasthyaSetu `LLMProvider` | **ADOPT** | Stable project-owned interface; direct provider adapter first. |
| LLM normalization SDK | LiteLLM SDK/core | **CONSIDER** | Very broad provider coverage; useful if direct adapters become repetitive. |
| Central LLM gateway | LiteLLM Proxy | **DEFER / CONDITIONAL** | High adoption but current architecture brings Redis, PostgreSQL, auth, spend/routing/admin/scheduler overlap. MIT core + separate enterprise subtree. |
| Experiment tracking | MLflow | **ADOPT FOR RESEARCH** | Mature Apache-2.0 experiment tracking/evaluation; keep separate from clinical DB. |
| Model registry metadata | MLflow Model Registry | **ADOPT, SUBORDINATE TO GOVERNANCE** | Registry stage/version does not equal clinical production approval. |
| MLflow LLM tracing | MLflow | **OFF FOR PATIENT TRAFFIC BY DEFAULT** | Automatic tracing can capture prompts/outputs. |
| MLflow AI gateway | MLflow | **NOT DEFAULT** | Avoid overlapping gateway stacks. |
| Classical ML | scikit-learn | **ADOPT** | Core preprocessing/calibration/metrics/baselines. |
| Classical boosting | XGBoost | **TASK-DEPENDENT** | Strong tabular baseline; version/model-card controlled. |
| Deep learning | PyTorch | **TASK-DEPENDENT** | Use when justified by task/data. |
| HPO | Optuna | **ADOPT/CONSIDER FOR RESEARCH** | v5 active; test-set leakage prohibited. |
| Explainability | SHAP | **PRIMARY WHERE APPROPRIATE** | Attribution only, not causality. |
| sklearn safe persistence | skops | **PREFERRED WHEN COMPATIBLE** | Secure persistence design without pickle; explicit trusted types. |
| Portable inference | ONNX Runtime | **PREFERRED WHEN PARITY PASSES** | Active MIT runtime; disable vendor telemetry for healthcare profile. |
| General extracted model service | BentoML | **CONSIDER LATER** | Good service packaging/OTel/health; not needed for small in-process models. |
| Kubernetes inference | KServe | **FUTURE** | CNCF/K8s model-fleet platform; premature for modular monolith. |
| GPU inference server | Triton | **FUTURE SPECIALIZED** | High-throughput GPU serving only when needed. |
| Self-hosted LLM serving | vLLM | **FUTURE CANDIDATE** | Very active/high-adoption; GPU/runtime heavy, not MVP. |
| Vector storage | pgvector | **ADOPT** | Fits canonical PostgreSQL architecture. |
| Local embeddings/rerankers | Sentence Transformers | **PREFERRED CANDIDATE** | Pin exact model revision; model license reviewed separately. |
| RAG/agent framework | LangChain | **NOT CORE/DEFAULT** | Broad agent platform adds unnecessary surface for governed retrieval. |
| RAG/agent framework | LlamaIndex | **NOT CORE/DEFAULT** | Broad toolkit; current project focus shifted toward parsing/extraction products. |
| RAG pipeline framework | Haystack | **CONSIDER LATER** | Production/stable Apache-2.0, but security policy leaves SSRF/injection/untrusted-pipeline controls to app/operator. |
| LLM eval | Project-native pytest | **PRIMARY** | Directly tests schemas and deterministic safety invariants. |
| LLM red-team/eval | Promptfoo | **OPTIONAL** | Treat configs/plugins as executable/trusted code; isolated offline/CI use. |
| LLM eval alternative | DeepEval | **ALTERNATIVE** | Do not adopt multiple overlapping frameworks initially. |
| QML framework | PennyLane | **PRIMARY** | Hybrid QML + device abstraction + simulator-first workflow. |
| QML comparison | Qiskit Machine Learning | **ADOPT SECONDARY** | Explicit VQC, QSVC/quantum kernels, QNN implementation; useful IBM/Qiskit path. |
| Quantum SDK | Qiskit | **ADOPT THROUGH QML RESEARCH LAYER** | Backend/primitives/transpilation for Qiskit ML. |
| Model drift/evaluation | Evidently | **DEFER** | Revisit once a deployed model has real monitoring/labels. |

### R2-E model safety invariants

```text
Model output never downgrades deterministic safety.
MLflow is not clinical authority.
Model artifacts are trusted-origin, immutable and hashed.
Arbitrary pickle/joblib/dill/cloudpickle uploads are prohibited.
Threshold/calibration versions are separate from weights.
RAG uses approved versioned corpora with provenance.
Broad agent frameworks are not required for RAG.
QML is research/simulator-first and cannot claim advantage without fair benchmarks.
General telemetry excludes clinical prompts/responses.
```

### R2-E minimal implementation rule

Do not add every research dependency to the main API environment.

Use dependency groups/profiles, for example conceptually:

```text
core
ml-research
qml-research
rag-local
model-serving
```

The patient API should not import Qiskit/PennyLane/MLflow merely because they exist in the monorepo.


---

## R3 Reconciled Final Adoption Register — 2026-10-10

R3 overrides ambiguous earlier shorthand such as "ADOPT" when that could be interpreted as "install in the default runtime."

| Capability | Preferred technology | R3 final status | Runtime rule |
|---|---|---|---|
| Core API | FastAPI/Pydantic | **CORE** | base runtime |
| Persistence | PostgreSQL/SQLAlchemy/Alembic | **CORE** | base runtime |
| Vector retrieval | pgvector | **ACTIVATE WITH RAG** | same PostgreSQL |
| Pseudonymous sessions | SwasthyaSetu-owned | **CORE** | no IdP required |
| Authenticated IdP | Keycloak | **PREFERRED / SPIKE-GATED** | identity phase only |
| Object storage | `ObjectStoragePort` | **CORE CONTRACT** | local adapter first |
| Self-hosted object store | SeaweedFS | **PREFERRED LATER** | document/pilot profile |
| Background jobs | `JobDispatcher` | **CORE CONTRACT** | in-process test/local |
| Durable jobs | Procrastinate | **PREFERRED / SPIKE-GATED** | async phase |
| Durable-job fallback | Celery | **FALLBACK** | only if needed |
| Reliable events | PostgreSQL outbox | **ADOPT** | product DB |
| Cache | Valkey | **OPTIONAL** | never source of truth |
| Service messaging | NATS JetStream | **FUTURE** | no early broker |
| Secret management | `SecretProvider` | **CORE CONTRACT** | environment/local |
| Self-hosted secret manager | OpenBao | **LATER** | protected deployment |
| Observability | OpenTelemetry | **ADOPT CONTRACT** | application instrumentation |
| Metrics | Prometheus | **PILOT/SELF-HOSTED** | ops profile |
| Dashboard | Grafana | **OPTIONAL** | ops profile |
| Log backend | Loki | **DEFER** | structured logs first |
| Security scan | Trivy | **ADOPT CI** | CI |
| Secret scan | Gitleaks | **ADOPT CI** | CI |
| OCR | PaddleOCR | **PREFERRED BASELINE / BENCHMARK-GATED** | document worker profile |
| Document parser | Docling | **ADOPT/CONSIDER** | behind parser port |
| OCR challenger | Surya | **BENCHMARK** | research/spike only |
| ASR baseline | faster-whisper | **BASELINE/FALLBACK** | language profile |
| India ASR | IndicConformer | **BENCHMARK-GATED** | language profile |
| Translation | IndicTrans2 | **PREFERRED** | behind port |
| Language ID | IndicLID | **CANDIDATE** | behind port |
| Transliteration | IndicXlit | **CANDIDATE** | behind port |
| Hosted India language services | BHASHINI | **OPTIONAL PILOT** | external adapter |
| FHIR | HAPI FHIR | **ADOPT SIDE-CAR** | P16 |
| FHIR remote client | project-owned httpx adapter | **PREFERRED** | P16/P17 |
| LLM boundary | SwasthyaSetu `LLMProvider` | **ADOPT** | in-process orchestration |
| LiteLLM SDK | LiteLLM | **CONSIDER** | optional adapter internals |
| LiteLLM Proxy | LiteLLM | **DEFER** | not MVP |
| ML experiments | MLflow | **ADOPT RESEARCH** | separate research profile |
| Classical ML | scikit-learn | **ADOPT** | P18 |
| HPO | Optuna | **RESEARCH** | P18 |
| Explainability | SHAP | **ADOPT WHERE APPROPRIATE** | P18 |
| Safe sklearn persistence | skops | **PREFERRED** | approved models |
| Portable inference | ONNX Runtime | **PREFERRED IF PARITY PASSES** | inference adapter |
| Embeddings/rerankers | Sentence Transformers | **PREFERRED CANDIDATE** | RAG profile |
| RAG framework | LangChain | **NOT CORE** | explicit future decision only |
| RAG framework | LlamaIndex | **NOT CORE** | explicit future decision only |
| RAG framework | Haystack | **CONDITIONAL FUTURE** | complex pipeline only |
| LLM eval | pytest fixtures | **PRIMARY** | dev/test |
| LLM red-team eval | Promptfoo | **OPTIONAL RESEARCH** | isolated |
| QML | PennyLane | **PRIMARY RESEARCH** | P19 profile |
| QML | Qiskit Machine Learning | **SECONDARY RESEARCH** | P19 profile |
| Model service | BentoML | **CONDITIONAL FUTURE** | extraction only |
| K8s inference | KServe | **FUTURE** | no early Kubernetes |
| GPU inference | Triton | **FUTURE** | specialized workload |
| Self-hosted LLM server | vLLM | **FUTURE** | explicit self-hosted decision |
| Model monitoring | Evidently | **FUTURE** | after deployed model/labels |
| MinIO | MinIO | **REJECTED AS NEW DEFAULT** | existing-system integration only |

### R3 precedence

Where an earlier register row says `ADOPT BEHIND ADAPTER` but R3 says `BENCHMARK-GATED`, `RESEARCH`, `LATER` or `DEFER`, the R3 lifecycle classification controls implementation timing.

---

## P3-A persistence activation — 2026-10-11

| Component | Locked version | License | R3 class | Activated scope |
|---|---:|---|---|---|
| SQLAlchemy | 2.1.4 | MIT | CORE_RUNTIME | Async PostgreSQL engine, sessions, metadata, transactions |
| Alembic | 1.20.0 | MIT | CORE_RUNTIME | Explicit reviewed migration lineage and drift checks |
| Psycopg / psycopg-binary | 3.3.6 | LGPL-3.0-only | CORE_RUNTIME | PostgreSQL driver with binary wheels for host/container runtime |

No database extension, external exporter, cache, broker, worker, or object-storage service was
activated with these components.
